"""
MongoDB connection and database management.
"""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import Config

logger = logging.getLogger(__name__)


class Database:
    """
    Main database class managing MongoDB connection and collections.
    """
    
    def __init__(self):
        """Initialize database connection."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
        # Collection managers
        self.users: Optional["UsersDB"] = None
        self.sessions: Optional["SessionsDB"] = None
        self.settings: Optional["SettingsDB"] = None
    
    async def connect(self):
        """Establish database connection."""
        try:
            self.client = AsyncIOMotorClient(
                Config.MONGO_DB_URL,
                serverSelectionTimeoutMS=5000
            )
            
            # Verify connection
            await self.client.admin.command("ping")
            
            self.db = self.client[Config.MONGO_DB_NAME]
            
            # Initialize collection managers
            from .users import UsersDB
            from .sessions import SessionsDB
            from .settings_db import SettingsDB
            
            self.users = UsersDB(self.db)
            self.sessions = SessionsDB(self.db)
            self.settings = SettingsDB(self.db)
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB: {Config.MONGO_DB_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance."""
        try:
            # Users collection indexes
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index("username")
            await self.db.users.create_index("joined_at")
            
            # Sessions collection indexes
            await self.db.sessions.create_index("user_id", unique=True)
            await self.db.sessions.create_index("is_active")
            await self.db.sessions.create_index("created_at")
            
            # Settings collection indexes
            await self.db.settings.create_index("user_id", unique=True)
            
            # Tasks collection indexes
            await self.db.tasks.create_index("user_id")
            await self.db.tasks.create_index("status")
            await self.db.tasks.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    async def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    async def get_stats(self) -> dict:
        """Get database statistics."""
        stats = {
            "users": await self.db.users.count_documents({}),
            "active_sessions": await self.db.sessions.count_documents({"is_active": True}),
            "total_tasks": await self.db.tasks.count_documents({}),
            "completed_tasks": await self.db.tasks.count_documents({"status": "completed"})
        }
        return stats
