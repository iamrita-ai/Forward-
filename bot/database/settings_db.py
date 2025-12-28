"""
User settings database operations.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class SettingsDB:
    """
    User settings database operations manager.
    """
    
    DEFAULT_SETTINGS = {
        "destination_chat_id": None,
        "start_pic": None,
        "auto_delete": False,
        "forward_mode": "copy",  # copy, forward
        "preserve_caption": True,
        "notifications_enabled": True
    }
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize settings database manager."""
        self.collection = db.settings
        self.global_collection = db.global_settings
    
    async def get_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Get user settings with defaults.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User settings dictionary
        """
        try:
            settings = await self.collection.find_one({"user_id": user_id})
            
            if settings:
                # Merge with defaults
                result = self.DEFAULT_SETTINGS.copy()
                result.update({k: v for k, v in settings.items() if k != "_id"})
                return result
            
            return self.DEFAULT_SETTINGS.copy()
            
        except Exception as e:
            logger.error(f"Error getting settings for {user_id}: {e}")
            return self.DEFAULT_SETTINGS.copy()
    
    async def update_setting(
        self,
        user_id: int,
        key: str,
        value: Any
    ) -> bool:
        """
        Update a single setting.
        
        Args:
            user_id: Telegram user ID
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful
        """
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {key: value, "updated_at": datetime.utcnow()},
                    "$setOnInsert": {"user_id": user_id, "created_at": datetime.utcnow()}
                },
                upsert=True
            )
            return True
            
        except Exception as e:
            logger.error(f"Error updating setting {key} for {user_id}: {e}")
            return False
    
    async def set_destination_chat(self, user_id: int, chat_id: int) -> bool:
        """Set destination chat ID for forwarding."""
        return await self.update_setting(user_id, "destination_chat_id", chat_id)
    
    async def get_destination_chat(self, user_id: int) -> Optional[int]:
        """Get destination chat ID."""
        settings = await self.get_settings(user_id)
        return settings.get("destination_chat_id")
    
    async def set_start_pic(self, user_id: int, file_id: str) -> bool:
        """Set user's custom start picture."""
        return await self.update_setting(user_id, "start_pic", file_id)
    
    async def get_start_pic(self, user_id: int) -> Optional[str]:
        """Get user's start picture."""
        settings = await self.get_settings(user_id)
        return settings.get("start_pic")
    
    async def reset_settings(self, user_id: int) -> bool:
        """Reset all settings to defaults."""
        try:
            await self.collection.delete_one({"user_id": user_id})
            logger.info(f"Settings reset for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error resetting settings for {user_id}: {e}")
            return False
    
    # Global settings (owner only)
    
    async def get_global_setting(self, key: str) -> Optional[Any]:
        """Get a global setting."""
        try:
            setting = await self.global_collection.find_one({"key": key})
            return setting.get("value") if setting else None
        except Exception as e:
            logger.error(f"Error getting global setting {key}: {e}")
            return None
    
    async def set_global_setting(self, key: str, value: Any) -> bool:
        """Set a global setting."""
        try:
            await self.global_collection.update_one(
                {"key": key},
                {
                    "$set": {"value": value, "updated_at": datetime.utcnow()},
                    "$setOnInsert": {"key": key, "created_at": datetime.utcnow()}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting global setting {key}: {e}")
            return False
    
    async def get_bot_start_pic(self) -> Optional[str]:
        """Get global bot start picture."""
        return await self.get_global_setting("bot_start_pic")
    
    async def set_bot_start_pic(self, file_id: str) -> bool:
        """Set global bot start picture."""
        return await self.set_global_setting("bot_start_pic", file_id)
