from pyrogram import Client, filters
from pyrogram.types import Message
from app.utils import forward_media_batch, is_user_subscribed, save_user, get_all_users
from app.database import add_task, cancel_task, get_stats
from config import *

active_tasks = {}

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_photo(START_PIC, caption=f"""
👋 Hello {message.from_user.first_name}!

Welcome to *Serena Forward* Bot.

Use:
👉 `/batch <channel_username_or_id>` - To set batch target
👉 `/forward <start_id> <count>` - Forward files
👉 `/cancel` - Stop current task
👉 `/stats` - View stats
👉 `/users` - List all users
👉 `/help` - Get help guide
""")

@app.on_message(filters.command("batch"))
async def batch_set(client: Client, message: Message):
    if not await is_user_subscribed(client, message):
        return
    try:
        chat = message.text.split()[1]
        active_tasks[message.from_user.id] = {"chat": chat}
        await message.reply(f"✅ Set Batch Target: `{chat}`\nNow send `/forward <start_id> <count>`.")
    except IndexError:
        await message.reply("⚠️ Usage: `/batch <channel_username_or_id>`")

@app.on_message(filters.command("forward"))
async def forward_files(client: Client, message: Message):
    if not await is_user_subscribed(client, message):
        return
    user_id = message.from_user.id
    if user_id not in active_tasks:
        return await message.reply("⚠️ First set the channel with `/batch`.")

    args = message.text.split()
    if len(args) != 3:
        return await message.reply("⚠️ Usage: `/forward <start_id> <count>`")

    start_id = int(args[1])
    count = int(args[2])

    chat = active_tasks[user_id]["chat"]
    task_id = f"{user_id}_{start_id}"

    await add_task(user_id, task_id)
    await forward_media_batch(client, message, chat, start_id, count, task_id)

@app.on_message(filters.command("cancel"))
async def cancel_forward(client: Client, message: Message):
    user_id = message.from_user.id
    task_id = f"{user_id}_ongoing"
    await cancel_task(task_id)
    await message.reply("🛑 Task cancelled successfully.")

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply("""
📘 Help Guide:

1. Join our channel first.
2. Use `/batch <channel>` to set source.
3. Then run `/forward <start_id> <count>`
4. Bot will forward videos/audio/zip/text/stickers to your DM.
5. After delivery, data gets auto-deleted from server.
6. Only owner can access full features.
""")

@app.on_message(filters.command("stats"))
async def stats(client: Client, message: Message):
    if message.from_user.id not in OWNER_IDS:
        return await message.reply("🚫 Admin only command.")
    stats_data = await get_stats()
    await message.reply(f"""
📊 Bot Stats:

👥 Users: {stats_data['total_users']}
📥 Active Tasks: {len(active_tasks)}
""")

@app.on_message(filters.command("users"))
async def list_users(client: Client, message: Message):
    if message.from_user.id not in OWNER_IDS:
        return await message.reply("🚫 Admin only command.")
    users = await get_all_users()
    response = "\n".join([f"- [{u['username']}](tg://user?id={u['id']}) ({u['id']})" for u in users])
    await message.reply(response, disable_web_page_preview=True)
