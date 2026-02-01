"""
Compliance & Risk Checker - validates creative against brand and regulatory rules
"""

import logging
from typing import List, Dict, Any
from app.llm_client import LLMClient
from app.schemas import ComplianceResult, CreativeOption

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Checks creative options for compliance issues"""
    
    # Hard-coded prohibited phrases
    PROHIBITED_PHRASES = [
        "guaranteed returns",
        "risk-free",
        "guaranteed profit",
        "no risk",
        "always win",
        "100% safe",
        "guaranteed income",
        "promised returns"
    ]
    
    # Required disclaimers by product type
    REQUIRED_DISCLAIMERS = {
        "crypto": "Crypto assets are highly volatile. Your capital is at risk.",
        "stocks": "Your capital is at risk. Past performance is not indicative of future results.",
        "CFDs": "CFDs are complex instruments. 68% of retail investor accounts lose money. Your capital is at risk.",
        "default": "Your capital is at risk."
    }
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def check_compliance(
        self,
        option: CreativeOption,
        product_scope: str,
        must_not_say: List[str] = None
    ) -> ComplianceResult:
        """
        Check creative option for compliance issues.
        
        Returns ComplianceResult with status and flags.
        """
        must_not_say = must_not_say or []
        all_prohibited = self.PROHIBITED_PHRASES + must_not_say
        
        # Collect all copy text
        all_text = []
        for lang, copy_vars in option.copy_variants.items():
            all_text.extend(copy_vars.headline_variants)
            all_text.extend(copy_vars.subhead_variants)
            all_text.extend(copy_vars.body_variants)
            all_text.extend(copy_vars.cta_variants)
        
        combined_text = " ".join(all_text).lower()
        
        # Check for prohibited phrases
        flags = []
        for phrase in all_prohibited:
            if phrase.lower() in combined_text:
                flags.append(f"Contains prohibited phrase: '{phrase}'")
        
        # Use LLM for deeper compliance check
        llm_result = self._llm_compliance_check(option, product_scope, combined_text)
        flags.extend(llm_result.get("flags", []))
        
        # Determine status
        if flags:
            status = "fail" if any("prohibited" in f.lower() or "guarantee" in f.lower() for f in flags) else "warning"
        else:
            status = "pass"
        
        # Get required disclaimers
        required_disclaimers = [self.REQUIRED_DISCLAIMERS.get(product_scope, self.REQUIRED_DISCLAIMERS["default"])]
        
        # Generate safe edits if needed
        suggested_edits = []
        if flags:
            suggested_edits = self._suggest_safe_edits(flags, combined_text)
        
        return ComplianceResult(
            status=status,
            flags=flags,
            required_disclaimers=required_disclaimers,
            suggested_safe_edits=suggested_edits
        )
    
    def _llm_compliance_check(
        self,
        option: CreativeOption,
        product_scope: str,
        text: str
    ) -> Dict[str, Any]:
        """Use LLM for nuanced compliance checking"""
        
        system_prompt = """You are a compliance officer for financial marketing. Check creative copy for regulatory violations.

Look for:
- Financial promises or guarantees
- Misleading claims
- Missing risk warnings
- Tone that suggests certainty
- Claims about returns or performance

Return JSON:
{
  "flags": ["list of issues found"],
  "severity": "high|medium|low",
  "notes": "compliance notes"
}"""

        user_prompt = f"""Check this creative copy for compliance issues:

Product: {product_scope}
Copy Text: {text}
Concept: {option.concept_name}

Identify any compliance issues. Return JSON only."""

        try:
            result = self.llm.generate_json(system_prompt, user_prompt, temperature=0.3)
            return result
        except Exception as e:
            logger.error(f"LLM compliance check failed: {e}")
            return {"flags": [], "severity": "low", "notes": "Could not perform LLM check"}
    
    def _suggest_safe_edits(self, flags: List[str], text: str) -> List[str]:
        """Suggest safe alternative edits"""
        suggestions = []
        
        for flag in flags:
            if "guaranteed" in flag.lower():
                suggestions.append("Replace 'guaranteed' with 'potential' or remove claim")
            elif "risk-free" in flag.lower():
                suggestions.append("Remove 'risk-free' - all investments carry risk")
            elif "promise" in flag.lower():
                suggestions.append("Remove promises - focus on features and education")
        
        return suggestions
