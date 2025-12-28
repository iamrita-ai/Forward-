import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import Client
from config import *
from app.database import connect_db

def check_initial_status():
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        db = client["serena_bot"]
        status = db.settings.find_one({"setting": "bot_status"})
        if status and status.get("status", "on") == "off":
            print("🔴 Bot is currently OFF. Use /on command to activate.")
            return False
        return True
    except Exception as e:
        print(f"Error checking bot status: {e}")
        return True

def start_bot():
    """Function to start the bot - called from web_server.py"""
    if not check_initial_status():
        return

    app = Client(
        "serena_forward",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    # Import handlers properly
    import app.handlers

    try:
        connect_db(MONGO_URI)
        print("🚀 Serena Forward Bot Started!")
        app.run()
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    start_bot()
