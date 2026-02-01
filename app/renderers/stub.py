"""
Stub renderer - returns placeholder URIs without actual generation
"""

import logging
from typing import Optional
from app.renderers.base import BaseRenderer
from app.schemas import MotionPrompt

logger = logging.getLogger(__name__)


class StubRenderer(BaseRenderer):
    """Stub renderer that doesn't actually generate images"""
    
    def __init__(self, storage_base_path: str = "/dbfs/mnt/marketing_agent/creatives"):
        self.storage_base_path = storage_base_path
    
    def render_image(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        aspect_ratio: str,
        seed: Optional[int] = None
    ) -> str:
        """Return placeholder URI"""
        logger.info(f"Stub renderer: Would generate image with prompt: {prompt[:100]}...")
        
        # Generate a placeholder path
        import uuid
        filename = f"image_{uuid.uuid4().hex[:8]}.png"
        uri = f"{self.storage_base_path}/{filename}"
        
        logger.info(f"Stub renderer: Returning placeholder URI: {uri}")
        return uri
    
    def render_motion(
        self,
        motion_prompt: MotionPrompt,
        asset_format: str
    ) -> str:
        """Return placeholder URI"""
        logger.info(f"Stub renderer: Would generate motion with {len(motion_prompt.storyboard_frames)} frames")
        
        import uuid
        filename = f"motion_{uuid.uuid4().hex[:8]}.gif"
        uri = f"{self.storage_base_path}/{filename}"
        
        logger.info(f"Stub renderer: Returning placeholder URI: {uri}")
        return uri
