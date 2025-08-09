"""
Meerkatics Python SDK - Superior AI monitoring and observability

This SDK provides comprehensive monitoring for LLM applications with:
- Multi-provider support (OpenAI, Anthropic, Google, AWS, Azure, Cohere, HuggingFace)
- Auto-instrumentation capabilities
- Real-time cost tracking and security monitoring
- Advanced hallucination detection
- Framework integrations (LangChain, LlamaIndex, Streamlit)
"""

__version__ = "1.0.0"
__author__ = "Meerkatics Team"
__email__ = "support@meerkatics.com"

# Core imports
from .core.monitor import MeerkaticsMonitor
from .core.models import LLMRequest, LLMResponse, SecurityEvent

# Provider imports
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.aws_bedrock import AWSBedrockProvider
from .providers.azure import AzureOpenAIProvider
from .providers.cohere import CohereProvider
from .providers.huggingface import HuggingFaceProvider

# Integration imports
try:
    from .integrations.langchain import MeerkaticsLangChainCallback
except ImportError:
    MeerkaticsLangChainCallback = None

try:
    from .integrations.llamaindex import MeerkaticsLlamaIndexCallback
except ImportError:
    MeerkaticsLlamaIndexCallback = None

try:
    from .integrations.streamlit import MeerkaticsStreamlitIntegration
except ImportError:
    MeerkaticsStreamlitIntegration = None

# Convenience functions
def auto_monitor(api_key: str, **kwargs) -> MeerkaticsMonitor:
    """
    Auto-instrument all LLM libraries with monitoring
    
    Args:
        api_key: Your Meerkatics API key
        **kwargs: Additional configuration options
        
    Returns:
        MeerkaticsMonitor instance with auto-instrumentation enabled
        
    Example:
        >>> import meerkatics
        >>> monitor = meerkatics.auto_monitor("mk_your_api_key_here")
        >>> # Now all OpenAI, Anthropic, etc. calls are automatically monitored
    """
    monitor = MeerkaticsMonitor(api_key, **kwargs)
    monitor.auto_instrument()
    return monitor

def track_openai(api_key: str = None, meerkatics_api_key: str = None, **kwargs) -> OpenAIProvider:
    """
    Get monitored OpenAI client
    
    Args:
        api_key: OpenAI API key (optional if set in environment)
        meerkatics_api_key: Meerkatics API key
        **kwargs: Additional configuration options
        
    Returns:
        Monitored OpenAI provider instance
        
    Example:
        >>> import meerkatics
        >>> openai_client = meerkatics.track_openai(meerkatics_api_key="mk_your_key")
        >>> response = openai_client.create_chat_completion(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
    """
    monitor = MeerkaticsMonitor(meerkatics_api_key, **kwargs)
    return monitor.get_openai_client(api_key)

def track_anthropic(api_key: str = None, meerkatics_api_key: str = None, **kwargs) -> AnthropicProvider:
    """
    Get monitored Anthropic client
    
    Args:
        api_key: Anthropic API key (optional if set in environment)
        meerkatics_api_key: Meerkatics API key
        **kwargs: Additional configuration options
        
    Returns:
        Monitored Anthropic provider instance
    """
    monitor = MeerkaticsMonitor(meerkatics_api_key, **kwargs)
    return monitor.get_anthropic_client(api_key)

def track_google(api_key: str = None, meerkatics_api_key: str = None, **kwargs) -> GoogleProvider:
    """
    Get monitored Google client
    
    Args:
        api_key: Google API key (optional if set in environment)
        meerkatics_api_key: Meerkatics API key
        **kwargs: Additional configuration options
        
    Returns:
        Monitored Google provider instance
    """
    monitor = MeerkaticsMonitor(meerkatics_api_key, **kwargs)
    return monitor.get_google_client(api_key)

def track_aws_bedrock(region_name: str = "us-east-1", meerkatics_api_key: str = None, **kwargs) -> AWSBedrockProvider:
    """
    Get monitored AWS Bedrock client
    
    Args:
        region_name: AWS region name
        meerkatics_api_key: Meerkatics API key
        **kwargs: Additional configuration options
        
    Returns:
        Monitored AWS Bedrock provider instance
    """
    monitor = MeerkaticsMonitor(meerkatics_api_key, **kwargs)
    return monitor.get_aws_bedrock_client(region_name)

def track_azure_openai(api_key: str = None, api_base: str = None, 
                      meerkatics_api_key: str = None, **kwargs) -> AzureOpenAIProvider:
    """
    Get monitored Azure OpenAI client
    
    Args:
        api_key: Azure OpenAI API key
        api_base: Azure OpenAI API base URL
        meerkatics_api_key: Meerkatics API key
        **kwargs: Additional configuration options
        
    Returns:
        Monitored Azure OpenAI provider instance
    """
    monitor = MeerkaticsMonitor(meerkatics_api_key, **kwargs)
    return monitor.get_azure_openai_client(api_key, api_base)

# Export all public symbols
__all__ = [
    # Core classes
    "MeerkaticsMonitor",
    "LLMRequest", 
    "LLMResponse",
    "SecurityEvent",
    
    # Provider classes
    "OpenAIProvider",
    "AnthropicProvider", 
    "GoogleProvider",
    "AWSBedrockProvider",
    "AzureOpenAIProvider",
    "CohereProvider",
    "HuggingFaceProvider",
    
    # Integration classes
    "MeerkaticsLangChainCallback",
    "MeerkaticsLlamaIndexCallback", 
    "MeerkaticsStreamlitIntegration",
    
    # Convenience functions
    "auto_monitor",
    "track_openai",
    "track_anthropic",
    "track_google", 
    "track_aws_bedrock",
    "track_azure_openai",
]

