import os
import time
import logging
from typing import Dict, Any, List, Optional, Union
import json

from .base import BaseProviderMonitor
from ..utils.tokenizers import TokenCounter

logger = logging.getLogger("sentinelops.providers.azure_openai")

class AzureOpenAIMonitor(BaseProviderMonitor):
    """
    Monitor for Azure OpenAI API calls.
    Supports both chat completion and completion endpoints.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: str = "2023-05-15",
        model: str = "gpt-35-turbo",
        application_name: str = "default-app",
        environment: str = "development",
        **kwargs
    ):
        """
        Initialize Azure OpenAI monitor.
        
        Args:
            api_key: Azure OpenAI API key (defaults to AZURE_OPENAI_API_KEY env var)
            azure_endpoint: Azure OpenAI endpoint URL (defaults to AZURE_OPENAI_ENDPOINT env var)
            deployment_name: Azure OpenAI deployment name (defaults to model name if not provided)
            api_version: Azure OpenAI API version
            model: Base model name (e.g., "gpt-35-turbo", "gpt-4")
            application_name: Name of the application using the monitor
            environment: Environment (e.g., "development", "production")
            **kwargs: Additional arguments for the base monitor
        """
        super().__init__(
            provider_name="azure_openai",
            model=model,
            application_name=application_name,
            environment=environment,
            **kwargs
        )
        
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No Azure OpenAI API key provided. Set AZURE_OPENAI_API_KEY env var or pass api_key.")
            
        self.azure_endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not self.azure_endpoint:
            logger.warning("No Azure OpenAI endpoint provided. Set AZURE_OPENAI_ENDPOINT env var or pass azure_endpoint.")
        
        self.deployment_name = deployment_name or model.replace(".", "")
        self.api_version = api_version
        self.client = None
        self.setup_client()
        
    def setup_client(self):
        """Set up the Azure OpenAI client."""
        try:
            import openai
            
            # Check if we're using the new client (>=1.0.0) or legacy client
            if hasattr(openai, "AzureOpenAI"):
                # New client
                self.client = openai.AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.azure_endpoint,
                    api_version=self.api_version
                )
                self.client_version = "v1"
            else:
                # Legacy client
                openai.api_type = "azure"
                openai.api_key = self.api_key
                openai.api_base = self.azure_endpoint
                openai.api_version = self.api_version
                self.client = openai
                self.client_version = "legacy"
                
            logger.info(f"Azure OpenAI client initialized (version: {self.client_version})")
        except ImportError:
            logger.error("OpenAI package not installed. Run 'pip install openai'.")
            raise
    
    def extract_completion(self, response: Any) -> str:
        """Extract completion text from Azure OpenAI response."""
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
        Monitor an Azure OpenAI chat completion call.
        
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
                    deployment_name=self.deployment_name,
                    messages=messages,
                    stream=stream,
                    **kwargs
                )
            else:
                return self.client.ChatCompletion.create(
                    engine=self.deployment_name,
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
        Monitor an Azure OpenAI completion call.
        
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
                    deployment_name=self.deployment_name,
                    prompt=prompt,
                    stream=stream,
                    **kwargs
                )
            else:
                return self.client.Completion.create(
                    engine=self.deployment_name,
                    prompt=prompt,
                    stream=stream,
                    **kwargs
                )
        
        # Monitor the call
        return self._monitor_call(prompt, client_function, **kwargs)
    
    def count_tokens(self, text: Union[str, List[Dict[str, str]]]) -> int:
        """
        Count tokens for Azure OpenAI models.
        Uses the same tokenizers as OpenAI.
        
        Args:
            text: Text content or messages list
            
        Returns:
            Token count
        """
        # Map Azure model names to OpenAI model names for tokenization
        model_mapping = {
            "gpt-35-turbo": "gpt-3.5-turbo",
            "gpt-35-turbo-16k": "gpt-3.5-turbo-16k",
            "gpt-4": "gpt-4",
            "gpt-4-32k": "gpt-4-32k",
            "gpt-4-vision": "gpt-4-vision-preview",
        }
        
        # Get the equivalent OpenAI model for tokenization
        openai_model = model_mapping.get(self.model, self.model)
        
        return TokenCounter.count_openai_tokens(text, openai_model)
