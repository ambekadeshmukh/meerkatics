# Meerkatics API Documentation

## Overview

Meerkatics provides a comprehensive API for monitoring, analyzing, and managing your LLM operations. This document outlines all available endpoints, their parameters, and example responses.

## Base URL

All API endpoints are relative to the base URL:

```
https://your-meerkatics-instance.com/api
```

## Authentication

All API requests require authentication using an API key. Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

To generate an API key, go to the Meerkatics dashboard and navigate to Settings > API Keys.

## Rate Limiting

The API is rate-limited to 100 requests per minute per API key. If you exceed this limit, you'll receive a `429 Too Many Requests` response.

## Common Response Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Endpoints

### Monitoring Events

#### Record LLM Event

```
POST /events
```

Records a new LLM usage event for monitoring and analysis.

**Request Body:**

```json
{
  "provider": "openai",
  "model": "gpt-4",
  "application": "chatbot",
  "request_id": "req_123456",
  "user_id": "user_123",
  "prompt": "Explain quantum computing in simple terms",
  "completion": "Quantum computing uses quantum bits or qubits...",
  "prompt_tokens": 10,
  "completion_tokens": 50,
  "total_tokens": 60,
  "latency_ms": 1200,
  "status": "success",
  "metadata": {
    "temperature": 0.7,
    "top_p": 1.0,
    "custom_field": "custom_value"
  }
}
```

**Response:**

```json
{
  "event_id": "evt_789012",
  "timestamp": "2023-10-15T14:30:45Z",
  "status": "recorded"
}
```

#### Get Event by ID

```
GET /events/{event_id}
```

Retrieves a specific event by its ID.

**Response:**

```json
{
  "event_id": "evt_789012",
  "timestamp": "2023-10-15T14:30:45Z",
  "provider": "openai",
  "model": "gpt-4",
  "application": "chatbot",
  "request_id": "req_123456",
  "user_id": "user_123",
  "prompt_tokens": 10,
  "completion_tokens": 50,
  "total_tokens": 60,
  "latency_ms": 1200,
  "status": "success",
  "cost": 0.0012,
  "metadata": {
    "temperature": 0.7,
    "top_p": 1.0,
    "custom_field": "custom_value"
  }
}
```

#### List Events

```
GET /events
```

Lists events with optional filtering.

**Query Parameters:**

