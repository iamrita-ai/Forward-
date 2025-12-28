"""
Main Bot Client for Serena Forward.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from pyrogram import Client, idle
from pyrogram.types import BotCommand

from config import Config
from bot.database import Database
from bot.helpers.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class SerenaBot(Client):
    """
    Main bot client with extended functionality.
    Handles initialization, plugin loading, and lifecycle management.
    """
    
    def __init__(self):
        """Initialize the Serena Forward Bot."""
        super().__init__(
            name="SerenaForward",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="bot/plugins"),
            workdir="./",
            workers=8
        )
        
        # Bot state
        self.start_time: datetime = datetime.now()
        self.is_enabled: bool = Config.BOT_ENABLED
        
        # Database connection
        self.db: Optional[Database] = None
        
        # User clients for session management
        self.user_clients: Dict[int, Client] = {}
        
        # Queue manager for batch tasks
        self.queue_manager: QueueManager = QueueManager()
        
        # Active tasks tracking
        self.active_tasks: Dict[int, dict] = {}
        
        # Rate limiting cache
        self.rate_limit_cache: Dict[int, list] = {}
    
    async def start(self):
        """Start the bot and initialize all components."""
        # Initialize database
        self.db = Database()
        await self.db.connect()
        logger.info("Database connected successfully")
        
        # Start the bot
        await super().start()
        
        # Set bot commands
        await self.set_bot_commands()
        
        # Load existing user sessions
        await self.load_user_sessions()
        
        # Get bot info
        me = await self.get_me()
        logger.info(f"Bot started as @{me.username} (ID: {me.id})")
        
        # Send startup notification to log channel
        try:
            await self.send_message(
                Config.LOG_CHANNEL,
                f"🤖 **Serena Forward Bot Started**\n\n"
                f"📅 Time: `{datetime.now()}`\n"
                f"👤 Bot: @{me.username}\n"
                f"🆔 ID: `{me.id}`"
            )
        except Exception as e:
            logger.warning(f"Could not send startup message to log channel: {e}")
    
    async def stop(self, *args):
        """Graceful shutdown."""
        logger.info("Shutting down bot...")
        
        # Close all user clients
        for user_id, client in self.user_clients.items():
            try:
                await client.stop()
                logger.info(f"Closed client for user {user_id}")
            except Exception as e:
                logger.error(f"Error closing client for user {user_id}: {e}")
        
        # Close database connection
        if self.db:
            await self.db.close()
        
        await super().stop(*args)
        logger.info("Bot stopped successfully")
    
    async def set_bot_commands(self):
        """Set the bot commands menu."""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("login", "Login with phone number"),
            BotCommand("logout", "Remove your session"),
            BotCommand("batch", "Start batch forwarding"),
            BotCommand("cancel", "Cancel ongoing task"),
            BotCommand("settings", "Open settings menu"),
            BotCommand("stats", "View bot statistics"),
        ]
        
        await self.set_bot_commands(commands)
        logger.info("Bot commands set successfully")
    
    async def load_user_sessions(self):
        """Load all active user sessions from database."""
        try:
            sessions = await self.db.sessions.get_all_active_sessions()
            
            for session_data in sessions:
                user_id = session_data.get("user_id")
                session_string = session_data.get("session_string")
                
                if user_id and session_string:
                    try:
                        client = Client(
                            name=f"user_{user_id}",
                            api_id=Config.API_ID,
                            api_hash=Config.API_HASH,
                            session_string=session_string,
                            in_memory=True
                        )
                        await client.start()
                        self.user_clients[user_id] = client
                        logger.info(f"Loaded session for user {user_id}")
                    except Exception as e:
                        logger.error(f"Failed to load session for user {user_id}: {e}")
                        # Mark session as invalid
                        await self.db.sessions.invalidate_session(user_id)
            
            logger.info(f"Loaded {len(self.user_clients)} user sessions")
        except Exception as e:
            logger.error(f"Error loading user sessions: {e}")
    
    def get_uptime(self) -> str:
        """Get bot uptime as formatted string."""
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        
        return " ".join(parts)
