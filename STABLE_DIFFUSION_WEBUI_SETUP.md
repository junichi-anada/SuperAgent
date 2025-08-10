# Stable Diffusion WebUI 統合ガイド

このプロジェクトにStable Diffusion WebUIが正常に統合されました。アダルトコンテンツ対応の高品質な画像生成が可能です。

## 🎯 主な機能

- **ローカル実行**: プライバシー保護、検閲なし
- **アダルトコンテンツ対応**: NSFWフィルターなし
- **高品質画像生成**: 豊富なモデルとカスタマイズ
- **既存システム統合**: 既存の画像生成フローに統合
- **プロバイダー選択**: フロントエンドで生成方式を選択可能

## 🚀 セットアップ手順

### 1. 環境変数の設定

`.env`ファイルを作成し、以下の設定を追加：

```bash
# 画像生成プロバイダーを WebUI に設定
IMAGE_GENERATION_PROVIDER=webui

# WebUI API URL（通常はデフォルトのままでOK）
WEBUI_API_URL=http://stable-diffusion-webui:7860
```

### 2. Docker Composeでサービス起動

GPU対応でStable Diffusion WebUIを起動：

```bash
# GPU対応でWebUIサービスを起動（NVIDIA GPUがある場合）
docker-compose --profile gpu up stable-diffusion-webui

# CPU専用でWebUIサービスを起動（WSL環境や GPU無しの場合）
docker-compose --profile cpu up stable-diffusion-webui-cpu

# または全サービスをGPU対応で起動
docker-compose --profile gpu up
```

**重要**:
- universonic/stable-diffusion-webui:latestイメージを使用（DockerHub公式）
- 初回起動時は、Stable Diffusion WebUIのダウンロードとインストールに時間がかかります（数GB〜10GB程度）
- **WSL環境の場合**: GPU版でエラーが出る場合は、CPU版を使用してください
- CPU版は処理速度が遅くなりますが、どの環境でも動作します

**ポート設定**:
- GPU版: http://localhost:7860
- CPU版: http://localhost:7861

**環境変数設定**:
CPU版を使用する場合は、`.env`ファイルで以下を設定：
```bash
WEBUI_API_URL=http://localhost:7861
```

### 3. WebUIの初期設定

WebUIが起動したら、ブラウザで `http://localhost:7860` にアクセス：

1. **モデルのダウンロード**:
   - `Settings` → `Stable Diffusion` → `SD model checkpoint`
   - 推奨モデル（アダルトコンテンツ対応）:
     - ChilloutMix
     - RealisticVision
     - Anything V3/V4/V5

2. **API設定の有効化**:
   - `Settings` → `API` → `Enable API` をチェック
   - `Apply settings` をクリック

3. **セキュリティ設定**:
   - `Settings` → `User interface` → `Disable safety filter` をチェック
   - アダルトコンテンツ生成を有効化

## 🧪 動作テスト

統合テストスクリプトを実行して動作確認：

```bash
cd backend
python test_stable_diffusion_webui.py
```

テスト内容：
- ✅ WebUI API接続確認
- ✅ モデル一覧取得
- ✅ 最適モデル選択
- ✅ 画像生成テスト
- ✅ エラーハンドリング
- ✅ 同期/非同期インターフェース

## 💻 使用方法

### フロントエンドから使用

1. エージェント作成/編集画面で「画像生成プロバイダー」を「Stable Diffusion WebUI」に選択
2. エージェントの外見情報を設定
3. 「画像を生成」ボタンをクリック

### プロバイダー比較

| プロバイダー | 特徴                         | 用途                                 |
| ------------ | ---------------------------- | ------------------------------------ |
| **WebUI**    | ローカル実行、無制限、高品質 | アダルトコンテンツ、プライバシー重視 |
| HuggingFace  | クラウドAPI、制限あり        | 一般的なコンテンツ                   |
| ModelsLab    | クラウドAPI、高品質、有料    | 商用利用                             |

## 🔧 高度な設定

### カスタムモデルの追加

1. モデルファイル（.safetensors）を以下にコピー：
   ```
   webui_models/Stable-diffusion/
   ```

2. WebUIで新しいモデルを選択

### 生成パラメータのカスタマイズ

`backend/services/llm_clients/stable_diffusion_webui_client.py` で設定変更可能：

- `width`, `height`: 画像サイズ
- `steps`: 生成ステップ数（品質に影響）
- `cfg_scale`: プロンプト従順度
- `sampler_name`: サンプラー選択

## 🛠️ トラブルシューティング

### WebUIに接続できない場合

1. **Dockerコンテナの確認**:
   ```bash
   docker-compose ps
   ```

2. **ログの確認**:
   ```bash
   docker-compose logs stable-diffusion-webui
   ```

3. **ポートの確認**:
   ```bash
   curl http://localhost:7860/sdapi/v1/progress
   ```

### GPU関連のエラー

1. **NVIDIA Docker確認**:
   ```bash
   nvidia-docker --version
   nvidia-smi
   ```

2. **Docker Compose設定確認**:
   - `docker-compose.yml`のGPU設定を確認
   - `--profile gpu`オプションの使用を確認

### モデルが見つからない場合

1. **モデルディレクトリの確認**:
   ```bash
   docker exec -it <webui-container> ls /app/stable-diffusion-webui/models/Stable-diffusion/
   ```

2. **モデルのダウンロード**:
   - WebUI経由でモデルをダウンロード
   - 手動でモデルファイルを配置

## 📝 開発者向け情報

### アーキテクチャ

```
Frontend (Next.js)
    ↓ HTTP Request
Backend (FastAPI)
    ↓ ImageGenerationService
WebUI Client
    ↓ HTTP API
Stable Diffusion WebUI (Docker)
    ↓ GPU Processing
Generated Image
```

### 主要ファイル

- `docker-compose.yml`: WebUIサービス定義
- `backend/services/llm_clients/stable_diffusion_webui_client.py`: WebUI APIクライアント
- `backend/services/image_generation_service.py`: 画像生成サービス（拡張済み）
- `frontend/components/AgentForm.js`: フロントエンド統合
- `backend/routers/agents.py`: API エンドポイント（更新済み）

### API仕様

画像生成エンドポイント:
```
POST /api/v1/agents/{agent_id}/generate-image
Content-Type: application/json

{
  "force_regenerate": true,
  "provider": "webui"
}
```

## 🎉 統合完了

Stable Diffusion WebUIが正常に統合されました！

### 主な利点

✅ **プライバシー保護**: すべてローカルで処理  
✅ **無制限生成**: APIリミットやコスト制限なし  
✅ **アダルトコンテンツ対応**: NSFWフィルターなし  
✅ **高品質**: 最新の生成モデルを使用  
✅ **カスタマイズ可能**: 豊富な設定オプション  
✅ **既存統合**: 既存のワークフローにシームレス統合  

エージェントの魅力的な画像生成をお楽しみください！