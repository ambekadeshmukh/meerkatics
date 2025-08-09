# LangChain Integration for Meerkatics

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import time

class MeerkaticsLangChainCallback:
    """LangChain callback handler for Meerkatics monitoring"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        self.start_times = {}
        self.request_data = {}
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts generating"""
        run_id = kwargs.get('run_id')
        self.start_times[run_id] = time.time()
        
        # Store request information
        self.request_data[run_id] = {
            'provider': self._extract_provider(serialized),
            'model': self._extract_model(serialized),
            'prompts': prompts,
            'serialized': serialized
        }
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes generating"""
        run_id = kwargs.get('run_id')
        start_time = self.start_times.pop(run_id, time.time())
        request_info = self.request_data.pop(run_id, {})
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract response text
        if hasattr(response, 'generations') and response.generations:
            response_text = response.generations[0][0].text
        else:
            response_text = str(response)
        
        # Track with Meerkatics
        self.monitor.track_custom_llm(
            provider=request_info.get('provider', 'langchain'),
            model=request_info.get('model', 'unknown'),
            prompt=request_info.get('prompts', [''])[0],
            response=response_text,
            usage={'total_tokens': len(response_text.split())},
            latency_ms=latency_ms,
            metadata={'langchain': True, 'run_id': run_id}
        )
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        run_id = kwargs.get('run_id')
        start_time = self.start_times.pop(run_id, time.time())
        request_info = self.request_data.pop(run_id, {})
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Track error with Meerkatics
        self.monitor.track_custom_llm(
            provider=request_info.get('provider', 'langchain'),
            model=request_info.get('model', 'unknown'),
            prompt=request_info.get('prompts', [''])[0],
            response="",
            usage={'total_tokens': 0},
            latency_ms=latency_ms,
            status='error',
            error=str(error),
            metadata={'langchain': True, 'run_id': run_id}
        )
    
    def _extract_provider(self, serialized: Dict[str, Any]) -> str:
        """Extract provider name from serialized LLM info"""
        class_name = serialized.get('_type', '').lower()
        
        if 'openai' in class_name:
            return 'openai'
        elif 'anthropic' in class_name:
            return 'anthropic'
        elif 'google' in class_name or 'palm' in class_name:
            return 'google'
        elif 'cohere' in class_name:
            return 'cohere'
        elif 'huggingface' in class_name:
            return 'huggingface'
        else:
            return 'langchain'
    
    def _extract_model(self, serialized: Dict[str, Any]) -> str:
        """Extract model name from serialized LLM info"""
        kwargs = serialized.get('kwargs', {})
        
        # Try different possible keys for model name
        for key in ['model_name', 'model', 'engine', 'deployment_name']:
            if key in kwargs:
                return kwargs[key]
        
        return 'unknown'
