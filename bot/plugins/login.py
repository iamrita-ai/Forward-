"""
Login handler with OTP-based authentication.
"""

import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ForceReply
from pyrogram.errors import (
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    FloodWait,
    PhoneNumberInvalid
)

from config import Config
from bot.helpers.decorators import check_subscription, bot_enabled, rate_limit
from bot.helpers.utils import format_phone_number
from strings.messages import Messages

logger = logging.getLogger(__name__)

# Store login states
login_states = {}


@Client.on_message(filters.command("login") & filters.private)
@bot_enabled
@check_subscription
@rate_limit(max_calls=5, window_seconds=300)
async def login_command(client: Client, message: Message):
    """Handle /login command."""
    user_id = message.from_user.id
    
    # Check if already logged in
    if user_id in client.user_clients:
        await message.reply_text(
            "✅ You are already logged in!\n\n"
            "Use /logout to remove your current session first.",
            quote=True
        )
        return
    
    # Check database for existing session
    has_session = await client.db.sessions.has_active_session(user_id)
    if has_session:
        await message.reply_text(
            "✅ You have an active session!\n\n"
            "Use /logout to remove it if you want to login again.",
            quote=True
        )
        return
    
    # Start login process
    login_states[user_id] = {"step": "phone"}
    
    await message.reply_text(
        Messages.LOGIN_PHONE_PROMPT,
        reply_markup=ForceReply(selective=True),
        quote=True
    )


@Client.on_message(filters.private & filters.reply & ~filters.command([
    "login", "logout", "cancel", "batch", "settings", "help", "start"
]))
async def handle_login_reply(client: Client, message: Message):
    """Handle login process replies."""
    user_id = message.from_user.id
    
    if user_id not in login_states:
        return
    
    state = login_states[user_id]
    step = state.get("step")
    
    if step == "phone":
        await handle_phone_input(client, message, state)
    elif step == "otp":
        await handle_otp_input(client, message, state)
    elif step == "2fa":
        await handle_2fa_input(client, message, state)


async def handle_phone_input(client: Client, message: Message, state: dict):
    """Handle phone number input."""
    user_id = message.from_user.id
    phone = format_phone_number(message.text.strip())
    
    # Delete the message containing phone number for privacy
    try:
        await message.delete()
    except:
        pass
    
    status_msg = await client.send_message(
        user_id,
        "📲 Sending verification code..."
    )
    
    try:
        # Create a temporary client for login
        user_client = Client(
            name=f"user_{user_id}",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            in_memory=True
        )
        
        await user_client.connect()
        
        # Send code
        sent_code = await user_client.send_code(phone)
        
        state["step"] = "otp"
        state["phone"] = phone
        state["phone_code_hash"] = sent_code.phone_code_hash
        state["client"] = user_client
        
        await status_msg.edit_text(
            Messages.LOGIN_OTP_PROMPT.format(phone=phone[:4] + "****" + phone[-2:])
        )
        
    except PhoneNumberInvalid:
        await status_msg.edit_text(
            "❌ Invalid phone number format.\n\n"
            "Please enter a valid phone number with country code.\n"
            "Example: `+1234567890`"
        )
        del login_states[user_id]
        
    except FloodWait as e:
        await status_msg.edit_text(
            f"⚠️ Too many attempts. Please wait {e.value} seconds and try again."
        )
        del login_states[user_id]
        
    except Exception as e:
        logger.error(f"Login error for {user_id}: {e}")
        await status_msg.edit_text(
            f"❌ Error: {str(e)}\n\nPlease try again with /login"
        )
        del login_states[user_id]


async def handle_otp_input(client: Client, message: Message, state: dict):
    """Handle OTP input."""
    user_id = message.from_user.id
    
    # Parse OTP - handle spaced format like "6 7 8 3"
    otp = message.text.strip().replace(" ", "").replace("-", "")
    
    # Delete OTP message for security
    try:
        await message.delete()
    except:
        pass
    
    status_msg = await client.send_message(
        user_id,
        "🔐 Verifying code..."
    )
    
    try:
        user_client = state["client"]
        
        # Sign in with OTP
        await user_client.sign_in(
            phone_number=state["phone"],
            phone_code_hash=state["phone_code_hash"],
            phone_code=otp
        )
        
        # Get session string
        session_string = await user_client.export_session_string()
        
        # Save session to database
        await client.db.sessions.save_session(
            user_id=user_id,
            phone_number=state["phone"],
            session_string=session_string
        )
        
        # Store client in active clients
        client.user_clients[user_id] = user_client
        
        # Cleanup
        del login_states[user_id]
        
        await status_msg.edit_text(Messages.LOGIN_SUCCESS)
        
        # Log to channel
        try:
            me = await user_client.get_me()
            await client.send_message(
                Config.LOG_CHANNEL,
                f"🔐 **New Login**\n\n"
                f"👤 User: {message.from_user.mention}\n"
                f"🆔 ID: `{user_id}`\n"
                f"📱 Account: @{me.username or 'N/A'}\n"
                f"📅 Time: `{message.date}`"
            )
        except Exception as e:
            logger.warning(f"Could not log login: {e}")
        
    except SessionPasswordNeeded:
        state["step"] = "2fa"
        await status_msg.edit_text(Messages.LOGIN_2FA_PROMPT)
        
    except PhoneCodeInvalid:
        await status_msg.edit_text(
            "❌ Invalid code. Please enter the correct code.\n\n"
            "Format: `1 2 3 4 5 6` or `123456`"
        )
        
    except PhoneCodeExpired:
        await status_msg.edit_text(
            "❌ Code expired. Please start again with /login"
        )
        del login_states[user_id]
        
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        await status_msg.edit_text(
            f"❌ Error: {str(e)}\n\nPlease try again with /login"
        )
        del login_states[user_id]


async def handle_2fa_input(client: Client, message: Message, state: dict):
    """Handle 2FA password input."""
    user_id = message.from_user.id
    password = message.text.strip()
    
    # Delete password message for security
    try:
        await message.delete()
    except:
        pass
    
    status_msg = await client.send_message(
        user_id,
        "🔐 Verifying 2FA password..."
    )
    
    try:
        user_client = state["client"]
        
        # Check password
        await user_client.check_password(password)
        
        # Get session string
        session_string = await user_client.export_session_string()
        
        # Save session
        await client.db.sessions.save_session(
            user_id=user_id,
            phone_number=state["phone"],
            session_string=session_string
        )
        
        # Store client
        client.user_clients[user_id] = user_client
        
        # Cleanup
        del login_states[user_id]
        
        await status_msg.edit_text(Messages.LOGIN_SUCCESS)
        
    except Exception as e:
        logger.error(f"2FA verification error: {e}")
        await status_msg.edit_text(
            f"❌ Error: {str(e)}\n\nPlease try again with /login"
        )
        del login_states[user_id]


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_login(client: Client, message: Message):
    """Cancel ongoing login process."""
    user_id = message.from_user.id
    
    if user_id in login_states:
        state = login_states[user_id]
        
        # Disconnect temporary client if exists
        if "client" in state:
            try:
                await state["client"].disconnect()
            except:
                pass
        
        del login_states[user_id]
        await message.reply_text("❌ Login process cancelled.", quote=True)
    else:
        # Check for active batch task
        if client.queue_manager.cancel_task(user_id):
            await message.reply_text("❌ Batch task cancelled.", quote=True)
        else:
            await message.reply_text(
                "ℹ️ No active process to cancel.",
                quote=True
            )
