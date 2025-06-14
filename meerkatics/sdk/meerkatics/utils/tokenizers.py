import tiktoken
import logging
from typing import Dict, Optional, Union, List

logger = logging.getLogger("meerkatics.tokenizers")

class TokenCounter:
    """
    A utility class for counting tokens across different LLM providers and models.
    Supports OpenAI, Anthropic, Hugging Face, and fallback estimation methods.
    """
    
    @staticmethod
    def count_tokens(text: Union[str, List[Dict[str, str]]], provider: str, model: str) -> int:
        """
        Count tokens in text based on provider and model.
        
        Args:
            text: Text content or messages list (for chat models)
            provider: LLM provider (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-3.5-turbo", "claude-2")
            
        Returns:
            Number of tokens in the text
        """
        if provider.lower() == "openai":
            return TokenCounter.count_openai_tokens(text, model)
        elif provider.lower() == "anthropic":
            return TokenCounter.count_anthropic_tokens(text, model)
        elif provider.lower() == "huggingface":
            return TokenCounter.count_huggingface_tokens(text, model)
        else:
            # Fallback to estimation
            return TokenCounter.estimate_tokens(text)
    
    @staticmethod
    def count_openai_tokens(text: Union[str, List[Dict[str, str]]], model: str) -> int:
        """Count tokens using OpenAI's tiktoken library."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"Model {model} not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        
        if isinstance(text, str):
            # For completion-style API
            return len(encoding.encode(text))
        elif isinstance(text, list):
            # For chat-style API
            num_tokens = 0
            for message in text:
                # Every message follows <im_start>{role/name}\n{content}<im_end>\n
                num_tokens += 4
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # If there's a name, the role is omitted
                        num_tokens -= 1  # Role is always required and always 1 token
            num_tokens += 2  # Every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise ValueError("Text must be a string or a list of message dictionaries")
    
    @staticmethod
    def count_anthropic_tokens(text: str, model: str) -> int:
        """
        Count tokens for Anthropic models.
        Anthropic uses the same tokenizer as OpenAI's cl100k_base.
        """
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error counting Anthropic tokens: {str(e)}. Using estimation.")
            return TokenCounter.estimate_tokens(text)
    
    @staticmethod
    def count_huggingface_tokens(text: str, model: str) -> int:
        """
        Count tokens for Hugging Face models.
        Attempts to load the tokenizer for the specific model.
        """
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(model)
            return len(tokenizer.encode(text))
        except Exception as e:
            logger.warning(f"Error loading Hugging Face tokenizer: {str(e)}. Using estimation.")
            return TokenCounter.estimate_tokens(text)
    
    @staticmethod
    def estimate_tokens(text: Union[str, List[Dict[str, str]]]) -> int:
        """
        Estimate token count when model-specific tokenizers are unavailable.
        This is a fallback method and not as accurate as model-specific tokenizers.
        
        Args:
            text: Text content or messages list
            
        Returns:
            Estimated token count
        """
        if isinstance(text, str):
            # Rough estimation: ~4 characters per token for English text
            return len(text) // 4
        elif isinstance(text, list):
            # For message lists, estimate each message
            total = 0
            for message in text:
                # Add tokens for each message component
                for value in message.values():
                    total += len(value) // 4
            return total
        else:
            raise ValueError("Text must be a string or a list of message dictionaries")