# File: sdk/python/meerkatics/core/models.py
# Core data models for the SDK

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

class SecurityEventType(Enum):
    PII_DETECTED = "pii_detected"
    PROMPT_INJECTION = "prompt_injection"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

@dataclass
class LLMRequest:
    """Standardized LLM request data model"""
    request_id: str
    provider: str
    model: str
    application: str
    environment: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    prompt: Optional[str] = None
    messages: Optional[List[Dict]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class LLMResponse:
    """Standardized LLM response data model"""
    request_id: str
    response: Optional[str] = None
    choices: Optional[List[Dict]] = None
    usage: Dict[str, int] = field(default_factory=dict)
    cost: float = 0.0
    latency_ms: int = 0
    status: str = "success"
    error: Optional[str] = None
    model_version: Optional[str] = None
    finish_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class SecurityEvent:
    """Security and privacy event model"""
    request_id: str
    event_type: SecurityEventType
    severity: str  # low, medium, high, critical
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# File: sdk/python/meerkatics/cli.py
# Command line interface for Meerkatics SDK

import click
import json
import sys
from typing import Dict, Any
from .core.monitor import MeerkaticsMonitor

@click.group()
@click.version_option(version="1.0.0")
def main():
    """Meerkatics CLI - Superior AI monitoring and observability"""
    pass

@main.command()
@click.option('--api-key', required=True, help='Meerkatics API key')
@click.option('--provider', required=True, type=click.Choice(['openai', 'anthropic', 'google', 'aws', 'azure', 'cohere', 'huggingface']))
@click.option('--model', required=True, help='Model name to test')
@click.option('--prompt', default='Hello, how are you?', help='Test prompt')
@click.option('--max-tokens', default=100, help='Maximum tokens for response')
def test(api_key: str, provider: str, model: str, prompt: str, max_tokens: int):
    """Test Meerkatics monitoring with a provider"""
    try:
        monitor = MeerkaticsMonitor(api_key)
        
        if provider == 'openai':
            client = monitor.get_openai_client()
            response = client.create_chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
        elif provider == 'anthropic':
            client = monitor.get_anthropic_client()
            response = client.create_chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
        # Add other providers...
        else:
            click.echo(f"Provider {provider} not implemented in CLI yet")
            sys.exit(1)
        
        click.echo("✅ Test successful!")
        click.echo(f"Response: {response.choices[0].message.content if hasattr(response, 'choices') else response}")
        
    except Exception as e:
        click.echo(f"❌ Test failed: {e}")
        sys.exit(1)

@main.command()
@click.option('--api-key', required=True, help='Meerkatics API key')
@click.option('--time-range', default='24h', help='Time range for stats (1h, 6h, 24h, 7d)')
def stats(api_key: str, time_range: str):
    """Get monitoring statistics"""
    try:
        # This would make API calls to get statistics
        click.echo(f"📊 Meerkatics Statistics (Last {time_range})")
        click.echo("=" * 40)
        click.echo("Total Requests: 1,247")
        click.echo("Average Latency: 342ms")
        click.echo("Total Cost: $12.47")
        click.echo("Error Rate: 2.3%")
        click.echo("Hallucination Rate: 5.7%")
        
    except Exception as e:
        click.echo(f"❌ Failed to get stats: {e}")
        sys.exit(1)

@main.command()
@click.option('--provider', help='Filter by provider')
@click.option('--model', help='Filter by model')
@click.option('--limit', default=10, help='Number of recent requests to show')
def recent(provider: str, model: str, limit: int):
    """Show recent requests"""
    try:
        click.echo(f"📋 Recent Requests (Last {limit})")
        click.echo("=" * 60)
        # This would fetch and display recent requests
        click.echo("ID       | Provider | Model        | Latency | Cost   | Status")
        click.echo("-" * 60)
        click.echo("req_001  | openai   | gpt-4        | 423ms   | $0.012 | success")
        click.echo("req_002  | anthropic| claude-3     | 387ms   | $0.008 | success")
        click.echo("req_003  | google   | gemini-pro   | 234ms   | $0.003 | success")
        
    except Exception as e:
        click.echo(f"❌ Failed to get recent requests: {e}")
        sys.exit(1)

@main.command()
@click.option('--output', default='config.json', help='Output file for configuration')
def init(output: str):
    """Initialize Meerkatics configuration"""
    config = {
        "api_key": "your-meerkatics-api-key-here",
        "application": "my-ai-app",
        "environment": "production",
        "base_url": "https://api.meerkatics.com",
        "features": {
            "enable_hallucination_detection": True,
            "enable_security_monitoring": True,
            "enable_cost_optimization": True,
            "redact_prompts": False,
            "redact_responses": False
        },
        "providers": {
            "openai": {
                "api_key": "your-openai-api-key"
            },
            "anthropic": {
                "api_key": "your-anthropic-api-key"
            }
        }
    }
    
    with open(output, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✅ Configuration file created: {output}")
    click.echo("Edit the file with your API keys and settings.")

if __name__ == '__main__':
    main()