# Telegram Stealth Relay Bot (Dockerized)

**Telegram 消息无痕搬运/偷鸡机器人**

[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

这是一个基于 [Telethon](https://docs.telethon.dev/) 开发的高级 Telegram 消息转发系统。它结合了 **Userbot** (用户客户端) 和 **Bot API** (机器人客户端) 的优势，能够从任何您已加入的频道/群组（包括受限频道）监听消息，并以**“无痕模式”**（去除“转发自 xxx”标签）转发到您的目标频道。

## ✨ 核心功能

* **🕵️ 全能监听 (Userbot)**：使用真实用户账号监听，突破普通机器人无法加入频道的限制。支持监听公开频道、私有群组、甚至机器人。
* **👻 无痕转发 (Stealth Mode)**：
    * 通过机器人“复制并重新发送”的方式运作。
    * **彻底去除**原消息的 `Forwarded from` 来源标签。
    * 目标频道的成员看起来就像是机器人原创发布的消息。
* **📦 完美支持相册 (Media Group)**：内置智能缓存与锁机制，自动识别并合并多张图片/视频为一条完整的相册消息，拒绝刷屏。
* **🛡️ 智能命令过滤系统**：
    * **管理安全**：在机器人私聊中发送管理命令（如 `/add_listen`）时，系统会自动拦截，**绝不转发**到公开频道。
    * **交互隔离**：Userbot 的回复带有特殊标记（🤖），RelayBot 会自动识别并拦截，确保频道内容纯净。
* **📢 多路分发**：支持监听多个源频道，并将消息汇总转发到配置的一个或多个目标频道。
* **🐳 Docker 一键部署**：提供完整的 Docker Compose 配置，支持掉线自动重启，部署维护极其简单。

## 🛠️ 架构原理

本项目由两个协同工作的 Docker 容器组成：

1.  **Userbot (`telegram_bot.py`)**：
    * **角色**：监听者 (The Listener)。
    * **功能**：使用您的个人账号登录，监听 `config.json` 中配置的源频道，将消息转发给中间机器人。
    * **交互**：负责处理管理命令，并以 `🤖` 前缀回复执行结果。
2.  **RelayBot (`bot_relay.py`)**：
    * **角色**：发布者 (The Publisher)。
    * **功能**：使用机器人 Token 登录，接收来自 Userbot 的私聊消息。
    * **处理**：缓存相册媒体、过滤掉所有以 `/` 开头的命令和以 `🤖` 开头的系统回复，最后将清洗后的内容发送到最终目标频道。

##📂 **项目结构**
.
├── bot_relay.py        # 🚀 发布端：处理缓存、过滤命令、无痕发送
├── telegram_bot.py     # 🎧 监听端：处理监听、转发给机器人、响应命令
├── config.json         # ⚙️ 配置文件：定义监听映射
├── docker-compose.yml  # 🐳 Docker 编排文件
├── Dockerfile          # 📄 镜像构建文件
├── requirements.txt    # 🐍 Python 依赖
└── anon.session        # 🔐 (自动生成) Userbot 登录凭证
## 🚀 部署指南

### 1. 准备工作
* 一台安装了 Linux 的服务器 (VPS)。
* 已安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
* **Telegram API ID & Hash**：登录 [my.telegram.org](https://my.telegram.org) 获取。
* **Bot Token**：联系 [@BotFather](https://t.me/BotFather) 创建新机器人。
* **目标频道**：创建频道并将您的机器人设为**管理员**。

### 2. 获取代码
```bash
git clone [https://github.com/您的用户名/您的仓库名.git](https://github.com/您的用户名/您的仓库名.git)
cd 您的仓库名
