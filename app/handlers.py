from pyrogram import filters
from pyrogram.types import Message
from app.main import app

print("Registering debug handlers...")

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    print(f"🤖 RECEIVED /start FROM USER: {message.from_user.id} ({message.from_user.first_name})")
    try:
        await message.reply("🎉 Hello! I'm ALIVE and WORKING! ✅\n\nSend /test to verify functionality.")
        print("✅ Sent /start response")
    except Exception as e:
        print(f"❌ Error sending /start response: {e}")

@app.on_message(filters.command("test"))
async def test(client, message: Message):
    print(f"🧪 RECEIVED /test FROM USER: {message.from_user.id} ({message.from_user.first_name})")
    try:
        response = f"""✅ TEST SUCCESSFUL!

User Info:
• Name: {message.from_user.first_name}
• ID: {message.from_user.id}
• Username: @{message.from_user.username or 'None'}

Bot Status: ✅ ONLINE and RESPONDING!"""
        await message.reply(response)
        print("✅ Sent /test response")
    except Exception as e:
        print(f"❌ Error sending /test response: {e}")

@app.on_message(filters.command("help"))
async def help(client, message: Message):
    print(f"📖 RECEIVED /help FROM USER: {message.from_user.id}")
    try:
        await message.reply("📚 Available commands:\n• /start - Welcome\n• /test - Test bot\n• /help - This message")
        print("✅ Sent /help response")
    except Exception as e:
        print(f"❌ Error sending /help response: {e}")

@app.on_message(filters.text & ~filters.command(["start", "test", "help"]))
async def debug_text(client, message: Message):
    print(f"💬 TEXT MESSAGE from {message.from_user.id}: '{message.text}'")
    # Don't auto-reply to avoid spam

print("✅ Debug handlers registered successfully!")
