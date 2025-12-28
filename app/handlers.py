import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import *
from app.utils import (
    forward_media_batch, is_user_subscribed, save_user,
    check_bot_status, toggle_bot_status
)
from app.database import (
    add_task, cancel_task, get_stats, set_output_channel,
    get_output_channel, reset_output_channel, get_all_users
)

active_tasks = {}

@Client.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    if not await check_bot_status(message):
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Join Channel", url=FORCE_SUB_LINK)],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{CONTACT_LINKS[0].replace('@', '')}")]
    ])
    
    await message.reply_photo(START_PIC, caption=f"""
👋 Hello {message.from_user.first_name}!

Welcome to *Serena Forward* Bot.

Use:
👉 `/batch <channel_username_or_id>` - To set batch target
👉 `/forward <start_id> <count>` - Forward files
👉 `/cancel` - Stop current task
👉 `/help` - Get help guide
""", reply_markup=keyboard)

@Client.on_message(filters.command("batch"))
async def batch_set(client: Client, message: Message):
    if not await check_bot_status(message) or not await is_user_subscribed(client, message):
        return
        
    try:
        chat = message.text.split()[1]
        active_tasks[message.from_user.id] = {"chat": chat}
        await message.reply(f"✅ Set Batch Target: `{chat}`\nNow send `/forward <start_id> <count>`.")
    except IndexError:
        await message.reply("⚠️ Usage: `/batch <channel_username_or_id>`")

@Client.on_message(filters.command("forward"))
async def forward_files(client: Client, message: Message):
    if not await check_bot_status(message) or not await is_user_subscribed(client, message):
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

@Client.on_message(filters.command("cancel"))
async def cancel_forward(client: Client, message: Message):
    if not await check_bot_status(message):
        return
        
    user_id = message.from_user.id
    task_id = f"{user_id}_ongoing"
    from app.database import cancel_task
    await cancel_task(task_id)
    await message.reply("🛑 Task cancelled successfully.")

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    if not await check_bot_status(message):
        return
        
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Join Channel", url=FORCE_SUB_LINK)],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{CONTACT_LINKS[0].replace('@', '')}")]
    ])
    
    await message.reply("""
📘 Help Guide:

1. Join our channel first.
2. Use `/batch <channel>` to set source.
3. Then run `/forward <start_id> <count>`
4. Bot will forward videos/audio/zip/text/stickers to your DM.
5. After delivery, data gets auto-deleted from server.
6. Only owner can access full features.
""", reply_markup=keyboard)

@Client.on_message(filters.command("stats"))
async def stats(client: Client, message: Message):
    if not await check_bot_status(message) or message.from_user.id not in OWNER_IDS:
        return await message.reply("🚫 Admin only command.")
        
    stats_data = await get_stats()
    await message.reply(f"""
📊 Bot Stats:

👥 Users: {stats_data['total_users']}
📥 Active Tasks: {len(active_tasks)}
""")

@Client.on_message(filters.command("users"))
async def list_users(client: Client, message: Message):
    if not await check_bot_status(message) or message.from_user.id not in OWNER_IDS:
        return await message.reply("🚫 Admin only command.")
        
    users = await get_all_users()
    response = "\n".join([f"- [{u['username']}](tg://user?id={u['id']}) ({u['id']})" for u in users])
    await message.reply(response, disable_web_page_preview=True)

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_IDS))
async def broadcast(client: Client, message: Message):
    if not await check_bot_status(message):
        return
        
    if not message.reply_to_message:
        return await message.reply("Please reply to a message to broadcast.")
        
    users = await get_all_users()
    success = 0
    failed = 0
    
    for user in users:
        try:
            await message.reply_to_message.forward(user['id'])
            success += 1
        except:
            failed += 1
            
    await message.reply(f"Broadcast completed!\nSuccess: {success}\nFailed: {failed}")

@Client.on_message(filters.command("settings") & filters.user(OWNER_IDS))
async def settings_menu(client: Client, message: Message):
    if not await check_bot_status(message):
        return
        
    output_channel = await get_output_channel()
    current_status = await check_bot_status(message)
    status_text = "ON" if current_status else "OFF"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Set Output Channel", callback_data="set_channel")],
        [InlineKeyboardButton("🗑 Reset Output Channel", callback_data="reset_channel")],
        [InlineKeyboardButton(f"⚡ Bot Status: Toggle", callback_data="toggle_status")]
    ])
    
    channel_info = f"\nOutput Channel: `{output_channel}`" if output_channel else "\nNo output channel set"
    await message.reply(f"⚙️ Bot Settings:{channel_info}", reply_markup=keyboard)

@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    if query.data == "set_channel":
        await query.message.edit_text("Please send the channel ID where files should be forwarded:")
        # We'll handle the next message in another handler
    elif query.data == "reset_channel":
        await reset_output_channel()
        await query.message.edit_text("✅ Output channel has been reset!")
    elif query.data == "toggle_status":
        new_status = await toggle_bot_status()
        status_text = "ON" if new_status.lower() == "on" else "OFF"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Set Output Channel", callback_data="set_channel")],
            [InlineKeyboardButton("🗑 Reset Output Channel", callback_data="reset_channel")],
            [InlineKeyboardButton(f"⚡ Bot Status: {status_text}", callback_data="toggle_status")]
        ])
        await query.message.edit_text("⚙️ Bot Settings:", reply_markup=keyboard)

@Client.on_message(filters.private & filters.user(OWNER_IDS) & filters.regex(r"^-?\d+$"))
async def handle_channel_input(client: Client, message: Message):
    try:
        channel_id = int(message.text)
        await set_output_channel(channel_id)
        await message.reply("✅ Output channel has been set!")
    except ValueError:
        await message.reply("Invalid channel ID. Please send a valid numeric ID.")

@Client.on_message(filters.command("on") & filters.user(OWNER_IDS))
async def turn_on(client: Client, message: Message):
    await toggle_bot_status("on")
    await message.reply("🟢 Bot is now ON!")

@Client.on_message(filters.command("stop") & filters.user(OWNER_IDS))
async def turn_off(client: Client, message: Message):
    await toggle_bot_status("off")
    await message.reply("🔴 Bot is now OFF!")
