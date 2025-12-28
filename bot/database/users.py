"""
User database operations.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class UsersDB:
    """
    User database operations manager.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize users database manager."""
        self.collection = db.users
    
    async def add_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> bool:
        """
        Add a new user or update existing user.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            True if new user was added, False if updated
        """
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "first_name": first_name,
                        "last_name": last_name,
                        "last_active": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "joined_at": datetime.utcnow(),
                        "is_banned": False,
                        "is_premium": False
                    }
                },
                upsert=True
            )
            
            return result.upserted_id is not None
            
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            return await self.collection.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        try:
            cursor = self.collection.find({})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_user_count(self) -> int:
        """Get total user count."""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def get_active_users(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get users active in the last N days."""
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            cursor = self.collection.find({"last_active": {"$gte": cutoff}})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def ban_user(self, user_id: int) -> bool:
        """Ban a user."""
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": True}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    async def unban_user(self, user_id: int) -> bool:
        """Unban a user."""
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"is_banned": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    async def is_banned(self, user_id: int) -> bool:
        """Check if user is banned."""
        try:
            user = await self.get_user(user_id)
            return user.get("is_banned", False) if user else False
        except Exception as e:
            logger.error(f"Error checking ban status for {user_id}: {e}")
            return False
    
    async def update_last_active(self, user_id: int):
        """Update user's last active timestamp."""
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating last active for {user_id}: {e}")
    
    async def get_user_ids(self) -> List[int]:
        """Get all user IDs for broadcasting."""
        try:
            cursor = self.collection.find({}, {"user_id": 1})
            users = await cursor.to_list(length=None)
            return [user["user_id"] for user in users]
        except Exception as e:
            logger.error(f"Error getting user IDs: {e}")
            return []
