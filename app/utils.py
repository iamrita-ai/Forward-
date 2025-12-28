import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from pyrogram.errors import FloodWait, BadRequest
from pyrogram.enums import ParseMode
from config import LOG_CHANNEL, FORCE_SUB_LINK, CONTACT_LINKS, PROGRESS_DELAY
from app.database import get_output_channel
from app.progress import progress_for_pyrogram
from time import time

async def is_user_subscribed(client, message):
    try:
        user = await client.get_chat_member(FORCE_SUB_LINK.replace("https://t.me/", ""), message.from_user.id)
        if user.status in ["left", "kicked"]:
            raise Exception
        save_user(message.from_user)
        return True
    except:
        contacts = ", ".join([f"@{c}" if c.startswith("@") else c for c in CONTACT_LINKS])
        await message.reply(f"🔒 You must join [our channel]({FORCE_SUB_LINK}) to use this bot.\n\nContact: {contacts}", parse_mode=ParseMode.MARKDOWN)
        return False

def save_user(user):
    from app.database import db
    db.users.update_one({"id": user.id}, {
        "$set": {"id": user.id, "username": user.username, "first_name": user.first_name}
    }, upsert=True)

async def check_bot_status(message):
    from app.database import get_bot_status
    status = await get_bot_status()
    if status == "off":
        if message.from_user.id not in [int(x) for x in os.getenv("OWNER_IDS", "1598576202,6518065496").split(",")]:
            await message.reply("🔴 Bot is currently offline. Please try again later.")
            return False
    return True

async def toggle_bot_status(new_status=None):
    from app.database import get_bot_status, set_bot_status
    current_status = await get_bot_status()
    
    if new_status:
        final_status = new_status
    else:
        final_status = "off" if current_status == "on" else "on"
    
    await set_bot_status(final_status)
    return final_status

async def forward_media_batch(client, message, chat, start_id, count, task_id):
    sent_count = 0
    msg_id = start_id
    output_channel = await get_output_channel()
    target_chat = output_channel if output_channel else message.chat.id
    
    # Pin the tracking message
    progress_msg = await message.reply(f"📤 Starting forward operation...\nProgress: 0/{count}")
    try:
        await progress_msg.pin()
    except:
        pass
    
    start_time = time()
    
    while sent_count < count:
        try:
            msg = await client.get_messages(chat, msg_id)
            if not msg:
                break

            if msg.media or msg.text or msg.sticker:
                # Show progress during download/upload
                progress_message = await message.reply("Starting...")
                
                if hasattr(msg, 'document') and msg.document:
                    sent = await msg.forward(
                        target_chat,
                        progress=progress_for_pyrogram,
                        progress_args=("📥 Downloading", progress_message, start_time)
                    )
                else:
                    sent = await msg.forward(target_chat)
                    
                await progress_message.delete()
                sent_count += 1
                
                # Update pinned message
                try:
                    await progress_msg.edit_text(f"📤 Forwarding in progress...\nProgress: {sent_count}/{count}")
                except:
                    pass

            msg_id += 1
            await asyncio.sleep(0.5)

        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
        except BadRequest:
            msg_id += 1
        except Exception as e:
            print(str(e))
            break

    await progress_msg.edit_text(f"✅ Successfully forwarded {sent_count}/{count} items!")
    from app.database import db
    db.tasks.delete_one({"task_id": task_id})
