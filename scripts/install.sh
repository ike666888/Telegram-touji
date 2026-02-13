#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-}"
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

if [ ! -d "$PROJECT_DIR/.git" ] && [ -z "$REPO_URL" ]; then
  echo "[ERROR] 未设置 REPO_URL，无法自动克隆仓库。"
  echo "[HINT] 例如: REPO_URL=https://github.com/<你的用户名>/Telegram-touji.git bash scripts/install.sh"
  exit 1
fi

if [ ! -d "$PROJECT_DIR/.git" ]; then
  echo "[INFO] 克隆仓库到 $PROJECT_DIR"
  git clone "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

if [ -f config.json ]; then
  read -r -p "[INFO] 检测到 config.json，是否重新生成并覆盖? [y/N]: " REBUILD_CONFIG
  REBUILD_CONFIG="${REBUILD_CONFIG:-N}"
else
  REBUILD_CONFIG="Y"
fi

if [[ "$REBUILD_CONFIG" =~ ^[Yy]$ ]]; then
  echo "[STEP] 请输入配置参数（回车使用默认值）"
  read -r -p "api_id (默认: 12345678): " API_ID
  API_ID="${API_ID:-12345678}"
  read -r -p "api_hash (默认: your_api_hash): " API_HASH
  API_HASH="${API_HASH:-your_api_hash}"
  read -r -p "master_account_id (默认: 123456789): " MASTER_ACCOUNT_ID
  MASTER_ACCOUNT_ID="${MASTER_ACCOUNT_ID:-123456789}"
  read -r -p "source_chat (默认: -1001234567890): " SOURCE_CHAT
  SOURCE_CHAT="${SOURCE_CHAT:--1001234567890}"
  read -r -p "target_bot (默认: @your_middle_bot): " TARGET_BOT
  TARGET_BOT="${TARGET_BOT:-@your_middle_bot}"
  read -r -p "relay.bot_token (默认: 123456:ABCDEF_your_bot_token): " BOT_TOKEN
  BOT_TOKEN="${BOT_TOKEN:-123456:ABCDEF_your_bot_token}"
  read -r -p "dest_channels (逗号分隔，默认: -1009876543210): " DEST_CHANNELS_RAW
  DEST_CHANNELS_RAW="${DEST_CHANNELS_RAW:--1009876543210}"

  DEST_CHANNELS_JSON="$(python - <<'PY' "$DEST_CHANNELS_RAW"
import sys
arr=[x.strip() for x in sys.argv[1].split(',') if x.strip()]
if not arr:
    arr=['-1009876543210']
print('[' + ', '.join(arr) + ']')
PY
)"

  cat > config.json <<EOF
{
  "api_id": ${API_ID},
  "api_hash": "${API_HASH}",
  "master_account_id": ${MASTER_ACCOUNT_ID},
  "bot_mappings": [
    {
      "source_chat": ${SOURCE_CHAT},
      "target_bot": "${TARGET_BOT}"
    }
  ],
  "relay": {
    "api_id": ${API_ID},
    "api_hash": "${API_HASH}",
    "bot_token": "${BOT_TOKEN}",
    "dest_channels": ${DEST_CHANNELS_JSON}
  },
  "proxy": null
}
EOF

  cat > .env <<EOF
API_ID=${API_ID}
API_HASH=${API_HASH}
MASTER_ACCOUNT_ID=${MASTER_ACCOUNT_ID}
RELAY_API_ID=${API_ID}
RELAY_API_HASH=${API_HASH}
RELAY_BOT_TOKEN=${BOT_TOKEN}
RELAY_DEST_CHANNELS=${DEST_CHANNELS_RAW}
EOF

  echo "[OK] 已生成 config.json 与 .env"
else
  echo "[INFO] 保留现有配置"
fi

$COMPOSE_CMD up -d --build

echo "[OK] 服务已启动。"
echo "[INFO] 查看日志: $COMPOSE_CMD logs -f"
