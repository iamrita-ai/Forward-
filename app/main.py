import sys
import os
import asyncio
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import Client
from config import *

print("Creating bot client...")

# Create the app instance at module level
app = Client(
    "serena_forward",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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
    print("Starting bot function called...")
    
    if not check_initial_status():
        print("Bot status check failed")
        return

    try:
        from app.database import connect_db
        connect_db(MONGO_URI)
        print("Connected to MongoDB successfully!")
        
        print("Attempting to start Pyrogram client...")
        
        # Import handlers to register them
        from app import handlers
        print("Handlers imported and registered")
        
        # Create new event loop for this thread
        print("Creating new event loop...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("Event loop created and set")
        
        # Run the bot
        print("Running app.run() with custom event loop...")
        loop.run_until_complete(app.start())
        print("Bot started successfully!")
        
        # Keep the loop running
        print("Starting idle loop...")
        loop.run_forever()
        print("Bot run completed")
        
    except KeyboardInterrupt:
        print("Bot stopped by user")
        if 'loop' in locals():
            loop.stop()
    except Exception as e:
        print(f"Critical error starting bot: {e}")
        import traceback
        traceback.print_exc()

print("Main module fully loaded")
