# Meerkatics API Reference

This document provides a comprehensive reference for the Meerkatics REST API, allowing you to programmatically access monitoring data, configure alerts, and integrate with other systems.

## Base URL

```
https://your-meerkatics-deployment/api/v1
```

## Authentication

All API requests require authentication. Meerkatics supports two authentication methods:

### API Key Authentication

Include your API key in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

### Bearer Token Authentication

Include a JWT token in the `Authorization` header:

```
Authorization: Bearer your-token-here
```

To obtain a token, use the `/auth/token` endpoint with your credentials.

## Response Format

All API responses are in JSON format and include a standard structure:

```json
{
  "status": "success",
  "data": {
    // Response data here
  },
  "message": null
}
```

For error responses:

```json
{
  "status": "error",
  "data": null,
  "message": "Error message describing what went wrong"
}
```

## Rate Limiting

API requests are subject to rate limiting. The default limits are:

- 100 requests per minute per API key
- 1000 requests per hour per API key

Rate limit information is included in response headers:

- `X-Rate-Limit-Limit`: Total requests allowed in the period
- `X-Rate-Limit-Remaining`: Remaining requests in the current period
- `X-Rate-Limit-Reset`: Time in seconds until the limit resets

## Endpoints

### Authentication

#### POST /auth/token

Obtain a JWT token for API access.

**Request Body:**

```json
{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2023-12-31T23:59:59Z"
  },
  "message": null
}
```

#### POST /auth/refresh

Refresh an existing token.

**Request Body:**

```json
{
  "refresh_token": "your-refresh-token"
}
```

**Response:**

Same as `/auth/token`.

### Metrics

#### GET /metrics/summary

Get a summary of key metrics for your LLM applications.

**Query Parameters:**

- `start_time`: Start time (ISO 8601 format)
- `end_time`: End time (ISO 8601 format)
- `provider`: Filter by LLM provider
- `model`: Filter by model name
- `application`: Filter by application name
- `environment`: Filter by environment

**Response:**

```json
{
  "status": "success",
  "data": {
    "request_count": 12500,
    "error_count": 45,
    "error_rate": 0.0036,
    "avg_latency_ms": 1250.5,
    "p95_latency_ms": 2345.7,
    "total_tokens": 1456789,
    "prompt_tokens": 345678,
    "completion_tokens": 1111111,
    "estimated_cost_usd": 125.45,
    "hallucination_rate": 0.023
  },
  "message": null
}
```

#### POST /metrics/query

Query time-series metrics with custom filters.

**Request Body:**

```json
{
  "metrics": ["request_count", "avg_latency_ms", "error_rate"],
  "filters": {
    "provider": "openai",
    "model": "gpt-4",
    "application": "support-bot",
    "environment": "production"
  },
  "time_range": {
    "start": "2023-12-01T00:00:00Z",
    "end": "2023-12-31T23:59:59Z",
    "interval": "1d"
  },
  "group_by": ["model", "application"]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "timestamps": ["2023-12-01T00:00:00Z", "2023-12-02T00:00:00Z", ...],
    "series": [
      {
        "metric": "request_count",
        "groups": [
          {
            "model": "gpt-4",
            "application": "support-bot",
            "values": [1234, 1345, ...]
          }
        ]
      },
      // Additional metrics...
    ]
  },
  "message": null
}
```

#### GET /metrics/providers

Get a list of all monitored LLM providers.

**Response:**

```json
{
  "status": "success",
  "data": [
    "openai",
    "anthropic",
    "cohere",
    "huggingface",
    "bedrock"
  ],
  "message": null
}
```

#### GET /metrics/models

Get a list of all monitored models.

**Query Parameters:**

- `provider`: Filter by provider

**Response:**

```json
{
  "status": "success",
  "data": [
    {
      "provider": "openai",
      "models": ["gpt-3.5-turbo", "gpt-4", "text-davinci-003"]
    },
    {
      "provider": "anthropic",
      "models": ["claude-2", "claude-instant-1"]
    }
  ],
  "message": null
}
```

