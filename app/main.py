import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from app.handlers import *
from app.database import connect_db

if BOT_STATUS.lower() != "on":
    print("🔴 Bot is currently OFF. Use /on command to activate.")
    exit()

app = Client(
    "serena_forward",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="app")
)

connect_db(MONGO_URI)

print("🚀 Serena Forward Bot Started!")

if __name__ == "__main__":
    app.run()
