# telegram_bot.py
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.events import NewMessage
import asyncio
import json

# === 缓存与锁 ===
media_group_cache = {}
media_group_lock = asyncio.Lock()

# === 读取配置 ===
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_id = config['api_id']
api_hash = config['api_hash']
master_account_id = config['master_account_id']
bot_mappings = config['bot_mappings']
proxy_config = config.get('proxy', None)

proxy = None
if proxy_config and proxy_config.get('proxy_type'):
    proxy_type = proxy_config['proxy_type']
    proxy_addr = proxy_config['addr']
    proxy_port = proxy_config['port']
    proxy_username = proxy_config.get('username')
    proxy_password = proxy_config.get('password')

    if proxy_type.lower() == 'socks5':
        proxy = ('socks5', proxy_addr, proxy_port, proxy_username, proxy_password)
    elif proxy_type.lower() == 'http':
        proxy = ('http', proxy_addr, proxy_port, proxy_username, proxy_password)
else:
    proxy = None

client = TelegramClient('anon', api_id, api_hash, proxy=proxy)
forwarding_map = {}

def update_config_file(new_bot_mappings):
    global bot_mappings, forwarding_map
    bot_mappings = new_bot_mappings
    config['bot_mappings'] = new_bot_mappings
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    print("config.json 已更新！")
    asyncio.create_task(rebuild_forwarding_map())

async def rebuild_forwarding_map():
    global forwarding_map
    forwarding_map = {}
    for mapping in bot_mappings:
        source_chat = mapping['source_chat']
        target_bot = mapping['target_bot']
        try:
            try:
                src_id = int(source_chat)
            except ValueError:
                src_id = source_chat
            
            source_entity = await client.get_entity(src_id)
            target_entity = await client.get_entity(str(target_bot))
            peer_id = await client.get_peer_id(source_entity)
            forwarding_map[peer_id] = target_entity
            print(f"映射更新: {source_chat} -> {target_bot}")
        except Exception as e:
            print(f"映射失败 ({source_chat}): {e}")

@client.on(NewMessage())
async def handler(event):
    if event.chat_id in forwarding_map:
        target_bot = forwarding_map[event.chat_id]
        if event.message.grouped_id:
            async with media_group_lock:
                if event.message.grouped_id not in media_group_cache:
                    media_group_cache[event.message.grouped_id] = {
                        'messages': [], 'task': None, 'target_bot': target_bot
                    }
                media_group_cache[event.message.grouped_id]['messages'].append(event.message.id)
                if media_group_cache[event.message.grouped_id]['task']:
                    media_group_cache[event.message.grouped_id]['task'].cancel()
                media_group_cache[event.message.grouped_id]['task'] = asyncio.create_task(
                    process_media_group(event.message.grouped_id, event.chat_id)
                )
        else:
            try:
                await client.forward_messages(target_bot, event.message.id, from_peer=event.chat_id)
            except Exception as e:
                print(f"转发失败: {e}")

async def process_media_group(grouped_id, from_peer):
    await asyncio.sleep(1.5)
    async with media_group_lock:
        if grouped_id in media_group_cache:
            data = media_group_cache[grouped_id]
            try:
                await client.forward_messages(data['target_bot'], data['messages'], from_peer=from_peer)
            except Exception as e:
                print(f"媒体组转发错: {e}")
            finally:
                del media_group_cache[grouped_id]

async def join_chat(entity):
    await client(JoinChannelRequest(entity))

async def leave_chat(entity):
    await client(LeaveChannelRequest(entity))

async def main():
    await client.start()
    print("Userbot 客户端已启动！")
    await rebuild_forwarding_map()

    # === 命令处理器 (已移除收藏夹限制，并添加 🤖 标记) ===
    @client.on(NewMessage(func=lambda e: e.is_private and e.sender_id == master_account_id))
    async def command_handler(event):
        # 注意：这里不再限制 event.chat_id，允许在任何私聊（包括机器人窗口）使用命令
        
        text = event.message.text
        if not text.startswith('/'):
            return

        parts = text.split(' ', 1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # 所有回复都加上 "🤖 " 前缀，方便 RelayBot 识别过滤
        if cmd == '/join':
            try:
                ent = await client.get_entity(args)
                await join_chat(ent)
                await event.reply(f"🤖 已尝试加入: {ent.title}")
            except Exception as e:
                await event.reply(f"🤖 加入失败: {e}")

        elif cmd == '/leave':
            try:
                ent = await client.get_entity(args)
                await leave_chat(ent)
                await event.reply(f"🤖 已尝试退出: {ent.title}")
            except Exception as e:
                await event.reply(f"🤖 退出失败: {e}")

        elif cmd == '/add_listen':
            sub_parts = args.split(' ', 1)
            if len(sub_parts) == 2:
                src, bot = sub_parts[0], sub_parts[1].strip()
                if not bot.startswith('@'):
                    await event.reply("🤖 错误: 机器人用户名需以 @ 开头")
                    return
                try:
                    await client.get_entity(bot)
                    exists = next((m for m in bot_mappings if str(m['source_chat']) == str(src)), None)
                    if exists:
                        if exists['target_bot'] == bot:
                            await event.reply(f"🤖 '{src}' 已经在监听列表中了。")
                        else:
                            # 更新
                            new_map = [m for m in bot_mappings if str(m['source_chat']) != str(src)]
                            new_map.append({'source_chat': src, 'target_bot': bot})
                            update_config_file(new_map)
                            await event.reply(f"🤖 更新成功: {src} -> {bot}")
                    else:
                        # 新增
                        new_map = bot_mappings + [{'source_chat': src, 'target_bot': bot}]
                        update_config_file(new_map)
                        await event.reply(f"🤖 添加成功: {src} -> {bot}")
                except Exception as e:
                    await event.reply(f"🤖 操作失败: {e}")
            else:
                await event.reply("🤖 用法: /add_listen <源ID> <@目标机器人>")

        elif cmd == '/remove_listen':
            if args:
                new_map = [m for m in bot_mappings if str(m['source_chat']) != str(args)]
                if len(new_map) < len(bot_mappings):
                    update_config_file(new_map)
                    await event.reply(f"🤖 已移除监听: {args}")
                else:
                    await event.reply(f"🤖 '{args}' 不在列表中。")
            else:
                await event.reply("🤖 用法: /remove_listen <源ID>")

        elif cmd == '/list_listen':
            if bot_mappings:
                info = "\n".join([f"{m['source_chat']} -> {m['target_bot']}" for m in bot_mappings])
                await event.reply(f"🤖 当前监听:\n{info}")
            else:
                await event.reply("🤖 当前列表为空。")

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())