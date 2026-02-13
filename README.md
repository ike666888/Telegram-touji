# Telegram Stealth Relay Bot (Dockerized)

**Telegram 消息无痕搬运/偷鸡机器人**

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

* 项目来源：https://github.com/ikun245/Telegram-toujibot
* 通过 AI 修复原版没有自动转发的功能并且保留原版命令功能，实现 Docker 化部署。
* 基于 [Telethon](https://docs.telethon.dev/)：Userbot 负责监听，RelayBot 负责无痕发布。

## ✨ 核心功能

* **全能监听 (Userbot)**：使用真实用户账号监听公开/私有频道消息。
* **无痕转发 (Stealth Mode)**：由 RelayBot 复制重发，去除 `Forwarded from` 标签。
* **相册聚合转发**：自动缓存 grouped_id，避免相册拆散刷屏。
* **命令与系统消息过滤**：拦截 `/命令` 和 `🤖` 系统回执，保证目标频道干净。
* **多目标分发**：可配置多个目标频道。

## 🔧 配置说明

编辑 `config.json`（可参考 `config.example.json`）：

* `api_id` / `api_hash`：Telegram 应用凭据（Userbot）。
* `master_account_id`：可发管理命令的账号 ID。
* `bot_mappings`：源频道 -> 中间机器人映射。
* `relay`：RelayBot 配置（`api_id`、`api_hash`、`bot_token`、`dest_channels`）。

## 🚀 一键安装命令

> 适用于 Linux / Debian / Ubuntu。会自动检测 Docker 与 Compose，然后拉起容器。

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/ikun245/Telegram-toujibot/main/scripts/install.sh)"
```

> 如果你已经在本仓库目录下，也可以直接执行：

```bash
bash scripts/install.sh
```

## 🎮 管理命令

* `/add_listen <源ID> <@目标机器人>`
* `/remove_listen <源ID>`
* `/list_listen`
* `/join <频道链接或用户名>`
* `/leave <频道链接或用户名>`

## 🧠 建议优化/重构方向

1. 将 `telegram_bot.py` 与 `bot_relay.py` 的配置读取统一为同一个模块，减少重复逻辑。
2. 为关键路径（配置加载、映射构建、消息发送）补充结构化日志（如 JSON logging）。
3. 给命令处理和配置读写增加最小单元测试，提高回归稳定性。
4. 将部署脚本发布到稳定地址（如你自己的仓库），避免引用上游缺失脚本。
