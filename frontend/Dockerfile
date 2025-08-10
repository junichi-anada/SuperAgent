# Node.jsの公式イメージをベースにする
FROM node:latest

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をキャッシュするために、package.jsonを先にコピー
COPY package*.json ./

# ディレクトリの所有権をnodeユーザーに変更
RUN chown -R node:node /app

# ユーザーをnodeに切り替え
USER node

# 依存関係をインストール
RUN npm install

# アプリケーションのコードをコピー
COPY . .

# ビルド時の環境変数を設定
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# アプリケーションをビルド
RUN npm run build

# 3000番ポートでアプリケーションを起動
EXPOSE 3000
CMD ["npm", "run", "dev"]