- `start_time`: ISO timestamp for the start of the time range
- `end_time`: ISO timestamp for the end of the time range
- `provider`: Filter by provider (e.g., "openai", "anthropic")
- `model`: Filter by model (e.g., "gpt-4", "claude-2")
- `application`: Filter by application
- `status`: Filter by status (e.g., "success", "error")
- `limit`: Maximum number of events to return (default: 50, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "events": [
    {
      "event_id": "evt_789012",
      "timestamp": "2023-10-15T14:30:45Z",
      "provider": "openai",
      "model": "gpt-4",
      "application": "chatbot",
      "total_tokens": 60,
      "status": "success",
      "cost": 0.0012
    },
    {
      "event_id": "evt_789013",
      "timestamp": "2023-10-15T14:32:10Z",
      "provider": "anthropic",
      "model": "claude-2",
      "application": "summarizer",
      "total_tokens": 120,
      "status": "success",
      "cost": 0.0036
    }
  ],
  "total": 245,
  "limit": 50,
  "offset": 0
}
```

### Metrics

#### Get Summary Metrics

```
GET /metrics/summary
```

Returns summary metrics for the specified time period.

**Query Parameters:**

- `time_window`: Time window for metrics (e.g., "1h", "24h", "7d", "30d", default: "24h")
- `provider`: Filter by provider
- `model`: Filter by model
- `application`: Filter by application

**Response:**

```json
{
  "request_count": 1250,
  "total_tokens": 187500,
  "prompt_tokens": 62500,
  "completion_tokens": 125000,
  "total_cost": 2.81,
  "success_count": 1200,
  "error_count": 50,
  "error_rate": 0.04,
  "avg_latency": 1150,
  "avg_tokens_per_request": 150
}
```

#### Get Usage Over Time

```
GET /metrics/usage
```

Returns token usage over time.

**Query Parameters:**

- `interval`: Time interval for aggregation (e.g., "hour", "day", "week", default: "day")
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `provider`: Filter by provider
- `model`: Filter by model
- `application`: Filter by application

**Response:**

```json
[
  {
    "date": "2023-10-10",
    "total_tokens": 35000
  },
  {
    "date": "2023-10-11",
    "total_tokens": 42000
  },
  {
    "date": "2023-10-12",
    "total_tokens": 38500
  }
]
```

#### Get Cost Over Time

```
GET /metrics/cost
```

Returns cost over time.

**Query Parameters:**

- `interval`: Time interval for aggregation (e.g., "hour", "day", "week", default: "day")
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `provider`: Filter by provider
- `model`: Filter by model
- `application`: Filter by application

**Response:**

```json
[
  {
    "date": "2023-10-10",
    "total_cost": 0.53
  },
  {
    "date": "2023-10-11",
    "total_cost": 0.63
  },
  {
    "date": "2023-10-12",
    "total_cost": 0.58
  }
]
```

#### Get Top Models by Usage

```
GET /metrics/top-models
```

Returns the top models by token usage.

**Query Parameters:**

- `time_window`: Time window for metrics (e.g., "1h", "24h", "7d", "30d", default: "24h")
- `limit`: Maximum number of models to return (default: 5, max: 20)

**Response:**

```json
[
  {
    "provider": "openai",
    "model": "gpt-4",
    "total_tokens": 85000
  },
  {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "total_tokens": 65000
  },
  {
    "provider": "anthropic",
    "model": "claude-2",
    "total_tokens": 25000
  }
]
```

#### Get Top Applications by Cost

```
GET /metrics/top-applications
```

Returns the top applications by cost.

**Query Parameters:**

- `time_window`: Time window for metrics (e.g., "1h", "24h", "7d", "30d", default: "24h")
- `limit`: Maximum number of applications to return (default: 5, max: 20)

**Response:**

```json
[
  {
    "application": "chatbot",
    "total_cost": 1.50
  },
  {
    "application": "summarizer",
    "total_cost": 0.75
  },
  {
    "application": "translator",
    "total_cost": 0.45
  }
]
```

#### Get Error Rate by Model

```
GET /metrics/error-rates
```

Returns error rates by model.

**Query Parameters:**

- `time_window`: Time window for metrics (e.g., "1h", "24h", "7d", "30d", default: "24h")

**Response:**

```json
[
  {
    "provider": "openai",
    "model": "gpt-4",
    "error_rate": 0.02,
    "request_count": 500,
    "error_count": 10
  },
  {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "error_rate": 0.04,
    "request_count": 750,
    "error_count": 30
  },
  {
    "provider": "anthropic",
    "model": "claude-2",
    "error_rate": 0.05,
    "request_count": 200,
    "error_count": 10
  }
]
```

#### Get Latency Statistics

```
GET /metrics/latency
```

Returns latency statistics for a specific provider, model, and application.

**Query Parameters:**

- `time_window`: Time window for metrics (e.g., "1h", "24h", "7d", "30d", default: "24h")
- `provider`: Filter by provider
- `model`: Filter by model
- `application`: Filter by application

**Response:**

```json
{
  "min_latency": 450,
  "max_latency": 2500,
  "avg_latency": 1150,
  "std_latency": 350,
  "p50_latency": 1050,
  "p90_latency": 1750,
  "p95_latency": 2000,
  "p99_latency": 2300
}
```

#### Get Dashboard Metrics

```
GET /metrics/dashboard
```

Returns all metrics needed for the dashboard.

**Query Parameters:**

- `time_window`: Time window for metrics (e.g., "1h", "24h", "7d", "30d", default: "24h")

**Response:**

```json
{
  "summary": {
    "request_count": 1250,
    "total_tokens": 187500,
    "total_cost": 2.81,
    "error_rate": 0.04,
    "avg_latency": 1150
  },
  "top_models": [
    {
      "provider": "openai",
      "model": "gpt-4",
      "total_tokens": 85000
    },
    {
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "total_tokens": 65000
    },
    {
      "provider": "anthropic",
      "model": "claude-2",
      "total_tokens": 25000
    }
  ],
  "top_applications": [
    {
      "application": "chatbot",
      "total_cost": 1.50
    },
    {
      "application": "summarizer",
      "total_cost": 0.75
    },
    {
      "application": "translator",
      "total_cost": 0.45
    }
  ],
  "error_rates": [
    {
      "provider": "openai",
      "model": "gpt-4",
      "error_rate": 0.02
    },
    {
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "error_rate": 0.04
    },
    {
      "provider": "anthropic",
      "model": "claude-2",
      "error_rate": 0.05
    }
  ],
  "usage_over_time": [
    {
      "date": "2023-10-10",
      "total_tokens": 35000
    },
    {
      "date": "2023-10-11",
      "total_tokens": 42000
    },
    {
      "date": "2023-10-12",
      "total_tokens": 38500
    }
  ],
  "cost_over_time": [
    {
      "date": "2023-10-10",
      "total_cost": 0.53
    },
    {
      "date": "2023-10-11",
      "total_cost": 0.63
    },
    {
      "date": "2023-10-12",
      "total_cost": 0.58
    }
  ]
}
```

### Anomaly Detection

#### List Anomalies

```
GET /anomalies
```

Lists detected anomalies.

**Query Parameters:**

- `start_time`: ISO timestamp for the start of the time range
- `end_time`: ISO timestamp for the end of the time range
- `severity`: Filter by severity (e.g., "low", "medium", "high", "critical")
- `status`: Filter by status (e.g., "open", "acknowledged", "resolved")
- `limit`: Maximum number of anomalies to return (default: 50, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "anomalies": [
    {
      "anomaly_id": "anom_123456",
      "timestamp": "2023-10-15T10:30:00Z",
      "type": "latency_spike",
      "severity": "high",
      "status": "open",
      "description": "Unusual latency spike detected for gpt-4",
      "affected_provider": "openai",
      "affected_model": "gpt-4",
      "affected_application": "chatbot",
      "metric_value": 3500,
      "baseline_value": 1200,
      "deviation_percentage": 191.67
    },
    {
      "anomaly_id": "anom_123457",
      "timestamp": "2023-10-15T11:15:00Z",
      "type": "error_rate_increase",
      "severity": "medium",
      "status": "acknowledged",
      "description": "Increased error rate detected for claude-2",
      "affected_provider": "anthropic",
      "affected_model": "claude-2",
      "affected_application": "summarizer",
      "metric_value": 0.12,
      "baseline_value": 0.03,
      "deviation_percentage": 300.00
    }
  ],
  "total": 8,
  "limit": 50,
  "offset": 0
}
```

