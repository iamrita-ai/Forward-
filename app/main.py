from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from app.handlers import *
from app.database import connect_db

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
