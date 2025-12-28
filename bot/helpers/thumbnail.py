"""
Thumbnail generation utilities.
"""

import os
import logging
import asyncio
from typing import Optional

import cv2
from PIL import Image

from config import Config

logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """
    Generate thumbnails for videos and images.
    """
    
    MAX_SIZE = (320, 320)
    
    @staticmethod
    async def generate_video_thumbnail(
        video_path: str,
        output_path: Optional[str] = None,
        time_offset: float = 1.0
    ) -> Optional[str]:
        """
        Generate thumbnail from video file.
        
        Args:
            video_path: Path to video file
            output_path: Optional custom output path
            time_offset: Time in seconds to capture frame
            
        Returns:
            Path to thumbnail or None if failed
        """
        if not output_path:
            output_path = os.path.join(
                Config.THUMB_PATH,
                f"thumb_{os.path.basename(video_path)}.jpg"
            )
        
        try:
            # Run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                ThumbnailGenerator._extract_frame,
                video_path,
                output_path,
                time_offset
            )
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None
    
    @staticmethod
    def _extract_frame(
        video_path: str,
        output_path: str,
        time_offset: float
    ) -> Optional[str]:
        """Extract frame from video (synchronous)."""
        cap = None
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return None
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            frame_number = int(fps * time_offset)
            
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = cap.read()
            
            if not ret:
                # Try first frame if offset fails
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                
                if not ret:
                    logger.error("Could not read any frame from video")
                    return None
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create PIL Image
            img = Image.fromarray(frame_rgb)
            
            # Resize maintaining aspect ratio
            img.thumbnail(ThumbnailGenerator.MAX_SIZE, Image.Resampling.LANCZOS)
            
            # Save as JPEG
            img.save(output_path, "JPEG", quality=85)
            
            logger.debug(f"Thumbnail generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            return None
        finally:
            if cap:
                cap.release()
    
    @staticmethod
    async def resize_image(
        image_path: str,
        output_path: Optional[str] = None,
        max_size: tuple = (320, 320)
    ) -> Optional[str]:
        """
        Resize image to thumbnail size.
        
        Args:
            image_path: Path to image
            output_path: Optional output path
            max_size: Maximum dimensions
            
        Returns:
            Path to resized image or None
        """
        if not output_path:
            output_path = os.path.join(
                Config.THUMB_PATH,
                f"thumb_{os.path.basename(image_path)}"
            )
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                ThumbnailGenerator._resize_image_sync,
                image_path,
                output_path,
                max_size
            )
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return None
    
    @staticmethod
    def _resize_image_sync(
        image_path: str,
        output_path: str,
        max_size: tuple
    ) -> Optional[str]:
        """Resize image (synchronous)."""
        try:
            with Image.open(image_path) as img:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(output_path, "JPEG", quality=85)
                return output_path
        except Exception as e:
            logger.error(f"Image resize error: {e}")
            return None
