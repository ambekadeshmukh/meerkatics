# SentinelOps SDK Usage Guide

This guide provides comprehensive instructions for integrating and using the SentinelOps SDK to monitor your LLM applications.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Provider-Specific Monitors](#provider-specific-monitors)
   - [OpenAI](#openai)
   - [Anthropic](#anthropic)
   - [HuggingFace](#huggingface)
   - [AWS Bedrock](#aws-bedrock)
   - [Google Vertex AI](#google-vertex-ai)
   - [Cohere](#cohere)
   - [Replicate](#replicate)
   - [Azure OpenAI](#azure-openai)
4. [Advanced Features](#advanced-features)
   - [Batching](#batching)
   - [Caching](#caching)
   - [Sampling](#sampling)
   - [Custom Metadata](#custom-metadata)
   - [Error Handling](#error-handling)
5. [Framework Integrations](#framework-integrations)
   - [LangChain](#langchain)
   - [LlamaIndex](#llamaindex)
   - [Haystack](#haystack)
6. [Configuration](#configuration)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting](#troubleshooting)

## Installation

Install the SentinelOps SDK via pip:

```bash
pip install sentinelops
```

For specific Python versions or environments:

```bash
# For specific Python version
python3.8 -m pip install sentinelops

# In a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install sentinelops
```

Verify the installation:

```bash
python -c "import sentinelops; print(sentinelops.__version__)"
```

## Basic Usage

The simplest way to use SentinelOps is with provider-specific monitors:

```python
from sentinelops.providers.openai import OpenAIMonitor

# Initialize the monitor
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",  # Optional, defaults to OPENAI_API_KEY env var
    model="gpt-3.5-turbo",
    application_name="my-application",
    environment="development"
)

# Use the monitor with your existing code
response = monitor.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how can you help me today?"}
    ]
)

# Continue using the response as usual
print(response["choices"][0]["message"]["content"])
```

This will:
1. Initialize a monitor for the specified model and application
2. Send the request to OpenAI's API
3. Collect metrics about the request (tokens, latency, cost)
4. Return the original response from OpenAI

## Provider-Specific Monitors

SentinelOps provides specialized monitors for all major LLM providers.

### OpenAI

```python
from sentinelops.providers.openai import OpenAIMonitor

monitor = OpenAIMonitor(
    api_key="your-openai-api-key",  # Optional
    model="gpt-4",
    application_name="customer-support-bot",
    environment="production"
)

# Chat completions
response = monitor.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like today?"}
    ],
    temperature=0.7,
    max_tokens=100
)

# Text completions
response = monitor.completion(
    prompt="Summarize the following article:",
    max_tokens=200,
    temperature=0.5
)

# Embeddings
response = monitor.embedding(
    input="The quick brown fox jumps over the lazy dog.",
    model="text-embedding-ada-002"  # Override the default model
)
```

### Anthropic

```python
from sentinelops.providers.anthropic import AnthropicMonitor

monitor = AnthropicMonitor(
    api_key="your-anthropic-api-key",  # Optional
    model="claude-2",
    application_name="content-generation"
)

# Claude completion
response = monitor.completion(
    prompt="\n\nHuman: How do I make chocolate chip cookies?\n\nAssistant:",
    max_tokens_to_sample=1000,
    temperature=0.7
)

# Claude messages API
response = monitor.messages(
    messages=[
        {"role": "user", "content": "What are the benefits of meditation?"}
    ],
    max_tokens=1000,
    temperature=0.7
)
```

### HuggingFace

```python
from sentinelops.providers.huggingface import HuggingFaceMonitor

monitor = HuggingFaceMonitor(
    api_key="your-huggingface-api-key",  # Optional
    model="mistralai/Mistral-7B-Instruct-v0.1",
    application_name="text-generation"
)

# Text generation
response = monitor.text_generation(
    prompt="Write a short story about a robot that discovers emotions:",
    max_new_tokens=250,
    temperature=0.8
)

# Chat completion (for chat models)
response = monitor.chat_completion(
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    max_new_tokens=200,
    temperature=0.7
)
```

### AWS Bedrock

```python
from sentinelops.providers.bedrock import BedrockMonitor

monitor = BedrockMonitor(
    model="anthropic.claude-v2",  # Or "amazon.titan-text", "ai21.j2-ultra", etc.
    application_name="financial-advisor",
    region_name="us-east-1"  # Optional
)

# Using Anthropic's Claude on Bedrock
response = monitor.completion(
    prompt="\n\nHuman: What investment strategies work best during inflation?\n\nAssistant:",
    max_tokens_to_sample=500,
    temperature=0.7
)

# Using Amazon Titan
response = monitor.text_generation(
    prompt="Explain the benefits of cloud computing:",
    max_tokens=200
)
```

### Google Vertex AI

```python
from sentinelops.providers.vertex import VertexAIMonitor

monitor = VertexAIMonitor(
    model="gemini-pro",  # or "text-bison", "chat-bison", etc.
    application_name="product-descriptions",
    project_id="your-gcp-project-id",  # Optional
    location="us-central1"  # Optional
)

# Text generation with Gemini
response = monitor.text_generation(
    prompt="Write a product description for a smart water bottle:",
    max_output_tokens=200,
    temperature=0.7
)

# Chat completion with Gemini
response = monitor.chat_completion(
    messages=[
        {"role": "user", "content": "Suggest names for my tech startup focusing on AI healthcare"}
    ],
    max_output_tokens=150,
    temperature=0.8
)
```

### Cohere

```python
from sentinelops.providers.cohere import CohereMonitor

monitor = CohereMonitor(
    api_key="your-cohere-api-key",  # Optional
    model="command",  # or "command-light", "command-nightly", etc.
    application_name="search-enhancement"
)

# Generate text
response = monitor.generate(
    prompt="Write a blog introduction about space exploration:",
    max_tokens=250,
    temperature=0.75
)

# Get embeddings
response = monitor.embed(
    texts=["This is a document about space exploration", "This is about healthcare"],
    model="embed-english-v2.0"  # Optional
)
```

### Replicate

```python
from sentinelops.providers.replicate import ReplicateMonitor

monitor = ReplicateMonitor(
    api_token="your-replicate-api-token",  # Optional
    model="meta/llama-2-70b-chat",
    application_name="creative-writing"
)

# Run a model
response = monitor.run(
    prompt="Write a short sci-fi story about AI:",
    input_params={
        "max_length": 500,
        "temperature": 0.75,
        "top_p": 0.9
    }
)
```

### Azure OpenAI

```python
from sentinelops.providers.azure_openai import AzureOpenAIMonitor

monitor = AzureOpenAIMonitor(
    api_key="your-azure-openai-api-key",  # Optional
    endpoint="https://your-resource-name.openai.azure.com",
    deployment_name="your-deployment-name",
    api_version="2023-05-15",
    application_name="document-summarization"
)

# Chat completions
response = monitor.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Summarize the key points from the last meeting"}
    ],
    temperature=0.5,
    max_tokens=300
)

# Embeddings
response = monitor.embedding(
    input="The quarterly financial report shows promising results.",
    deployment_name="text-embedding-ada-002"  # Optional, overrides the default
)
```

## Advanced Features

### Batching

For high-volume applications, enable batching to reduce API overhead:

```python
from sentinelops.providers.openai import OpenAIMonitor

monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="high-volume-app",
    
    # Enable batching
    enable_batching=True,
    batch_size=10,        # Send metrics in batches of 10
    flush_interval=5.0    # Or after 5 seconds, whichever comes first
)

# Use the monitor as usual
# Metrics will be sent in batches rather than individually
```

To manually flush the batch (e.g., before application shutdown):

```python
# Ensure all pending metrics are sent
monitor.batch_processor.flush()
```

### Caching

Reduce duplicate API calls with caching:

```python
from sentinelops.providers.openai import OpenAIMonitor

monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="caching-app",
    
    # Enable caching
    enable_caching=True,
    cache_ttl=3600,        # Cache responses for 1 hour
    cache_max_size=1000,   # Store up to 1000 responses
    disk_cache=True,       # Persist cache to disk
    cache_dir="./cache"    # Optional cache directory
)

# Identical requests will be served from cache if within TTL
```

### Sampling

For very high-volume applications, enable sampling to reduce monitoring overhead:

```python
from sentinelops.providers.openai import OpenAIMonitor

monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="very-high-volume-app",
    
    # Enable sampling
    sampling_rate=0.1  # Monitor 10% of requests
)

# Only 10% of requests will be monitored, but all will be processed
```

### Custom Metadata

Add custom metadata to provide context for monitored requests:

```python
from sentinelops.providers.openai import OpenAIMonitor

monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="custom-metadata-app"
)

# Add custom metadata to a specific request
response = monitor.chat_completion(
    messages=[
        {"role": "user", "content": "Summarize this document"}
    ],
    metadata={
        "user_id": "user-123",
        "session_id": "session-456",
        "document_id": "doc-789",
        "feature": "document-summarization",
        "importance": "high"
    }
)
```

### Error Handling

SentinelOps captures API errors automatically while allowing you to handle them:

```python
from sentinelops.providers.openai import OpenAIMonitor
import openai

monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="error-handling-app"
)

try:
    # This will throw an error if the API request fails
    response = monitor.chat_completion(
        messages=[
            {"role": "user", "content": "Tell me about this image"}
        ]
    )
except openai.error.InvalidRequestError as e:
    # The error will be monitored automatically
    print(f"Invalid request: {str(e)}")
    # Implement fallback logic here
except Exception as e:
    print(f"Other error: {str(e)}")
```

## Framework Integrations

### LangChain

Integrate SentinelOps with LangChain:

```python
from sentinelops.integrations.langchain import MonitoredLLM, MonitoredChatModel
from sentinelops.providers.openai import OpenAIMonitor
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Create a SentinelOps monitor
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="langchain-app"
)

# Create monitored LangChain models
llm = MonitoredLLM(
    llm=OpenAI(temperature=0.7),
    monitor=monitor
)

chat_model = MonitoredChatModel(
    chat_model=ChatOpenAI(temperature=0.7),
    monitor=monitor
)

# Use in LangChain as normal
prompt = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?"
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("eco-friendly water bottles")
print(result)
```

### LlamaIndex

Integrate SentinelOps with LlamaIndex:

```python
from sentinelops.integrations.llamaindex import monitor_llamaindex
from sentinelops.providers.openai import OpenAIMonitor
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms import OpenAI

# Create a SentinelOps monitor
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="llamaindex-app"
)

# Create a LlamaIndex LLM
llm = OpenAI(model="gpt-3.5-turbo")

# Monitor the LLM
monitored_llm = monitor_llamaindex(llm, monitor)

# Use in LlamaIndex as normal
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents, llm=monitored_llm)
query_engine = index.as_query_engine()
response = query_engine.query("What are the key points in the document?")
print(response)
```

### Haystack

Integrate SentinelOps with Haystack:

```python
from sentinelops.integrations.haystack import MonitoredGenerator
from sentinelops.providers.openai import OpenAIMonitor
from haystack.nodes import PromptNode
from haystack.pipelines import Pipeline

# Create a SentinelOps monitor
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="haystack-app"
)

# Create a monitored PromptNode
prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo",
    api_key="your-openai-api-key"
)

monitored_node = MonitoredGenerator(
    generator=prompt_node,
    monitor=monitor
)

# Use in Haystack pipeline as normal
pipeline = Pipeline()
pipeline.add_node(component=monitored_node, name="generator", inputs=["Query"])
result = pipeline.run(query="How does photosynthesis work?")
print(result)
```

## Configuration

### Environment Variables

SentinelOps SDK can be configured using environment variables:

```bash
# API configuration
export SENTINELOPS_API_URL="https://your-sentinelops-instance.com/api"
export SENTINELOPS_API_KEY="your-api-key"

# Provider API keys
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export HUGGINGFACE_API_KEY="your-huggingface-api-key"
export COHERE_API_KEY="your-cohere-api-key"
export REPLICATE_API_TOKEN="your-replicate-api-token"

# Optional configuration
export SENTINELOPS_ENVIRONMENT="production"
export SENTINELOPS_SAMPLING_RATE="1.0"
export SENTINELOPS_ENABLE_BATCHING="true"
export SENTINELOPS_BATCH_SIZE="10"
export SENTINELOPS_FLUSH_INTERVAL="5.0"
export SENTINELOPS_ENABLE_CACHING="false"
```

### Configuration File

For more advanced configuration, create a `sentinelops.yaml` file in your project directory:

```yaml
# sentinelops.yaml
api:
  url: "https://your-sentinelops-instance.com/api"
  key: "your-api-key"

application:
  name: "my-application"
  environment: "production"
  version: "1.0.0"

monitoring:
  enabled: true
  sampling_rate: 1.0
  log_requests: true
  log_responses: true
  
batching:
  enabled: true
  batch_size: 10
  flush_interval: 5.0
  
caching:
  enabled: false
  ttl: 3600
  max_size: 1000
  disk_cache: false
  
providers:
  openai:
    api_key: "your-openai-api-key"
  anthropic:
    api_key: "your-anthropic-api-key"
```

Load the configuration file in your code:

```python
from sentinelops import load_config
from sentinelops.providers.openai import OpenAIMonitor

# Load config from sentinelops.yaml
load_config()

# Create a monitor using the loaded config
monitor = OpenAIMonitor(
    model="gpt-4",
    # Other settings from config file will be applied automatically
)
```

### Programmatic Configuration

Configure SentinelOps programmatically:

```python
from sentinelops import configure
from sentinelops.providers.openai import OpenAIMonitor

# Configure globally
configure(
    api_url="https://your-sentinelops-instance.com/api",
    api_key="your-api-key",
    environment="production",
    enable_batching=True,
    batch_size=10,
    sampling_rate=1.0
)

# Create a monitor using the global config
monitor = OpenAIMonitor(
    model="gpt-4",
    application_name="my-app"
)
```

## Performance Considerations

### Overhead

The SentinelOps SDK is designed to add minimal overhead to your LLM requests:

- Typical latency overhead: <10ms per request
- Memory overhead: Negligible (<1MB)
- CPU overhead: Negligible (<1% of a single core)

### Optimizations

For high-performance applications:

1. **Enable batching**: Reduces network overhead for telemetry data.
   ```python
   monitor = OpenAIMonitor(
       # ... other settings
       enable_batching=True,
       batch_size=20  # Adjust based on request volume
   )
   ```

2. **Use sampling**: Reduce monitoring overhead in high-volume applications.
   ```python
   monitor = OpenAIMonitor(
       # ... other settings
       sampling_rate=0.1  # Monitor 10% of requests
   )
   ```

3. **Async support**: Use async methods for non-blocking operations.
   ```python
   # Async example
   from sentinelops.providers.openai import AsyncOpenAIMonitor
   
   monitor = AsyncOpenAIMonitor(
       api_key="your-openai-api-key",
       model="gpt-3.5-turbo"
   )
   
   # Use in async code
   response = await monitor.chat_completion(
       messages=[{"role": "user", "content": "Hello"}]
   )
   ```

4. **Local processing**: Use local mode for development environments.
   ```python
   monitor = OpenAIMonitor(
       # ... other settings
       local_mode=True  # Don't send telemetry to SentinelOps backend
   )
   ```

## Troubleshooting

### Common Issues

#### Connection Errors

**Problem**: SDK cannot connect to SentinelOps backend.

**Solution**:
1. Verify API URL and key:
   ```python
   from sentinelops import test_connection
   
   success, message = test_connection(
       api_url="https://your-sentinelops-instance.com/api",
       api_key="your-api-key"
   )
   print(message)
   ```

2. Check network connectivity and firewall settings.

3. Ensure the SentinelOps backend is running.

#### Missing Metrics

**Problem**: Metrics are not appearing in the dashboard.

**Solution**:
1. Verify the request was successful:
   ```python
   response = monitor.chat_completion(
       messages=[{"role": "user", "content": "Hello"}],
       debug=True  # Enables debug logging
   )
   ```

2. Check batching configuration:
   ```python
   # Manually flush pending metrics
   monitor.batch_processor.flush()
   ```

3. Check sampling configuration:
   ```python
   # Ensure sampling rate is not too low
   monitor = OpenAIMonitor(
       # ... other settings
       sampling_rate=1.0  # Monitor 100% of requests
   )
   ```

#### API Provider Errors

**Problem**: Errors when making API requests to LLM providers.

**Solution**:
1. Verify API keys:
   ```python
   import openai
   openai.api_key = "your-openai-api-key"
   
   # Test direct API access
   try:
       openai.ChatCompletion.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "Hello"}]
       )
       print("API access working correctly")
   except Exception as e:
       print(f"API error: {str(e)}")
   ```

2. Check the provider's service status.

3. Review the provider's API documentation for changes.

#### Missing Dependencies

**Problem**: Import errors or missing dependencies.

**Solution**:
1. Install the required provider package:
   ```bash
   # For OpenAI
   pip install openai
   
   # For Anthropic
   pip install anthropic
   
   # For other providers
   pip install huggingface_hub cohere replicate boto3 google-cloud-aiplatform
   ```

2. Install the full SentinelOps package with all dependencies:
   ```bash
   pip install "sentinelops[all]"
   ```

### Debugging

Enable debug logging for more visibility:

```python
import logging
from sentinelops import configure_logging

# Set up logging
configure_logging(level=logging.DEBUG)

# Create monitor and use as normal
monitor = OpenAIMonitor(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
    application_name="debugging-app"
)
```

Use the diagnostics tool to verify your setup:

```python
from sentinelops.diagnostics import run_diagnostics

# Run comprehensive diagnostics
results = run_diagnostics(
    api_url="https://your-sentinelops-instance.com/api",
    api_key="your-api-key"
)

# Print detailed results
print(results.summary())
```

### Getting Help

If you're still experiencing issues:

1. Check the [SentinelOps Documentation](https://docs.sentinelops.com) for detailed guides.
2. Visit the [GitHub repository](https://github.com/sentinelops/sentinelops) to search for known issues.
3. Join our [Discord community](https://discord.gg/sentinelops) for community support.
4. For enterprise support, contact [support@sentinelops.com](mailto:support@sentinelops.com).

## Next Steps

- Explore the [Dashboard Guide](./dashboard-guide.md) to visualize your monitoring data.
- Learn about [Advanced Integrations](./advanced-integrations.md) for specialized use cases.
- Discover [Custom Monitoring](./custom-monitoring.md) for non-standard LLMs and scenarios.