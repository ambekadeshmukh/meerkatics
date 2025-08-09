import boto3
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from ..core.monitor import LLMRequest, LLMResponse
from .base import BaseLLMProvider

class AWSBedrockProvider(BaseLLMProvider):
    """AWS Bedrock provider with comprehensive monitoring"""
    
    def __init__(self, region_name: str = 'us-east-1', monitor=None):
        super().__init__(None, monitor)  # No API key needed for Bedrock
        self.region_name = region_name
        
        try:
            self.bedrock = boto3.client('bedrock-runtime', region_name=region_name)
        except Exception as e:
            raise ImportError(f"AWS Bedrock setup failed: {e}")
    
    def create_completion(self, **kwargs) -> Any:
        """Create completion with monitoring"""
        return self.create_chat_completion(**kwargs)
    
    def create_chat_completion(self, **kwargs) -> Any:
        """Create chat completion with monitoring"""
        request_id = self.monitor._generate_request_id()
        start_time = time.time()
        
        # Extract parameters
        model_id = kwargs.get('model', 'anthropic.claude-v2')
        messages = kwargs.get('messages', [])
        max_tokens = kwargs.get('max_tokens', 1000)
        
        # Convert messages to prompt for Bedrock
        prompt = self._convert_messages_to_prompt(messages, model_id)
        
        # Create request event
        request_data = LLMRequest(
            request_id=request_id,
            provider='aws_bedrock',
            model=model_id,
            application=self.monitor.application,
            environment=self.monitor.environment,
            user_id=self.monitor.user_id,
            session_id=self.monitor.session_id,
            prompt=prompt if not self.monitor.redact_prompts else self.monitor._redact_text(prompt),
            messages=messages if not self.monitor.redact_prompts else self.monitor._redact_messages(messages),
            parameters={k: v for k, v in kwargs.items() if k not in ['messages', 'model']},
            timestamp=datetime.now(timezone.utc),
            metadata=self.monitor.metadata.copy()
        )
        
        try:
            # Prepare request body based on model
            body = self._prepare_request_body(model_id, prompt, kwargs)
            
            # Make the actual API call
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract response text and usage
            response_text, usage = self._parse_response(model_id, response_body)
            cost = self._calculate_cost(model_id, usage)
            
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
                model_version=model_id,
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
                'model': model_id
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
    
    def _convert_messages_to_prompt(self, messages: List[Dict], model_id: str) -> str:
        """Convert chat messages to prompt format"""
        if 'anthropic' in model_id.lower():
            # Anthropic format
            prompt_parts = []
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                if role == 'system':
                    prompt_parts.append(f"System: {content}")
                elif role == 'user':
                    prompt_parts.append(f"\n\nHuman: {content}")
                elif role == 'assistant':
                    prompt_parts.append(f"\n\nAssistant: {content}")
            prompt = "".join(prompt_parts) + "\n\nAssistant:"
        else:
            # Generic format
            prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
        
        return prompt
    
    def _prepare_request_body(self, model_id: str, prompt: str, kwargs: Dict) -> Dict:
        """Prepare request body based on model type"""
        if 'anthropic' in model_id.lower():
            return {
                "prompt": prompt,
                "max_tokens_to_sample": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 1.0),
                "stop_sequences": kwargs.get('stop', [])
            }
        elif 'ai21' in model_id.lower():
            return {
                "prompt": prompt,
                "maxTokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7),
                "topP": kwargs.get('top_p', 1.0)
            }
        elif 'cohere' in model_id.lower():
            return {
                "prompt": prompt,
                "max_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7),
                "p": kwargs.get('top_p', 1.0)
            }
        else:
            # Default format
            return {
                "prompt": prompt,
                "max_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7)
            }
    
    def _parse_response(self, model_id: str, response_body: Dict) -> tuple:
        """Parse response based on model type"""
        if 'anthropic' in model_id.lower():
            response_text = response_body.get('completion', '')
            usage = {
                'prompt_tokens': response_body.get('prompt_tokens', 0),
                'completion_tokens': response_body.get('completion_tokens', 0),
                'total_tokens': response_body.get('prompt_tokens', 0) + response_body.get('completion_tokens', 0)
            }
        elif 'ai21' in model_id.lower():
            response_text = response_body.get('completions', [{}])[0].get('data', {}).get('text', '')
            # AI21 doesn't provide token counts, estimate
            usage = {
                'prompt_tokens': len(response_text.split()) * 1.3,
                'completion_tokens': len(response_text.split()) * 1.3,
                'total_tokens': len(response_text.split()) * 2.6
            }
        elif 'cohere' in model_id.lower():
            response_text = response_body.get('generations', [{}])[0].get('text', '')
            # Cohere estimation
            usage = {
                'prompt_tokens': len(response_text.split()) * 1.3,
                'completion_tokens': len(response_text.split()) * 1.3,
                'total_tokens': len(response_text.split()) * 2.6
            }
        else:
            # Default parsing
            response_text = str(response_body)
            usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        
        return response_text, usage
    
    def _get_pricing(self) -> Dict[str, Dict[str, float]]:
        """AWS Bedrock pricing (as of 2024)"""
        return {
            'anthropic.claude-v2': {'prompt': 0.008, 'completion': 0.024},
            'anthropic.claude-v1': {'prompt': 0.008, 'completion': 0.024},
            'anthropic.claude-instant-v1': {'prompt': 0.0008, 'completion': 0.0024},
            'ai21.j2-ultra': {'prompt': 0.0188, 'completion': 0.0188},
            'ai21.j2-mid': {'prompt': 0.0125, 'completion': 0.0125},
            'cohere.command-text': {'prompt': 0.0015, 'completion': 0.002},
            'default': {'prompt': 0.001, 'completion': 0.002}
        }
    
    def get_detector_name(self) -> str:
        return "aws_bedrock"
