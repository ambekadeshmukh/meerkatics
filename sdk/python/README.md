# Meerkatics Python SDK

## 🔍 Superior AI Monitoring and Observability

Meerkatics provides comprehensive monitoring and observability for your AI and Large Language Model (LLM) applications. Get real-time insights into performance, cost, quality, and security - all with minimal setup.

### ✨ Key Features

- **🚀 Auto-Instrumentation**: Zero-code monitoring for all major LLM providers
- **🔒 Security Monitoring**: Built-in PII detection and prompt injection protection  
- **🧠 Hallucination Detection**: Advanced multi-modal analysis to catch AI hallucinations
- **💰 Cost Optimization**: Real-time cost tracking and optimization recommendations
- **📊 Real-time Dashboards**: Live monitoring with WebSocket updates
- **🔧 Developer-First**: Superior DX that beats enterprise solutions

### 🏢 Supported Providers

| Provider | Models | Status |
|----------|--------|---------|
| **OpenAI** | GPT-4, GPT-3.5, Embeddings, DALL-E | ✅ Full Support |
| **Anthropic** | Claude 3, Claude 2, Claude Instant | ✅ Full Support |
| **Google** | Gemini Pro, PaLM | ✅ Full Support |
| **AWS Bedrock** | Claude, Titan, Llama | ✅ Full Support |
| **Azure OpenAI** | All Azure OpenAI models | ✅ Full Support |
| **Cohere** | Command, Embed | ✅ Full Support |
| **Hugging Face** | Inference API + Local models | ✅ Full Support |

### 🛠️ Framework Integrations

- **LangChain**: Automatic chain monitoring
- **LlamaIndex**: Query engine monitoring  
- **Streamlit**: Built-in dashboard integration
- **FastAPI**: Middleware for API monitoring

## 🚀 Quick Start

### Installation

```bash
pip install meerkatics

# Or install with all provider dependencies
pip install "meerkatics[all]"

# Or install specific providers
pip install "meerkatics[openai,anthropic]"
```

### Auto-Instrumentation (Easiest)

```python
import meerkatics

# Auto-instrument all LLM libraries
monitor = meerkatics.auto_monitor(api_key="mk_your_api_key_here")

# Now all OpenAI, Anthropic, etc. calls are automatically monitored
import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Explicit Monitoring

```python
import meerkatics

# Create monitor with configuration
monitor = meerkatics.MeerkaticsMonitor(
    api_key="mk_your_api_key_here",
    application="my-chatbot",
    environment="production",
    enable_security_monitoring=True,
    enable_hallucination_detection=True
)

# Get monitored clients
openai_client = monitor.get_openai_client()
anthropic_client = monitor.get_anthropic_client()

# Use them normally - monitoring happens automatically
response = openai_client.create_chat_completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
```

### Provider-Specific Monitoring

```python
import meerkatics

# OpenAI
openai_client = meerkatics.track_openai(
    meerkatics_api_key="mk_your_key"
)

# Anthropic  
anthropic_client = meerkatics.track_anthropic(
    meerkatics_api_key="mk_your_key"
)

# Google
google_client = meerkatics.track_google(
    meerkatics_api_key="mk_your_key"
)
```

## 🔧 Advanced Configuration

### Security & Privacy

```python
monitor = meerkatics.MeerkaticsMonitor(
    api_key="mk_your_key",
    
    # Privacy settings
    redact_prompts=True,          # Redact PII from prompts
    redact_responses=True,        # Redact PII from responses
    auto_detect_pii=True,         # Automatic PII detection
    
    # Security monitoring
    enable_security_monitoring=True,
    detect_prompt_injection=True,
    
    # Performance settings
    buffer_size=100,              # Batch size for sending events
    flush_interval=30,            # Seconds between flushes
    retry_attempts=3,             # Retry failed requests
    
    # Metadata
    user_id="user_123",
    session_id="session_456",
    metadata={"team": "ai-research", "experiment": "v2.1"}
)
```

### Custom LLM Tracking

```python
# Track any custom LLM or local model
monitor.track_custom_llm(
    provider="ollama",
    model="llama2-7b",
    prompt="What is machine learning?",
    response="Machine learning is a subset of AI...",
    usage={'prompt_tokens': 10, 'completion_tokens': 50, 'total_tokens': 60},
    latency_ms=1200,
    cost=0.0,  # Free local model
    metadata={"local": True, "gpu": "RTX-4090"}
)
```

## 🎯 Framework Integrations

### LangChain Integration

```python
from langchain.callbacks import CallbackManager
from langchain.llms import OpenAI
import meerkatics

# Create monitor and callback
monitor = meerkatics.MeerkaticsMonitor(api_key="mk_your_key")
callback = meerkatics.MeerkaticsLangChainCallback(monitor)

# Use with LangChain
llm = OpenAI(
    callback_manager=CallbackManager([callback]),
    temperature=0.7
)

response = llm("Tell me about AI monitoring")
```

### LlamaIndex Integration

```python
from llama_index.core import Settings
import meerkatics

# Create monitor and callback
monitor = meerkatics.MeerkaticsMonitor(api_key="mk_your_key")
callback = meerkatics.MeerkaticsLlamaIndexCallback(monitor)

# Configure LlamaIndex
Settings.callback_manager.add_handler(callback)

# Use LlamaIndex normally - monitoring happens automatically
```

### Streamlit Integration

```python
import streamlit as st
import meerkatics

# Create monitor and Streamlit integration
monitor = meerkatics.MeerkaticsMonitor(api_key="mk_your_key")
streamlit_integration = meerkatics.MeerkaticsStreamlitIntegration(monitor)

# Add monitoring sidebar to your Streamlit app
streamlit_integration.display_metrics_sidebar()

# Create full monitoring dashboard
streamlit_integration.create_monitoring_dashboard()
```

## 📊 Monitoring Features

### Real-time Metrics
- Request volume and rate
- Latency percentiles (p50, p95, p99)
- Error rates and types
- Cost tracking and attribution
- Token usage patterns

### Quality Analysis
- Hallucination detection with confidence scores
- Response quality scoring
- Semantic consistency checking
- Factual verification against knowledge bases

### Security Monitoring
- PII detection in prompts and responses
- Prompt injection attempt detection
- Data leak prevention
- Unauthorized access monitoring

### Cost Optimization
- Real-time cost tracking per request
- Cost breakdown by model, application, user
- Optimization recommendations
- Budget alerts and spending limits

## 🔧 CLI Usage

```bash
# Test monitoring setup
meerkatics test --api-key mk_your_key --provider openai --model gpt-4

# Get statistics
meerkatics stats --api-key mk_your_key --time-range 24h

# View recent requests
meerkatics recent --provider openai --limit 10

# Initialize configuration
meerkatics init --output config.json
```

## 🏗️ Environment Variables

```bash
# Meerkatics configuration
export MEERKATICS_API_KEY="mk_your_api_key_here"
export MEERKATICS_BASE_URL="https://api.meerkatics.com"
export MEERKATICS_APPLICATION="my-app"
export MEERKATICS_ENVIRONMENT="production"

# Provider API keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key" 
export GOOGLE_API_KEY="your-google-key"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📚 [Documentation](https://docs.meerkatics.com)
- 💬 [Discord Community](https://discord.gg/meerkatics)
- 🐛 [Bug Reports](https://github.com/meerkatics/meerkatics/issues)
- 📧 [Email Support](mailto:support@meerkatics.com)

---

**Built with ❤️ by the Meerkatics Team**