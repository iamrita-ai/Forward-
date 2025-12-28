"""
Task queue manager for batch operations.
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a batch task."""
    task_id: str
    user_id: int
    source_chat: int
    start_message_id: int
    total_messages: int
    destination_chat: int
    
    # Progress tracking
    current: int = 0
    failed: int = 0
    status: TaskStatus = TaskStatus.PENDING
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Runtime data
    status_message_id: Optional[int] = None
    error_message: Optional[str] = None


class QueueManager:
    """
    Manages task queues for batch operations.
    Ensures one active task per user.
    """
    
    def __init__(self):
        """Initialize queue manager."""
        self.tasks: Dict[int, Task] = {}  # user_id -> Task
        self.locks: Dict[int, asyncio.Lock] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def get_lock(self, user_id: int) -> asyncio.Lock:
        """Get or create lock for user."""
        if user_id not in self.locks:
            self.locks[user_id] = asyncio.Lock()
        return self.locks[user_id]
    
    def has_active_task(self, user_id: int) -> bool:
        """Check if user has an active task."""
        task = self.tasks.get(user_id)
        return task is not None and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
    
    def get_task(self, user_id: int) -> Optional[Task]:
        """Get user's current task."""
        return self.tasks.get(user_id)
    
    def create_task(
        self,
        user_id: int,
        source_chat: int,
        start_message_id: int,
        total_messages: int,
        destination_chat: int
    ) -> Optional[Task]:
        """
        Create a new task for user.
        
        Args:
            user_id: User ID
            source_chat: Source channel/group ID
            start_message_id: Starting message ID
            total_messages: Number of messages to forward
            destination_chat: Destination chat ID
            
        Returns:
            Created task or None if user has active task
        """
        if self.has_active_task(user_id):
            return None
        
        task = Task(
            task_id=f"{user_id}_{datetime.now().timestamp()}",
            user_id=user_id,
            source_chat=source_chat,
            start_message_id=start_message_id,
            total_messages=total_messages,
            destination_chat=destination_chat
        )
        
        self.tasks[user_id] = task
        logger.info(f"Created task {task.task_id} for user {user_id}")
        
        return task
    
    def start_task(self, user_id: int) -> bool:
        """Mark task as running."""
        task = self.tasks.get(user_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            return True
        return False
    
    def update_progress(
        self,
        user_id: int,
        increment: int = 1,
        failed: bool = False
    ):
        """Update task progress."""
        task = self.tasks.get(user_id)
        if task:
            task.current += increment
            if failed:
                task.failed += 1
    
    def complete_task(self, user_id: int):
        """Mark task as completed."""
        task = self.tasks.get(user_id)
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            logger.info(f"Task {task.task_id} completed")
    
    def fail_task(self, user_id: int, error: str = None):
        """Mark task as failed."""
        task = self.tasks.get(user_id)
        if task:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = error
            logger.error(f"Task {task.task_id} failed: {error}")
    
    def cancel_task(self, user_id: int) -> bool:
        """Cancel user's active task."""
        task = self.tasks.get(user_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            logger.info(f"Task {task.task_id} cancelled")
            return True
        return False
    
    def remove_task(self, user_id: int):
        """Remove task from queue."""
        if user_id in self.tasks:
            del self.tasks[user_id]
    
    def get_task_stats(self, user_id: int) -> Optional[dict]:
        """Get task statistics."""
        task = self.tasks.get(user_id)
        if not task:
            return None
        
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "current": task.current,
            "total": task.total_messages,
            "failed": task.failed,
            "percentage": (task.current / task.total_messages * 100) if task.total_messages > 0 else 0,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None
        }
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove old completed/failed tasks."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for user_id, task in self.tasks.items():
            if task.completed_at and task.completed_at < cutoff:
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.tasks[user_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")
