# Telegram Stealth Relay Bot (Dockerized)

## 🚀 一键安装（交互填写配置）

```bash
REPO_URL="https://github.com/<你的用户名>/Telegram-touji.git" \
bash -c "$(curl -fsSL https://raw.githubusercontent.com/<你的用户名>/Telegram-touji/main/scripts/install.sh)"
```

> 注意：请替换为你自己的 GitHub 用户名/仓库地址，避免指向他人仓库。

脚本会交互询问并生成：
- `config.json`
- `.env`

并自动执行 `docker compose up -d --build`。

## 🔧 当前已完成的优化

1. **统一配置模块**：`telegram_bot.py` 与 `bot_relay.py` 都改为通过 `common_config.py` 读取配置，减少重复逻辑。
2. **结构化日志**：通过 `structured_logger.py` 输出 JSON 日志，覆盖配置加载、映射构建、消息发送关键路径。
3. **限流 + 重试 + 死信**：通过 `delivery.py` 为转发链路加入限流、重试、DLQ（`logs/*.jsonl`）。
4. **.env 支持 + 热重载**：支持 `.env` 覆盖配置；运行时检测 `config.json` 变更并热重载。
5. **最小单元测试**：新增配置解析与命令解析测试。

## 📁 关键文件

- `common_config.py`：统一配置读取/保存、`.env` 加载、环境变量覆盖。
- `structured_logger.py`：JSON logging。
- `delivery.py`：限流、重试、DLQ。
- `command_utils.py`：命令解析。
- `tests/`：最小单元测试。

## 🧪 本地测试

```bash
python -m unittest discover -s tests -v
python -m py_compile telegram_bot.py bot_relay.py common_config.py structured_logger.py delivery.py command_utils.py
bash -n scripts/install.sh
```
