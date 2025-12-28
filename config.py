"""
Configuration module for Serena Forward Bot.
All values can be overridden via environment variables.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Bot configuration class with environment variable support."""
    
    # Telegram API Credentials
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # MongoDB Configuration
    MONGO_DB_URL: str = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "serena_forward")
    
    # Owner Configuration
    OWNER_IDS: List[int] = [
        1598576202,
        6518065496
    ]
    
    # Log Channel
    LOG_CHANNEL: int = int(os.getenv("LOG_CHANNEL", "-1003286415377"))
    
    # Force Subscription
    FORCE_SUB_CHANNEL: str = os.getenv("FORCE_SUB_CHANNEL", "serenaunzipbot")
    FORCE_SUB_LINK: str = f"https://t.me/{FORCE_SUB_CHANNEL}"
    
    # Contact Links
    OWNER_CONTACT: str = "https://t.me/technicalserena"
    SUPPORT_USERNAME: str = "@Xioqui_xin"
    
    # Bot Settings
    START_PIC: Optional[str] = os.getenv("START_PIC", None)
    BOT_START_PIC: Optional[str] = os.getenv("BOT_START_PIC", None)
    PROGRESS_UPDATE_DELAY: int = int(os.getenv("PROGRESS_UPDATE_DELAY", "7"))
    MAX_BATCH_LIMIT: int = int(os.getenv("MAX_BATCH_LIMIT", "1000"))
    
    # Flood Wait Handling
    FLOOD_WAIT_THRESHOLD: int = int(os.getenv("FLOOD_WAIT_THRESHOLD", "60"))
    
    # Session Encryption
    SESSION_ENCRYPTION_KEY: str = os.getenv(
        "SESSION_ENCRYPTION_KEY", 
        "default-key-change-in-production-32b"
    )
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Directories
    DOWNLOAD_DIR: str = os.getenv("DOWNLOAD_DIR", "./downloads")
    THUMB_DIR: str = os.getenv("THUMB_DIR", "./thumbnails")
    SESSION_DIR: str = os.getenv("SESSION_DIR", "./sessions")
    
    # Bot Status
    BOT_ENABLED: bool = True
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration values."""
        required = ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_DB_URL"]
        missing = []
        
        for field in required:
            value = getattr(cls, field, None)
            if not value or value == "0" or value == "":
                missing.append(field)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        for directory in [cls.DOWNLOAD_DIR, cls.THUMB_DIR, cls.SESSION_DIR]:
            os.makedirs(directory, exist_ok=True)


# Validate configuration on import
try:
    Config.validate()
    Config.create_directories()
except ValueError as e:
    print(f"Configuration Error: {e}")
