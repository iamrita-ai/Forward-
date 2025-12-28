from pyrogram import filters
from pyrogram.types import Message
from app.main import app

print("Registering simple handlers...")

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    print(f"🤖 /start received from {message.from_user.id}")
    await message.reply("🎉 Hello! I'm alive and working! Send /test to verify.")

@app.on_message(filters.command("test"))
async def test(client, message: Message):
    print(f"🧪 /test received from {message.from_user.id}")
    user_info = f"User: {message.from_user.first_name} (@{message.from_user.username or 'No username'})"
    await message.reply(f"✅ Test successful!\n\n{user_info}\nID: {message.from_user.id}")

@app.on_message(filters.command("help"))
async def help(client, message: Message):
    print(f"📖 /help received from {message.from_user.id}")
    await message.reply("📚 Commands: /start, /test, /help")

@app.on_message(filters.text)
async def echo(client, message: Message):
    print(f"💬 Message from {message.from_user.id}: {message.text}")
    # Don't reply to every message to avoid spam, just log it

print("✅ Simple handlers registered")
