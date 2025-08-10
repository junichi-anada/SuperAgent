#!/bin/sh

# データベースのマイグレーションを実行
alembic upgrade head

# Uvicornサーバーを起動
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --ws websockets
