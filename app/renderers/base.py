"""
Base renderer interface for image and motion generation
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.schemas import AssetPrompt, MotionPrompt


class BaseRenderer(ABC):
    """Base class for image and motion renderers"""
    
    @abstractmethod
    def render_image(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        aspect_ratio: str,
        seed: Optional[int] = None
    ) -> str:
        """
        Render an image from a prompt.
        
        Returns:
            URI/path to generated image
        """
        pass
    
    @abstractmethod
    def render_motion(
        self,
        motion_prompt: MotionPrompt,
        asset_format: str
    ) -> str:
        """
        Render motion/GIF from storyboard.
        
        Returns:
            URI/path to generated motion asset
        """
        pass
