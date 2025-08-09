# meerkatics/sdk/meerkatics/providers/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from ..sdk import LLMMonitor

class BaseProviderMonitor(ABC):
    """Base class for all provider-specific monitors."""
    
    def __init__(
        self, 
        provider_name: str,
        model: str,
        application_name: str = "default-app",
        environment: str = "development",
        **kwargs
    ):
        self.monitor = LLMMonitor(
            provider=provider_name,
            model=model,
            application_name=application_name,
            environment=environment,
            **kwargs
        )
        self.provider_name = provider_name
        self.model = model
    
    @abstractmethod
    def setup_client(self):
        """Set up the provider-specific client."""
        pass
        
    @abstractmethod
    def extract_completion(self, response: Any) -> str:
        """Extract completion text from provider-specific response."""
        pass
        
    def _monitor_call(self, prompt: str, client_func, **kwargs):
        """Common monitoring wrapper for all providers."""
        return self.monitor.call(prompt, client_func, **kwargs)