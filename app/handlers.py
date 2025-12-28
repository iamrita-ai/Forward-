import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyrogram import filters
from pyrogram.types import Message
from config import *

print("Loading handlers module...")

# Import app from main
try:
    from app.main import app
    print("Successfully imported app from main")
except Exception as e:
    print(f"Error importing app: {e}")
    app = None

if app:
    print("Registering handlers...")

    @app.on_message(filters.command("start"))
    async def start(client, message: Message):
        print(f"=== RECEIVED /start FROM USER {message.from_user.id} ===")
        try:
            await message.reply("🎉 Hello! Serena Forward Bot is working perfectly! ✅\n\nSend /test to verify all functions.")
            print("✅ Response sent successfully")
        except Exception as e:
            print(f"❌ Error sending response: {e}")
            import traceback
            traceback.print_exc()

    @app.on_message(filters.command("test"))
    async def test(client, message: Message):
        print(f"=== RECEIVED /test FROM USER {message.from_user.id} ===")
        try:
            response = "✅ Test Successful!\n\nBot is responding correctly!\n\nAvailable commands:\n• /start - Welcome message\n• /test - Test bot response\n• /help - Get help"
            await message.reply(response)
            print("✅ Test response sent successfully")
        except Exception as e:
            print(f"❌ Error sending test response: {e}")
            import traceback
            traceback.print_exc()

    @app.on_message(filters.command("help"))
    async def help_cmd(client, message: Message):
        print(f"=== RECEIVED /help FROM USER {message.from_user.id} ===")
        try:
            await message.reply("📚 Help Menu:\n\nThis is Serena Forward Bot!\n\nCommands:\n• /start - Start the bot\n• /test - Test bot functionality\n• /help - Show this help")
            print("✅ Help response sent successfully")
        except Exception as e:
            print(f"❌ Error sending help response: {e}")
            import traceback
            traceback.print_exc()

    @app.on_message(filters.all)
    async def catch_all(client, message: Message):
        print(f"=== RECEIVED MESSAGE FROM USER {message.from_user.id} ===")
        print(f"Message type: {type(message)}")
        print(f"Message content: {message.text if hasattr(message, 'text') else 'Non-text message'}")

    print("✅ All handlers registered successfully!")
else:
    print("❌ App not available, handlers not registered")
