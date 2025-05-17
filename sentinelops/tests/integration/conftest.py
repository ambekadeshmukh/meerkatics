import os
import sys
import pytest
import sqlite3
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the necessary modules
from sentinelops.backend.api_server.services.alerts import AlertService
from sentinelops.backend.api_server.models.alerts import AlertConfig, AlertThreshold, AlertType, AlertSeverity

# SQLite in-memory database for testing
@pytest.fixture
def test_db_connection():
    """
    Create an in-memory SQLite database for testing.
    This avoids the need for PostgreSQL installation.
    """
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Create necessary tables
    cursor = conn.cursor()
    
    # Create request_metrics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS request_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT,
        timestamp TEXT,
        provider TEXT,
        model TEXT,
        application TEXT,
        request_id TEXT,
        user_id TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        total_tokens INTEGER,
        latency_ms REAL,
        cost REAL,
        status TEXT,
        error TEXT
    )
    ''')
    
    # Create alert_configs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alert_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        enabled INTEGER,
        alert_type TEXT,
        severity TEXT,
        thresholds TEXT,  # JSON string
        filters TEXT,      # JSON string
        notify_emails TEXT, # JSON string
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # Create alert_events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alert_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_id INTEGER,
        triggered_at TEXT,
        metric TEXT,
        value REAL,
        threshold REAL,
        message TEXT,
        status TEXT,
        FOREIGN KEY (config_id) REFERENCES alert_configs (id)
    )
    ''')
    
    conn.commit()
    yield conn
    
    # Close the connection after the test
    conn.close()

@pytest.fixture
def test_db_cleanup(test_db_connection):
    """Clean up test data after each test."""
    yield
    cursor = test_db_connection.cursor()
    cursor.execute("DELETE FROM request_metrics")
    cursor.execute("DELETE FROM alert_events")
    cursor.execute("DELETE FROM alert_configs")
    test_db_connection.commit()

@pytest.fixture
def api_client():
    """Create a FastAPI TestClient for making API requests."""
    from fastapi.testclient import TestClient
    from sentinelops.backend.api_server.main import app
    
    client = TestClient(app)
    return client

@pytest.fixture
def api_auth_headers():
    """Provide authentication headers for API requests."""
    return {"X-API-Key": "test-api-key"}

@pytest.fixture
def alert_service(test_db_connection):
    """Create an AlertService instance for testing."""
    service = AlertService(db_connection=test_db_connection)
    return service

@pytest.fixture
def mock_smtp_server():
    """Mock an SMTP server for testing email alerts."""
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        yield mock_server

@pytest.fixture
def mock_slack_client():
    """Mock the Slack client for testing Slack alerts."""
    with patch('slack_sdk.WebClient') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat_postMessage.return_value = {"ok": True}
        yield mock_instance

@pytest.fixture
def mock_twilio_client():
    """Mock the Twilio client for testing SMS alerts."""
    with patch('twilio.rest.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.messages.create.return_value = MagicMock(sid="SM123")
        yield mock_instance

@pytest.fixture
def mock_webhook_server():
    """Mock a webhook server for testing webhook alerts."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        yield mock_post