#### GET /metrics/applications

Get a list of all monitored applications.

**Response:**

```json
{
  "status": "success",
  "data": [
    "support-bot",
    "content-generator",
    "search-assistant",
    "code-helper"
  ],
  "message": null
}
```

### Requests

#### GET /requests

Get a list of recent requests.

**Query Parameters:**

- `start_time`: Start time (ISO 8601 format)
- `end_time`: End time (ISO 8601 format)
- `provider`: Filter by LLM provider
- `model`: Filter by model name
- `application`: Filter by application name
- `environment`: Filter by environment
- `success`: Filter by success status (true/false)
- `limit`: Maximum number of results (default: 100)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "status": "success",
  "data": {
    "total": 1245,
    "items": [
      {
        "request_id": "r1-123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2023-12-15T14:22:56Z",
        "provider": "openai",
        "model": "gpt-4",
        "application": "support-bot",
        "environment": "production",
        "inference_time_ms": 1245.6,
        "success": true,
        "prompt_tokens": 345,
        "completion_tokens": 678,
        "total_tokens": 1023,
        "estimated_cost_usd": 0.12
      },
      // Additional requests...
    ]
  },
  "message": null
}
```

#### GET /requests/{request_id}

Get details for a specific request.

**Path Parameters:**

- `request_id`: Request ID

**Response:**

```json
{
  "status": "success",
  "data": {
    "request_id": "r1-123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2023-12-15T14:22:56Z",
    "provider": "openai",
    "model": "gpt-4",
    "application": "support-bot",
    "environment": "production",
    "inference_time_ms": 1245.6,
    "success": true,
    "prompt_tokens": 345,
    "completion_tokens": 678,
    "total_tokens": 1023,
    "estimated_cost_usd": 0.12,
    "prompt": "Summarize the key points of...",
    "completion": "The key points are...",
    "metadata": {
      "user_id": "u-123",
      "session_id": "s-456",
      "request_ip": "192.168.1.1"
    },
    "error": null
  },
  "message": null
}
```

### Anomalies

#### GET /anomalies

Get detected anomalies.

**Query Parameters:**

- `start_time`: Start time (ISO 8601 format)
- `end_time`: End time (ISO 8601 format)
- `provider`: Filter by LLM provider
- `model`: Filter by model name
- `application`: Filter by application name
- `environment`: Filter by environment
- `type`: Filter by anomaly type
- `severity`: Filter by severity (low, medium, high, critical)
- `resolved`: Filter by resolution status (true/false)
- `limit`: Maximum number of results (default: 100)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "status": "success",
  "data": {
    "total": 12,
    "items": [
      {
        "anomaly_id": "a1-123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2023-12-15T14:22:56Z",
        "type": "latency_spike",
        "severity": "high",
        "provider": "openai",
        "model": "gpt-4",
        "application": "support-bot",
        "environment": "production",
        "description": "Latency spike of 350% above normal baseline",
        "affected_requests": 145,
        "resolved": false,
        "resolved_at": null
      },
      // Additional anomalies...
    ]
  },
  "message": null
}
```

#### GET /anomalies/{anomaly_id}

Get details for a specific anomaly.

**Path Parameters:**

- `anomaly_id`: Anomaly ID

**Response:**

```json
{
  "status": "success",
  "data": {
    "anomaly_id": "a1-123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2023-12-15T14:22:56Z",
    "type": "latency_spike",
    "severity": "high",
    "provider": "openai",
    "model": "gpt-4",
    "application": "support-bot",
    "environment": "production",
    "description": "Latency spike of 350% above normal baseline",
    "affected_requests": 145,
    "resolved": false,
    "resolved_at": null,
    "related_metrics": {
      "baseline_latency_ms": 350.5,
      "anomaly_latency_ms": 1225.6,
      "percent_increase": 350
    },
    "sample_request_ids": [
      "r1-123e4567-e89b-12d3-a456-426614174000",
      "r1-234e5678-e89b-12d3-a456-426614174000"
    ]
  },
  "message": null
}
```

