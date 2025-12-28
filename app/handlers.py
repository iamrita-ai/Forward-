import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import *

# Import app from main
from app.main import app

active_tasks = {}

print("Registering handlers...")  # Debug line

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    print(f"Received /start from {message.from_user.id}")  # Debug line
    
    from app.utils import check_bot_status
    try:
        if not await check_bot_status(message):
            return
    except:
        pass
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Join Channel", url=FORCE_SUB_LINK)],
        [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{CONTACT_LINKS[0].replace('@', '') if CONTACT_LINKS else 'technicalserena'}")]
    ])
    
    try:
        await message.reply_photo(START_PIC, caption=f"""
👋 Hello {message.from_user.first_name}!

Welcome to *Serena Forward* Bot.

Use:
👉 `/batch <channel_username_or_id>` - To set batch target
👉 `/forward <start_id> <count>` - Forward files
👉 `/cancel` - Stop current task
👉 `/help` - Get help guide
""", reply_markup=keyboard)
        print("Sent start response")  # Debug line
    except Exception as e:
        print(f"Error in start handler: {e}")
        await message.reply("Hello! Bot is working.")

@app.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    print(f"Received /help from {message.from_user.id}")  # Debug line
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Join Channel", url=FORCE_SUB_LINK)],
            [InlineKeyboardButton("📞 Contact Support", url=f"https://t.me/{CONTACT_LINKS[0].replace('@', '') if CONTACT_LINKS else 'technicalserena'}")]
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
        print("Sent help response")  # Debug line
    except Exception as e:
        print(f"Error in help handler: {e}")
        await message.reply("Help command is working!")

# Simple test command to verify bot is responding
@app.on_message(filters.command("test"))
async def test(client, message: Message):
    print(f"Received /test from {message.from_user.id}")
    await message.reply("✅ Bot is working perfectly!")
