# LlamaIndex Integration for Meerkatics

from typing import Any, Dict, List, Optional
import time

class MeerkaticsLlamaIndexCallback:
    """LlamaIndex callback handler for Meerkatics monitoring"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.active_requests = {}
    
    def on_event_start(self, event_type: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """Called when an event starts"""
        event_id = kwargs.get('event_id', f"event_{int(time.time() * 1000)}")
        
        if event_type == "llm":
            self.active_requests[event_id] = {
                'start_time': time.time(),
                'event_type': event_type,
                'payload': payload or {}
            }
        
        return event_id
    
    def on_event_end(self, event_type: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called when an event ends"""
        event_id = kwargs.get('event_id')
        
        if event_type == "llm" and event_id in self.active_requests:
            request_info = self.active_requests.pop(event_id)
            start_time = request_info['start_time']
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract information from payload
            start_payload = request_info.get('payload', {})
            end_payload = payload or {}
            
            prompt = self._extract_prompt(start_payload)
            response = self._extract_response(end_payload)
            model_info = self._extract_model_info(start_payload, end_payload)
            
            # Track with Meerkatics
            self.monitor.track_custom_llm(
                provider=model_info.get('provider', 'llamaindex'),
                model=model_info.get('model', 'unknown'),
                prompt=prompt,
                response=response,
                usage=self._extract_usage(end_payload),
                latency_ms=latency_ms,
                metadata={'llamaindex': True, 'event_id': event_id}
            )
    
    def on_event_error(self, event_type: str, exception: Exception, **kwargs) -> None:
        """Called when an event encounters an error"""
        event_id = kwargs.get('event_id')
        
        if event_type == "llm" and event_id in self.active_requests:
            request_info = self.active_requests.pop(event_id)
            start_time = request_info['start_time']
            latency_ms = int((time.time() - start_time) * 1000)
            
            start_payload = request_info.get('payload', {})
            prompt = self._extract_prompt(start_payload)
            model_info = self._extract_model_info(start_payload, {})
            
            # Track error with Meerkatics
            self.monitor.track_custom_llm(
                provider=model_info.get('provider', 'llamaindex'),
                model=model_info.get('model', 'unknown'),
                prompt=prompt,
                response="",
                usage={'total_tokens': 0},
                latency_ms=latency_ms,
                status='error',
                error=str(exception),
                metadata={'llamaindex': True, 'event_id': event_id}
            )
    
    def _extract_prompt(self, payload: Dict[str, Any]) -> str:
        """Extract prompt from payload"""
        # Try different possible keys
        for key in ['prompt', 'messages', 'query', 'input']:
            if key in payload:
                value = payload[key]
                if isinstance(value, str):
                    return value
                elif isinstance(value, list):
                    return str(value)
        return ""
    
    def _extract_response(self, payload: Dict[str, Any]) -> str:
        """Extract response from payload"""
        # Try different possible keys
        for key in ['response', 'output', 'completion', 'result']:
            if key in payload:
                value = payload[key]
                if isinstance(value, str):
                    return value
                elif hasattr(value, 'text'):
                    return value.text
        return ""
    
    def _extract_model_info(self, start_payload: Dict[str, Any], end_payload: Dict[str, Any]) -> Dict[str, str]:
        """Extract model information from payloads"""
        info = {'provider': 'llamaindex', 'model': 'unknown'}
        
        # Look for model info in both payloads
        for payload in [start_payload, end_payload]:
            if 'model' in payload:
                info['model'] = payload['model']
            if 'llm' in payload and hasattr(payload['llm'], 'model_name'):
                info['model'] = payload['llm'].model_name
            if 'llm' in payload and hasattr(payload['llm'], '_get_model_name'):
                try:
                    info['model'] = payload['llm']._get_model_name()
                except:
                    pass
        
        return info
    
    def _extract_usage(self, payload: Dict[str, Any]) -> Dict[str, int]:
        """Extract token usage from payload"""
        usage = {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0}
        
        if 'usage' in payload:
            usage.update(payload['usage'])
        elif 'token_usage' in payload:
            usage.update(payload['token_usage'])
        
        return usage