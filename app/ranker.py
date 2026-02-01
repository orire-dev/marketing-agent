"""
Ranker - scores and ranks creative options
"""

import logging
from typing import List
from app.schemas import CreativeOption, OptionScores
from app.rag import Chunk

logger = logging.getLogger(__name__)


class Ranker:
    """Ranks creative options by multiple criteria"""
    
    def rank_options(
        self,
        options: List[CreativeOption],
        chunks: dict,
        product_scope: str
    ) -> List[CreativeOption]:
        """
        Score and rank options.
        
        Returns options sorted by composite score (highest first).
        """
        # Score each option
        for option in options:
            scores = self._calculate_scores(option, chunks, product_scope, options)
            option.scores = scores
        
        # Sort by composite score
        def composite_score(opt: CreativeOption) -> float:
            s = opt.scores
            # Weighted composite
            return (
                s.brand_fit * 0.25 +
                s.clarity * 0.20 +
                s.conversion_intent * 0.25 +
                s.compliance_safety * 0.20 +  # High weight for compliance
                s.novelty * 0.10
            )
        
        ranked = sorted(options, key=composite_score, reverse=True)
        
        logger.info(f"Ranked {len(ranked)} options")
        return ranked
    
    def _calculate_scores(
        self,
        option: CreativeOption,
        chunks: dict,
        product_scope: str,
        all_options: List[CreativeOption]
    ) -> OptionScores:
        """Calculate scores for an option"""
        
        # Brand fit: check alignment with brand chunks
        brand_fit = self._score_brand_fit(option, chunks.get("brand", []))
        
        # Clarity: check copy clarity
        clarity = self._score_clarity(option)
        
        # Conversion intent: check CTA strength and messaging
        conversion_intent = self._score_conversion_intent(option)
        
        # Compliance safety: inverse of compliance issues
        compliance_safety = 1.0 if option.compliance.status == "pass" else (
            0.7 if option.compliance.status == "warning" else 0.3
        )
        
        # Novelty: distance from other options
        novelty = self._score_novelty(option, all_options)
        
        return OptionScores(
            brand_fit=brand_fit,
            clarity=clarity,
            conversion_intent=conversion_intent,
            compliance_safety=compliance_safety,
            novelty=novelty
        )
    
    def _score_brand_fit(self, option: CreativeOption, brand_chunks: List[Chunk]) -> float:
        """Score how well option fits brand"""
        if not brand_chunks:
            return 0.7  # Default
        
        # Simple heuristic: check if design spec mentions brand elements
        design_text = f"{option.design_spec.layout} {option.design_spec.brand_color_usage_notes}".lower()
        
        brand_keywords = ["etoro", "brand", "color", "typography", "style"]
        matches = sum(1 for kw in brand_keywords if kw in design_text)
        
        return min(0.5 + (matches * 0.1), 1.0)
    
    def _score_clarity(self, option: CreativeOption) -> float:
        """Score message clarity"""
        # Check if copy is clear and concise
        all_copy = []
        for copy_vars in option.copy_variants.values():
            all_copy.extend(copy_vars.headline_variants)
            all_copy.extend(copy_vars.body_variants)
        
        # Simple heuristic: shorter, clearer copy scores higher
        avg_length = sum(len(c) for c in all_copy) / max(len(all_copy), 1)
        
        # Ideal length: 50-150 chars
        if 50 <= avg_length <= 150:
            return 0.9
        elif 30 <= avg_length <= 200:
            return 0.7
        else:
            return 0.5
    
    def _score_conversion_intent(self, option: CreativeOption) -> float:
        """Score conversion potential"""
        # Check CTA strength
        cta_keywords = ["start", "trade", "join", "invest", "get started", "sign up"]
        
        all_ctas = []
        for copy_vars in option.copy_variants.values():
            all_ctas.extend(copy_vars.cta_variants)
        
        cta_text = " ".join(all_ctas).lower()
        matches = sum(1 for kw in cta_keywords if kw in cta_text)
        
        return min(0.6 + (matches * 0.15), 1.0)
    
    def _score_novelty(self, option: CreativeOption, all_options: List[CreativeOption]) -> float:
        """Score how novel/distinct this option is"""
        if len(all_options) <= 1:
            return 0.8  # Only option
        
        # Compare concept names and rationales
        other_concepts = [opt.concept_name.lower() for opt in all_options if opt.option_id != option.option_id]
        this_concept = option.concept_name.lower()
        
        # Check uniqueness
        similarity = sum(1 for other in other_concepts if this_concept[:10] in other or other[:10] in this_concept)
        
        # More unique = higher novelty
        return max(0.3, 1.0 - (similarity * 0.2))
