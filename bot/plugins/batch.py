"""
Batch forwarding handler.
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, MessageIdInvalid, ChatAdminRequired

from config import Config
from bot.helpers.decorators import check_subscription, check_login, bot_enabled, rate_limit
from bot.helpers.progress import ProgressBar, BatchProgressTracker
from bot.helpers.thumbnail import ThumbnailGenerator
from bot.helpers.cleanup import CleanupManager
from bot.helpers.utils import parse_chat_id, parse_message_link, get_readable_size
from bot.helpers.queue_manager import TaskStatus
from strings.messages import Messages

logger = logging.getLogger(__name__)

# Batch states
batch_states = {}


@Client.on_message(filters.command("batch") & filters.private)
@bot_enabled
@check_subscription
@check_login
@rate_limit(max_calls=3, window_seconds=60)
async def batch_command(client: Client, message: Message):
    """Handle /batch command to start batch forwarding."""
    user_id = message.from_user.id
    
    # Check for existing active task
    if client.queue_manager.has_active_task(user_id):
        task = client.queue_manager.get_task(user_id)
        await message.reply_text(
            f"⚠️ You already have an active batch task!\n\n"
            f"Progress: {task.current}/{task.total_messages}\n"
            f"Status: {task.status.value}\n\n"
            f"Use /cancel to stop the current task.",
            quote=True
        )
        return
    
    # Check if user has destination chat set
    dest_chat = await client.db.settings.get_destination_chat(user_id)
    if not dest_chat:
        await message.reply_text(
            "⚠️ **Destination chat not set!**\n\n"
            "Please set a destination chat first:\n"
            "1. Go to /settings\n"
            "2. Click 'Set Chat ID'\n"
            "3. Send the chat ID where you want files forwarded",
            quote=True
        )
        return
    
    # Initialize batch state
    batch_states[user_id] = {"step": "source"}
    
    await message.reply_text(
        Messages.BATCH_SOURCE_PROMPT,
        quote=True
    )


@Client.on_message(filters.private & filters.text & ~filters.command([
    "start", "login", "logout", "batch", "cancel", "help",
    "settings", "stats", "users", "broadcast", "stop", "on"
]))
async def handle_batch_input(client: Client, message: Message):
    """Handle batch workflow inputs."""
    user_id = message.from_user.id
    
    if user_id not in batch_states:
        return
    
    state = batch_states[user_id]
    step = state.get("step")
    
    if step == "source":
        await handle_source_input(client, message, state)
    elif step == "count":
        await handle_count_input(client, message, state)


async def handle_source_input(client: Client, message: Message, state: dict):
    """Handle source message link/ID input."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Parse message link
    parsed = parse_message_link(text)
    
    if not parsed:
        await message.reply_text(
            "❌ Invalid message link.\n\n"
            "Please send a valid Telegram message link:\n"
            "`https://t.me/channel/123`\n"
            "`https://t.me/c/1234567890/123`",
            quote=True
        )
        return
    
    chat_id, msg_id = parsed
    
    # Verify access to the source
    user_client = client.user_clients.get(user_id)
    if not user_client:
        await message.reply_text(
            "❌ Session not active. Please /login again.",
            quote=True
        )
        del batch_states[user_id]
        return
    
    try:
        # Try to get the message to verify access
        await user_client.get_messages(chat_id, msg_id)
        
        state["source_chat"] = chat_id
        state["start_msg_id"] = msg_id
        state["step"] = "count"
        
        await message.reply_text(
            Messages.BATCH_COUNT_PROMPT.format(max_limit=Config.MAX_BATCH_LIMIT),
            quote=True
        )
        
    except Exception as e:
        logger.error(f"Source verification error: {e}")
        await message.reply_text(
            f"❌ Cannot access that message.\n\n"
            f"Error: {str(e)}\n\n"
            "Make sure your logged-in account has access to that channel/group.",
            quote=True
        )


async def handle_count_input(client: Client, message: Message, state: dict):
    """Handle message count input."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    try:
        count = int(text)
        
        if count <= 0:
            await message.reply_text(
                "❌ Please enter a positive number.",
                quote=True
            )
            return
        
        if count > Config.MAX_BATCH_LIMIT:
            await message.reply_text(
                f"❌ Maximum limit is {Config.MAX_BATCH_LIMIT} messages.\n\n"
                f"Please enter a smaller number.",
                quote=True
            )
            return
        
        state["count"] = count
        
        # Get destination chat
        dest_chat = await client.db.settings.get_destination_chat(user_id)
        
        # Create task
        task = client.queue_manager.create_task(
            user_id=user_id,
            source_chat=state["source_chat"],
            start_message_id=state["start_msg_id"],
            total_messages=count,
            destination_chat=dest_chat
        )
        
        if not task:
            await message.reply_text(
                "❌ Could not 
