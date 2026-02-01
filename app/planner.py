"""
Planner agent - interprets request and creates generation plan
"""

import json
import logging
from typing import Dict, Any
from app.llm_client import LLMClient
from app.rag import RAGRetriever

logger = logging.getLogger(__name__)


class Planner:
    """Plans the generation approach based on request"""
    
    def __init__(self, llm_client: LLMClient, retriever: RAGRetriever):
        self.llm = llm_client
        self.retriever = retriever
    
    def create_plan(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a generation plan.
        
        Returns plan JSON with:
        - needed_retrievals: what to retrieve
        - generation_strategy: how to generate options
        - compliance_checks: what to check
        """
        system_prompt = """You are a marketing strategy planner. Analyze the creative brief and create a structured plan for generating marketing creative options.

Output a JSON object with:
{
  "needed_retrievals": {
    "brand": ["list of specific topics to retrieve"],
    "product": ["product features to focus on"],
    "segment": ["persona attributes to consider"]
  },
  "generation_strategy": {
    "num_options": 3,
    "distinct_directions": ["brief description of each direction"],
    "tone_approach": "description of tone to use",
    "style_constraints": ["key style constraints"]
  },
  "compliance_checks": {
    "required_disclaimers": ["list"],
    "prohibited_claims": ["list"],
    "regulatory_notes": "notes"
  }
}"""

        user_prompt = f"""Create a generation plan for this creative brief:

Product: {request.get('product_scope')}
Channel: {request.get('channel')}
Asset: {request.get('asset')}
Languages: {request.get('languages')}
Style: {request.get('style_guidance', 'Not specified')}
Segment: {request.get('segment_id', 'Not specified')}
Campaign Goal: {request.get('campaign_goal', 'Not specified')}

Return ONLY valid JSON."""

        try:
            plan = self.llm.generate_json(system_prompt, user_prompt)
            logger.info(f"Generated plan: {json.dumps(plan, indent=2)}")
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            # Return default plan
            return {
                "needed_retrievals": {
                    "brand": ["visual_identity", "tone_of_voice"],
                    "product": [request.get('product_scope', 'general')],
                    "segment": ["default"]
                },
                "generation_strategy": {
                    "num_options": request.get('num_options', 3),
                    "distinct_directions": ["Educational", "Benefit-focused", "Social proof"],
                    "tone_approach": "Friendly, professional, empowering",
                    "style_constraints": request.get('style_guidance', '').split(', ') if request.get('style_guidance') else []
                },
                "compliance_checks": {
                    "required_disclaimers": ["Capital at risk"],
                    "prohibited_claims": ["Guaranteed returns", "Risk-free"],
                    "regulatory_notes": "Ensure all financial disclaimers are included"
                }
            }