#### Get Anomaly by ID

```
GET /anomalies/{anomaly_id}
```

Retrieves a specific anomaly by its ID.

**Response:**

```json
{
  "anomaly_id": "anom_123456",
  "timestamp": "2023-10-15T10:30:00Z",
  "type": "latency_spike",
  "severity": "high",
  "status": "open",
  "description": "Unusual latency spike detected for gpt-4",
  "affected_provider": "openai",
  "affected_model": "gpt-4",
  "affected_application": "chatbot",
  "metric_value": 3500,
  "baseline_value": 1200,
  "deviation_percentage": 191.67,
  "related_events": [
    "evt_789012",
    "evt_789013",
    "evt_789014"
  ],
  "detection_method": "z_score",
  "detection_parameters": {
    "threshold": 3.0,
    "window_size": "1h"
  }
}
```

#### Update Anomaly Status

```
PATCH /anomalies/{anomaly_id}
```

Updates the status of an anomaly.

**Request Body:**

```json
{
  "status": "acknowledged",
  "comment": "Investigating the issue"
}
```

**Response:**

```json
{
  "anomaly_id": "anom_123456",
  "status": "acknowledged",
  "updated_at": "2023-10-15T14:45:30Z"
}
```

### Hallucination Detection

#### List Hallucinations

```
GET /hallucinations
```

Lists detected hallucinations.

**Query Parameters:**

