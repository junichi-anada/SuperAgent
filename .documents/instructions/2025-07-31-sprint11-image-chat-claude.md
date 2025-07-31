# 指示書: Sprint 11 - 画像付きAIチャット実装 (モック)

## 1. 目的
チャット対話において、AIが画像を返信できる機能をモックで実装する。
**注意:** このタスクはモック環境での実装を対象とします。実際のAI (ComfyUI) との連携は範囲外です。

## 2. 指示方針
- **技術スタック:** FastAPI, Next.js, SQLAlchemy, Alembicを使用すること。
- **参考資料:** プロジェクトの全体像や細かい仕様で迷ったら、必ず `.documents/Project.md` を確認すること。
- **コーディング規約:** PythonはPEP8、JavaScriptはPrettierの標準ルールに従うこと。
- **アウトプット形式:** 作業が完了したら、変更・追加したファイルのパスと、それぞれの作業内容の簡単なサマリーをJSON形式で報告すること。
- **進捗報告:** 以下の作業手順を1つ実行するごとに、「ステップX完了」と簡潔に報告すること。

## 3. 作業手順

### ステップ1: バックエンドの機能拡張
1.  **モデルとスキーマの修正:** `backend/models.py` と `backend/schemas.py` の `Message` モデル/スキーマに、`image_url` (String, nullable) を追加してください。
2.  **マイグレーション:** `alembic revision --autogenerate -m "Add image_url to messages"` と `alembic upgrade head` を実行して、DBを更新してください。
3.  **WebSocketの修正:** `backend/routers/chat.py` のWebSocketエンドポイントを修正し、AIからのモック返信メッセージに、ダミーの画像URL (`https://via.placeholder.com/300`) を含めてDBに保存し、クライアントに送信するようにしてください。

### ステップ2: フロントエンドの画像表示実装
- **ファイル:** `frontend/pages/chats/[id].js` を修正してください。
- **作業内容:**
    1.  WebSocketで受信したメッセージオブジェクトに `image_url` が含まれている場合、メッセージテキストの下にその画像を表示するロジックを追加してください。
    2.  画像は `<img>` タグを使用して表示してください。

## 4. 完了報告
全ての作業が完了したら、最終的な成果物として、指示方針で定めた通りのJSON報告を行ってください。
