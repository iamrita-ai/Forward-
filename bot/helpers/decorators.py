"""
Decorator functions for command handlers.
"""

import time
import logging
from functools import wraps
from typing import Callable, List, Optional

from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import UserNotParticipant, ChatAdminRequired

from config import Config
from strings.messages import Messages

logger = logging.getLogger(__name__)


def check_subscription(func: Callable) -> Callable:
    """
    Decorator to check if user is subscribed to force sub channel.
    """
    @wraps(func)
    async def wrapper(client: Client, update: Message | CallbackQuery, *args, **kwargs):
        user_id = update.from_user.id if update.from_user else None
        
        if not user_id:
            return
        
        # Skip check for owners
        if Config.is_owner(user_id):
            return await func(client, update, *args, **kwargs)
        
        try:
            member = await client.get_chat_member(
                f"@{Config.FORCE_SUB_CHANNEL}",
                user_id
            )
            
            if member.status in ["left", "kicked"]:
                raise UserNotParticipant(f"User {user_id} not subscribed")
                
        except UserNotParticipant:
            from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📢 Join Channel",
                    url=Config.FORCE_SUB_LINK
                )],
                [InlineKeyboardButton(
                    "🔄 Check Again",
                    callback_data="check_subscription"
                )]
            ])
            
            if isinstance(update, Message):
                await update.reply_text(
                    Messages.FORCE_SUB,
                    reply_markup=keyboard
                )
            else:
                await update.answer(
                    "Please join our channel first!",
                    show_alert=True
                )
            return
            
        except ChatAdminRequired:
            logger.warning("Bot is not admin in force sub channel")
        except Exception as e:
            logger.error(f"Subscription check error: {e}")
        
        return await func(client, update, *args, **kwargs)
    
    return wrapper


def check_login(func: Callable) -> Callable:
    """
    Decorator to check if user is logged in with a session.
    """
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        
        # Check if user has an active client
        if user_id not in client.user_clients:
            # Try to load from database
            has_session = await client.db.sessions.has_active_session(user_id)
            
            if not has_session:
                await message.reply_text(
                    Messages.NOT_LOGGED_IN,
                    quote=True
                )
                return
        
        return await func(client, message, *args, **kwargs)
    
    return wrapper


def owner_only(func: Callable) -> Callable:
    """
    Decorator to restrict command to owners only.
    """
    @wraps(func)
    async def wrapper(client: Client, update: Message | CallbackQuery, *args, **kwargs):
        user_id = update.from_user.id if update.from_user else None
        
        if not user_id or not Config.is_owner(user_id):
            if isinstance(update, Message):
                await update.reply_text(
                    "⛔ This command is restricted to bot owners only.",
                    quote=True
                )
            else:
                await update.answer(
                    "This is restricted to owners only!",
                    show_alert=True
                )
            return
        
        return await func(client, update, *args, **kwargs)
    
    return wrapper


def rate_limit(
    max_calls: int = None,
    window_seconds: int = None
) -> Callable:
    """
    Decorator for rate limiting user commands.
    
    Args:
        max_calls: Maximum calls allowed in window
        window_seconds: Time window in seconds
    """
    _max_calls = max_calls or Config.RATE_LIMIT_MESSAGES
    _window = window_seconds or Config.RATE_LIMIT_WINDOW
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(client: Client, message: Message, *args, **kwargs):
            user_id = message.from_user.id
            
            # Skip for owners
            if Config.is_owner(user_id):
                return await func(client, message, *args, **kwargs)
            
            now = time.time()
            
            # Initialize or clean old entries
            if user_id not in client.rate_limit_cache:
                client.rate_limit_cache[user_id] = []
            
            # Remove old entries
            client.rate_limit_cache[user_id] = [
                t for t in client.rate_limit_cache[user_id]
                if now - t < _window
            ]
            
            # Check limit
            if len(client.rate_limit_cache[user_id]) >= _max_calls:
                await message.reply_text(
                    f"⚠️ Rate limit exceeded. Please wait {_window} seconds.",
                    quote=True
                )
                return
            
            # Record this call
            client.rate_limit_cache[user_id].append(now)
            
            return await func(client, message, *args, **kwargs)
        
        return wrapper
    
    return decorator


def bot_enabled(func: Callable) -> Callable:
    """
    Decorator to check if bot is enabled.
    """
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if not client.is_enabled and not Config.is_owner(message.from_user.id):
            await message.reply_text(
                "🔴 Bot is currently disabled. Please try again later.",
                quote=True
            )
            return
        
        return await func(client, message, *args, **kwargs)
    
    return wrapper
