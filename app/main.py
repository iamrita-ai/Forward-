import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=== BOT CONNECTION DIAGNOSTICS ===")

# Test imports first
try:
    from pyrogram import Client
    print("✅ Pyrogram imported successfully")
except Exception as e:
    print(f"❌ Pyrogram import failed: {e}")
    exit(1)

from config import *

print(f"API_ID: {API_ID}")
print(f"API_HASH length: {len(API_HASH)}")
print(f"BOT_TOKEN length: {len(BOT_TOKEN)}")

# Validate credentials
errors = []
if not API_ID or API_ID == 0:
    errors.append("API_ID is not set or invalid")
if not API_HASH or len(API_HASH) != 32:
    errors.append("API_HASH is not set or invalid (should be 32 chars)")
if not BOT_TOKEN or ":" not in BOT_TOKEN:
    errors.append("BOT_TOKEN is not set or invalid (should contain ':')")

if errors:
    print("❌ CONFIGURATION ERRORS:")
    for error in errors:
        print(f"  • {error}")
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
    """Enhanced diagnostic async function to start the bot"""
    print("🔧 Starting enhanced bot connection diagnostics...")
    
    try:
        print("🔌 Attempting to connect to Telegram (timeout: 30s)...")
        
        # Create connection with timeout
        try:
            await asyncio.wait_for(app.start(), timeout=30.0)
            print("🎉 SUCCESS! Bot connected to Telegram!")
        except asyncio.TimeoutError:
            print("⏰ TIMEOUT: Could not connect to Telegram within 30 seconds")
            print("💡 Possible causes:")
            print("  • Network restrictions on Render")
            print("  • Invalid credentials")
            print("  • Telegram blocked in your region")
            return False
        except Exception as connect_error:
            print(f"💥 CONNECTION ERROR: {connect_error}")
            import traceback
            traceback.print_exc()
            return False
        
        # Get bot info
        try:
            print("👤 Getting bot information...")
            bot_me = await app.get_me()
            print(f"🤖 Bot successfully authenticated!")
            print(f"   Username: @{bot_me.username}")
            print(f"   ID: {bot_me.id}")
            print(f"   First Name: {bot_me.first_name}")
        except Exception as info_error:
            print(f"⚠️ Could not get bot info: {info_error}")
        
        print("✅ Bot is ready and listening for messages!")
        print("📨 Try sending /test to your bot now!")
        
        # Keep running with periodic checks
        print("💤 Keeping bot alive...")
        check_count = 0
        while True:
            check_count += 1
            print(f"📡 Heartbeat check #{check_count}")
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        print("⏹️ Bot stopped by user")
        return True
    except Exception as e:
        print(f"💥 FATAL ERROR in bot execution: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_bot():
    """Sync wrapper for enhanced bot start"""
    print("🔄 Setting up asyncio environment...")
    try:
        # For Python 3.10+, create event loop differently
        try:
            loop = asyncio.new_event_loop()
        except:
            loop = asyncio.get_event_loop_policy().new_event_loop()
            
        asyncio.set_event_loop(loop)
        print("✅ Asyncio environment ready")
        print("🚀 Launching bot connection...")
        result = loop.run_until_complete(start_bot_async())
        return result
    except Exception as e:
        print(f"💥 FATAL THREAD ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
