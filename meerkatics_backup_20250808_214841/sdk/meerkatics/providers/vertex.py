# meerkatics/sdk/meerkatics/providers/vertex.py
# Enhancing the existing Vertex AI implementation with Gemini support

import os
import time
import logging
from typing import Dict, Any, List, Optional, Union

from ..metrics.token_counter import count_tokens
from ..utils.cost import calculate_cost
from ..sdk import LLMMonitor

logger = logging.getLogger(__name__)

class VertexAIMonitor(LLMMonitor):
    """
    Monitoring wrapper for Google Vertex AI models.
    Enhanced with Gemini model support.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gemini-pro",
        application_name: str = "default-app",
        environment: str = "development",
        project_id: Optional[str] = None,
        location: str = "us-central1",
        **kwargs
    ):
        # Determine model family
        if "gemini" in model.lower():
            model_family = "gemini"
        elif "palm" in model.lower():
            model_family = "palm"
        else:
            model_family = "text"
            
        super().__init__(
            provider="google", 
            model=model,
            application_name=application_name,
            environment=environment,
            **kwargs
        )
        
        self.api_key = api_key
        self.project_id = project_id
        self.location = location
        self.model_family = model_family
        self._setup_client()
        
    def _setup_client(self):
        """Set up the Google Vertex AI client."""
        try:
            import vertexai
            from vertexai.language_models import TextGenerationModel, ChatModel
            from vertexai.generative_models import GenerativeModel
            
            # Initialize Vertex AI
            vertexai.init(
                project=self.project_id, 
                location=self.location
            )
            
            # Create the appropriate client based on model type
            if self.model_family == "gemini":
                self.client = GenerativeModel(self.model)
                self.model_type = "gemini"
            elif self.model_family == "palm":
                self.client = TextGenerationModel.from_pretrained(self.model)
                self.model_type = "text"
            else:
                # Determine model type from name
                if "chat" in self.model:
                    self.client = ChatModel.from_pretrained(self.model)
                    self.model_type = "chat"
                else:
                    self.client = TextGenerationModel.from_pretrained(self.model)
                    self.model_type = "text"
                
        except ImportError:
            raise ImportError("Required packages not installed. Run 'pip install google-cloud-aiplatform'")
    
    def text_generation(
        self, 
        prompt: str,
        max_output_tokens: int = 1024,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.95,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Vertex AI models with monitoring."""
        def client_function(prompt_text, **kw):
            if self.model_type == "gemini":
                response = self.client.generate_content(
                    prompt_text,
                    generation_config={
                        "max_output_tokens": max_output_tokens,
                        "temperature": temperature,
                        "top_k": top_k,
                        "top_p": top_p,
                    },
                    **kw
                )
                return {"text": response.text, "candidates": response.candidates}
            elif self.model_type == "text":
                response = self.client.predict(
                    prompt_text,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    **kw
                )
                return {"text": response.text, "safety_attributes": getattr(response, "safety_attributes", None)}
            else:
                # For chat models, start a new chat and send a message
                chat = self.client.start_chat()
                response = chat.send_message(
                    prompt_text,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    **kw
                )
                return {"text": response.text, "safety_attributes": getattr(response, "safety_attributes", None)}
                
        return self.call(prompt, client_function, **kwargs)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_output_tokens: int = 1024,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.95,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat responses using Vertex AI chat models."""
        # Extract the prompt for monitoring
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        
        def client_function(prompt_text, **kw):
            if self.model_type == "gemini":
                # Convert messages to Gemini format
                gemini_messages = []
                for msg in messages:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    if role == "user":
                        gemini_messages.append({"role": "user", "parts": [{"text": content}]})
                    elif role == "assistant":
                        gemini_messages.append({"role": "model", "parts": [{"text": content}]})
                    elif role == "system":
                        # Include system message as user message with special prefix
                        gemini_messages.append({"role": "user", "parts": [{"text": f"[SYSTEM]: {content}"}]})
                
                response = self.client.generate_content(
                    gemini_messages,
                    generation_config={
                        "max_output_tokens": max_output_tokens,
                        "temperature": temperature,
                        "top_k": top_k,
                        "top_p": top_p,
                    },
                    **kw
                )
                return {"text": response.text, "candidates": response.candidates}
            elif self.model_type == "chat":
                # Start a chat session
                chat = self.client.start_chat()
                
                # Add previous messages to the chat
                for idx, msg in enumerate(messages[:-1]):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    
                    # Skip adding system messages as they're handled differently
                    if role != "system":
                        if idx % 2 == 0:  # Even indices are user messages
                            _ = chat.send_message(content)
                        # Odd indices are already part of the chat history as responses
                
                # Send the final message and get response
                final_msg = messages[-1].get("content", "")
                response = chat.send_message(
                    final_msg,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    top_k=top_k,
                    top_p=top_p,
                    **kw
                )
                
                return {"text": response.text, "safety_attributes": getattr(response, "safety_attributes", None)}
            else:
                # Text models don't support chat directly
                return self.text_generation(prompt, max_output_tokens, temperature, top_k, top_p, **kw)
        
        return self.call(prompt, client_function, **kwargs)
    
    def _extract_completion_text(self, response: Any) -> str:
        """Extract completion text from the API response."""
        if isinstance(response, dict) and "text" in response:
            return response["text"]
        elif hasattr(response, "text"):
            return response.text
        else:
            return str(response)