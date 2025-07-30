# Node.jsの公式イメージをベースにする
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係をインストール
COPY package*.json ./
RUN npm install

# アプリケーションのコードをコピー
COPY . .

# アプリケーションをビルド
RUN npm run build

# 3000番ポートでアプリケーションを起動
EXPOSE 3000
CMD ["npm", "run", "dev"]
