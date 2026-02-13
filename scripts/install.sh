#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/ikun245/Telegram-toujibot.git"
PROJECT_DIR="${PROJECT_DIR:-Telegram-touji}"

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] 未检测到 Docker，请先安装 Docker。"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "[ERROR] 未检测到 docker compose / docker-compose。"
  exit 1
fi

if [ ! -d "$PROJECT_DIR/.git" ]; then
  git clone "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

if [ ! -f config.json ] && [ -f config.example.json ]; then
  cp config.example.json config.json
fi

echo "[INFO] 请先编辑 config.json，填写 API 和频道参数。"
echo "[INFO] 编辑完成后按回车继续启动容器..."
read -r _

$COMPOSE_CMD up -d --build

echo "[OK] 服务已启动。查看日志：$COMPOSE_CMD logs -f"
