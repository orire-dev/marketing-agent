"""
Copy Generator - generates messaging options using Claude
"""

import json
import logging
import uuid
from typing import List, Dict, Any
from app.llm_client import LLMClient
from app.schemas import CreativeOption, CopyVariants, DesignSpec, AssetPrompt, ComplianceResult, OptionScores
from app.rag import Chunk

logger = logging.getLogger(__name__)


class CopyGenerator:
    """Generates marketing copy and creative directions"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def format_chunks_for_prompt(self, chunks: Dict[str, List[Chunk]]) -> str:
        """Format retrieved chunks for inclusion in prompt"""
        formatted = []
        
        for source_type, chunk_list in chunks.items():
            formatted.append(f"\n=== {source_type.upper()} SOURCES ===")
            for chunk in chunk_list:
                formatted.append(f"\n[chunk_id: {chunk.chunk_id}]")
                formatted.append(f"Source: {chunk.doc_name} - {chunk.section or 'N/A'}")
                formatted.append(f"Content: {chunk.text}")
        
        return "\n".join(formatted)
    
    def generate_options(
        self,
        request: Dict[str, Any],
        plan: Dict[str, Any],
        chunks: Dict[str, List[Chunk]],
        num_options: int = 3
    ) -> List[CreativeOption]:
        """
        Generate multiple creative options.
        
        Returns list of CreativeOption objects.
        """
        chunks_text = self.format_chunks_for_prompt(chunks)
        
        system_prompt = f"""You are an expert marketing copywriter and creative director for eToro, a social trading platform.

BRAND RULES (from retrieved sources):
{chunks_text}

CRITICAL CONSTRAINTS:
1. NEVER make financial promises, guarantees, or claims about returns
2. Always include required disclaimers (capital at risk, etc.)
3. Follow eToro brand voice: friendly, professional, empowering
4. Use clear, accessible language - avoid jargon
5. Respect style guidance: {request.get('style_guidance', 'standard')}

OUTPUT FORMAT:
You MUST return a JSON array of creative options. Each option must have this exact structure:
{{
  "option_id": "unique_id",
  "concept_name": "Concept Title",
  "rationale": "Why this direction works",
  "audience_fit_notes": "How this fits the target audience",
  "copy": {{
    "en": {{
      "primary_text": "Main ad copy text for the platform (follows platform length rules)",
      "headline": "Ad headline",
      "secondary_line": "Optional secondary line",
      "cta": "Call-to-action text",
      "headline_variants": ["headline 1", "headline 2"],
      "subhead_variants": ["subhead 1"],
      "body_variants": ["body text"],
      "cta_variants": ["CTA 1", "CTA 2"]
    }},
    "de": {{...}}
  }},
  "design_spec": {{
    "layout": "layout description",
    "typography_intent": "typography guidance",
    "imagery_direction": "visual direction",
    "brand_color_usage_notes": "color guidance",
    "animation_vibe": "motion direction if applicable"
  }},
  "compliance": {{
    "status": "pass|warning|fail",
    "flags": [],
    "required_disclaimers": [],
    "suggested_safe_edits": []
  }},
  "scores": {{
    "brand_fit": 0.0-1.0,
    "clarity": 0.0-1.0,
    "conversion_intent": 0.0-1.0,
    "compliance_safety": 0.0-1.0,
    "novelty": 0.0-1.0
  }}
}}

IMPORTANT: Return ONLY valid JSON. No markdown code blocks, no explanations, no text outside the JSON array.
Generate {num_options} DISTINCT creative directions with rich, detailed content. Each should have a different concept/angle."""

        user_prompt = f"""Generate creative options for:

Product: {request.get('product_scope')}
Channel: {request.get('channel')}
Asset Format: {request.get('asset')}
Languages: {request.get('languages')}
Style: {request.get('style_guidance', 'standard')}
Segment: {request.get('segment_id', 'general')}
Campaign Goal: {request.get('campaign_goal', 'awareness')}

