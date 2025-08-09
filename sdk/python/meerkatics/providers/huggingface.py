# Hugging Face Provider Implementation

import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from ..core.monitor import LLMRequest, LLMResponse
from .base import BaseLLMProvider

class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face provider with monitoring"""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, monitor=None):
        super().__init__(api_key, monitor)
        self.api_url = api_url or "https://api-inference.huggingface.co/models"
        
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests package is required. Install with: pip install requests")
    
    def create_completion(self, **kwargs) -> Any:
        """Create completion with monitoring"""
        return self.create_chat_completion(**kwargs)
    
    def create_chat_completion(self, **kwargs) -> Any:
        """Create chat completion with monitoring"""
        request_id = self.monitor._generate_request_id()
        start_time = time.time()
        
        # Extract monitoring data
        model = kwargs.get('model', 'microsoft/DialoGPT-medium')
        messages = kwargs.get('messages', [])
        prompt = kwargs.get('prompt') or self._convert_messages_to_prompt(messages)
        
        # Create request event
        request_data = LLMRequest(
            request_id=request_id,
            provider='huggingface',
            model=model,
            application=self.monitor.application,
            environment=self.monitor.environment,
            user_id=self.monitor.user_id,
            session_id=self.monitor.session_id,
            prompt=prompt if not self.monitor.redact_prompts else self.monitor._redact_text(prompt),
            messages=messages if not self.monitor.redact_prompts else self.monitor._redact_messages(messages),
            parameters={k: v for k, v in kwargs.items() if k not in ['messages', 'prompt', 'model']},
            timestamp=datetime.now(timezone.utc),
            metadata=self.monitor.metadata.copy()
        )
        
        try:
            # Prepare request
            headers = {"Authorization": f"Bearer {self.api_key}"}
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get('max_tokens', 1000),
                    "temperature": kwargs.get('temperature', 0.7),
                    "top_p": kwargs.get('top_p', 1.0),
                    "do_sample": True
                }
            }
            
            # Make the actual API call
            response = self.requests.post(
                f"{self.api_url}/{model}",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response text
            if isinstance(result, list) and result:
                response_text = result[0].get('generated_text', '')
                # Remove the original prompt from response
                if response_text.startswith(prompt):
                    response_text = response_text[len(prompt):].strip()
            else:
                response_text = str(result)
            
            # Estimate usage
            prompt_tokens = len(prompt.split()) * 1.3
            completion_tokens = len(response_text.split()) * 1.3
            
            usage = {
                'prompt_tokens': int(prompt_tokens),
                'completion_tokens': int(completion_tokens),
                'total_tokens': int(prompt_tokens + completion_tokens)
            }
            cost = self._calculate_cost(model, usage)
            
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
            
            return {
                'choices': [{'message': {'content': response_text}}],
                'usage': usage,
                'model': model
            }
            
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
            prompt_parts.append(f"{role}: {content}")
        return "\n".join(prompt_parts) + "\nassistant:"
    
    def _get_pricing(self) -> Dict[str, Dict[str, float]]:
        """Hugging Face pricing (mostly free for inference API)"""
        return {
            'default': {'prompt': 0.0, 'completion': 0.0}  # Free tier
        }
    
    def get_detector_name(self) -> str:
        return "huggingface"
