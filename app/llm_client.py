"""
Claude LLM client with JSON validation and retry logic
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import Anthropic, APIError
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class LLMClient:
    """Claude API client with JSON parsing and retry logic"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        # Use a known working Claude model
        # Available models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
        # Try haiku first (fastest, cheapest), fallback to sonnet if needed
        self.default_model = "claude-3-haiku-20240307"  # Fast and reliable model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, json.JSONDecodeError, ValidationError))
    )
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Optional[type[BaseModel]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Generate JSON response from Claude with validation and retry.
        
        Args:
            system_prompt: System prompt for Claude
            user_prompt: User prompt
            response_schema: Optional Pydantic model to validate against
            model: Model name (defaults to claude-3-5-sonnet-20241022)
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            
        Returns:
            Parsed JSON as dict
            
        Raises:
            ValueError: If JSON parsing fails after retries
            ValidationError: If Pydantic validation fails
        """
        model = model or self.default_model
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            # Extract text content
            text_content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    text_content += block.text
            
            # Parse JSON with improved extraction
            try:
                json_str = text_content.strip()
                
                # Remove markdown code blocks if present
                if "```json" in json_str:
                    json_start = json_str.find("```json") + 7
                    json_end = json_str.find("```", json_start)
                    if json_end > json_start:
                        json_str = json_str[json_start:json_end].strip()
                elif "```" in json_str:
                    # Try to find JSON array or object
                    json_start = json_str.find("[")
                    if json_start == -1:
                        json_start = json_str.find("{")
                    if json_start >= 0:
                        # Find matching closing bracket
                        if json_str[json_start] == "[":
                            bracket_count = 0
                            for i in range(json_start, len(json_str)):
                                if json_str[i] == "[":
                                    bracket_count += 1
                                elif json_str[i] == "]":
                                    bracket_count -= 1
                                    if bracket_count == 0:
                                        json_str = json_str[json_start:i+1]
                                        break
                        else:
                            brace_count = 0
                            for i in range(json_start, len(json_str)):
                                if json_str[i] == "{":
                                    brace_count += 1
                                elif json_str[i] == "}":
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_str = json_str[json_start:i+1]
                                        break
                    else:
                        # Fallback: remove markdown
                        json_start = json_str.find("```") + 3
                        json_end = json_str.find("```", json_start)
                        if json_end > json_start:
                            json_str = json_str[json_start:json_end].strip()
                
                # Clean up any leading/trailing whitespace or newlines
                json_str = json_str.strip()
                
                # Try parsing
                parsed_json = json.loads(json_str)
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error, attempting repair: {e}")
                # Retry with repair prompt
                repair_prompt = f"""The previous response had invalid JSON. Please return ONLY valid JSON, no markdown, no explanations:

{text_content}

Repair the JSON and return only the corrected JSON:"""
                
                return self._repair_json(system_prompt, repair_prompt, response_schema, model)
            
            # Validate against schema if provided
            if response_schema:
                try:
                    validated = response_schema(**parsed_json)
                    return validated.model_dump()
                except ValidationError as e:
                    logger.error(f"Schema validation failed: {e}")
                    raise
            
            return parsed_json
            
        except APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_json: {e}")
            raise
    
    def _repair_json(
        self,
        system_prompt: str,
        repair_prompt: str,
        response_schema: Optional[type[BaseModel]],
        model: str
    ) -> Dict[str, Any]:
        """Repair invalid JSON with a follow-up request"""
        repair_system = f"""{system_prompt}

CRITICAL: You must return ONLY valid JSON. No markdown code blocks, no explanations, no text outside the JSON. Just the raw JSON object."""
        
        response = self.client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.3,  # Lower temperature for repair
            system=repair_system,
            messages=[{
                "role": "user",
                "content": repair_prompt
            }]
        )
        
        text_content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text_content += block.text
        
        # Clean and parse
        json_str = text_content.strip()
        # Remove any markdown
        json_str = json_str.replace("```json", "").replace("```", "").strip()
        
        parsed_json = json.loads(json_str)
        
        if response_schema:
            validated = response_schema(**parsed_json)
            return validated.model_dump()
        
        return parsed_json
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """Generate plain text response (no JSON parsing)"""
        model = model or self.default_model
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )
        
        text_content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text_content += block.text
        
        return text_content
