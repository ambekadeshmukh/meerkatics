# meerkatics/sdk/meerkatics/providers/replicate.py

import os
import time
import logging
from typing import Dict, Any, List, Optional, Union

from ..metrics.token_counter import count_tokens
from ..utils.cost import calculate_cost
from .base import BaseProviderMonitor

logger = logging.getLogger(__name__)

class ReplicateMonitor(BaseProviderMonitor):
    """
    Monitoring wrapper for Replicate models.
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        model: str = "meta/llama-2-70b-chat",
        application_name: str = "default-app",
        environment: str = "development",
        **kwargs
    ):
        super().__init__(
            provider_name="replicate", 
            model=model,
            application_name=application_name,
            environment=environment,
            **kwargs
        )
        
        self.api_token = api_token or os.environ.get("REPLICATE_API_TOKEN")
        self.client = self.setup_client()
        
    def setup_client(self):
        """Set up the Replicate client."""
        try:
            import replicate
            if self.api_token:
                replicate.Client(api_token=self.api_token)
            return replicate
        except ImportError:
            raise ImportError("Replicate package not installed. Run 'pip install replicate'")
    
    def extract_completion(self, response: Any) -> str:
        """Extract completion text from Replicate response."""
        if isinstance(response, list):
            return "".join(response)
        elif isinstance(response, str):
            return response
        else:
            return str(response)
    
    def run(
        self, 
        prompt: str,
        version: Optional[str] = None,
        input_params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Run a Replicate model with monitoring.
        
        Args:
            prompt: Input text prompt
            version: Specific model version (optional)
            input_params: Additional model parameters
            **kwargs: Additional arguments for run
            
        Returns:
            Response from the model
        """
        input_params = input_params or {}
        input_params["prompt"] = prompt
        
        model_string = self.model
        if version:
            model_string = f"{model_string}:{version}"
            
        def client_function(prompt_text, **kw):
            return self.client.run(
                model_string,
                input=input_params,
                **kw
            )
        
        return self._monitor_call(prompt, client_function, **kwargs)