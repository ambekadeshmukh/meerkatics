# Integration Testing Framework

This document provides a comprehensive guide to the SentinelOps integration testing framework, which verifies that different components of the system work correctly together.

## Overview

Integration tests in SentinelOps focus on testing the interactions between different components of the system, ensuring that they work together as expected. These tests are crucial for verifying that:

1. API endpoints function correctly
2. Alert configurations are properly processed
3. Alerts are triggered when conditions are met
4. Data flows correctly from the stream processor to the database
5. Frontend components can interact with backend APIs

## Test Structure

The integration tests are organized into the following files:

- `conftest.py`: Contains shared fixtures and test setup
- `test_alerts_api.py`: Tests for the alerts API endpoints
- `test_alert_service.py`: Tests for the alert service functionality
- `test_frontend_backend_integration.py`: Tests for frontend-backend interactions
- `test_stream_processor_integration.py`: Tests for stream processor integration

## Key Components Tested

### 1. Alerts API

The alerts API tests verify that:
- Alert configurations can be created, retrieved, updated, and deleted
- Alert history can be retrieved
- Alert endpoints properly validate input data
- Authentication and authorization work correctly

### 2. Alert Service

The alert service tests verify that:
- Alerts are properly processed and delivered through different channels
- Alert thresholds are correctly evaluated
- Alert throttling works as expected
- Alert history is properly recorded

### 3. Frontend-Backend Integration

The frontend-backend integration tests verify that:
- Frontend components can fetch data from backend APIs
- Data is properly formatted for frontend consumption
- Frontend can submit configurations to the backend

### 4. Stream Processor Integration

The stream processor integration tests verify that:
- Events are correctly processed and stored in the database
- Metrics are properly aggregated
- Alerts are triggered when thresholds are exceeded
- Error rates are correctly calculated

## Setting Up the Test Environment

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- All dependencies installed from `requirements-test.txt`

### Configuration

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

### Database Setup

The test database is automatically set up by the fixtures in `conftest.py`. The fixtures will:

1. Connect to the test database
2. Create necessary tables if they don't exist
3. Clean up test data after each test

## Running the Tests

### Running All Integration Tests

```bash
cd sentinelops
pytest tests/integration
```

### Running Specific Test Categories

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

```bash
pytest --cov=sentinelops tests/integration
```

## Test Fixtures

The `conftest.py` file provides several important fixtures:

### Database Fixtures

- `test_db_connection`: Provides a connection to the test database
- `test_db_cleanup`: Cleans up test data after each test

### API Fixtures

- `api_client`: Provides a FastAPI TestClient for making API requests
- `api_auth_headers`: Provides authentication headers for API requests

### Service Fixtures

- `alert_service`: Provides an instance of the AlertService for testing
- `metrics_processor`: Provides an instance of the MetricsProcessor for testing

### Mock Service Fixtures

- `mock_smtp_server`: Mocks an SMTP server for testing email alerts
- `mock_slack_client`: Mocks the Slack client for testing Slack alerts
- `mock_twilio_client`: Mocks the Twilio client for testing SMS alerts
- `mock_webhook_server`: Mocks a webhook server for testing webhook alerts

## Writing New Integration Tests

### Best Practices

1. **Use fixtures**: Leverage the existing fixtures in `conftest.py` to avoid duplicating setup code.
2. **Isolate tests**: Each test should be independent and not rely on the state from other tests.
3. **Clean up after tests**: Use the `test_db_cleanup` fixture to ensure test data is removed.
4. **Mock external services**: Use the mock service fixtures to avoid making real API calls.
5. **Test edge cases**: Include tests for error conditions and edge cases.
6. **Use meaningful assertions**: Make assertions that verify the expected behavior.

### Example: Testing an Alert Configuration

```python
def test_create_alert_config(api_client, api_auth_headers, test_db_connection):
    """Test creating a new alert configuration."""
    # Define the alert configuration
    config_data = {
        "name": "Test Alert",
        "description": "Test alert description",
        "enabled": True,
        "alert_type": "COST",
        "severity": "MEDIUM",
        "thresholds": [
            {
                "metric": "total_cost",
                "operator": ">",
                "value": 10.0,
                "duration_minutes": 5
            }
        ],
        "filters": {"provider": "openai", "model": "gpt-4"},
        "notify_emails": ["admin@example.com"]
    }
    
    # Make the API request
    response = api_client.post(
        "/api/v1/alerts/configs",
        json=config_data,
        headers=api_auth_headers
    )
    
    # Verify the response
    assert response.status_code == 201
    config_id = response.json()["id"]
    assert config_id is not None
    
    # Verify the configuration was stored in the database
    cursor = test_db_connection.cursor()
    cursor.execute(
        "SELECT * FROM alert_configs WHERE id = %s",
        (config_id,)
    )
    result = cursor.fetchone()
    assert result is not None
    assert result["name"] == "Test Alert"
```

### Example: Testing Alert Triggering

```python
def test_alert_triggering(metrics_processor, test_db_connection, 
                         alert_service, mock_smtp_server):
    """Test that alerts are triggered when thresholds are exceeded."""
    # Create an alert configuration
    config = AlertConfig(
        name="Test Cost Alert",
        description="Alert when cost exceeds threshold",
        enabled=True,
        alert_type=AlertType.COST,
        severity=AlertSeverity.MEDIUM,
        thresholds=[
            AlertThreshold(
                metric="total_cost",
                operator=">",
                value=10.0,
                duration_minutes=5
            )
        ],
        filters={"provider": "openai", "model": "gpt-4"},
        notify_emails=["admin@example.com"]
    )
    
    config_id = alert_service.create_alert_config(config)
    config.id = config_id
    
    # Create high-cost events
    high_cost_events = [
        {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "provider": "openai",
            "model": "gpt-4",
            "cost": 15.0,  # Exceeds threshold
            # ... other event fields
        }
    ]
    
    # Process events with mocked alert service
    with patch.object(alert_service, 'send_alert') as mock_send_alert:
        mock_send_alert.return_value = True
        
        metrics_processor.alert_service = alert_service
        metrics_processor.process_events(high_cost_events)
        
        # Verify alert was triggered
        mock_send_alert.assert_called()
        
        # Verify alert event was created in the database
        cursor = test_db_connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM alert_events WHERE config_id = %s",
            (config_id,)
        )
        alert_count = cursor.fetchone()[0]
        assert alert_count >= 1
```

## Continuous Integration

The integration tests are configured to run automatically in CI environments using GitHub Actions. The workflow is defined in `.github/workflows/integration-tests.yml`.

The CI workflow:

1. Sets up a PostgreSQL database for testing
2. Installs dependencies
3. Creates a test environment file
4. Runs the integration tests
5. Generates and uploads a coverage report

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

### Test Failures

If tests are failing:

1. Check the test logs for error messages
2. Verify that the test database is properly configured
3. Ensure that the test fixtures are working correctly
4. Check for any changes to the application code that might affect the tests

## Conclusion

The integration testing framework provides a comprehensive way to verify that different components of the SentinelOps system work together correctly. By following the guidelines in this document, you can ensure that your integration tests are effective and maintainable.
