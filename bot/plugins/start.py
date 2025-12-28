"""
Start command and welcome message handler.
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from config import Config
from bot.helpers.decorators import check_subscription, bot_enabled
from strings.messages import Messages

logger = logging.getLogger(__name__)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Build start message keyboard."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton("🔐 Login", callback_data="login_info"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ],
        [
            InlineKeyboardButton(
                "📢 Channel",
                url=Config.FORCE_SUB_LINK
            ),
            InlineKeyboardButton(
                "👨‍💻 Developer",
                url=Config.OWNER_CONTACT_1
            )
        ],
        [
            InlineKeyboardButton(
                "💬 Support",
                url=f"https://t.me/{Config.OWNER_CONTACT_2.replace('@', '')}"
            )
        ]
    ])


@Client.on_message(filters.command("start") & filters.private)
@bot_enabled
@check_subscription
async def start_command(client: Client, message: Message):
    """Handle /start command."""
    user = message.from_user
    user_id = user.id
    
    # Add user to database
    await client.db.users.add_user(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Get start picture
    start_pic = None
    
    # Check user's custom start pic first
    user_pic = await client.db.settings.get_start_pic(user_id)
    if user_pic:
        start_pic = user_pic
    else:
        # Check global bot start pic
        bot_pic = await client.db.settings.get_bot_start_pic()
        if bot_pic:
            start_pic = bot_pic
        elif Config.START_PIC:
            start_pic = Config.START_PIC
    
    welcome_text = Messages.START.format(
        user=user.mention,
        bot_name="Serena Forward"
    )
    
    keyboard = get_start_keyboard()
    
    try:
        if start_pic:
            await message.reply_photo(
                photo=start_pic,
                caption=welcome_text,
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                text=welcome_text,
                reply_markup=keyboard
            )
    except Exception as e:
        logger.error(f"Error sending start message: {e}")
        await message.reply_text(
            text=welcome_text,
            reply_markup=keyboard
        )


@Client.on_callback_query(filters.regex("^back_to_start$"))
@check_subscription
async def back_to_start(client: Client, callback: CallbackQuery):
    """Handle back to start callback."""
    user = callback.from_user
    
    welcome_text = Messages.START.format(
        user=user.mention,
        bot_name="Serena Forward"
    )
    
    keyboard = get_start_keyboard()
    
    try:
        await callback.message.edit_text(
            text=welcome_text,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error editing to start: {e}")
    
    await callback.answer()


@Client.on_callback_query(filters.regex("^check_subscription$"))
async def check_sub_callback(client: Client, callback: CallbackQuery):
    """Handle subscription check callback."""
    user_id = callback.from_user.id
    
    try:
        member = await client.get_chat_member(
            f"@{Config.FORCE_SUB_CHANNEL}",
            user_id
        )
        
        if member.status not in ["left", "kicked"]:
            await callback.answer("✅ Verified! You can use the bot now.", show_alert=True)
            
            # Send start message
            await start_command(client, callback.message)
            return
            
    except Exception as e:
        logger.debug(f"Subscription check error: {e}")
    
    await callback.answer(
        "❌ You haven't joined yet. Please join the channel first.",
        show_alert=True
    )
