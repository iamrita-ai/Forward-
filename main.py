#!/usr/bin/env python3
"""
Serena Forward Bot - Main Entry Point
A production-ready Telegram forwarding bot with user session management.
"""

import asyncio
import logging
import sys
from datetime import datetime

from bot.client import SerenaBot
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", mode="a")
    ]
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)


async def main():
    """Main async entry point."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Initialize and start the bot
        bot = SerenaBot()
        
        logger.info("=" * 50)
        logger.info("Starting Serena Forward Bot...")
        logger.info(f"Bot Start Time: {datetime.now()}")
        logger.info("=" * 50)
        
        await bot.start()
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
