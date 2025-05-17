# SentinelOps Project Structure

This document provides an overview of the SentinelOps project structure, explaining the organization of directories, key components, and how they interact with each other.

## Overview

SentinelOps is organized into several main components:

```
sentinelops/
├── backend/
│   ├── api_server/
│   ├── stream_processor/
│   └── database/
├── frontend/
├── sdk/
├── tests/
│   ├── backend/
│   ├── integration/
│   └── sdk/
├── docs/
└── scripts/
```

## Key Components

### Backend

The backend consists of several key components:

#### API Server (`backend/api_server/`)

The API server provides RESTful endpoints for configuring and retrieving data from SentinelOps.

```
api_server/
├── main.py                 # FastAPI application entry point
├── routers/                # API route definitions
│   ├── alerts.py           # Alert configuration and history endpoints
│   ├── metrics.py          # Metrics retrieval endpoints
│   └── ...
├── routes/                 # Legacy route definitions (being consolidated)
│   └── alerts.py           # Additional alert endpoints
├── services/               # Business logic
│   ├── alerts.py           # Alert management service
│   ├── alert_service.py    # Alert sending service (being consolidated)
│   └── ...
├── models/                 # Data models
│   ├── alerts.py           # Alert-related models
│   └── ...
└── middleware/             # Request processing middleware
    ├── auth.py             # Authentication middleware
    └── ...
```

**Note on Consolidation**: As noted in the project memory, there are duplicate implementations of alert-related files that are being consolidated:
- `routes/alerts.py` and `routers/alerts.py` will be merged into `routers/alerts.py`
- `services/alerts.py` and `services/alert_service.py` will be merged into `services/alerts.py`

#### Stream Processor (`backend/stream_processor/`)

The stream processor ingests and processes events from AI service calls, storing metrics in the database and triggering alerts when thresholds are exceeded.

```
stream_processor/
├── main.py                 # Stream processor entry point
├── processors/             # Event processors
│   ├── metrics_processor.py # Processes metrics events
│   └── ...
├── consumers/              # Event consumers
│   ├── kafka_consumer.py   # Consumes events from Kafka
│   └── ...
└── producers/              # Event producers
    ├── kafka_producer.py   # Produces events to Kafka
    └── ...
```

#### Database (`backend/database/`)

Contains database connection and schema management code.

```
database/
├── connection.py           # Database connection management
├── schema.py               # Database schema definitions
└── migrations/             # Database migrations
```

### Frontend (`frontend/`)

The frontend provides a web-based dashboard for visualization and management.

```
frontend/
├── public/                 # Static assets
├── src/                    # Source code
│   ├── components/         # React components
│   │   ├── alerts/         # Alert-related components
│   │   ├── dashboard/      # Dashboard components
│   │   └── ...
│   ├── pages/              # Page components
│   ├── services/           # API client services
│   └── ...
├── package.json            # NPM package configuration
└── ...
```

### SDK (`sdk/`)

The SDK provides client libraries for integrating SentinelOps into applications.

```
sdk/
├── python/                 # Python SDK
│   ├── sentinelops/        # SDK package
│   │   ├── __init__.py     # Package initialization
│   │   ├── client.py       # Main client class
│   │   ├── providers/      # Provider-specific implementations
│   │   └── utils/          # Utility functions
│   └── setup.py            # Package setup
├── javascript/             # JavaScript SDK
└── ...
```

### Tests (`tests/`)

The tests directory contains unit, integration, and end-to-end tests.

```
tests/
├── backend/                # Backend unit tests
│   ├── api_server/         # API server tests
│   ├── stream_processor/   # Stream processor tests
│   └── ...
├── integration/            # Integration tests
│   ├── conftest.py         # Shared fixtures and test setup
│   ├── test_alerts_api.py  # Tests for the alerts API endpoints
│   ├── test_alert_service.py # Tests for the alert service
│   ├── test_frontend_backend_integration.py # Tests for frontend-backend interactions
│   ├── test_stream_processor_integration.py # Tests for stream processor integration
│   └── README.md           # Integration test documentation
└── sdk/                    # SDK tests
```

### Documentation (`docs/`)

Contains project documentation.

```
docs/
├── api-reference.md        # API reference documentation
├── architecture.md         # Architecture overview
├── integration-testing.md  # Integration testing documentation
├── project-structure.md    # This document
└── ...
```

### Scripts (`scripts/`)

Contains utility scripts for development, deployment, and maintenance.

```
scripts/
├── setup_db.py             # Database setup script
├── generate_test_data.py   # Test data generation script
└── ...
```

## Component Interactions

### Data Flow

1. **SDK → Stream Processor**: The SDK sends events to the stream processor.
2. **Stream Processor → Database**: The stream processor processes events and stores metrics in the database.
3. **Stream Processor → Alert Service**: The stream processor triggers alerts when thresholds are exceeded.
4. **API Server → Database**: The API server reads and writes data to the database.
5. **Frontend → API Server**: The frontend communicates with the API server to retrieve and update data.

### Alert Flow

1. **Configuration**: Alert configurations are created via the API server and stored in the database.
2. **Monitoring**: The stream processor continuously monitors metrics against alert thresholds.
3. **Triggering**: When a threshold is exceeded, the stream processor triggers the alert service.
4. **Notification**: The alert service sends notifications through configured channels (email, Slack, SMS, webhook).
5. **Recording**: The alert event is recorded in the database for historical tracking.

## Database Schema

The main database tables include:

- `request_metrics`: Stores metrics from AI service calls
- `alert_configs`: Stores alert configurations
- `alert_events`: Stores alert event history
- `users`: Stores user information
- `api_keys`: Stores API keys for authentication

## Configuration

Configuration is managed through environment variables, which can be set in:

- `.env`: Development environment variables
- `.env.test`: Test environment variables
- `.env.production`: Production environment variables

## Deployment

The application can be deployed using:

- Docker Compose: For local development and testing
- Kubernetes: For production deployment

Deployment configurations are stored in:

- `docker-compose.yml`: Docker Compose configuration
- `kubernetes/`: Kubernetes manifests

## Continuous Integration

Continuous integration is configured using GitHub Actions:

- `.github/workflows/unit-tests.yml`: Runs unit tests
- `.github/workflows/integration-tests.yml`: Runs integration tests
- `.github/workflows/build.yml`: Builds and publishes Docker images

## Conclusion

This document provides an overview of the SentinelOps project structure. For more detailed information about specific components, refer to the other documentation files in the `docs/` directory.