Must Say: {request.get('must_say', [])}
Must Not Say: {request.get('must_not_say', [])}

Generate {num_options} options with distinct creative directions."""

        try:
            # Generate options JSON
            # Note: Claude-3-Haiku max is 4096 tokens, so we limit to that
            options_json = self.llm.generate_json(
                system_prompt,
                user_prompt,
                temperature=0.8,  # Higher for creativity
                max_tokens=4096  # Max for Haiku model
            )
            
            # Parse into CreativeOption objects
            options = []
            logger.info(f"Received response type: {type(options_json)}")
            
            if isinstance(options_json, list):
                options_data = options_json
                logger.info(f"Parsing {len(options_data)} options from array")
            elif isinstance(options_json, dict):
                if "options" in options_json:
                    options_data = options_json["options"]
                    logger.info(f"Parsing {len(options_data)} options from dict.options")
                elif "option" in options_json:
                    # Single option wrapped
                    options_data = [options_json["option"]]
                    logger.info("Parsing single option from dict.option")
                else:
                    # Try to treat the whole dict as a single option
                    options_data = [options_json]
                    logger.info("Treating dict as single option")
            else:
                logger.error(f"Unexpected response format: {type(options_json)}, value: {str(options_json)[:200]}")
                raise ValueError(f"Unexpected response format: {type(options_json)}")
            
            for opt_data in options_data:
                # Ensure option_id exists
                if "option_id" not in opt_data:
                    opt_data["option_id"] = str(uuid.uuid4())
                
                # Parse copy per language
                copy_dict = {}
                for lang, copy_vars in opt_data.get("copy", {}).items():
                    copy_dict[lang] = CopyVariants(**copy_vars)
                
                opt_data["copy_variants"] = copy_dict
                
                # Parse design spec
                opt_data["design_spec"] = DesignSpec(**opt_data.get("design_spec", {}))
                
                # Parse compliance
                opt_data["compliance"] = ComplianceResult(**opt_data.get("compliance", {
                    "status": "pass",
                    "flags": [],
                    "required_disclaimers": [],
                    "suggested_safe_edits": []
                }))
                
                # Parse scores
                opt_data["scores"] = OptionScores(**opt_data.get("scores", {
                    "brand_fit": 0.7,
                    "clarity": 0.7,
                    "conversion_intent": 0.7,
                    "compliance_safety": 0.9,
                    "novelty": 0.7
                }))
                
                # Create prompts (will be filled by prompt_builder)
                opt_data["prompts"] = {}
                
                options.append(CreativeOption(**opt_data))
            
            logger.info(f"Generated {len(options)} creative options")
            return options
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            # Return a fallback option
            return [self._create_fallback_option(request)]
    
    def _create_fallback_option(self, request: Dict[str, Any]) -> CreativeOption:
        """Create a fallback option if generation fails"""
        from app.schemas import CreativeOption, CopyVariants, DesignSpec, ComplianceResult, OptionScores
        import uuid
        
        return CreativeOption(
            option_id=str(uuid.uuid4()),
            concept_name="Default Creative Direction",
            rationale="Fallback option due to generation error",
            audience_fit_notes="General audience",
            copy_variants={
                lang: CopyVariants(
                    headline_variants=[f"Trade {request.get('product_scope', 'assets')} on eToro"],
                    cta_variants=["Start Trading"]
                )
                for lang in request.get('languages', ['en'])
            },
            design_spec=DesignSpec(
                layout="Centered layout with product imagery",
                typography_intent="Bold, modern sans-serif",
                imagery_direction="Clean, premium visuals",
                brand_color_usage_notes="Use primary brand colors",
                animation_vibe=None
            ),
            prompts={},
            compliance=ComplianceResult(
                status="warning",
                flags=["Generated from fallback"],
                required_disclaimers=["Capital at risk"],
                suggested_safe_edits=[]
            ),
            scores=OptionScores(
                brand_fit=0.5,
                clarity=0.6,
                conversion_intent=0.5,
                compliance_safety=0.8,
                novelty=0.3
            )
        )