- `start_time`: ISO timestamp for the start of the time range
- `end_time`: ISO timestamp for the end of the time range
- `provider`: Filter by provider
- `model`: Filter by model
- `application`: Filter by application
- `confidence_min`: Minimum confidence score (0-1)
- `limit`: Maximum number of hallucinations to return (default: 50, max: 1000)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "hallucinations": [
    {
      "hallucination_id": "hall_123456",
      "event_id": "evt_789012",
      "timestamp": "2023-10-15T09:30:00Z",
      "provider": "openai",
      "model": "gpt-4",
      "application": "chatbot",
      "prompt": "What is the capital of France?",
      "completion": "The capital of France is Berlin.",
      "confidence_score": 0.92,
      "detection_method": "factual_consistency",
      "explanation": "Incorrect factual statement. The capital of France is Paris, not Berlin."
    },
    {
      "hallucination_id": "hall_123457",
      "event_id": "evt_789015",
      "timestamp": "2023-10-15T10:15:00Z",
      "provider": "anthropic",
      "model": "claude-2",
      "application": "summarizer",
      "prompt": "Summarize the history of quantum computing.",
      "completion": "Quantum computing was invented by Albert Einstein in 1950...",
      "confidence_score": 0.85,
      "detection_method": "factual_consistency",
      "explanation": "Incorrect attribution and date. Einstein did not invent quantum computing, and the concept emerged in the 1980s."
    }
  ],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

#### Get Hallucination by ID

```
GET /hallucinations/{hallucination_id}
```

Retrieves a specific hallucination by its ID.

**Response:**

```json
{
  "hallucination_id": "hall_123456",
  "event_id": "evt_789012",
  "timestamp": "2023-10-15T09:30:00Z",
  "provider": "openai",
  "model": "gpt-4",
  "application": "chatbot",
  "user_id": "user_123",
  "prompt": "What is the capital of France?",
  "completion": "The capital of France is Berlin.",
  "confidence_score": 0.92,
  "detection_method": "factual_consistency",
  "explanation": "Incorrect factual statement. The capital of France is Paris, not Berlin.",
  "evidence": [
    {
      "source": "knowledge_base",
      "content": "Paris is the capital and most populous city of France."
    }
  ],
  "metadata": {
    "detection_time_ms": 150,
    "model_parameters": {
      "temperature": 0.7,
      "top_p": 1.0
    }
  }
}
```

### Alerts

#### Send Alert

```
POST /alerts
```

Sends an alert through configured channels.

**Request Body:**

```json
{
  "title": "High Error Rate Detected",
  "message": "The error rate for gpt-4 has increased to 15% in the last hour.",
  "severity": "error",
  "metadata": {
    "provider": "openai",
    "model": "gpt-4",
    "application": "chatbot",
    "error_rate": 0.15,
    "baseline_error_rate": 0.03
  },
  "channels": ["email", "slack"]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Alert sent successfully"
}
```

#### Get Alert History

```
GET /alerts/history
```

Gets alert history.

**Query Parameters:**

- `limit`: Maximum number of alerts to return (default: 50, max: 1000)
- `severity`: Filter by severity (e.g., "info", "warning", "error", "critical")

**Response:**

```json
[
  {
    "title": "High Error Rate Detected",
    "message": "The error rate for gpt-4 has increased to 15% in the last hour.",
    "severity": "error",
    "timestamp": "2023-10-15T14:30:00Z",
    "metadata": {
      "provider": "openai",
      "model": "gpt-4",
      "application": "chatbot",
      "error_rate": 0.15,
      "baseline_error_rate": 0.03,
      "triggered_by": "system"
    }
  },
  {
    "title": "Latency Spike Detected",
    "message": "Unusual latency spike detected for claude-2.",
    "severity": "warning",
    "timestamp": "2023-10-15T13:45:00Z",
    "metadata": {
      "provider": "anthropic",
      "model": "claude-2",
      "application": "summarizer",
      "latency_ms": 3200,
      "baseline_latency_ms": 1500,
      "triggered_by": "system"
    }
  }
]
```

#### Test Alert Channel

```
POST /alerts/test
```

Sends a test alert to verify channel configuration.

**Query Parameters:**

- `channel`: Channel to test (e.g., "email", "slack", "webhook", "sms")

**Response:**

```json
{
  "success": true,
  "message": "Test alert sent successfully to email"
}
```

#### Get Alert Configuration

```
GET /alerts/config
```

Gets current alert configuration.

