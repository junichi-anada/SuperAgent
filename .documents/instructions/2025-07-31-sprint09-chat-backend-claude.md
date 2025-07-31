# 指示書: Sprint 9 - AIチャットバックエンド実装

## 1. 目的
ユーザーとAIエージェント間の対話を可能にするための、チャット機能のバックエンドを実装する。

## 2. 指示方針
- **技術スタック:** FastAPI, SQLAlchemy, Alembicを使用すること。
- **参考資料:** プロジェクトの全体像や細かい仕様で迷ったら、必ず `.documents/Project.md` を確認すること。
- **コーディング規約:** PythonはPEP8に従うこと。
- **アウトプット形式:** 作業が完了したら、変更・追加したファイルのパスと、それぞれの作業内容の簡単なサマリーをJSON形式で報告すること。
- **進捗報告:** 以下の作業手順を1つ実行するごとに、「ステップX完了」と簡潔に報告すること。

## 3. 作業手順

### ステップ1: DBモデルとマイグレーションの作成
1.  **モデルの追加:** `backend/models.py` に `Chat` と `Message` モデルを追加してください。
    - `Chat` モデル: `id`, `user_id` (FK to users), `agent_id` (FK to agents), `created_at`
    - `Message` モデル: `id`, `chat_id` (FK to chats), `content`, `sender` (user or ai), `created_at`
2.  **マイグレーションファイルの生成:** `alembic revision --autogenerate -m "Create chats and messages tables"` を実行してください。
3.  **DBへの適用:** `alembic upgrade head` を実行して、テーブルをデータベースに作成してください。

### ステップ2: スキーマとCRUDの追加
1.  **スキーマの追加:** `backend/schemas.py` に `Chat`, `Message`, `MessageCreate` などのPydanticスキーマを追加してください。
2.  **CRUD関数の追加:** `backend/crud.py` に、チャットセッションとメッセージを作成・取得するための関数を追加してください。

### ステップ3: APIエンドポイントの実装
1.  **ルーターの作成:** `backend/routers/chat.py` を新規作成してください。
2.  **エンドポイントの実装:**
    - `POST /chats/`: 新しいチャットセッションを開始する。
    - `GET /chats/{chat_id}/messages`: 特定のチャットのメッセージ履歴を取得する。
    - `POST /chats/{chat_id}/messages`: 新しいメッセージを送信する。
        - **重要:** このエンドポイントは、ユーザーからのメッセージをDBに保存した後、Sprint 2で作成したモックAPI (`/api/v1/chat/mock`) を内部的に呼び出し、その応答をAIからのメッセージとしてDBに保存する処理も実装してください。
3.  **認証:** 全てのエンドポイントをJWT認証で保護してください。
4.  **メインアプリへの統合:** `backend/main.py` で、作成した `chat` ルーターをインクルードしてください。

## 4. 完了報告
全ての作業が完了したら、最終的な成果物として、指示方針で定めた通りのJSON報告を行ってください。
