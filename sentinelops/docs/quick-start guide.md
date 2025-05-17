# SentinelOps Quick Start Guide

SentinelOps is a comprehensive observability platform for LLM applications. It provides monitoring, metrics collection, and visualization for all major LLM providers.

## Table of Contents

1. [Installation](#installation)
2. [Core Components](#core-components)
3. [Python SDK Integration](#python-sdk-integration)
4. [Monitoring Dashboard](#monitoring-dashboard)
5. [Configuring Alerts](#configuring-alerts)
6. [Deployment Options](#deployment-options)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Git

### Quick Setup

Clone the repository:

```bash
git clone https://github.com/your-username/sentinelops.git
cd sentinelops
```

Run the quick deployment script (Mac/Linux):

```bash
./infrastructure/scripts/quick-deploy.sh
```

This will:
- Set up the environment
- Create configuration files
- Launch all services via Docker Compose
- Check service health

After installation, access:
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- Prometheus: http://localhost:9090

## Core Components

SentinelOps consists of the following components:

- Python SDK: Integrates with your LLM applications to collect metrics
- Data Processor: Processes and enriches monitoring data
- API Server: Provides REST API for querying metrics and configurations
- Dashboard: Web UI for visualizing metrics and setting up alerts
- Metrics Storage: PostgreSQL database for metrics storage
- Message Queue: Kafka for reliable message processing

## Python SDK Integration

### Installation

```bash
pip install sentinelops
```

### Basic Usage

```python
from sentinelops.providers.openai import OpenAIMonitor

# Initialize the monitor
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="my-application"
)

# Use it to make API calls
response = monitor.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response['choices'][0]['message']['content'])
```

### Supporting Additional LLM Providers

SentinelOps supports all major LLM providers:

#### Anthropic (Claude)

```python
from sentinelops.providers.anthropic import AnthropicMonitor

monitor = AnthropicMonitor(
    api_key="your-anthropic-api-key",
    model="claude-2",
    application_name="my-application"
)

response = monitor.completion(
    prompt="\n\nHuman: Hello, how are you?\n\nAssistant:",
    max_tokens_to_sample=100
)
```

#### HuggingFace

```python
from sentinelops.providers.huggingface import HuggingFaceMonitor

monitor = HuggingFaceMonitor(
    api_key="your-huggingface-api-key",
    model="gpt2",
    application_name="my-application"
)

response = monitor.text_generation(
    prompt="Hello, how are you?"
)
```

#### AWS Bedrock

```python
from sentinelops.providers.bedrock import BedrockMonitor

monitor = BedrockMonitor(
    model="anthropic.claude-v2",
    application_name="my-application"
)

response = monitor.completion(
    prompt="\n\nHuman: Hello, how are you?\n\nAssistant:",
    max_tokens_to_sample=100
)
```

#### Google Vertex AI

```python
from sentinelops.providers.vertex import VertexAIMonitor

monitor = VertexAIMonitor(
    model="gemini-pro",
    application_name="my-application",
    project_id="your-gcp-project-id"
)

response = monitor.text_generation(
    prompt="Hello, how are you?"
)
```

## Advanced Features

### Batching

For high-volume applications, enable batching to reduce overhead:

```python
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="my-application",
    enable_batching=True,
    batch_size=10,
    flush_interval=5.0
)
```

### Caching

Enable caching to reduce duplicate API calls:

```python
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="my-application",
    enable_caching=True,
    cache_ttl=3600,  # 1 hour
    disk_cache=True
)
```

## Monitoring Dashboard

The SentinelOps dashboard provides:

- Cost breakdown by provider, model, and application
- Performance metrics (latency, token usage, request volume)
- Hallucination detection metrics and examples
- Alert management and configuration

### Dashboard Navigation

- Home: Overview of key metrics
- Cost: Detailed cost analysis and optimization recommendations
- Performance: Latency, throughput, and error rate metrics
- Quality: Hallucination detection and content quality metrics
- Prompts: Prompt analytics and optimization
- Alerts: Alert configuration and history
- Settings: System configuration

## Configuring Alerts

SentinelOps provides flexible alerting for various metrics:

1. Go to the Alerts page
2. Click Create Alert
3. Configure alert parameters:

- Name: Descriptive name
- Type: Cost, Performance, Error Rate, Quality, Hallucination
- Severity: Low, Medium, High, Critical
- Thresholds: Metric value thresholds
- Filters: Limit to specific providers, models, applications
- Notifications: Email recipients

### Example alert configurations:

- Cost Spike: Alert when hourly cost exceeds $5
- High Latency: Alert when P95 latency exceeds 2000ms
- Error Rate: Alert when error rate exceeds 5%
- Hallucination Rate: Alert when hallucination rate exceeds 10%

## Deployment Options

### Local Development

```bash
./infrastructure/scripts/quick-deploy.sh
```

### AWS Deployment

```bash
./infrastructure/aws/deploy.sh
```

This script will:
1. Prompt for deployment parameters
2. Create CloudFormation stack
3. Deploy SentinelOps on EC2
4. Configure security and networking

Kubernetes Deployment
For production environments, Kubernetes deployment is recommended:
bash# Install Helm chart
helm install sentinelops ./infrastructure/kubernetes/chart
Troubleshooting
Common Issues
Issue: Services fail to start
Solution: Check Docker logs:
bashdocker-compose -f infrastructure/docker-compose.yml logs
Issue: SDK not sending metrics
Solution:

Check Kafka connection in SDK configuration
Verify network connectivity to SentinelOps server
Check data-processor logs

Issue: Dashboard shows no data
Solution:

Check if API server is running
Verify database connection
Check if metrics are being collected

Getting Help

GitHub Issues: https://github.com/your-username/sentinelops/issues
Documentation: https://sentinelops.readthedocs.io/

