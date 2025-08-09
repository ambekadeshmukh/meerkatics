# Cohere Provider Implementation

import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from ..core.monitor import LLMRequest, LLMResponse
from .base import BaseLLMProvider

class CohereProvider(BaseLLMProvider):
    """Cohere provider with monitoring"""
    
    def __init__(self, api_key: Optional[str] = None, monitor=None):
        super().__init__(api_key, monitor)
        
        try:
            import cohere
            self.cohere = cohere
            self.client = cohere.Client(self.api_key)
        except ImportError:
            raise ImportError("cohere package is required. Install with: pip install cohere")
    
    def create_completion(self, **kwargs) -> Any:
        """Create completion with monitoring"""
        return self.create_chat_completion(**kwargs)
    
    def create_chat_completion(self, **kwargs) -> Any:
        """Create chat completion with monitoring"""
        request_id = self.monitor._generate_request_id()
        start_time = time.time()
        
        # Extract monitoring data
        model = kwargs.get('model', 'command')
        messages = kwargs.get('messages', [])
        prompt = kwargs.get('prompt') or self._convert_messages_to_prompt(messages)
        
        # Create request event
        request_data = LLMRequest(
            request_id=request_id,
            provider='cohere',
            model=model,
            application=self.monitor.application,
            environment=self.monitor.environment,
            user_id=self.monitor.user_id,
            session_id=self.monitor.session_id,
            prompt=prompt if not self.monitor.redact_prompts else self.monitor._redact_text(prompt),
            messages=messages if not self.monitor.redact_prompts else self.monitor._redact_messages(messages),
            parameters={k: v for k, v in kwargs.items() if k not in ['messages', 'prompt']},
            timestamp=datetime.now(timezone.utc),
            metadata=self.monitor.metadata.copy()
        )
        
        try:
            # Make the actual API call
            response = self.client.generate(
                prompt=prompt,
                model=model,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                p=kwargs.get('top_p', 1.0),
                stop_sequences=kwargs.get('stop', [])
            )
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Estimate usage (Cohere doesn't provide token counts directly)
            prompt_tokens = len(prompt.split()) * 1.3
            completion_tokens = len(response.generations[0].text.split()) * 1.3 if response.generations else 0
            
            usage = {
                'prompt_tokens': int(prompt_tokens),
                'completion_tokens': int(completion_tokens),
                'total_tokens': int(prompt_tokens + completion_tokens)
            }
            cost = self._calculate_cost(model, usage)
            
            # Extract response text
            response_text = response.generations[0].text if response.generations else ""
            
            # Create response event
            response_data = LLMResponse(
                request_id=request_id,
                response=response_text if not self.monitor.redact_responses else self.monitor._redact_text(response_text),
                choices=[{"message": {"content": response_text}, "finish_reason": "stop"}],
                usage=usage,
                cost=cost,
                latency_ms=latency_ms,
                status='success',
                error=None,
                model_version=model,
                finish_reason='stop',
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
    
    def _convert_messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert chat messages to a single prompt"""
        prompt_parts = []
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts)
    
    def _get_pricing(self) -> Dict[str, Dict[str, float]]:
        """Cohere pricing (as of 2024)"""
        return {
            'command': {'prompt': 0.0015, 'completion': 0.0015},
            'command-light': {'prompt': 0.0003, 'completion': 0.0003},
            'command-nightly': {'prompt': 0.0015, 'completion': 0.0015},
            'default': {'prompt': 0.0015, 'completion': 0.0015}
        }
    
    def get_detector_name(self) -> str:
        return "cohere"
