"""
OpenAI LLM client for content generation
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI
from openai import APIError
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class OpenAILLMClient:
    """OpenAI GPT-4 client with JSON parsing and retry logic"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = "gpt-4-turbo-preview"  # or "gpt-4" or "gpt-3.5-turbo"
    
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
        Generate JSON response from OpenAI with validation and retry.
        """
        model = model or self.default_model
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"} if response_schema else None
            )
            
            text_content = response.choices[0].message.content
            
            # Parse JSON
            try:
                json_str = text_content.strip()
                
                # Remove markdown code blocks if present
                if "```json" in json_str:
                    json_start = json_str.find("```json") + 7
                    json_end = json_str.find("```", json_start)
                    if json_end > json_start:
                        json_str = json_str[json_start:json_end].strip()
                elif "```" in json_str:
                    json_start = json_str.find("{")
                    if json_start == -1:
                        json_start = json_str.find("[")
                    if json_start >= 0:
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
                
                json_str = json_str.strip()
                parsed_json = json.loads(json_str)
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error, attempting repair: {e}")
                return self._repair_json(system_prompt, user_prompt, text_content, response_schema, model)
            
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
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_json: {e}")
            raise
    
    def _repair_json(
        self,
        system_prompt: str,
        user_prompt: str,
        invalid_json: str,
        response_schema: Optional[type[BaseModel]],
        model: str
    ) -> Dict[str, Any]:
        """Repair invalid JSON with a follow-up request"""
        repair_prompt = f"""{user_prompt}

The previous response had invalid JSON. Please return ONLY valid JSON, no markdown, no explanations:

{invalid_json}

Repair the JSON and return only the corrected JSON:"""
        
        repair_system = f"""{system_prompt}

CRITICAL: You must return ONLY valid JSON. No markdown code blocks, no explanations, no text outside the JSON. Just the raw JSON object."""
        
        response = self.client.chat.completions.create(
            model=model,
            max_tokens=4096,
            temperature=0.3,
            messages=[
                {"role": "system", "content": repair_system},
                {"role": "user", "content": repair_prompt}
            ],
            response_format={"type": "json_object"} if response_schema else None
        )
        
        text_content = response.choices[0].message.content
        json_str = text_content.strip()
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
        
        response = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content
