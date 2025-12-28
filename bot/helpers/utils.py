"""
Utility functions for Serena Forward Bot.
"""

import re
import os
import math
import asyncio
import logging
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)


def get_readable_size(size_bytes: Union[int, float]) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def get_readable_time(seconds: int) -> str:
    """
    Convert seconds to human-readable time format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string (e.g., "2m, 30s")
    """
    if seconds < 0:
        return "0s"
    
    periods = [
        ('d', 86400),
        ('h', 3600),
        ('m', 60),
        ('s', 1)
    ]
    
    parts = []
    
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            parts.append(f"{int(period_value)}{period_name}")
    
    return ", ".join(parts) if parts else "0s"


def parse_chat_id(chat_input: str) -> Optional[int]:
    """
    Parse a chat ID from various input formats.
    
    Accepts:
        - Numeric ID: -1001234567890
        - Username: @channel_username
        - Link: https://t.me/channel_username
        - Private link: https://t.me/c/1234567890/
        
    Args:
        chat_input: Chat identifier string
        
    Returns:
        Parsed chat ID or None
    """
    chat_input = chat_input.strip()
    
    # Direct numeric ID
    if chat_input.lstrip('-').isdigit():
        return int(chat_input)
    
    # Private channel link
    private_match = re.match(
        r'https?://t\.me/c/(\d+)/?.*',
        chat_input
    )
    if private_match:
        return int(f"-100{private_match.group(1)}")
    
    # Public link or username
    username_match = re.match(
        r'(?:https?://t\.me/|@)?([a-zA-Z][a-zA-Z0-9_]{4,})',
        chat_input
    )
    if username_match:
        return username_match.group(1)
    
    return None


def parse_message_link(link: str) -> Optional[Tuple[Union[int, str], int]]:
    """
    Parse a message link to extract chat and message IDs.
    
    Args:
        link: Telegram message link
        
    Returns:
        Tuple of (chat_id, message_id) or None
    """
    # Private channel: https://t.me/c/1234567890/123
    private_match = re.match(
        r'https?://t\.me/c/(\d+)/(\d+)',
        link
    )
    if private_match:
        chat_id = int(f"-100{private_match.group(1)}")
        message_id = int(private_match.group(2))
        return (chat_id, message_id)
    
    # Public channel: https://t.me/channel/123
    public_match = re.match(
        r'https?://t\.me/([a-zA-Z][a-zA-Z0-9_]{4,})/(\d+)',
        link
    )
    if public_match:
        return (public_match.group(1), int(public_match.group(2)))
    
    return None


def sanitize_filename(filename: str, max_length: int = 60) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        max_length: Maximum length
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace multiple spaces
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    # Truncate if needed
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename or "unnamed_file"


def format_phone_number(phone: str) -> str:
    """
    Format phone number, adding + if missing.
    
    Args:
        phone: Phone number string
        
    Returns:
        Formatted phone number
    """
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    if not phone.startswith('+'):
        # Try to detect country code
        if phone.startswith('0'):
            phone = phone[1:]
        phone = '+' + phone
    
    return phone


async def split_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks.
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Yields:
        List chunks
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def truncate_text(text: str, max_length: int = 1024) -> str:
    """
    Truncate text with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
