# Azure OpenAI Provider Implementation

import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from ..core.monitor import LLMRequest, LLMResponse
from .base import BaseLLMProvider

class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider with monitoring"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, 
                 api_version: str = "2023-12-01-preview", monitor=None):
        super().__init__(api_key, monitor)
        self.api_base = api_base
        self.api_version = api_version
        
        try:
            import openai
            self.openai = openai
            if self.api_key:
                self.openai.api_key = self.api_key
            if api_base:
                self.openai.api_base = api_base
            self.openai.api_type = "azure"
            self.openai.api_version = api_version
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
    def create_completion(self, **kwargs) -> Any:
        """Create completion with monitoring"""
        request_id = self.monitor._generate_request_id()
        start_time = time.time()
        
        # Extract monitoring data
        engine = kwargs.get('engine') or kwargs.get('model', 'gpt-35-turbo')
        prompt = kwargs.get('prompt', '')
        
        # Create request event
        request_data = LLMRequest(
            request_id=request_id,
            provider='azure_openai',
            model=engine,
            application=self.monitor.application,
            environment=self.monitor.environment,
            user_id=self.monitor.user_id,
            session_id=self.monitor.session_id,
            prompt=prompt if not self.monitor.redact_prompts else self.monitor._redact_text(prompt),
            messages=None,
            parameters={k: v for k, v in kwargs.items() if k not in ['prompt']},
            timestamp=datetime.now(timezone.utc),
            metadata=self.monitor.metadata.copy()
        )
        
        try:
            # Make the actual API call
            response = self.openai.Completion.create(**kwargs)
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            usage = response.get('usage', {})
            cost = self._calculate_cost(engine, usage)
            
            # Extract response text
            response_text = response.choices[0].text if response.choices else ""
            
            # Create response event
            response_data = LLMResponse(
                request_id=request_id,
                response=response_text if not self.monitor.redact_responses else self.monitor._redact_text(response_text),
                choices=response.choices,
                usage=usage,
                cost=cost,
                latency_ms=latency_ms,
                status='success',
                error=None,
                model_version=response.get('model'),
                finish_reason=response.choices[0].finish_reason if response.choices else None,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Send monitoring data
            self.monitor._track_request(request_data, response_data)
            
            # Check for security issues
            self.monitor._check_security(request_data, response_data)
            
            return response
            
        except Exception as e:
            # Handle errors
            latency_ms = int((time.time() - start_time) * 1000)
            
            response_data = LLMResponse(
                request_id=request_id,
                response=None,
                choices=None,
                usage={},
                cost=0.0,
                latency_ms=latency_ms,
                status='error',
                error=str(e),
                model_version=None,
                finish_reason=None,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.monitor._track_request(request_data, response_data)
            raise
    
    def create_chat_completion(self, **kwargs) -> Any:
        """Create chat completion with monitoring"""
        request_id = self.monitor._generate_request_id()
        start_time = time.time()
        
        # Extract monitoring data
        engine = kwargs.get('engine') or kwargs.get('model', 'gpt-35-turbo')
        messages = kwargs.get('messages', [])
        
        # Create request event
        request_data = LLMRequest(
            request_id=request_id,
            provider='azure_openai',
            model=engine,
            application=self.monitor.application,
            environment=self.monitor.environment,
            user_id=self.monitor.user_id,
            session_id=self.monitor.session_id,
            prompt=None,
            messages=messages if not self.monitor.redact_prompts else self.monitor._redact_messages(messages),
            parameters={k: v for k, v in kwargs.items() if k not in ['messages']},
            timestamp=datetime.now(timezone.utc),
            metadata=self.monitor.metadata.copy()
        )
        
        try:
            # Make the actual API call
            response = self.openai.ChatCompletion.create(**kwargs)
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            usage = response.get('usage', {})
            cost = self._calculate_cost(engine, usage)
            
            # Extract response text
            response_text = response.choices[0].message.content if response.choices else ""
            
            # Create response event
            response_data = LLMResponse(
                request_id=request_id,
                response=response_text if not self.monitor.redact_responses else self.monitor._redact_text(response_text),
                choices=response.choices,
                usage=usage,
                cost=cost,
                latency_ms=latency_ms,
                status='success',
                error=None,
                model_version=response.get('model'),
                finish_reason=response.choices[0].finish_reason if response.choices else None,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Send monitoring data
            self.monitor._track_request(request_data, response_data)
            
            # Check for security issues
            self.monitor._check_security(request_data, response_data)
            
            return response
            
        except Exception as e:
            # Handle errors
            latency_ms = int((time.time() - start_time) * 1000)
            
            response_data = LLMResponse(
                request_id=request_id,
                response=None,
                choices=None,
                usage={},
                cost=0.0,
                latency_ms=latency_ms,
                status='error',
                error=str(e),
                model_version=None,
                finish_reason=None,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.monitor._track_request(request_data, response_data)
            raise
    
    def _get_pricing(self) -> Dict[str, Dict[str, float]]:
        """Azure OpenAI pricing (as of 2024)"""
        return {
            'gpt-4': {'prompt': 0.03, 'completion': 0.06},
            'gpt-4-32k': {'prompt': 0.06, 'completion': 0.12},
            'gpt-35-turbo': {'prompt': 0.0015, 'completion': 0.002},
            'gpt-35-turbo-16k': {'prompt': 0.003, 'completion': 0.004},
            'text-davinci-003': {'prompt': 0.02, 'completion': 0.02},
            'default': {'prompt': 0.001, 'completion': 0.002}
        }
    
    def get_detector_name(self) -> str:
        return "azure_openai"