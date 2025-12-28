"""
Configuration module for Serena Forward Bot.
All values are optional and can be overridden via environment variables.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Main configuration class with environment variable support."""
    
    # Telegram API Credentials
    API_ID: int = int(os.environ.get("API_ID", "0"))
    API_HASH: str = os.environ.get("API_HASH", "")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    # MongoDB Configuration
    MONGO_DB_URL: str = os.environ.get("MONGO_DB_URL", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.environ.get("MONGO_DB_NAME", "serena_forward")
    
    # Owner Configuration
    OWNER_IDS: List[int] = [
        1598576202,
        6518065496
    ]
    
    # Add additional owners from environment
    _extra_owners = os.environ.get("OWNER_IDS", "")
    if _extra_owners:
        OWNER_IDS.extend([int(x.strip()) for x in _extra_owners.split(",") if x.strip()])
    
    # Log Channel
    LOG_CHANNEL: int = int(os.environ.get("LOG_CHANNEL", "-1003286415377"))
    
    # Force Subscription
    FORCE_SUB_CHANNEL: str = os.environ.get("FORCE_SUB_CHANNEL", "serenaunzipbot")
    FORCE_SUB_LINK: str = f"https://t.me/{FORCE_SUB_CHANNEL}"
    
    # Owner Contact Links
    OWNER_CONTACT_1: str = os.environ.get("OWNER_CONTACT_1", "https://t.me/technicalserena")
    OWNER_CONTACT_2: str = os.environ.get("OWNER_CONTACT_2", "@Xioqui_xin")
    
    # Media Configuration
    START_PIC: Optional[str] = os.environ.get("START_PIC", None)
    BOT_START_PIC: Optional[str] = os.environ.get("BOT_START_PIC", None)
    
    # Progress & Performance
    PROGRESS_UPDATE_DELAY: int = int(os.environ.get("PROGRESS_UPDATE_DELAY", "7"))
    MAX_BATCH_LIMIT: int = int(os.environ.get("MAX_BATCH_LIMIT", "500"))
    FLOOD_WAIT_MULTIPLIER: float = float(os.environ.get("FLOOD_WAIT_MULTIPLIER", "1.5"))
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = int(os.environ.get("RATE_LIMIT_MESSAGES", "30"))
    RATE_LIMIT_WINDOW: int = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
    
    # Session Encryption
    SESSION_ENCRYPTION_KEY: str = os.environ.get(
        "SESSION_ENCRYPTION_KEY", 
        "your-32-byte-secret-key-here!!"
    )
    
    # Paths
    DOWNLOAD_PATH: str = os.environ.get("DOWNLOAD_PATH", "./downloads")
    THUMB_PATH: str = os.environ.get("THUMB_PATH", "./thumbnails")
    SESSION_PATH: str = os.environ.get("SESSION_PATH", "./sessions")
    
    # Bot State
    BOT_ENABLED: bool = True
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration values."""
        required = ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_DB_URL"]
        missing = []
        
        for key in required:
            value = getattr(cls, key, None)
            if not value or value == "0" or value == "":
                missing.append(key)
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def is_owner(cls, user_id: int) -> bool:
        """Check if a user is an owner."""
        return user_id in cls.OWNER_IDS


# Create directories if they don't exist
for path in [Config.DOWNLOAD_PATH, Config.THUMB_PATH, Config.SESSION_PATH]:
    os.makedirs(path, exist_ok=True)
