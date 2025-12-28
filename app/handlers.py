from pyrogram import filters
from pyrogram.types import Message

print("Registering connection test handlers...")

# Import app from main (will be available after main loads)
try:
    from app.main import app
    print("✅ App reference obtained")
except Exception as e:
    print(f"⚠️ Could not import app yet: {e}")
    app = None

if app:
    @app.on_message(filters.command("start"))
    async def start(client, message: Message):
        print(f"🤖 /start received from {message.from_user.id} ({message.from_user.first_name})")
        try:
            await message.reply("🎉 Hello! Bot connection is WORKING! ✅\n\nSend /test to verify messaging.")
            print("✅ /start response sent")
        except Exception as e:
            print(f"❌ Error in /start: {e}")

    @app.on_message(filters.command("test"))
    async def test(client, message: Message):
        print(f"🧪 /test received from {message.from_user.id} ({message.from_user.first_name})")
        try:
            response = f"""✅ CONNECTION TEST SUCCESSFUL!

📡 Real-time connection confirmed!
👤 User: {message.from_user.first_name}
🆔 ID: {message.from_user.id}
📍 Time: Just now

Bot is fully operational! 🚀"""
            await message.reply(response)
            print("✅ /test response sent")
        except Exception as e:
            print(f"❌ Error in /test: {e}")

    @app.on_message(filters.text)
    async def debug_text(client, message: Message):
        print(f"💬 Message from {message.from_user.id}: '{message.text[:50]}{'...' if len(message.text) > 50 else ''}'")

    print("✅ Connection test handlers registered")
else:
    print("❌ Cannot register handlers - app not available")
