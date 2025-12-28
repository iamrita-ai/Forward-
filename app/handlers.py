import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import *

# Import app from main
from app.main import app

active_tasks = {}

# Import utils functions inside handlers to avoid circular imports
async def forward_media_batch(client, message, chat, start_id, count, task_id):
    from app.utils import forward_media_batch as util_forward
    await util_forward(client, message, chat, start_id, count, task_id)

async def is_user_subscribed(client, message):
    from app.utils import is_user_subscribed as util_check
    return await util_check(client, message)

def save_user(user):
    from app.utils import save_user as util_save
    util_save(user)

async def check_bot_status(message):
    from app.utils import check_bot_status as util_check_status
    return await util_check_status(message)

async def toggle_bot_status():
    from app.utils import toggle_bot_status as util_toggle
    return await util_toggle()

@app.on_message(filters.command("start"))
async def start(client, message: Message):
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

@app.on_message(filters.command("batch"))
async def batch_set(client, message: Message):
    if not await check_bot_status(message):
        from app.utils import is_user_subscribed
        if not await is_user_subscribed(client, message):
            return
    else:
        from app.utils import is_user_subscribed
        if not await is_user_subscribed(client, message):
            return
        
    try:
        chat = message.text.split()[1]
        active_tasks[message.from_user.id] = {"chat": chat}
        await message.reply(f"✅ Set Batch Target: `{chat}`\nNow send `/forward <start_id> <count>`.")
    except IndexError:
        await message.reply("⚠️ Usage: `/batch <channel_username_or_id>`")

@app.on_message(filters.command("forward"))
async def forward_files(client, message: Message):
    if not await check_bot_status(message):
        from app.utils import is_user_subscribed
        if not await is_user_subscribed(client, message):
            return
    else:
        from app.utils import is_user_subscribed
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

    from app.database import add_task
    await add_task(user_id, task_id)
    
    from app.utils import forward_media_batch
    await forward_media_batch(client, message, chat, start_id, count, task_id)

@app.on_message(filters.command("cancel"))
async def cancel_forward(client, message: Message):
    if not await check_bot_status(message):
        return
        
    user_id = message.from_user.id
    task_id = f"{user_id}_ongoing"
    from app.database import cancel_task
    await cancel_task(task_id)
    await message.reply("🛑 Task cancelled successfully.")

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
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

@app.on_message(filters.command("stats"))
async def stats(client, message: Message):
    if not await check_bot_status(message) or message.from_user.id not in OWNER_IDS:
        return await message.reply("🚫 Admin only command.")
        
    from app.database import get_stats
    stats_data = await get_stats()
    await message.reply(f"""
📊 Bot Stats:

👥 Users: {stats_data['total_users']}
📥 Active Tasks: {len(active_tasks)}
""")

@app.on_message(filters.command("users"))
async def list_users(client, message: Message):
    if not await check_bot_status(message) or message.from_user.id not in OWNER_IDS:
        return await message.reply("🚫 Admin only command.")
        
    from app.database import get_all_users
    users = await get_all_users()
    response = "\n".join([f"- [{u['username']}](tg://user?id={u['id']}) ({u['id']})" for u in users])
    await message.reply(response, disable_web_page_preview=True)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_IDS))
async def broadcast(client, message: Message):
    if not await check_bot_status(message):
        return
        
    if not message.reply_to_message:
        return await message.reply("Please reply to a message to broadcast.")
        
    from app.database import get_all_users
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

@app.on_message(filters.command("settings") & filters.user(OWNER_IDS))
async def settings_menu(client, message: Message):
    if not await check_bot_status(message):
        return
        
    from app.database import get_output_channel
    output_channel = await get_output_channel()
    from app.database import get_bot_status
    current_status = await get_bot_status()
    status_text = "ON" if current_status == "on" else "OFF"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Set Output Channel", callback_data="set_channel")],
        [InlineKeyboardButton("🗑 Reset Output Channel", callback_data="reset_channel")],
        [InlineKeyboardButton(f"⚡ Bot Status: Toggle", callback_data="toggle_status")]
    ])
    
    channel_info = f"\nOutput Channel: `{output_channel}`" if output_channel else "\nNo output channel set"
    await message.reply(f"⚙️ Bot Settings:{channel_info}", reply_markup=keyboard)

@app.on_callback_query()
async def callback_handler(client, query: CallbackQuery):
    if query.data == "set_channel":
        await query.message.edit_text("Please send the channel ID where files should be forwarded:")
        # We'll handle the next message in another handler
    elif query.data == "reset_channel":
        from app.database import reset_output_channel
        await reset_output_channel()
        await query.message.edit_text("✅ Output channel has been reset!")
    elif query.data == "toggle_status":
        from app.utils import toggle_bot_status
        new_status = await toggle_bot_status()
        status_text = "ON" if new_status == "on" else "OFF"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Set Output Channel", callback_data="set_channel")],
            [InlineKeyboardButton("🗑 Reset Output Channel", callback_data="reset_channel")],
            [InlineKeyboardButton(f"⚡ Bot Status: Toggle", callback_data="toggle_status")]
        ])
        await query.message.edit_text("⚙️ Bot Settings:", reply_markup=keyboard)

@app.on_message(filters.private & filters.user(OWNER_IDS) & filters.regex(r"^-?\d+$"))
async def handle_channel_input(client, message: Message):
    try:
        channel_id = int(message.text)
        from app.database import set_output_channel
        await set_output_channel(channel_id)
        await message.reply("✅ Output channel has been set!")
    except ValueError:
        await message.reply("Invalid channel ID. Please send a valid numeric ID.")

@app.on_message(filters.command("on") & filters.user(OWNER_IDS))
async def turn_on(client, message: Message):
    from app.utils import toggle_bot_status
    await toggle_bot_status()
    await message.reply("🟢 Bot is now ON!")

@app.on_message(filters.command("stop") & filters.user(OWNER_IDS))
async def turn_off(client, message: Message):
    from app.database import set_bot_status
    await set_bot_status("off")
    await message.reply("🔴 Bot is now OFF!")
