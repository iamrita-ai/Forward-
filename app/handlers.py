import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import *

print("Loading handlers module...")

# Import app from main
try:
    from app.main import app
    print("Successfully imported app from main")
except Exception as e:
    print(f"Error importing app: {e}")
    app = None

active_tasks = {}

if app:
    print("Registering handlers...")

    @app.on_message(filters.command("start"))
    async def start(client, message: Message):
        print(f"Received /start from user {message.from_user.id}")
        try:
            await message.reply("Hello! Bot is working! ✅")
            print("Sent response to /start")
        except Exception as e:
            print(f"Error sending response: {e}")

    @app.on_message(filters.command("test"))
    async def test(client, message: Message):
        print(f"Received /test from user {message.from_user.id}")
        try:
            await message.reply("✅ Test command working perfectly!")
            print("Sent response to /test")
        except Exception as e:
            print(f"Error sending test response: {e}")

    @app.on_message(filters.command("help"))
    async def help_cmd(client, message: Message):
        print(f"Received /help from user {message.from_user.id}")
        try:
            await message.reply("Help command is working! 📚")
            print("Sent response to /help")
        except Exception as e:
            print(f"Error sending help response: {e}")

    print("Handlers registered successfully!")
else:
    print("App not available, handlers not registered")
