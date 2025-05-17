# SentinelOps Integration Tests

This directory contains integration tests for the SentinelOps project, which verify that different components of the system work correctly together.

## Overview

The integration tests cover the following areas:

1. **API Endpoints**: Testing all alert-related API endpoints
2. **Alert Service**: Testing the alert service functionality
3. **Frontend-Backend Integration**: Testing interactions between frontend components and backend APIs
4. **Stream Processor Integration**: Testing data flow from the stream processor to the database and alert triggering

## Prerequisites

Before running the integration tests, you need to have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Docker (optional, for containerized testing)

## Setup

### 1. Create a Test Database

Create a dedicated PostgreSQL database for testing:

```bash
createdb test_sentinelops
```

### 2. Install Test Dependencies

Install the required Python packages:

```bash
pip install -r requirements-test.txt
```

### 3. Configure Test Environment

Create a `.env.test` file in the project root with the following configuration:

```
# Database settings
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_USER=your_username
TEST_DB_PASSWORD=your_password
TEST_DB_NAME=test_sentinelops

# Alert settings (for testing notification channels)
ALERT_EMAIL_ENABLED=true
ALERT_EMAIL_SMTP_SERVER=localhost
ALERT_EMAIL_SMTP_PORT=1025
ALERT_EMAIL_USERNAME=test@example.com
ALERT_EMAIL_PASSWORD=test_password
ALERT_EMAIL_FROM=alerts@sentinelops.com
ALERT_EMAIL_TO=admin@example.com
ALERT_EMAIL_USE_TLS=false

ALERT_SLACK_ENABLED=true
ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/test/webhook
ALERT_SLACK_CHANNEL=#test-alerts

ALERT_WEBHOOK_ENABLED=true
ALERT_WEBHOOK_URL=https://example.com/webhook
ALERT_WEBHOOK_HEADERS={"Content-Type": "application/json"}
ALERT_WEBHOOK_METHOD=POST

ALERT_SMS_ENABLED=true
ALERT_SMS_TWILIO_ACCOUNT_SID=test_account_sid
ALERT_SMS_TWILIO_AUTH_TOKEN=test_auth_token
ALERT_SMS_FROM_NUMBER=+15555555555
ALERT_SMS_TO_NUMBERS=+16666666666

# API settings
API_KEY_SECRET=test-api-key
JWT_SECRET_KEY=test-jwt-secret
```

## Running the Tests

### Running All Integration Tests

To run all integration tests:

```bash
cd sentinelops
pytest tests/integration
```

### Running Specific Test Categories

To run specific test categories:

```bash
# API tests
pytest tests/integration/test_alerts_api.py

# Alert service tests
pytest tests/integration/test_alert_service.py

# Frontend-backend integration tests
pytest tests/integration/test_frontend_backend_integration.py

# Stream processor integration tests
pytest tests/integration/test_stream_processor_integration.py
```

### Running with Coverage

To run tests with coverage reporting:

```bash
pytest --cov=sentinelops tests/integration
```

## Test Structure

The integration tests are organized as follows:

- `conftest.py`: Contains shared fixtures and test setup
- `test_alerts_api.py`: Tests for the alerts API endpoints
- `test_alert_service.py`: Tests for the alert service functionality
- `test_frontend_backend_integration.py`: Tests for frontend-backend interactions
- `test_stream_processor_integration.py`: Tests for stream processor integration

## Mocking External Services

The tests use mocks for external services to avoid actual API calls:

- SMTP server for email alerts
- Slack API for Slack notifications
- Twilio API for SMS alerts
- Webhook endpoints

## Database Reset

The test database is automatically set up and cleaned between test runs using pytest fixtures. Tables are created if they don't exist, and test data is removed after each test.

## Continuous Integration

These tests are designed to run in CI environments. For GitHub Actions, a workflow is provided in `.github/workflows/integration-tests.yml`.

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Verify that PostgreSQL is running
2. Check that the database credentials in `.env.test` are correct
3. Ensure the test database exists

### Mock Server Issues

If you encounter issues with mocked services:

1. Check that the mock configuration in `conftest.py` is correct
2. Verify that the patching is applied correctly in the tests

## Contributing

When adding new integration tests:

1. Follow the existing patterns for fixtures and test structure
2. Use meaningful test names that describe what is being tested
3. Add appropriate assertions to verify the expected behavior
4. Update this README if you add new test categories or requirements
