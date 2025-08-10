# 画像生成機能セットアップガイド

このガイドでは、SuperAgentの画像生成機能のセットアップと使用方法を説明します。

## 概要

SuperAgentは3つの画像生成プロバイダーをサポートしています：

1. **Hugging Face** - デフォルトのプロバイダー（無料、要APIキー）
2. **ModelsLab** - 高品質な画像生成（有料、要APIキー）
3. **Stable Diffusion WebUI** - ローカル実行（無料、要セットアップ）

## セットアップ

### 1. 環境変数の設定

`.env`ファイルに以下の設定を追加します：

```bash
# 画像生成プロバイダーの選択
# Options: huggingface, modelslab, webui
IMAGE_GENERATION_PROVIDER=webui

# Hugging Face（デフォルト）を使用する場合
HUGGINGFACE_API_KEY=your-huggingface-api-key-here

# ModelsLabを使用する場合
MODELSLAB_API_KEY=your-modelslab-api-key-here
MODELSLAB_MODEL_ID=your-model-id-here

# Stable Diffusion WebUIを使用する場合
# GPU版
WEBUI_API_URL=http://stable-diffusion-webui:7860
# CPU版（デフォルト）
WEBUI_API_URL=http://stable-diffusion-webui-cpu:8080

# タイムアウト設定（秒）
WEBUI_TIMEOUT=600
```

### 2. Stable Diffusion WebUIのセットアップ（webui使用時）

詳細は[STABLE_DIFFUSION_WEBUI_SETUP.md](./STABLE_DIFFUSION_WEBUI_SETUP.md)を参照してください。

#### CPU版の起動（推奨）

```bash
# docker-compose.ymlにCPU版の設定が含まれています
docker-compose up -d stable-diffusion-webui-cpu
```

#### GPU版の起動

```bash
# docker-compose.ymlのコメントを解除してGPU版を有効化
docker-compose up -d stable-diffusion-webui
```

## 画像生成機能の使い方

### チャット内での画像生成

エージェントとのチャットで以下のようなメッセージを送信すると、画像が生成されます：

- 「写真を見せてください」
- 「あなたの画像が欲しいです」
- 「写真を送って」
- 「全身の写真が見たい」
- 「別角度の写真はありますか？」
- 「今日の写真を見せて」
- 「公園での写真が見たいです」

### 画像生成の流れ

1. **リクエスト検出**: `ImageRequestDetector`がユーザーメッセージから画像要求を検出
2. **プロンプト生成**: `ImagePromptAnalyzer`がエージェントの属性と会話コンテキストからプロンプトを生成
3. **画像生成**: 選択されたプロバイダーで画像を生成
4. **保存と配信**: 生成された画像を保存し、WebSocket経由でユーザーに配信

### エージェント属性と画像生成

エージェントの以下の属性が画像生成に使用されます：

- **基本属性**: gender, ethnicity, age
- **外見**: hair_style, hair_color, eye_color, body_type
- **服装**: clothing
- **背景**: background

これらの属性を詳細に設定することで、より一貫性のある画像が生成されます。

## テスト

### 画像生成機能のテスト

```bash
cd backend
python test_chat_image_generation.py
```

このテストスクリプトは以下を確認します：
- 画像リクエストの検出
- WebSocket経由での画像生成
- 生成された画像URLの有効性
- チャット履歴での画像表示

### 個別機能のテスト

```bash
# 画像生成サービスの直接テスト
python test_image_generation.py

# エージェント画像生成テスト
python test_agent_image_generation.py

# WebUI接続テスト
python test_stable_diffusion_webui.py
```

## トラブルシューティング

### 1. 画像が生成されない

**確認事項**:
- 環境変数が正しく設定されているか
- 選択したプロバイダーのAPIキーが有効か
- WebUIを使用している場合、コンテナが起動しているか

```bash
# 環境変数の確認
docker-compose exec backend env | grep IMAGE

# WebUIの状態確認
docker-compose ps stable-diffusion-webui-cpu

# ログの確認
docker-compose logs -f backend
```

### 2. WebUI接続エラー

**解決方法**:
```bash
# WebUIの再起動
docker-compose restart stable-diffusion-webui-cpu

# 接続テスト
curl http://localhost:8080/sdapi/v1/txt2img
```

### 3. タイムアウトエラー

**解決方法**:
- `WEBUI_TIMEOUT`を増やす（デフォルト: 600秒）
- CPU版の場合、画像生成に時間がかかるため待つ
- サーバーのリソースを確認

### 4. メモリ不足エラー

**解決方法**:
- Docker のメモリ制限を増やす
- 画像解像度を下げる（512x512推奨）
- 不要なコンテナを停止する

## パフォーマンス最適化

### 1. 画像キャッシュ

生成された画像は自動的にキャッシュされ、同じエージェントの画像は再利用されます。

### 2. 非同期生成

画像生成は非同期で実行され、進捗状況がWebSocket経由でリアルタイムに通知されます。

### 3. シード値の保存

生成された画像のシード値が保存され、一貫性のある画像生成が可能です。

## セキュリティ考慮事項

1. **APIキーの管理**: 環境変数でAPIキーを管理し、コードにハードコードしない
2. **画像の保存場所**: 生成された画像は`backend/static/agent_images/`に保存される
3. **アクセス制御**: 画像URLは認証されたユーザーのみアクセス可能

## 今後の改善点

1. **画像の品質向上**: より高度なプロンプトエンジニアリング
2. **複数画像の生成**: 異なるポーズや角度の画像を同時生成
3. **画像編集機能**: 既存画像の編集・加工
4. **バッチ処理**: 複数エージェントの画像を一括生成

## 関連ドキュメント

- [CHAT_SETUP_GUIDE.md](./CHAT_SETUP_GUIDE.md) - チャット機能の詳細
- [STABLE_DIFFUSION_WEBUI_SETUP.md](./STABLE_DIFFUSION_WEBUI_SETUP.md) - WebUIの詳細設定
- [README.md](./README.md) - プロジェクト全体のドキュメント