# bot_relay.py
from telethon import TelegramClient, events
import asyncio

# === 配置区域 ===
API_ID = telegram官网申请
API_HASH = 'telegram官网申请'
BOT_TOKEN = '你的BOT_TOKEN'
DEST_CHANNELS = [最终转发的频道id]
# DEST_CHANNELS = [最终转发的频道id]
# DEST_CHANNELS = [最终转发的频道id]
# 可以无限添加最终转发的频道
# === 缓存 ===
media_group_cache = {}
media_group_lock = asyncio.Lock()

client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handler(event):
    sender = await event.get_sender()
    if sender and sender.is_self: return

    text_content = event.raw_text or ""
    stripped_text = text_content.strip()

    # === 1. 拦截命令 (您发送的) ===
    if stripped_text.startswith('/'):
        print(f"🛑 拦截命令: {stripped_text}")
        return

    # === 2. 拦截系统提示 (Userbot 回复的，带 🤖 标记) ===
    if stripped_text.startswith('🤖'):
        print(f"🛑 拦截系统回复: {stripped_text}")
        return

    # === 3. 正常转发逻辑 ===
    if event.message.grouped_id:
        async with media_group_lock:
            gid = event.message.grouped_id
            if gid not in media_group_cache:
                media_group_cache[gid] = {'messages': [], 'task': None}
            media_group_cache[gid]['messages'].append(event.message)
            
            if media_group_cache[gid]['task']:
                media_group_cache[gid]['task'].cancel()
            media_group_cache[gid]['task'] = asyncio.create_task(process_media_group(gid))
        print(f"📥 缓存相册: {gid}")
    else:
        print(f"📤 转发单条消息...")
        await send_copy(event.message)

async def process_media_group(gid):
    try:
        await asyncio.sleep(2)
        async with media_group_lock:
            if gid not in media_group_cache: return
            msgs = media_group_cache[gid]['messages']
            del media_group_cache[gid]
        
        if not msgs: return
        msgs.sort(key=lambda x: x.id)
        media = [m.media for m in msgs]
        caption = next((m.text for m in msgs if m.text), None)

        for cid in DEST_CHANNELS:
            try:
                await client.send_message(cid, message=caption, file=media)
                print(f"✅ 相册已发到 {cid}")
            except Exception as e:
                print(f"❌ 发送失败 {cid}: {e}")
    except: pass

async def send_copy(msg):
    for cid in DEST_CHANNELS:
        try:
            await client.send_message(cid, message=msg, file=msg.media)
            print(f"✅ 消息已发到 {cid}")
        except Exception as e:
            print(f"❌ 发送失败 {cid}: {e}")

print("🚀 RelayBot (支持命令与回复拦截) 已启动...")
client.run_until_disconnected()
