"""
OpenAI DALL-E renderer for image generation
"""

import logging
import os
import base64
import requests
from typing import Optional
from app.renderers.base import BaseRenderer
from app.schemas import MotionPrompt

logger = logging.getLogger(__name__)


class OpenAIRenderer(BaseRenderer):
    """DALL-E image renderer"""
    
    def __init__(self, api_key: Optional[str] = None, storage_base_path: str = "/tmp/marketing_agent/creatives"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.storage_base_path = storage_base_path
        self.base_url = "https://api.openai.com/v1/images/generations"
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Image generation will be disabled.")
    
    def render_image(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        aspect_ratio: str,
        seed: Optional[int] = None
    ) -> str:
        """Generate image using DALL-E"""
        
        if not self.api_key:
            logger.warning("No OpenAI API key. Returning placeholder.")
            return self._placeholder_uri(prompt)
        
        try:
            # Map aspect ratio to DALL-E size
            # DALL-E 3 supports: 1024x1024, 1792x1024, 1024x1792
            # For 1:1, use 1024x1024
            size_map = {
                "1:1": "1024x1024",
                "4:5": "1024x1280",  # Approximate
                "9:16": "1024x1792",
                "16:9": "1792x1024"
            }
            size = size_map.get(aspect_ratio, "1024x1024")
            
            # Build prompt with negative prompt
            full_prompt = prompt
            if negative_prompt:
                full_prompt = f"{prompt}. Avoid: {negative_prompt}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # DALL-E 3 doesn't support seed parameter
            payload = {
                "model": "dall-e-3",
                "prompt": full_prompt[:4000],  # DALL-E 3 has 4000 char limit
                "size": size,
                "quality": "standard",
                "n": 1
            }
            
            # Note: DALL-E 3 doesn't support seed parameter
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                error_type = error_data.get("error", {}).get("type", "unknown")
                error_code = error_data.get("error", {}).get("code", "")
                
                # Provide user-friendly error messages
                if "billing" in error_msg.lower() or "limit" in error_msg.lower():
                    logger.error(f"OpenAI billing limit reached: {error_msg}")
                    raise ValueError(f"OpenAI billing limit reached. Please check your OpenAI account billing at https://platform.openai.com/account/billing. Error: {error_msg}")
                elif "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    logger.error(f"OpenAI API authentication error: {error_msg}")
                    raise ValueError(f"OpenAI API authentication failed. Please check your API key. Error: {error_msg}")
                else:
                    logger.error(f"OpenAI API error ({response.status_code}): {error_msg}")
                    raise ValueError(f"OpenAI API error: {error_msg} (Code: {error_code}, Type: {error_type})")
            
            response.raise_for_status()
            data = response.json()
            image_url = data["data"][0]["url"]
            
            logger.info(f"Generated image: {image_url}")
            return image_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during image generation: {e}")
            raise ValueError(f"Network error connecting to OpenAI API: {str(e)}")
        except ValueError as e:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Image generation failed: {e}", exc_info=True)
            raise ValueError(f"Image generation failed: {str(e)}")
    
    def render_motion(
        self,
        motion_prompt: MotionPrompt,
        asset_format: str
    ) -> str:
        """Render motion/GIF - placeholder for now"""
        logger.warning("Motion rendering not yet implemented. Returning placeholder.")
        return self._placeholder_uri(f"Motion: {motion_prompt.storyboard_frames[0].visual}")
    
    def _placeholder_uri(self, prompt: str) -> str:
        """Return placeholder URI when generation fails"""
        import uuid
        filename = f"placeholder_{uuid.uuid4().hex[:8]}.png"
        return f"{self.storage_base_path}/{filename}"
