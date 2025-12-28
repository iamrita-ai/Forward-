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
        print(f"=== RECEIVED /start FROM USER {message.from_user.id} ({message.from_user.username or 'No username'}) ===")
        try:
            welcome_text = f"""🎉 Hello {message.from_user.first_name}!

✅ Serena Forward Bot is working perfectly!

Available commands:
• /test - Test bot response
• /help - Get help information

Bot is ready to forward files!"""
            
            await message.reply(welcome_text)
            print("✅ Welcome message sent successfully")
        except Exception as e:
            print(f"❌ Error sending welcome message: {e}")
            import traceback
            traceback.print_exc()

    @app.on_message(filters.command("test"))
    async def test(client, message: Message):
        print(f"=== RECEIVED /test FROM USER {message.from_user.id} ({message.from_user.username or 'No username'}) ===")
        try:
            response = f"""✅ Test Successful!

User Info:
• ID: {message.from_user.id}
• Name: {message.from_user.first_name}
• Username: @{message.from_user.username or 'Not set'}

Bot Status: ✅ Online and responding!

Available commands:
• /start - Welcome message
• /test - Test bot response  
• /help - Get help"""
            
            await message.reply(response)
            print("✅ Test response sent successfully")
        except Exception as e:
            print(f"❌ Error sending test response: {e}")
            import traceback
            traceback.print_exc()

    @app.on_message(filters.command("help"))
    async def help_cmd(client, message: Message):
        print(f"=== RECEIVED /help FROM USER {message.from_user.id} ({message.from_user.username or 'No username'}) ===")
        try:
            help_text = """📚 Serena Forward Bot Help

Commands:
• /start - Show welcome message
• /test - Test if bot is responding
• /help - Show this help message

How to use:
1. Join our channel first
2. Use /batch <channel> to set source
3. Use /forward <start_id> <count> to forward files

For support: @technicalserena"""
            
            await message.reply(help_text)
            print("✅ Help response sent successfully")
        except Exception as e:
            print(f"❌ Error sending help response: {e}")
            import traceback
            traceback.print_exc()

    # Echo handler for debugging
    @app.on_message(filters.text & ~filters.command(["start", "test", "help"]))
    async def echo(client, message: Message):
        print(f"=== RECEIVED TEXT MESSAGE FROM USER {message.from_user.id}: '{message.text}' ===")
        try:
            await message.reply(f"Echo: {message.text}\n\nI received your message! ✅")
            print("✅ Echo response sent")
        except Exception as e:
            print(f"❌ Error sending echo response: {e}")

    print("✅ All handlers registered successfully!")
    
else:
    print("❌ App not available, handlers not registered")
