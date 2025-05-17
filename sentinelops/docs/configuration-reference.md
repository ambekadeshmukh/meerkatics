# SentinelOps Configuration Reference

This document provides a comprehensive reference for all SentinelOps configuration options.

## SDK Configuration

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | string | `"openai"` | LLM provider name |
| `model` | string | Provider-specific | Model name |
| `application_name` | string | `"default-app"` | Your application name |
| `environment` | string | `"development"` | Environment (development, staging, production) |
| `log_requests` | boolean | `true` | Whether to log request prompts |
| `log_responses` | boolean | `true` | Whether to log response completions |
| `kafka_config` | object | `null` | Kafka configuration for sending metrics |

### Kafka Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bootstrap_servers` | string | `"localhost:9092"` | Kafka bootstrap servers |
| `topic` | string | `"llm-monitoring"` | Kafka topic for monitoring data |
| `client_id` | string | `"sentinelops-sdk"` | Kafka client ID |
| `acks` | string | `"1"` | Kafka acknowledgment level |

### Batching Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_batching` | boolean | `false` | Enable request batching |
| `batch_size` | integer | `10` | Number of items per batch |
| `flush_interval` | float | `5.0` | Maximum seconds between flushes |

### Caching Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_caching` | boolean | `false` | Enable response caching |
| `cache_ttl` | integer | `3600` | Cache time-to-live in seconds |
| `cache_max_size` | integer | `1000` | Maximum number of cached items |
| `disk_cache` | boolean | `false` | Whether to persist cache to disk |
| `cache_dir` | string | `null` | Directory for disk cache |

## Provider-Specific Configuration

### OpenAI

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | Environment variable | OpenAI API key |
| `organization` | string | `null` | OpenAI organization ID |
| `api_base` | string | `null` | Custom API base URL |

### Anthropic

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | Environment variable | Anthropic API key |
| `api_url` | string | `null` | Custom API URL |

### HuggingFace

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | Environment variable | HuggingFace API key |
| `api_url` | string | `null` | Custom API URL |

### AWS Bedrock

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aws_access_key_id` | string | Environment variable | AWS access key |
| `aws_secret_access_key` | string | Environment variable | AWS secret key |
| `region_name` | string | `"us-east-1"` | AWS region name |

### Google Vertex AI

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project_id` | string | Environment variable | Google Cloud project ID |
| `location` | string | `"us-central1"` | Google Cloud region |

## Infrastructure Configuration

### Docker Compose

The `.env` file in the `infrastructure` directory configures Docker Compose deployment:

| Parameter | Description |
|-----------|-------------|
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_PORT` | PostgreSQL port |
| `API_PORT` | API server port |
| `JWT_SECRET` | Secret for JWT authentication |
| `FRONTEND_PORT` | Frontend dashboard port |
| `API_URL` | URL for frontend to access API |
| `PROMETHEUS_PORT` | Prometheus port |

### AWS Deployment

The AWS CloudFormation template accepts the following parameters:

| Parameter | Description |
|-----------|-------------|
| `InstanceType` | EC2 instance type |
| `KeyName` | EC2 key pair name |
| `SSHLocation` | IP range for SSH access |
| `AccessLocation` | IP range for web access |
| `DBPassword` | Database password |
| `JWTSecret` | JWT secret for authentication |

## API Configuration

The API server configuration is stored in `config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8000
  debug: false
  cors_origins:
    - http://localhost:3000
    - http://localhost:80

database:
  host: postgres
  port: 5432
  username: sentinelopsuser
  password: sentinelopsdev
  database: sentinelops

auth:
  jwt_secret: ${JWT_SECRET}
  token_expiry: 86400  # 24 hours
  refresh_expiry: 604800  # 7 days

logging:
  level: info
  format: json
  path: /var/log/sentinelops

prometheus:
  enabled: true
  path: /metrics
```

## Alert Configuration

Alerts can be configured through the API or dashboard with the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Alert name |
| `description` | string | Alert description |
| `enabled` | boolean | Whether alert is active |
| `alert_type` | enum | Type (cost, performance, error_rate, quality, hallucination, system) |
| `severity` | enum | Severity (low, medium, high, critical) |
| `thresholds` | array | Metric thresholds that trigger the alert |
| `filters` | object | Filters to limit alert scope |
| `notify_emails` | array | Email addresses for notifications |

### Example Alert Configuration

```json
{
  "name": "High Latency Alert",
  "description": "Alert when P95 latency exceeds threshold",
  "enabled": true,
  "alert_type": "performance",
  "severity": "high",
  "thresholds": [
    {
      "metric": "p95_inference_time",
      "operator": ">",
      "value": 2000,
      "duration_minutes": 5
    }
  ],
  "filters": {
    "environment": "production",
    "time_window": "15m"
  },
  "notify_emails": [
    "alerts@example.com"
  ]
}
```
