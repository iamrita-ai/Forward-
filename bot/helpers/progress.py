"""
Progress bar utilities for download/upload operations.
"""

import time
import asyncio
import logging
from typing import Callable, Optional

from pyrogram.types import Message

from config import Config
from .utils import get_readable_size, get_readable_time

logger = logging.getLogger(__name__)


class ProgressBar:
    """
    Animated progress bar for file operations.
    """
    
    PROGRESS_TEMPLATE = """**{operation}**
`{filename}`
to my server

[{progress_bar}]
◌ Progress😉: 〘 {percentage}% 〙
Done: 〘{done} of {total}〙
◌ Speed🚀: 〘 {speed}/s 〙
◌ Time Left⏳: 〘 {eta} 〙"""
    
    def __init__(
        self,
        message: Message,
        filename: str,
        operation: str = "Downloading"
    ):
        """
        Initialize progress bar.
        
        Args:
            message: Message to update with progress
            filename: Name of file being processed
            operation: Operation type (Downloading/Uploading)
        """
        self.message = message
        self.filename = filename
        self.operation = operation
        self.start_time = time.time()
        self.last_update = 0
        self.cancelled = False
    
    async def update(
        self,
        current: int,
        total: int
    ):
        """
        Update progress bar.
        
        Args:
            current: Current bytes processed
            total: Total bytes
        """
        if self.cancelled:
            raise asyncio.CancelledError("Operation cancelled by user")
        
        now = time.time()
        
        # Rate limit updates
        if now - self.last_update < Config.PROGRESS_UPDATE_DELAY:
            return
        
        self.last_update = now
        
        try:
            # Calculate progress
            percentage = (current / total) * 100 if total > 0 else 0
            elapsed = now - self.start_time
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            
            # Build progress bar
            progress_bar = self._build_bar(percentage)
            
            # Format message
            text = self.PROGRESS_TEMPLATE.format(
                operation=self.operation,
                filename=self.filename[:50] + "..." if len(self.filename) > 50 else self.filename,
                progress_bar=progress_bar,
                percentage=f"{percentage:.2f}",
                done=get_readable_size(current),
                total=get_readable_size(total),
                speed=get_readable_size(speed),
                eta=get_readable_time(int(eta))
            )
            
            await self.message.edit_text(text)
            
        except Exception as e:
            logger.debug(f"Progress update error: {e}")
    
    def _build_bar(self, percentage: float, length: int = 20) -> str:
        """Build visual progress bar."""
        filled = int(length * percentage / 100)
        bar = "●" * filled + "○" * (length - filled)
        return bar
    
    def cancel(self):
        """Cancel the operation."""
        self.cancelled = True
    
    @staticmethod
    def get_callback(
        message: Message,
        filename: str,
        operation: str = "Downloading"
    ) -> Callable:
        """
        Get a callback function for Pyrogram's progress parameter.
        
        Returns:
            Async callback function
        """
        progress = ProgressBar(message, filename, operation)
        
        async def callback(current: int, total: int):
            await progress.update(current, total)
        
        return callback


class BatchProgressTracker:
    """
    Track progress for batch operations.
    """
    
    def __init__(
        self,
        message: Message,
        total_files: int
    ):
        """
        Initialize batch progress tracker.
        
        Args:
            message: Status message to update
            total_files: Total number of files to process
        """
        self.message = message
        self.total = total_files
        self.current = 0
        self.failed = 0
        self.start_time = time.time()
        self.last_update = 0
    
    async def update(
        self,
        increment: int = 1,
        failed: bool = False
    ):
        """Update batch progress."""
        self.current += increment
        if failed:
            self.failed += 1
        
        now = time.time()
        if now - self.last_update < 3:  # Update every 3 seconds
            return
        
        self.last_update = now
        
        try:
            elapsed = now - self.start_time
            avg_time = elapsed / self.current if self.current > 0 else 0
            eta = avg_time * (self.total - self.current)
            
            text = f"""📊 **Batch Progress**

✅ Completed: {self.current}/{self.total}
❌ Failed: {self.failed}
⏱ Elapsed: {get_readable_time(int(elapsed))}
⏳ ETA: {get_readable_time(int(eta))}

[{self._build_bar()}]"""
            
            await self.message.edit_text(text)
            
        except Exception as e:
            logger.debug(f"Batch progress update error: {e}")
    
    def _build_bar(self, length: int = 20) -> str:
        """Build progress bar."""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        filled = int(length * percentage / 100)
        return "█" * filled + "░" * (length - filled)
