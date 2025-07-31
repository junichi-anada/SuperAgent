# Pythonの公式イメージをベースにする
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# entrypoint.shに実行権限を付与
RUN chmod +x /app/entrypoint.sh

# エントリーポイントを設定
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
