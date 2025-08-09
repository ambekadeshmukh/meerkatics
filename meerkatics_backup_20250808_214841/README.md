# Meerkatics

<p align="center">
  <img src="docs/images/Meerkatics logo.png" alt="Meerkatics Logo" width="200"/>
</p>

<p align="center">
  <strong>Full observability for AI/LLM systems.</strong><br>
  Metrics, Logs, Insights — Built for DevOps.
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#installation">Installation</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## AI Systems are Black Boxes. Meerkatics gives you full visibility.

AI is taking over the world — but who is watching the AI itself? Meerkatics gives you deep visibility into LLMs and AI Agents: track inference times, memory usage, request success/failure, token costs, and more. Designed for developers, DevOps engineers, and AI teams who want their models to be fast, reliable, and cost-efficient.

- 🚀 **Lightweight agent** - Minimal performance impact
- 📊 **Beautiful Grafana dashboards** - Immediate insights
- 🔥 **Alerts for drift, errors, and hallucinations** - Prevent issues before they impact users

## Features

### Comprehensive Monitoring
- **Performance Metrics**: Inference time, model loading time, queue time, end-to-end latency
- **Resource Utilization**: Memory usage, GPU/CPU utilization, VRAM usage
- **Cost Tracking**: Token counts, API cost calculations, cost attribution by application
- **Reliability Metrics**: Success/failure rates, error types, response timeout rates
- **Quality Insights**: Hallucination detection, response consistency, model drift indicators

### Powerful Dashboard
- Real-time metrics visualization
- Historical trend analysis
- Request/response explorer
- Anomaly detection and alerts
- Cost optimization insights

### Flexible Deployment
- **Self-hosted**: Deploy in your own infrastructure
- **Cloud-agnostic**: Works in AWS, Azure, GCP, or any Kubernetes environment
- **Integration-friendly**: Connects with existing monitoring stacks

### Multi-provider Support
- OpenAI (GPT-3.5, GPT-4, etc.)
- Anthropic (Claude models)
- Hugging Face models
- Self-hosted open-source LLMs
- Custom AI services

## Quick Start

```python
# Install the SDK
pip install meerkatics

# Monitor OpenAI requests
from meerkatics import OpenAIMonitor

# Initialize the monitor
monitor = OpenAIMonitor(
    api_key="your-openai-key",  # Or use OPENAI_API_KEY env var
    model="gpt-4",
    application_name="my-app",
    environment="production"
)

# Make a monitored API call
response = monitor.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about AI monitoring."}
    ]
)

# Use the response as usual
print(response["choices"][0]["message"]["content"])
```

## Installation

### SDK Installation

```bash
pip install meerkatics
```

### Infrastructure Deployment

#### Using Docker Compose (for local development)

```bash
git clone https://github.com/yourusername/meerkatics.git
cd meerkatics/infrastructure
docker-compose up -d
```

#### Using Kubernetes (for production)

```bash
# Add the Meerkatics Helm repository
helm repo add meerkatics https://charts.meerkatics.com

# Install Meerkatics
helm install meerkatics meerkatics/meerkatics \
  --namespace monitoring \
  --create-namespace
```

## Documentation

- [SDK Usage Guide](docs/sdk-usage.md)
- [Installation Guide](docs/installation.md)
- [Configuration Options](docs/configuration.md)
- [API Reference](docs/api-reference.md)
- [Dashboard Guide](docs/dashboard-guide.md)
- [Architecture Overview](docs/architecture.md)
- [Integration Examples](docs/integrations.md)

## Examples

### Basic Monitoring

```python
from meerkatics import AnthropicMonitor

monitor = AnthropicMonitor(
    api_key="your-anthropic-key",
    model="claude-2",
    application_name="customer-support-bot"
)

response = monitor.completion(
    prompt="\n\nHuman: How do I reset my password?\n\nAssistant:",
    max_tokens_to_sample=300
)
```

### Framework Integration

```python
from meerkatics import OpenAIMonitor
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create the monitor
monitor = OpenAIMonitor(
    model="gpt-3.5-turbo",
    application_name="langchain-app"
)

# Create a monitored LangChain LLM
class MonitoredLLM(OpenAI):
    def _call(self, prompt, stop=None, **kwargs):
        response = monitor.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response["choices"][0]["message"]["content"]

# Use it in your LangChain application
llm = MonitoredLLM(temperature=0.7)
prompt = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?"
)
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("eco-friendly water bottles"))
```

More examples can be found in the [examples](examples/) directory.

## Key Performance Insights

Meerkatics provides actionable insights for your AI systems:

- **Cost Optimization**: Identify expensive prompts and inefficient patterns
- **Performance Bottlenecks**: Pinpoint slow queries and optimize response times
- **Reliability Improvements**: Track and reduce error rates
- **Quality Assurance**: Detect model drift and output inconsistencies
- **Capacity Planning**: Understand usage patterns for better resource allocation

## Dashboard Preview

<p align="center">
  <img src="docs/images/dashboard-preview.png" alt="Meerkatics Dashboard" width="800"/>
</p>

## Contributing

We welcome contributions to Meerkatics! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/meerkatics.git
cd meerkatics

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/yourusername/meerkatics/issues): Bug reports and feature requests
- [Documentation](https://docs.meerkatics.com): Comprehensive guides and API reference
- [Discord Community](https://discord.gg/meerkatics): Join our community for help and discussions

---

<p align="center">
  Made with ❤️ by Beka for the AI engineering community
</p>
