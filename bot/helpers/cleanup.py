"""
Cleanup utilities for temporary files and storage management.
"""

import os
import shutil
import logging
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta

from config import Config

logger = logging.getLogger(__name__)


class CleanupManager:
    """
    Manage cleanup of temporary files and storage.
    """
    
    @staticmethod
    async def delete_file(file_path: str) -> bool:
        """
        Safely delete a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted successfully
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    async def delete_files(file_paths: List[str]) -> int:
        """
        Delete multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        for path in file_paths:
            if await CleanupManager.delete_file(path):
                deleted += 1
        return deleted
    
    @staticmethod
    async def cleanup_directory(
        directory: str,
        max_age_hours: int = 24
    ) -> int:
        """
        Clean up old files in a directory.
        
        Args:
            directory: Directory path
            max_age_hours: Maximum file age in hours
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(directory):
            return 0
        
        deleted = 0
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                # Check file age
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff:
                    if await CleanupManager.delete_file(file_path):
                        deleted += 1
            
            logger.info(f"Cleaned up {deleted} files from {directory}")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning directory {directory}: {e}")
            return deleted
    
    @staticmethod
    async def cleanup_user_files(user_id: int):
        """
        Clean up all temporary files for a user.
        
        Args:
            user_id: User ID
        """
        user_download_dir = os.path.join(Config.DOWNLOAD_PATH, str(user_id))
        user_thumb_dir = os.path.join(Config.THUMB_PATH, str(user_id))
        
        for directory in [user_download_dir, user_thumb_dir]:
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    logger.info(f"Cleaned up directory: {directory}")
                except Exception as e:
                    logger.error(f"Error cleaning directory {directory}: {e}")
    
    @staticmethod
    async def cleanup_session_files(user_id: int):
        """
        Clean up session files for a user.
        
        Args:
            user_id: User ID
        """
        session_pattern = f"user_{user_id}"
        
        try:
            for filename in os.listdir(Config.SESSION_PATH):
                if session_pattern in filename:
                    file_path = os.path.join(Config.SESSION_PATH, filename)
                    await CleanupManager.delete_file(file_path)
            
            # Also check root directory for session files
            for filename in os.listdir("./"):
                if filename.endswith(".session") and session_pattern in filename:
                    await CleanupManager.delete_file(filename)
                    
        except Exception as e:
            logger.error(f"Error cleaning session files for {user_id}: {e}")
    
    @staticmethod
    async def get_storage_usage() -> dict:
        """
        Get current storage usage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            "downloads": 0,
            "thumbnails": 0,
            "sessions": 0,
            "total": 0
        }
        
        for key, directory in [
            ("downloads", Config.DOWNLOAD_PATH),
            ("thumbnails", Config.THUMB_PATH),
            ("sessions", Config.SESSION_PATH)
        ]:
            if os.path.exists(directory):
                total = sum(
                    os.path.getsize(os.path.join(directory, f))
                    for f in os.listdir(directory)
                    if os.path.isfile(os.path.join(directory, f))
                )
                stats[key] = total
        
        stats["total"] = sum(v for k, v in stats.items() if k != "total")
        return stats
    
    @staticmethod
    async def run_scheduled_cleanup():
        """Run scheduled cleanup task."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean old files
                await CleanupManager.cleanup_directory(Config.DOWNLOAD_PATH, 24)
                await CleanupManager.cleanup_directory(Config.THUMB_PATH, 24)
                
                logger.info("Scheduled cleanup completed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduled cleanup error: {e}")
