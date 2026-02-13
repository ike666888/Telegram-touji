import asyncio
import json
import os
from typing import Any

from telethon import TelegramClient, events

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")

# === 缓存 ===
media_group_cache: dict[int, dict[str, Any]] = {}
media_group_lock = asyncio.Lock()


def load_relay_config() -> tuple[int, str, str, list[int]]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    relay = config.get("relay", {})
    api_id = int(relay.get("api_id", config.get("api_id", 0)))
    api_hash = relay.get("api_hash", config.get("api_hash", ""))
    bot_token = relay.get("bot_token", "")
    dest_channels = relay.get("dest_channels", [])

    if not api_id or not api_hash or not bot_token or not dest_channels:
        raise ValueError(
            "Relay 配置缺失。请在 config.json 的 relay 字段中设置 api_id/api_hash/bot_token/dest_channels。"
        )

    return api_id, api_hash, bot_token, [int(cid) for cid in dest_channels]


API_ID, API_HASH, BOT_TOKEN, DEST_CHANNELS = load_relay_config()
client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handler(event):
    sender = await event.get_sender()
    if sender and sender.is_self:
        return

    stripped_text = (event.raw_text or "").strip()

    # 1) 拦截命令
    if stripped_text.startswith("/"):
        print(f"🛑 拦截命令: {stripped_text}")
        return

    # 2) 拦截 Userbot 系统回复
    if stripped_text.startswith("🤖"):
        print(f"🛑 拦截系统回复: {stripped_text}")
        return

    # 3) 转发逻辑
    if event.message.grouped_id:
        async with media_group_lock:
            gid = event.message.grouped_id
            if gid not in media_group_cache:
                media_group_cache[gid] = {"messages": [], "task": None}
            media_group_cache[gid]["messages"].append(event.message)

            old_task = media_group_cache[gid]["task"]
            if old_task:
                old_task.cancel()
            media_group_cache[gid]["task"] = asyncio.create_task(process_media_group(gid))
        print(f"📥 缓存相册: {gid}")
    else:
        print("📤 转发单条消息...")
        await send_copy(event.message)


async def process_media_group(gid: int):
    try:
        await asyncio.sleep(2)
        async with media_group_lock:
            if gid not in media_group_cache:
                return
            msgs = media_group_cache[gid]["messages"]
            del media_group_cache[gid]

        if not msgs:
            return
        msgs.sort(key=lambda x: x.id)
        media = [m.media for m in msgs]
        caption = next((m.text for m in msgs if m.text), None)

        for cid in DEST_CHANNELS:
            try:
                await client.send_message(cid, message=caption, file=media)
                print(f"✅ 相册已发到 {cid}")
            except Exception as exc:
                print(f"❌ 相册发送失败 {cid}: {exc}")
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        print(f"❌ 处理相册异常: {exc}")


async def send_copy(msg):
    for cid in DEST_CHANNELS:
        try:
            await client.send_message(cid, message=msg, file=msg.media)
            print(f"✅ 消息已发到 {cid}")
        except Exception as exc:
            print(f"❌ 发送失败 {cid}: {exc}")


print("🚀 RelayBot 已启动...")
client.run_until_disconnected()
