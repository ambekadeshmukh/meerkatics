import os
import time
import logging
from typing import Dict, Any, List, Optional, Union
import json

from .base import BaseProviderMonitor
from ..utils.tokenizers import TokenCounter

logger = logging.getLogger("meerkatics.providers.openai")

class OpenAIMonitor(BaseProviderMonitor):
    """
    Monitor for OpenAI API calls.
    Supports both chat completion and completion endpoints.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        application_name: str = "default-app",
        environment: str = "development",
        **kwargs
    ):
        """
        Initialize OpenAI monitor.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name to use
            organization: OpenAI organization ID
            base_url: Custom base URL for API calls
            application_name: Name of the application using the monitor
            environment: Environment (e.g., "development", "production")
            **kwargs: Additional arguments for the base monitor
        """
        super().__init__(
            provider_name="openai",
            model=model,
            application_name=application_name,
            environment=environment,
            **kwargs
        )
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY env var or pass api_key.")
            
        self.organization = organization
        self.base_url = base_url
        self.client = None
        self.setup_client()
        
    def setup_client(self):
        """Set up the OpenAI client."""
        try:
            import openai
            
            # Check if we're using the new client (>=1.0.0) or legacy client
            if hasattr(openai, "OpenAI"):
                # New client
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    organization=self.organization,
                    base_url=self.base_url
                )
                self.client_version = "v1"
            else:
                # Legacy client
                openai.api_key = self.api_key
                if self.organization:
                    openai.organization = self.organization
                if self.base_url:
                    openai.api_base = self.base_url
                self.client = openai
                self.client_version = "legacy"
                
            logger.info(f"OpenAI client initialized (version: {self.client_version})")
        except ImportError:
            logger.error("OpenAI package not installed. Run 'pip install openai'.")
            raise
    
    def extract_completion(self, response: Any) -> str:
        """Extract completion text from OpenAI response."""
        try:
            if hasattr(response, "choices"):
                # Handle both completion and chat completion
                if hasattr(response.choices[0], "message"):
                    return response.choices[0].message.content
                else:
                    return response.choices[0].text
            elif isinstance(response, dict):
                # Handle dictionary response
                if "choices" in response:
                    if "message" in response["choices"][0]:
                        return response["choices"][0]["message"]["content"]
                    else:
                        return response["choices"][0]["text"]
            
            # If we can't extract, return string representation
            return str(response)
        except Exception as e:
            logger.warning(f"Failed to extract completion: {str(e)}")
            return str(response)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Monitor an OpenAI chat completion call.
        
        Args:
            messages: List of message objects
            stream: Whether to stream the response
            **kwargs: Additional arguments for the API call
            
        Returns:
            The API response
        """
        # Prepare the prompt for token counting (concatenate all messages)
        prompt_text = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            prompt_text += f"{role}: {content}\n"
        
        # Define the client function to call
        def client_function(prompt_text, **kw):
            if self.client_version == "v1":
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=stream,
                    **kwargs
                )
            else:
                return self.client.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    stream=stream,
                    **kwargs
                )
        
        # Monitor the call
        return self._monitor_call(prompt_text, client_function, **kwargs)
    
    def completion(
        self,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Monitor an OpenAI completion call.
        
        Args:
            prompt: The prompt text
            stream: Whether to stream the response
            **kwargs: Additional arguments for the API call
            
        Returns:
            The API response
        """
        # Define the client function to call
        def client_function(prompt_text, **kw):
            if self.client_version == "v1":
                return self.client.completions.create(
                    model=self.model,
                    prompt=prompt,
                    stream=stream,
                    **kwargs
                )
            else:
                return self.client.Completion.create(
                    model=self.model,
                    prompt=prompt,
                    stream=stream,
                    **kwargs
                )
        
        # Monitor the call
        return self._monitor_call(prompt, client_function, **kwargs)
    
    def count_tokens(self, text: Union[str, List[Dict[str, str]]]) -> int:
        """
        Count tokens for OpenAI models.
        
        Args:
            text: Text content or messages list
            
        Returns:
            Token count
        """
        return TokenCounter.count_openai_tokens(text, self.model)