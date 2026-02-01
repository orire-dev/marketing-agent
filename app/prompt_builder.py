"""
Creative Prompt Builder - generates image and motion prompts
"""

import logging
from typing import Dict, Any, List
from app.llm_client import LLMClient
from app.schemas import AssetPrompt, MotionPrompt, StoryboardFrame, CreativeOption, AssetFormat

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds image and motion generation prompts"""
    
    # Asset format to aspect ratio mapping
    ASPECT_RATIOS = {
        AssetFormat.SOCIAL_1X1: "1:1",
        AssetFormat.SOCIAL_4X5: "4:5",
        AssetFormat.STORY_9X16: "9:16",
        AssetFormat.BANNER_16X9: "16:9"
    }
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def build_prompts(
        self,
        option: CreativeOption,
        asset_format: AssetFormat,
        languages: List[str],
        style_guidance: str
    ) -> Dict[str, Dict[str, AssetPrompt]]:
        """
        Build image and motion prompts for an option across languages.
        
        Returns: {language: AssetPrompt}
        """
        prompts_per_lang = {}
        
        for lang in languages:
            # Get copy for this language
            copy_vars = option.copy_variants.get(lang)
            if not copy_vars:
                continue
            
            # Build image prompt
            image_prompt = self._build_image_prompt(
                option,
                copy_vars,
                asset_format,
                style_guidance,
                lang
            )
            
            # Build motion prompt if applicable
            motion_prompt = None
            if asset_format in [AssetFormat.STORY_9X16, AssetFormat.SOCIAL_4X5]:
                motion_prompt = self._build_motion_prompt(
                    option,
                    copy_vars,
                    asset_format,
                    lang
                )
            
            prompts_per_lang[lang] = AssetPrompt(
                image_prompt=image_prompt,
                negative_prompt=self._build_negative_prompt(),
                seed=None,  # Will be set by caller
                aspect_ratio=self.ASPECT_RATIOS.get(asset_format, "1:1"),
                motion_prompt=motion_prompt
            )
        
        return {asset_format.value: prompts_per_lang}
    
    def _build_image_prompt(
        self,
        option: CreativeOption,
        copy_vars: Any,
        asset_format: AssetFormat,
        style_guidance: str,
        language: str
    ) -> str:
        """Build image generation prompt"""
        
        # Use LLM to generate detailed image prompt
        system_prompt = """You are an expert at creating detailed image generation prompts for marketing creatives.

Given the creative concept, copy, design spec, and style guidance, create a detailed, model-agnostic image prompt.

The prompt should be:
- Specific about composition, lighting, colors
- Include brand elements (e.g., "eToro blue accent")
- Match the design spec and style guidance
- Suitable for the asset format
- Professional marketing quality

Return ONLY the prompt text, no explanations."""

        user_prompt = f"""Create an image generation prompt for:

Concept: {option.concept_name}
Headline: {copy_vars.headline_variants[0] if copy_vars.headline_variants else 'N/A'}
Design Spec: {option.design_spec.imagery_direction}
Typography Intent: {option.design_spec.typography_intent}
Brand Colors: {option.design_spec.brand_color_usage_notes}
Style Guidance: {style_guidance}
Asset Format: {asset_format.value}
Language: {language}

Create a detailed, professional image prompt."""

        try:
            prompt = self.llm.generate_text(
                system_prompt,
                user_prompt,
                temperature=0.7,
                max_tokens=500
            )
            return prompt.strip()
        except Exception as e:
            logger.error(f"Image prompt generation failed: {e}")
            # Fallback prompt
            return f"Professional marketing image for {option.concept_name}, {style_guidance}, {option.design_spec.imagery_direction}, eToro brand colors, {asset_format.value} format"
    
    def _build_motion_prompt(
        self,
        option: CreativeOption,
        copy_vars: Any,
        asset_format: AssetFormat,
        language: str
    ) -> MotionPrompt:
        """Build motion/GIF storyboard prompt"""
        
        system_prompt = """You are an expert at creating motion graphics storyboards for marketing.

Create a storyboard with 3-5 frames that tell the story of the creative concept.
Each frame should have timing, visual description, on-screen text, and transition.

Return JSON:
{
  "duration_s": 3.0,
  "fps": 24,
  "storyboard_frames": [
    {{
      "t": 0.0,
      "visual": "description",
      "on_screen_text": "text or null",
      "transition": "fade_in or cut or slide"
    }}
  ]
}"""

        user_prompt = f"""Create a motion storyboard for:

Concept: {option.concept_name}
Headline: {copy_vars.headline_variants[0] if copy_vars.headline_variants else 'N/A'}
CTA: {copy_vars.cta_variants[0] if copy_vars.cta_variants else 'N/A'}
Design: {option.design_spec.animation_vibe or 'smooth, professional'}
Asset: {asset_format.value}

Create 3-5 frames with smooth transitions."""

        try:
            motion_data = self.llm.generate_json(
                system_prompt,
                user_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            frames = [
                StoryboardFrame(**frame) for frame in motion_data.get("storyboard_frames", [])
            ]
            
            return MotionPrompt(
                duration_s=motion_data.get("duration_s", 3.0),
                fps=motion_data.get("fps", 24),
                storyboard_frames=frames
            )
        except Exception as e:
            logger.error(f"Motion prompt generation failed: {e}")
            # Fallback
            return MotionPrompt(
                duration_s=3.0,
                fps=24,
                storyboard_frames=[
                    StoryboardFrame(t=0.0, visual="Opening frame", on_screen_text=copy_vars.headline_variants[0] if copy_vars.headline_variants else None, transition="fade_in"),
                    StoryboardFrame(t=1.5, visual="Main visual", on_screen_text=None, transition="cut"),
                    StoryboardFrame(t=2.5, visual="CTA frame", on_screen_text=copy_vars.cta_variants[0] if copy_vars.cta_variants else None, transition="fade_out")
                ]
            )
    
    def _build_negative_prompt(self) -> str:
        """Build negative prompt (what to avoid)"""
        return "blurry, low quality, text errors, financial promises, guarantees, misleading imagery, cluttered, unprofessional"
