"""
Logout handler for session removal.
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import Config
from bot.helpers.decorators import check_subscription, bot_enabled
from bot.helpers.cleanup import CleanupManager
from strings.messages import Messages

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("logout") & filters.private)
@bot_enabled
@check_subscription
async def logout_command(client: Client, message: Message):
    """Handle /logout command."""
    user_id = message.from_user.id
    
    # Check if user has a session
    has_session = await client.db.sessions.has_active_session(user_id)
    
    if not has_session and user_id not in client.user_clients:
        await message.reply_text(
            "ℹ️ You are not logged in.",
            quote=True
        )
        return
    
    # Confirm logout
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Logout", callback_data="confirm_logout"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_logout")
        ]
    ])
    
    await message.reply_text(
        "⚠️ **Are you sure you want to logout?**\n\n"
        "This will:\n"
        "• Terminate your session\n"
        "• Remove all session data\n"
        "• Cancel any active tasks\n\n"
        "You will need to login again to use forwarding features.",
        reply_markup=keyboard,
        quote=True
    )


@Client.on_callback_query(filters.regex("^confirm_logout$"))
async def confirm_logout(client: Client, callback: CallbackQuery):
    """Handle logout confirmation."""
    user_id = callback.from_user.id
    
    await callback.message.edit_text("🔄 Logging out...")
    
    try:
        # Cancel any active tasks
        client.queue_manager.cancel_task(user_id)
        
        # Disconnect user client if active
        if user_id in client.user_clients:
            try:
                await client.user_clients[user_id].stop()
            except Exception as e:
                logger.warning(f"Error stopping user client: {e}")
            
            del client.user_clients[user_id]
        
        # Delete session from database
        await client.db.sessions.delete_session(user_id)
        
        # Clean up session files
        await CleanupManager.cleanup_session_files(user_id)
        
        # Clean up user files
        await CleanupManager.cleanup_user_files(user_id)
        
        await callback.message.edit_text(Messages.LOGOUT_SUCCESS)
        
        # Log logout
        try:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"🚪 **User Logout**\n\n"
                f"👤 User: {callback.from_user.mention}\n"
                f"🆔 ID: `{user_id}`"
            )
        except:
            pass
        
    except Exception as e:
        logger.error(f"Logout error for {user_id}: {e}")
        await callback.message.edit_text(
            f"❌ Error during logout: {str(e)}\n\n"
            "Please try again or contact support."
        )


@Client.on_callback_query(filters.regex("^cancel_logout$"))
async def cancel_logout(client: Client, callback: CallbackQuery):
    """Handle logout cancellation."""
    await callback.message.edit_text("✅ Logout cancelled. Your session is still active.")
    await callback.answer()
