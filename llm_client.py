"""
LLM Client for Groq API integration.

Provides a wrapper for Groq API calls with error handling and retry logic.
"""
import os
import time
from typing import Optional, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """
    Client for interacting with Groq API.
    
    Handles API calls with retry logic and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize the LLM client.
        
        Args:
            api_key: Groq API key. If None, loads from environment variable.
            model: Model to use for API calls. Default is llama-3.3-70b-versatile.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    def call_api(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Call the Groq API with retry logic.
        
        Args:
            prompt: The user prompt to send.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens in response.
            system_prompt: Optional system prompt.
        
        Returns:
            str: The API response text.
        
        Raises:
            Exception: If all retries are exhausted.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"API call failed after {self.max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** attempt)
                print(f"API call failed (attempt {attempt + 1}/{self.max_retries}), retrying in {delay}s...")
                time.sleep(delay)
    
    def test_connection(self) -> bool:
        """
        Test API connectivity with a simple call.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            response = self.call_api("Say 'Connection successful' in one word.")
            print(f"API connection test successful. Response: {response}")
            return True
        except Exception as e:
            print(f"API connection test failed: {str(e)}")
            return False


def get_llm_client() -> LLMClient:
    """
    Get a configured LLM client instance.
    
    Returns:
        LLMClient: Configured client instance.
    """
    return LLMClient()


if __name__ == "__main__":
    # Test the client
    client = get_llm_client()
    client.test_connection()
