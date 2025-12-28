import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import Client
from config import *

print("Creating bot client...")

# Create the app instance
app = Client(
    "serena_forward",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

print("Bot client created")

# Import handlers to register them
from app import handlers
print("Handlers registered")

async def start_bot_async():
    """Async function to start the bot"""
    try:
        print("Starting bot connection...")
        
        # Start the bot first
        print("Initializing Pyrogram client...")
        await app.start()
        print("✅ Bot connected to Telegram successfully!")
        
        # Try to connect to MongoDB (non-critical)
        try:
            print("Connecting to MongoDB...")
            from app.database import connect_db
            connect_db(MONGO_URI)
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"⚠️ MongoDB connection warning (not critical): {e}")
        
        print("🎉 BOT IS NOW FULLY OPERATIONAL!")
        print("Waiting for messages...")
        
        # Keep bot running
        while True:
            await asyncio.sleep(60)
            
    except Exception as e:
        print(f"❌ Critical error starting bot: {e}")
        import traceback
        traceback.print_exc()

def start_bot():
    """Sync wrapper for async bot start"""
    try:
        print("Creating asyncio event loop...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("Running bot in event loop...")
        loop.run_until_complete(start_bot_async())
    except Exception as e:
        print(f"❌ Fatal error in bot thread: {e}")
        import traceback
        traceback.print_exc()
