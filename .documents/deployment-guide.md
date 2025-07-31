# デプロイ手順書

## 1. 目的
本番環境にアプリケーションをデプロイするための手順を定める。

## 2. 前提条件
- DockerおよびDocker Composeがインストール済みのサーバーが用意されていること。
- Gitリポジトリへのアクセス権があること。

## 3. デプロイ手順

### 3.1. ソースコードの取得
```bash
git clone https://github.com/junichi-anada/SuperAgent.git
cd SuperAgent
```

### 3.2. 環境変数の設定
- `.env` ファイルをプロジェクトルートに作成し、以下の内容を記述・編集します。
- **注意:** `SECRET_KEY` は必ず強固なランダム文字列に変更してください。

```dotenv
# Backend
DATABASE_URL=postgresql://user:password@db:5432/superagent
SECRET_KEY=your-super-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://<your-server-ip-or-domain>:8000
```

### 3.3. アプリケーションのビルドと起動
- 以下のコマンドを実行して、Dockerイメージをビルドし、コンテナをバックグラウンドで起動します。

```bash
docker-compose up --build -d
```

### 3.4. データベースのマイグレーション
- アプリケーションの初回起動時、またはDBスキーマに変更があった場合に実行します。

```bash
docker-compose exec backend alembic upgrade head
```

## 4. 動作確認
- ブラウザで `http://<your-server-ip-or-domain>:3000` にアクセスし、フロントエンドが表示されることを確認します。
- サインアップ、ログイン、エージェント作成、チャット機能が一通り動作することを確認します。
