"""
OpenAI Compatible API Service
"""

import os
from typing import Dict, Any, Optional
import openai
import logging


class OpenAIService:
    def __init__(self):
        """
        Initialize the OpenAI service with environment variables.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        self.client = (
            openai.OpenAI(api_key=self.api_key, base_url=self.api_base)
            if self.api_key
            else None
        )
        self.logger = logging.getLogger(__name__)

    def _create_chat_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful AI assistant for IT operations.",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Create a chat completion using the OpenAI API.
        
        Args:
            prompt: The user prompt.
            system_message: The system message to set the behavior.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            
        Returns:
            The generated text response.
        """
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Can be configured via environment
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            raise