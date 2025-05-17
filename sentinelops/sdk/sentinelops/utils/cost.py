import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("sentinelops.cost")

class CostCalculator:
    """
    Utility class for calculating costs of LLM API calls across different providers.
    Maintains up-to-date pricing information for popular models.
    """
    
    # Pricing data as of May 2025 (per 1000 tokens)
    # Format: {provider: {model: {"prompt": cost, "completion": cost}}}
    PRICING = {
        "openai": {
            # GPT-3.5 models
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
            "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
            "gpt-3.5-turbo-instruct": {"prompt": 0.0015, "completion": 0.002},
            
            # GPT-4 models
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
            "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
            "gpt-4-vision": {"prompt": 0.01, "completion": 0.03},
            
            # GPT-4o models
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
        },
        "anthropic": {
            "claude-instant-1": {"prompt": 0.0008, "completion": 0.0024},
            "claude-2": {"prompt": 0.008, "completion": 0.024},
            "claude-2.1": {"prompt": 0.008, "completion": 0.024},
            "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
            "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
            "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
        },
        "azure": {
            # Azure OpenAI pricing (may vary by region)
            "gpt-35-turbo": {"prompt": 0.0015, "completion": 0.002},
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
        },
        "cohere": {
            "command": {"prompt": 0.0015, "completion": 0.0015},
            "command-light": {"prompt": 0.0003, "completion": 0.0003},
            "command-r": {"prompt": 0.005, "completion": 0.005},
            "command-r-plus": {"prompt": 0.015, "completion": 0.015},
        },
        "mistral": {
            "mistral-tiny": {"prompt": 0.00014, "completion": 0.00042},
            "mistral-small": {"prompt": 0.0007, "completion": 0.0021},
            "mistral-medium": {"prompt": 0.0027, "completion": 0.0081},
            "mistral-large": {"prompt": 0.008, "completion": 0.024},
        },
        "google": {
            "gemini-pro": {"prompt": 0.00025, "completion": 0.0005},
            "gemini-ultra": {"prompt": 0.00125, "completion": 0.00375},
        }
    }
    
    @staticmethod
    def calculate_cost(
        provider: str, 
        model: str, 
        prompt_tokens: int, 
        completion_tokens: int,
        custom_pricing: Optional[Dict[str, Dict[str, float]]] = None
    ) -> float:
        """
        Calculate the cost of an LLM API call based on token usage.
        
        Args:
            provider: LLM provider name (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-4", "claude-2")
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            custom_pricing: Optional custom pricing data to override defaults
            
        Returns:
            Estimated cost in USD
        """
        pricing_data = custom_pricing or CostCalculator.PRICING
        
        # Normalize provider and model names
        provider = provider.lower()
        model = model.lower()
        
        # Handle Azure OpenAI special case
        if provider == "azure_openai":
            provider = "azure"
        
        # Try to get pricing for the specific model
        try:
            model_pricing = pricing_data.get(provider, {}).get(model, None)
            
            # If model not found, try to find a similar model
            if model_pricing is None:
                model_pricing = CostCalculator._find_similar_model_pricing(provider, model, pricing_data)
                
            if model_pricing:
                prompt_cost = (prompt_tokens / 1000) * model_pricing["prompt"]
                completion_cost = (completion_tokens / 1000) * model_pricing["completion"]
                return prompt_cost + completion_cost
            else:
                logger.warning(f"No pricing data found for {provider}/{model}. Using zero cost.")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return 0.0
    
    @staticmethod
    def _find_similar_model_pricing(
        provider: str, 
        model: str, 
        pricing_data: Dict[str, Dict[str, Dict[str, float]]]
    ) -> Optional[Dict[str, float]]:
        """
        Attempt to find pricing for a similar model when exact match is not found.
        
        Args:
            provider: LLM provider name
            model: Model name
            pricing_data: Pricing data dictionary
            
        Returns:
            Pricing information for a similar model, if found
        """
        provider_pricing = pricing_data.get(provider, {})
        
        # Common model name patterns
        if provider == "openai":
            if "gpt-4" in model:
                return provider_pricing.get("gpt-4", None)
            elif "gpt-3.5" in model or "gpt-35" in model:
                return provider_pricing.get("gpt-3.5-turbo", None)
        elif provider == "anthropic":
            if "claude-3" in model:
                if "haiku" in model:
                    return provider_pricing.get("claude-3-haiku", None)
                elif "sonnet" in model:
                    return provider_pricing.get("claude-3-sonnet", None)
                elif "opus" in model:
                    return provider_pricing.get("claude-3-opus", None)
            elif "claude-2" in model:
                return provider_pricing.get("claude-2", None)
            elif "claude-instant" in model:
                return provider_pricing.get("claude-instant-1", None)
        
        # If no similar model found, return None
        return None
    
    @staticmethod
    def get_supported_models() -> Dict[str, list]:
        """
        Get a list of all supported models grouped by provider.
        
        Returns:
            Dictionary of providers and their supported models
        """
        return {
            provider: list(models.keys())
            for provider, models in CostCalculator.PRICING.items()
        }
    
    @staticmethod
    def update_pricing(new_pricing: Dict[str, Dict[str, Dict[str, float]]]) -> None:
        """
        Update the pricing data with new information.
        
        Args:
            new_pricing: New pricing data to merge with existing data
        """
        for provider, models in new_pricing.items():
            if provider not in CostCalculator.PRICING:
                CostCalculator.PRICING[provider] = {}
                
            for model, costs in models.items():
                CostCalculator.PRICING[provider][model] = costs
    
    @staticmethod
    def estimate_monthly_cost(
        daily_requests: int,
        avg_prompt_tokens: int,
        avg_completion_tokens: int,
        provider: str,
        model: str
    ) -> float:
        """
        Estimate monthly cost based on usage patterns.
        
        Args:
            daily_requests: Average number of requests per day
            avg_prompt_tokens: Average number of tokens per prompt
            avg_completion_tokens: Average number of tokens per completion
            provider: LLM provider
            model: Model name
            
        Returns:
            Estimated monthly cost in USD
        """
        daily_cost = CostCalculator.calculate_cost(
            provider=provider,
            model=model,
            prompt_tokens=avg_prompt_tokens * daily_requests,
            completion_tokens=avg_completion_tokens * daily_requests
        )
        
        # Multiply by 30 for monthly estimate
        return daily_cost * 30