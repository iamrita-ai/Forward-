import asyncio
from pyrogram.errors import FloodWait, BadRequest
from pyrogram.enums import ParseMode
from config import LOG_CHANNEL, FORCE_SUB_LINK, CONTACT_LINKS
from app.database import db

async def is_user_subscribed(client, message):
    try:
        user = await client.get_chat_member(FORCE_SUB_LINK.replace("https://t.me/", ""), message.from_user.id)
        if user.status in ["left", "kicked"]:
            raise Exception
        save_user(message.from_user)
        return True
    except:
        await message.reply("🔒 You must join [our channel](%s) to use this bot.\n\nContact: %s" % (
            FORCE_SUB_LINK, CONTACT_LINKS), parse_mode=ParseMode.MARKDOWN)
        return False

def save_user(user):
    db.users.update_one({"id": user.id}, {
        "$set": {"id": user.id, "username": user.username, "first_name": user.first_name}
    }, upsert=True)

async def forward_media_batch(client, message, chat, start_id, count, task_id):
    sent_count = 0
    msg_id = start_id

    while sent_count < count:
        try:
            msg = await client.get_messages(chat, msg_id)
            if not msg:
                break

            if msg.media or msg.text or msg.sticker:
                await msg.forward(message.chat.id)
                sent_count += 1

            msg_id += 1
            await asyncio.sleep(0.5)

        except FloodWait as e:
            await asyncio.sleep(e.x + 5)
        except BadRequest:
            msg_id += 1
        except Exception as e:
            print(str(e))
            break

    await message.reply(f"✅ Sent {sent_count}/{count} items.")
    db.tasks.delete_one({"task_id": task_id})