#### POST /anomalies/{anomaly_id}/resolve

Mark an anomaly as resolved.

**Path Parameters:**

- `anomaly_id`: Anomaly ID

**Request Body:**

```json
{
  "resolution_note": "Fixed by restarting the API proxy server"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "anomaly_id": "a1-123e4567-e89b-12d3-a456-426614174000",
    "resolved": true,
    "resolved_at": "2023-12-15T15:30:00Z"
  },
  "message": "Anomaly resolved successfully"
}
```

### Alerts

#### GET /alerts/configs

Get alert configurations.

**Query Parameters:**

- `enabled`: Filter by enabled status (true/false)
- `type`: Filter by alert type
- `limit`: Maximum number of results (default: 100)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "status": "success",
  "data": {
    "total": 8,
    "items": [
      {
        "id": "alert-123e4567-e89b-12d3-a456-426614174000",
        "name": "High Latency Alert",
        "description": "Alert when latency exceeds threshold",
        "enabled": true,
        "alert_type": "performance",
        "severity": "high",
        "thresholds": [
          {
            "metric": "p95_latency_ms",
            "operator": ">",
            "value": 2000,
            "duration_minutes": 5
          }
        ],
        "filters": {
          "provider": "openai",
          "model": "gpt-4",
          "environment": "production"
        },
        "notify_emails": [
          "alerts@example.com"
        ],
        "created_at": "2023-11-15T10:00:00Z",
        "updated_at": "2023-11-15T10:00:00Z"
      },
      // Additional alert configs...
    ]
  },
  "message": null
}
```

#### POST /alerts/configs

Create a new alert configuration.

**Request Body:**

```json
{
  "name": "Cost Spike Alert",
  "description": "Alert when hourly cost exceeds threshold",
  "enabled": true,
  "alert_type": "cost",
  "severity": "medium",
  "thresholds": [
    {
      "metric": "hourly_cost_usd",
      "operator": ">",
      "value": 50,
      "duration_minutes": 10
    }
  ],
  "filters": {
    "environment": "production"
  },
  "notify_emails": [
    "alerts@example.com",
    "team@example.com"
  ]
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "id": "alert-234e5678-e89b-12d3-a456-426614174000",
    "name": "Cost Spike Alert",
    "description": "Alert when hourly cost exceeds threshold",
    "enabled": true,
    "alert_type": "cost",
    "severity": "medium",
    "thresholds": [
      {
        "metric": "hourly_cost_usd",
        "operator": ">",
        "value": 50,
        "duration_minutes": 10
      }
    ],
    "filters": {
      "environment": "production"
    },
    "notify_emails": [
      "alerts@example.com",
      "team@example.com"
    ],
    "created_at": "2023-12-15T16:00:00Z",
    "updated_at": "2023-12-15T16:00:00Z"
  },
  "message": "Alert configuration created successfully"
}
```

#### GET /alerts/configs/{alert_id}

Get a specific alert configuration.

**Path Parameters:**

- `alert_id`: Alert configuration ID

**Response:**

Similar to the individual item in `/alerts/configs` response.

#### PUT /alerts/configs/{alert_id}

Update an alert configuration.

**Path Parameters:**

- `alert_id`: Alert configuration ID

**Request Body:**

Similar to the request body for creating an alert.

**Response:**

Similar to the response for creating an alert.

#### DELETE /alerts/configs/{alert_id}

Delete an alert configuration.

**Path Parameters:**

- `alert_id`: Alert configuration ID

**Response:**

```json
{
  "status": "success",
  "data": null,
  "message": "Alert configuration deleted successfully"
}
```

#### GET /alerts/events

Get alert events.

**Query Parameters:**

- `start_time`: Start time (ISO 8601 format)
- `end_time`: End time (ISO 8601 format)
- `alert_id`: Filter by alert configuration ID
- `resolved`: Filter by resolution status (true/false)
- `limit`: Maximum number of results (default: 100)
- `offset`: Pagination offset (default: 0)

**Response:**

```json
{
  "status": "success",
  "data": {
    "total": 15,
    "items": [
      {
        "id": "event-123e4567-e89b-12d3-a456-426614174000",
        "alert_id": "alert-123e4567-e89b-12d3-a456-426614174000",
        "name": "High Latency Alert",
        "severity": "high",
        "triggered_at": "2023-12-15T14:00:00Z",
        "resolved_at": "2023-12-15T14:30:00Z",
        "resolved": true,
        "metric_value": 2500,
        "threshold_value": 2000,
        "details": {
          "provider": "openai",
          "model": "gpt-4",
          "environment": "production"
        }
      },
      // Additional alert events...
    ]
  },
  "message": null
}
```

### System

#### GET /system/health

Check the health of the Meerkatics system.

**Response:**

```json
{
  "status": "success",
  "data": {
    "version": "1.2.3",
    "components": {
      "api": {
        "status": "healthy",
        "version": "1.2.3"
      },
      "database": {
        "status": "healthy",
        "latency_ms": 5
      },
      "message_queue": {
        "status": "healthy",
        "pending_messages": 23
      },
      "time_series_db": {
        "status": "healthy",
        "latency_ms": 8
      }
    },
    "uptime_seconds": 345600
  },
  "message": null
}
```

#### GET /system/config

Get system configuration.

**Response:**

```json
{
  "status": "success",
  "data": {
    "metric_retention_days": 90,
    "raw_data_retention_days": 30,
    "sampling_rate": 1.0,
    "components_enabled": {
      "anomaly_detection": true,
      "hallucination_detection": true,
      "cost_optimization": true
    },
    "rate_limits": {
      "requests_per_minute": 100,
      "requests_per_hour": 1000
    }
  },
  "message": null
}
```

## Pagination

Endpoints that return lists of items support pagination through `limit` and `offset` parameters:

- `limit`: Maximum number of items to return (default: 100, max: 1000)
- `offset`: Number of items to skip (default: 0)

The response includes a `total` field indicating the total number of items available.

## Filtering

Many endpoints support filtering through query parameters. Common filters include:

- `start_time` / `end_time`: ISO 8601 formatted timestamps
- `provider`: LLM provider name
- `model`: Model name
- `application`: Application name
- `environment`: Environment name (e.g., "production", "staging")

## Date Ranges

For time-based queries, you can specify date ranges using ISO 8601 formatted timestamps:

```
start_time=2023-12-01T00:00:00Z&end_time=2023-12-31T23:59:59Z
```

You can also use relative time expressions:

- `now`: Current time
- `now-1h`: 1 hour ago
- `now-1d`: 1 day ago
- `now-1w`: 1 week ago
- `now-1M`: 1 month ago

Example:
```
start_time=now-1d&end_time=now
```

## Error Codes

Meerkatics API uses standard HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error responses include a message describing the error:

```json
{
  "status": "error",
  "data": null,
  "message": "Invalid parameters: start_time must be before end_time"
}
```

## Webhooks

Meerkatics can send webhook notifications for various events. Configure webhooks through the API or dashboard.

### Example Webhook Payload

```json
{
  "event_type": "alert_triggered",
  "timestamp": "2023-12-15T14:00:00Z",
  "data": {
    "alert_id": "alert-123e4567-e89b-12d3-a456-426614174000",
    "alert_name": "High Latency Alert",
    "severity": "high",
    "metric_value": 2500,
    "threshold_value": 2000,
    "details": {
      "provider": "openai",
      "model": "gpt-4",
      "environment": "production"
    }
  }
}
```

## SDK Integration

The Meerkatics SDK can interact with this API programmatically. See the [SDK Documentation](sdk-usage.md) for more information.