import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== BOT DIAGNOSTICS ===")

# Test imports first
try:
    from pyrogram import Client
    print("✅ Pyrogram imported successfully")
except Exception as e:
    print(f"❌ Pyrogram import failed: {e}")
    exit(1)

from config import *

print(f"API_ID: {API_ID}")
print(f"API_HASH length: {len(API_HASH) if API_HASH else 0}")
print(f"BOT_TOKEN length: {len(BOT_TOKEN) if BOT_TOKEN else 0}")

# Validate credentials
if not API_ID or API_ID == 0:
    print("❌ ERROR: API_ID is not set or invalid")
    exit(1)

if not API_HASH or len(API_HASH) < 30:
    print("❌ ERROR: API_HASH is not set or invalid")
    exit(1)

if not BOT_TOKEN or len(BOT_TOKEN) < 30:
    print("❌ ERROR: BOT_TOKEN is not set or invalid")
    exit(1)

print("✅ All credentials validated")

# Create the app instance
print("Creating Pyrogram client...")
try:
    app = Client(
        "serena_forward",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    print("✅ Pyrogram client created successfully")
except Exception as e:
    print(f"❌ Pyrogram client creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Import handlers
print("Importing handlers...")
try:
    from app import handlers
    print("✅ Handlers imported successfully")
except Exception as e:
    print(f"❌ Handler import failed: {e}")
    import traceback
    traceback.print_exc()

async def start_bot_async():
    """Diagnostic async function to start the bot"""
    print("🔧 Starting diagnostic bot connection...")
    
    try:
        print("🔌 Attempting to connect to Telegram...")
        await app.start()
        print("🎉 SUCCESS! Bot connected to Telegram!")
        
        # Get bot info
        try:
            bot_me = await app.get_me()
            print(f"🤖 Bot info: @{bot_me.username} (ID: {bot_me.id})")
        except Exception as e:
            print(f"⚠️ Could not get bot info: {e}")
        
        print("✅ Bot is ready and listening!")
        
        # Keep running
        print("💤 Keeping bot alive...")
        while True:
            await asyncio.sleep(30)
            
    except Exception as e:
        print(f"💥 FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_bot():
    """Sync wrapper for diagnostic bot start"""
    print("🔄 Setting up asyncio environment...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("✅ Asyncio environment ready")
        print("🚀 Launching bot...")
        result = loop.run_until_complete(start_bot_async())
        return result
    except Exception as e:
        print(f"💥 FATAL THREAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