**Response:**

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "from_address": "alerts@meerkatics.com",
    "to_addresses": ["admin@example.com", "team@example.com"],
    "use_tls": true
  },
  "slack": {
    "enabled": true,
    "channel": "#alerts"
  },
  "webhook": {
    "enabled": false,
    "url": "",
    "method": "POST"
  },
  "sms": {
    "enabled": false,
    "from_number": "",
    "to_numbers": []
  },
  "general": {
    "min_severity": "warning",
    "throttle_period_seconds": 300
  }
}
```

## SDK Usage Examples

### JavaScript/TypeScript

```javascript
import { Meerkatics } from 'meerkatics';

// Initialize the client
const client = new Meerkatics({
  apiKey: 'your_api_key',
  baseUrl: 'https://your-meerkatics-instance.com/api'
});

// Record an LLM event
await client.recordEvent({
  provider: 'openai',
  model: 'gpt-4',
  application: 'chatbot',
  request_id: 'req_123456',
  user_id: 'user_123',
  prompt: 'Explain quantum computing in simple terms',
  completion: 'Quantum computing uses quantum bits or qubits...',
  prompt_tokens: 10,
  completion_tokens: 50,
  total_tokens: 60,
  latency_ms: 1200,
  status: 'success',
  metadata: {
    temperature: 0.7,
    top_p: 1.0
  }
});

// Get dashboard metrics
const dashboard = await client.getDashboardMetrics({
  timeWindow: '24h'
});

console.log(`Total requests: ${dashboard.summary.request_count}`);
console.log(`Total cost: $${dashboard.summary.total_cost.toFixed(2)}`);
```

### Python

```python
from meerkatics import Meerkatics

# Initialize the client
client = Meerkatics(
    api_key='your_api_key',
    base_url='https://your-meerkatics-instance.com/api'
)

# Record an LLM event
client.record_event(
    provider='openai',
    model='gpt-4',
    application='chatbot',
    request_id='req_123456',
    user_id='user_123',
    prompt='Explain quantum computing in simple terms',
    completion='Quantum computing uses quantum bits or qubits...',
    prompt_tokens=10,
    completion_tokens=50,
    total_tokens=60,
    latency_ms=1200,
    status='success',
    metadata={
        'temperature': 0.7,
        'top_p': 1.0
    }
)

# Get dashboard metrics
dashboard = client.get_dashboard_metrics(time_window='24h')

print(f"Total requests: {dashboard['summary']['request_count']}")
print(f"Total cost: ${dashboard['summary']['total_cost']:.2f}")
```

## Webhook Events

Meerkatics can send webhook events to your server when certain events occur. Configure webhooks in the Meerkatics dashboard under Settings > Webhooks.

### Event Types

- `anomaly.detected`: Triggered when a new anomaly is detected
- `hallucination.detected`: Triggered when a hallucination is detected
- `error_rate.threshold_exceeded`: Triggered when the error rate exceeds a threshold
- `cost.threshold_exceeded`: Triggered when the cost exceeds a threshold
- `latency.threshold_exceeded`: Triggered when the latency exceeds a threshold

### Example Webhook Payload

```json
{
  "event_type": "anomaly.detected",
  "timestamp": "2023-10-15T14:30:00Z",
  "data": {
    "anomaly_id": "anom_123456",
    "type": "latency_spike",
    "severity": "high",
    "description": "Unusual latency spike detected for gpt-4",
    "affected_provider": "openai",
    "affected_model": "gpt-4",
    "affected_application": "chatbot",
    "metric_value": 3500,
    "baseline_value": 1200,
    "deviation_percentage": 191.67
  }
}
```

## Error Handling

All API endpoints return standard HTTP status codes. In case of an error, the response body will contain an error message:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Invalid parameter: time_window must be one of 1h, 24h, 7d, 30d"
  }
}
```

## Pagination

Endpoints that return lists of items support pagination using the `limit` and `offset` parameters. The response includes the total count of items and the current limit and offset:

```json
{
  "items": [...],
  "total": 245,
  "limit": 50,
  "offset": 0
}
```

## Versioning

The API is versioned using the URL path. The current version is v1:

```
https://your-meerkatics-instance.com/api/v1/events
```

## Support

If you encounter any issues or have questions about the API, please contact our support team at support@meerkatics.com or open an issue on our GitHub repository.
