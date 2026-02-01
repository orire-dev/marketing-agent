"""
Pydantic schemas for Marketing Agent API
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Channel(str, Enum):
    SOCIAL = "social"
    EMAIL = "email"
    DISPLAY = "display"
    VIDEO = "video"
    X_TWITTER = "x_twitter"  # X (Twitter)
    FACEBOOK = "facebook"


class AssetFormat(str, Enum):
    SOCIAL_1X1 = "social_1x1"
    SOCIAL_4X5 = "social_4x5"
    STORY_9X16 = "story_9x16"
    BANNER_16X9 = "banner_16x9"
    STATIC_IMAGE = "static_image"  # 1:1 static
    MOTION_AD = "motion_ad"  # 1:1 motion graphic
    SHORT_VIDEO = "short_video"  # 1:1 short video (5-15s)


class Language(str, Enum):
    EN = "en"
    DE = "de"
    ES = "es"
    FR = "fr"
    IT = "it"
    AR = "ar"
    HE = "he"


# Request Schemas
class GenerateRequest(BaseModel):
    """Request to generate marketing creative options"""
    
    product_scope: str = Field(..., description="Product/instrument scope (e.g., 'crypto', 'stocks', 'ETFs')")
    channel: Channel = Field(..., description="Marketing channel")
    asset: AssetFormat = Field(..., description="Asset format/size")
    languages: List[Language] = Field(..., min_length=1, description="Target languages")
    segment_id: Optional[str] = Field(None, description="Target segment ID")
    
    # Optional constraints
    style_guidance: Optional[str] = Field(None, description="Style guidance (e.g., 'clean, premium, bold typography')")
    campaign_goal: Optional[str] = Field(None, description="Campaign objective")
    must_say: Optional[List[str]] = Field(None, description="Required messaging elements")
    must_not_say: Optional[List[str]] = Field(None, description="Prohibited phrases/claims")
    tone: Optional[str] = Field(None, description="Tone override (e.g., 'friendly', 'professional')")
    
    # Generation parameters
    num_options: int = Field(3, ge=1, le=6, description="Number of creative options to generate")
    seed: Optional[int] = Field(None, description="Seed for deterministic generation")
    
    # API keys (optional, can use env vars as fallback)
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key for image generation (optional, can use env var)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_scope": "crypto",
                "channel": "social",
                "asset": "social_1x1",
                "languages": ["en", "de"],
                "style_guidance": "clean, premium, minimal copy, bold typography",
                "num_options": 3
            }
        }


# Response Schemas
class CopyVariants(BaseModel):
    """Copy variants for a language - platform-specific format"""
    # New format (primary for social ads)
    primary_text: Optional[str] = Field(None, description="Main ad copy text (platform-specific length)")
    headline: Optional[str] = Field(None, description="Ad headline")
    secondary_line: Optional[str] = Field(None, description="Optional secondary headline/subhead")
    cta: Optional[str] = Field(None, description="Call-to-action text")
    
    # Legacy format (for backward compatibility)
    headline_variants: List[str] = Field(default_factory=list)
    subhead_variants: List[str] = Field(default_factory=list)
    body_variants: List[str] = Field(default_factory=list)
    cta_variants: List[str] = Field(default_factory=list)
    
    def __init__(self, **data):
        # Auto-populate new format from legacy if needed
        if "primary_text" not in data and "body_variants" in data and data["body_variants"]:
            data["primary_text"] = data["body_variants"][0]
        if "headline" not in data and "headline_variants" in data and data["headline_variants"]:
            data["headline"] = data["headline_variants"][0]
        if "secondary_line" not in data and "subhead_variants" in data and data["subhead_variants"]:
            data["secondary_line"] = data["subhead_variants"][0]
        if "cta" not in data and "cta_variants" in data and data["cta_variants"]:
            data["cta"] = data["cta_variants"][0]
        super().__init__(**data)


class DesignSpec(BaseModel):
    """Design specification for creative"""
    layout: str = Field(..., description="Layout description")
    typography_intent: str = Field(..., description="Typography guidance")
    imagery_direction: str = Field(..., description="Image direction/visual style")
    brand_color_usage_notes: str = Field(..., description="Color palette guidance")
    animation_vibe: Optional[str] = Field(None, description="Animation/motion direction")


class StoryboardFrame(BaseModel):
    """Single frame in motion storyboard"""
    t: float = Field(..., description="Time in seconds")
    visual: str = Field(..., description="Visual description")
    on_screen_text: Optional[str] = Field(None, description="Text overlay")
    transition: Optional[str] = Field(None, description="Transition to next frame")


class MotionPrompt(BaseModel):
    """Motion/GIF generation prompt"""
    duration_s: float = Field(..., description="Duration in seconds")
    fps: int = Field(24, description="Frames per second")
    storyboard_frames: List[StoryboardFrame] = Field(..., min_length=2)


class AssetPrompt(BaseModel):
    """Image and motion prompts for an asset"""
    image_prompt: str = Field(..., description="Image generation prompt")
    negative_prompt: Optional[str] = Field(None, description="What to avoid in image")
    seed: Optional[int] = Field(None, description="Seed for reproducibility")
    aspect_ratio: str = Field(..., description="Aspect ratio (e.g., '1:1', '4:5')")
    motion_prompt: Optional[MotionPrompt] = Field(None, description="Motion/GIF prompt")
    generated_image_uri: Optional[str] = Field(None, description="URI to generated image/video")
    generation_status: Optional[str] = Field(None, description="Status: 'pending', 'completed', 'failed'")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")


class ComplianceResult(BaseModel):
    """Compliance check results"""
    status: Literal["pass", "warning", "fail"] = Field(..., description="Compliance status")
    flags: List[str] = Field(default_factory=list, description="Compliance issues found")
    required_disclaimers: List[str] = Field(default_factory=list, description="Required disclaimers")
    suggested_safe_edits: List[str] = Field(default_factory=list, description="Suggested edits for compliance")


class OptionScores(BaseModel):
    """Scoring for a creative option"""
    brand_fit: float = Field(..., ge=0.0, le=1.0, description="Alignment with brand (0-1)")
    clarity: float = Field(..., ge=0.0, le=1.0, description="Message clarity (0-1)")
    conversion_intent: float = Field(..., ge=0.0, le=1.0, description="Conversion potential (0-1)")
    compliance_safety: float = Field(..., ge=0.0, le=1.0, description="Compliance safety (0-1)")
    novelty: float = Field(..., ge=0.0, le=1.0, description="Novelty vs other options (0-1)")


class CreativeOption(BaseModel):
    """A single creative direction option"""
    option_id: str = Field(..., description="Unique option identifier")
    concept_name: str = Field(..., description="Concept name/title")
    rationale: str = Field(..., description="Why this direction")
    audience_fit_notes: str = Field(..., description="How this fits the target audience")
    
    copy_variants: Dict[str, CopyVariants] = Field(..., alias="copy", description="Copy per language (key=language code)")
    
    class Config:
        populate_by_name = True  # Allow both "copy" and "copy_variants"
    design_spec: DesignSpec = Field(..., description="Design specification")
    
    prompts: Dict[str, Dict[str, AssetPrompt]] = Field(
        ...,
        description="Prompts per asset per language: {asset: {language: AssetPrompt}}"
    )
    
    compliance: ComplianceResult = Field(..., description="Compliance check results")
    scores: OptionScores = Field(..., description="Scoring metrics")


class RetrievedSource(BaseModel):
    """Source document chunk used in generation"""
    doc: str = Field(..., description="Document name")
    section: Optional[str] = Field(None, description="Section name")
    page: Optional[int] = Field(None, description="Page number")
    chunk_id: str = Field(..., description="Chunk identifier")


class RequestMeta(BaseModel):
    """Metadata about the generation request"""
    channel: str
    format: str
    sizes: List[str]
    languages: List[str]
    segment_id: Optional[str]
    product_scope: str
    campaign_goal: Optional[str]
    date: datetime = Field(default_factory=datetime.utcnow)


class Constraints(BaseModel):
    """Constraints applied to generation"""
    tone: Optional[str]
    style: Optional[str]
    must_say: Optional[List[str]]
    must_not_say: Optional[List[str]]
    disclaimers: Optional[List[str]]


class GenerateResponse(BaseModel):
    """Complete generation response"""
    request_meta: RequestMeta
    constraints: Constraints
    options: List[CreativeOption] = Field(..., min_length=1, max_length=6)
    global_disclaimers: Dict[str, str] = Field(..., description="Disclaimers per language")
    audit: Dict[str, Any] = Field(
        ...,
        description="Audit trail: retrieved_sources, model_versions, timestamps"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_meta": {
                    "channel": "social",
                    "format": "social_1x1",
                    "sizes": ["1080x1080"],
                    "languages": ["en", "de"],
                    "product_scope": "crypto",
                    "date": "2024-01-31T12:00:00Z"
                },
                "options": []
            }
        }
