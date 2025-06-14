import os
import time
import logging
from typing import Dict, Any, List, Optional, Union
import json

from .base import BaseProviderMonitor
from ..utils.tokenizers import TokenCounter

logger = logging.getLogger("meerkatics.providers.anthropic")

class AnthropicMonitor(BaseProviderMonitor):
    """
    Monitor for Anthropic API calls.
    Supports Claude models.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-2",
        application_name: str = "default-app",
        environment: str = "development",
        **kwargs
    ):
        """
        Initialize Anthropic monitor.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name to use (e.g., "claude-2", "claude-instant-1")
            application_name: Name of the application using the monitor
            environment: Environment (e.g., "development", "production")
            **kwargs: Additional arguments for the base monitor
        """
        super().__init__(
            provider_name="anthropic",
            model=model,
            application_name=application_name,
            environment=environment,
            **kwargs
        )
        
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key provided. Set ANTHROPIC_API_KEY env var or pass api_key.")
            
        self.client = None
        self.setup_client()
        
    def setup_client(self):
        """Set up the Anthropic client."""
        try:
            # Check for anthropic package
            try:
                import anthropic
                self.client_type = "anthropic"
                
                # Check if we're using the newer version of the client
                if hasattr(anthropic, "Anthropic"):
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                else:
                    self.client = anthropropic.Client(api_key=self.api_key)
                
                logger.info("Anthropic client initialized")
            except ImportError:
                # Fallback to using requests directly
                logger.warning("Anthropic package not installed. Using requests instead. Run 'pip install anthropic' for better integration.")
                import requests
                self.client_type = "requests"
                self.client = requests
                
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
            raise
    
    def extract_completion(self, response: Any) -> str:
        """Extract completion text from Anthropic response."""
        try:
            if self.client_type == "anthropic":
                # Handle different response formats based on client version
                if hasattr(response, "completion"):
                    return response.completion
                elif hasattr(response, "content"):
                    if isinstance(response.content, list):
                        # Handle content blocks (newer API)
                        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
                        return "".join(text_blocks)
                    return response.content
                elif isinstance(response, dict):
                    if "completion" in response:
                        return response["completion"]
                    elif "content" in response:
                        if isinstance(response["content"], list):
                            # Handle content blocks (newer API)
                            text_blocks = [block.get("text", "") for block in response["content"] 
                                           if block.get("type") == "text"]
                            return "".join(text_blocks)
                        return response["content"]
            elif self.client_type == "requests" and isinstance(response, dict):
                if "completion" in response:
                    return response["completion"]
                elif "content" in response:
                    if isinstance(response["content"], list):
                        # Handle content blocks (newer API)
                        text_blocks = [block.get("text", "") for block in response["content"] 
                                       if block.get("type") == "text"]
                        return "".join(text_blocks)
                    return response["content"]
            
            # If we can't extract, return string representation
            return str(response)
        except Exception as e:
            logger.warning(f"Failed to extract completion: {str(e)}")
            return str(response)
    
    def completion(
        self,
        prompt: str,
        max_tokens_to_sample: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Monitor an Anthropic completion call.
        
        Args:
            prompt: The prompt text
            max_tokens_to_sample: Maximum number of tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional arguments for the API call
            
        Returns:
            The API response
        """
        # Format prompt according to Anthropic's requirements if not already formatted
        if not prompt.startswith("\n\nHuman: "):
            # Format for Claude: "\n\nHuman: {prompt}\n\nAssistant:"
            formatted_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"
        else:
            formatted_prompt = prompt
            
        # Define the client function to call
        def client_function(prompt_text, **kw):
            if self.client_type == "anthropic":
                # Check if we're using the newer version of the client
                if hasattr(self.client, "completions"):
                    # New API format
                    return self.client.completions.create(
                        model=self.model,
                        prompt=formatted_prompt,
                        max_tokens_to_sample=max_tokens_to_sample,
                        stream=stream,
                        **kwargs
                    )
                elif hasattr(self.client, "messages"):
                    # Even newer API format (messages API)
                    # Extract the human message from the formatted prompt
                    human_message = formatted_prompt.split("\n\nHuman: ")[1].split("\n\nAssistant:")[0]
                    return self.client.messages.create(
                        model=self.model,
                        messages=[{"role": "user", "content": human_message}],
                        max_tokens=max_tokens_to_sample,
                        stream=stream,
                        **kwargs
                    )
                else:
                    # Legacy API
                    return self.client.completion(
                        prompt=formatted_prompt,
                        model=self.model,
                        max_tokens_to_sample=max_tokens_to_sample,
                        stream=stream,
                        **kwargs
                    )
            elif self.client_type == "requests":
                # Direct API call using requests
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                
                data = {
                    "model": self.model,
                    "prompt": formatted_prompt,
                    "max_tokens_to_sample": max_tokens_to_sample,
                    **kwargs
                }
                
                response = self.client.post(
                    "https://api.anthropic.com/v1/complete",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
        
        # Monitor the call
        return self._monitor_call(formatted_prompt, client_function, **kwargs)
    
    def messages(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Monitor an Anthropic messages API call (newer API).
        
        Args:
            messages: List of message objects with role and content
            max_tokens: Maximum number of tokens to generate
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
            if self.client_type == "anthropic":
                # Check if we're using the newer version of the client with messages API
                if hasattr(self.client, "messages"):
                    return self.client.messages.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=max_tokens,
                        stream=stream,
                        **kwargs
                    )
                else:
                    # Convert messages to Claude prompt format
                    claude_prompt = "\n\n"
                    for message in messages:
                        role = message.get("role", "user")
                        content = message.get("content", "")
                        if role == "user":
                            claude_prompt += f"Human: {content}\n\n"
                        elif role == "assistant":
                            claude_prompt += f"Assistant: {content}\n\n"
                    
                    # Add final Assistant: prompt
                    if not claude_prompt.endswith("Assistant: "):
                        claude_prompt += "Assistant: "
                    
                    return self.client.completion(
                        prompt=claude_prompt,
                        model=self.model,
                        max_tokens_to_sample=max_tokens,
                        stream=stream,
                        **kwargs
                    )
            elif self.client_type == "requests":
                # Direct API call using requests
                headers = {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key,
                    "anthropic-version": "2023-06-01"
                }
                
                data = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    **kwargs
                }
                
                response = self.client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
        
        # Monitor the call
        return self._monitor_call(prompt_text, client_function, **kwargs)
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens for Anthropic models.
        
        Args:
            text: Text content
            
        Returns:
            Token count
        """
        return TokenCounter.count_anthropic_tokens(text, self.model)