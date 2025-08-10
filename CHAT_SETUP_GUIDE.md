# チャット機能セットアップガイド

このドキュメントでは、SuperAgentのチャット機能の設定方法と使用方法について説明します。

## 📋 目次

1. [環境設定](#環境設定)
2. [チャット機能の概要](#チャット機能の概要)
3. [トラブルシューティング](#トラブルシューティング)
4. [開発者向け情報](#開発者向け情報)

## 環境設定

### 1. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```bash
# .envファイルの作成
cp .env.example .env

# 必須の環境変数
GOOGLE_API_KEY=your-google-api-key-here  # Google Gemini APIキー
DATABASE_URL=postgresql://user:password@db:5432/superagent  # データベース接続URL

# オプション（画像生成機能を使用する場合）
IMAGE_GENERATION_PROVIDER=webui  # webui, huggingface, modelslab から選択
WEBUI_API_URL=http://stable-diffusion-webui-cpu:8080  # WebUI使用時のURL
```

### 2. サービスの起動

```bash
# すべてのサービスを起動
docker-compose up -d

# 特定のプロファイルで起動（CPU版WebUIを含む場合）
docker-compose --profile cpu up -d
```

### 3. データベースのマイグレーション

```bash
# バックエンドコンテナに入る
docker-compose exec backend bash

# マイグレーションを実行
cd /app
alembic upgrade head
```

## チャット機能の概要

### 主な機能

1. **リアルタイムチャット**
   - WebSocketを使用したリアルタイム通信
   - 自動再接続機能
   - エラーハンドリング

2. **AI応答生成**
   - Google Gemini APIを使用した応答生成
   - エージェントのパーソナリティを反映した応答
   - コンテキストを考慮した会話

3. **画像生成機能**（オプション）
   - Stable Diffusion WebUIとの連携
   - 会話内容に基づく画像生成
   - 生成された画像の保存とギャラリー表示

### 使用方法

1. **ユーザー登録/ログイン**
   ```
   http://localhost:3000/signup  # 新規登録
   http://localhost:3000/login   # ログイン
   ```

2. **エージェントの作成**
   - ログイン後、「+ 新しいエージェントを作成」をクリック
   - 名前、性格、外見などを設定

3. **チャットの開始**
   - エージェント詳細ページから「チャットを開始」をクリック
   - メッセージを入力して送信

## トラブルシューティング

### WebSocket接続エラー

**症状**: チャットが接続されない、メッセージが送信できない

**解決方法**:
1. ブラウザのコンソールでエラーを確認
2. バックエンドのログを確認：`docker-compose logs backend`
3. 認証トークンが正しく送信されているか確認

### AI応答が返ってこない

**症状**: メッセージを送信してもAIからの応答がない

**解決方法**:
1. Google API キーが正しく設定されているか確認
2. バックエンドのログでエラーを確認
3. LLMサービスのエラーハンドリングを確認

### 画像生成が機能しない

**症状**: 画像生成リクエストをしても画像が生成されない

**解決方法**:
1. Stable Diffusion WebUIが起動しているか確認
2. `WEBUI_API_URL`が正しく設定されているか確認
3. WebUIのAPIが有効になっているか確認

## 開発者向け情報

### テストツール

チャット機能の動作確認用スクリプトが用意されています：

```bash
# テストスクリプトの実行
cd backend
python test_chat_functionality.py --user testuser --password testpass
```

このスクリプトは以下をテストします：
- ユーザー認証
- REST APIでのメッセージ送信
- WebSocket接続とリアルタイム通信
- 画像生成機能（設定されている場合）

### アーキテクチャ

```
フロントエンド (Next.js)
    ↓
WebSocket / REST API
    ↓
バックエンド (FastAPI)
    ↓
┌─────────────┬──────────────┬─────────────────┐
│ LLM Service │ Image Service│ Database        │
│ (Gemini)    │ (WebUI)      │ (PostgreSQL)    │
└─────────────┴──────────────┴─────────────────┘
```

### 主要なファイル

- **バックエンド**
  - `backend/routers/chat.py` - チャットAPIエンドポイント
  - `backend/services/llm_service.py` - LLM統合サービス
  - `backend/services/prompt_builder.py` - プロンプト構築
  - `backend/services/error_handler.py` - エラーハンドリング

- **フロントエンド**
  - `frontend/components/ChatWindow.js` - チャットUI
  - `frontend/pages/chats/[id].js` - チャットページ
  - `frontend/contexts/AuthContext.js` - 認証コンテキスト

### デバッグ方法

1. **バックエンドログの確認**
   ```bash
   docker-compose logs -f backend
   ```

2. **WebSocketトラフィックの監視**
   - ブラウザの開発者ツール → Network → WS タブ
   - メッセージの送受信を確認

3. **データベースの確認**
   ```bash
   docker-compose exec db psql -U user -d superagent
   \dt  # テーブル一覧
   SELECT * FROM chats;  # チャット一覧
   SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;  # 最新メッセージ
   ```

### パフォーマンスチューニング

1. **WebSocket接続の最適化**
   - 再接続の間隔調整（`reconnectDelay`）
   - 最大再接続回数の調整（`maxReconnectAttempts`）

2. **LLM応答の最適化**
   - タイムアウト設定（`WEBUI_TIMEOUT`）
   - コンテキストサイズの調整

3. **データベースの最適化**
   - インデックスの追加
   - 古いメッセージの定期削除

## 📝 更新履歴

- 2025-08-10: 初版作成
  - WebSocket認証の修正
  - エラーハンドリングの改善
  - フロントエンドの安定性向上

## 🤝 貢献

問題や改善提案がある場合は、GitHubのIssueまたはPull Requestでお知らせください。