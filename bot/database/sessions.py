"""
Session database operations with encryption.
"""

import logging
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import Config

logger = logging.getLogger(__name__)


class SessionsDB:
    """
    Session database operations manager with encryption support.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize sessions database manager."""
        self.collection = db.sessions
        self._cipher = self._init_cipher()
    
    def _init_cipher(self) -> Fernet:
        """Initialize Fernet cipher for session encryption."""
        key = Config.SESSION_ENCRYPTION_KEY.encode()
        
        # Derive a proper key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"serena_forward_salt",
            iterations=100000
        )
        
        derived_key = base64.urlsafe_b64encode(kdf.derive(key))
        return Fernet(derived_key)
    
    def _encrypt(self, data: str) -> str:
        """Encrypt session string."""
        return self._cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """Decrypt session string."""
        return self._cipher.decrypt(data.encode()).decode()
    
    async def save_session(
        self,
        user_id: int,
        phone_number: str,
        session_string: str
    ) -> bool:
        """
        Save encrypted user session.
        
        Args:
            user_id: Telegram user ID
            phone_number: User's phone number
            session_string: Pyrogram session string
            
        Returns:
            True if successful
        """
        try:
            encrypted_session = self._encrypt(session_string)
            encrypted_phone = self._encrypt(phone_number)
            
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "phone_number": encrypted_phone,
                        "session_string": encrypted_session,
                        "is_active": True,
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "user_id": user_id,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.info(f"Session saved for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session for {user_id}: {e}")
            return False
    
    async def get_session(self, user_id: int) -> Optional[str]:
        """
        Get decrypted session string for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Decrypted session string or None
        """
        try:
            session = await self.collection.find_one({
                "user_id": user_id,
                "is_active": True
            })
            
            if session and session.get("session_string"):
                return self._decrypt(session["session_string"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting session for {user_id}: {e}")
            return None
    
    async def delete_session(self, user_id: int) -> bool:
        """
        Delete user session completely.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if deleted successfully
        """
        try:
            result = await self.collection.delete_one({"user_id": user_id})
            
            if result.deleted_count > 0:
                logger.info(f"Session deleted for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting session for {user_id}: {e}")
            return False
    
    async def invalidate_session(self, user_id: int) -> bool:
        """
        Mark session as inactive without deleting.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        try:
            result = await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"is_active": False, "invalidated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error invalidating session for {user_id}: {e}")
            return False
    
    async def has_active_session(self, user_id: int) -> bool:
        """Check if user has an active session."""
        try:
            session = await self.collection.find_one({
                "user_id": user_id,
                "is_active": True
            })
            return session is not None
            
        except Exception as e:
            logger.error(f"Error checking session for {user_id}: {e}")
            return False
    
    async def get_all_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions (decrypted)."""
        try:
            cursor = self.collection.find({"is_active": True})
            sessions = await cursor.to_list(length=None)
            
            decrypted_sessions = []
            for session in sessions:
                try:
                    decrypted_sessions.append({
                        "user_id": session["user_id"],
                        "session_string": self._decrypt(session["session_string"]),
                        "created_at": session.get("created_at")
                    })
                except Exception as e:
                    logger.warning(f"Could not decrypt session for {session['user_id']}: {e}")
            
            return decrypted_sessions
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
    
    async def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        try:
            return await self.collection.count_documents({"is_active": True})
        except Exception as e:
            logger.error(f"Error counting active sessions: {e}")
            return 0
