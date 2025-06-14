import pytest
import json
import uuid
from datetime import datetime
from fastapi import status

# Test alert API endpoints
class TestAlertsAPI:
    """Integration tests for the alerts API endpoints."""
    
    def test_send_alert(self, client, mock_smtp_server, mock_slack_api):
        """Test sending an alert through the API."""
        # Prepare test data
        alert_data = {
            "title": "Test Alert",
            "message": "This is a test alert from integration tests",
            "severity": "warning",
            "metadata": {
                "test": True,
                "source": "integration_test"
            },
            "channels": ["email", "slack"]
        }
        
        # Send alert
        response = client.post(
            "/api/alerts/",
            json=alert_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Alert sent successfully" in data["message"]
        
        # Verify email was sent
        mock_smtp_server.sendmail.assert_called_once()
        
        # Verify Slack notification was sent
        mock_slack_api.assert_called_once()
    
    def test_get_alert_history(self, client):
        """Test retrieving alert history."""
        # Send a test alert first to ensure there's history
        alert_data = {
            "title": "History Test Alert",
            "message": "This is a test alert for history",
            "severity": "info"
        }
        client.post(
            "/api/alerts/",
            json=alert_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Get alert history
        response = client.get(
            "/api/alerts/history",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify the test alert is in the history
        found = False
        for alert in data:
            if alert["title"] == "History Test Alert":
                found = True
                assert alert["message"] == "This is a test alert for history"
                assert alert["severity"] == "info"
                assert "timestamp" in alert
                assert "metadata" in alert
        assert found, "Test alert not found in history"
        
    def test_test_alert_channel(self, client, mock_smtp_server):
        """Test the alert channel test endpoint."""
        # Test email channel
        response = client.post(
            "/api/alerts/test?channel=email",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Test alert sent successfully to email" in data["message"]
        
        # Verify email was sent
        mock_smtp_server.sendmail.assert_called()
        
    def test_get_alert_config(self, client):
        """Test retrieving alert configuration."""
        response = client.get(
            "/api/alerts/config",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        config = response.json()
        
        # Verify config structure
        assert "email" in config
        assert "slack" in config
        assert "webhook" in config
        assert "sms" in config
        assert "general" in config
        
        # Verify email config (without sensitive data)
        assert "enabled" in config["email"]
        assert "smtp_server" in config["email"]
        assert "password" not in config["email"]  # Sensitive data should be excluded
        
    def test_alert_configs_crud(self, client, sample_alert_config):
        """Test CRUD operations for alert configurations."""
        # Create a new alert config
        config_data = sample_alert_config.dict()
        response = client.post(
            "/api/alerts/configs",
            json=config_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify creation response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "id" in data
        config_id = data["id"]
        
        # Get the created config
        response = client.get(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify get response
        assert response.status_code == status.HTTP_200_OK
        config = response.json()
        assert config["name"] == sample_alert_config.name
        assert config["alert_type"] == sample_alert_config.alert_type.value
        
        # Update the config
        config["description"] = "Updated description"
        response = client.put(
            f"/api/alerts/configs/{config_id}",
            json=config,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify update response
        assert response.status_code == status.HTTP_200_OK
        
        # Get the updated config
        response = client.get(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        updated_config = response.json()
        assert updated_config["description"] == "Updated description"
        
        # Delete the config
        response = client.delete(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify delete response
        assert response.status_code == status.HTTP_200_OK
        
        # Verify config is deleted
        response = client.get(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_get_all_alert_configs(self, client, sample_alert_config):
        """Test retrieving all alert configurations."""
        # Create a test config first
        config_data = sample_alert_config.dict()
        client.post(
            "/api/alerts/configs",
            json=config_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Get all configs
        response = client.get(
            "/api/alerts/configs",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        configs = response.json()
        assert isinstance(configs, list)
        assert len(configs) > 0
        
        # Verify enabled-only filter
        response = client.get(
            "/api/alerts/configs?enabled_only=true",
            headers={"X-API-Key": "test-api-key"}
        )
        enabled_configs = response.json()
        assert all(config["enabled"] for config in enabled_configs)
        
    def test_alert_events(self, client, test_db_connection, sample_alert_config):
        """Test alert events endpoints."""
        # Create a test config
        cursor = test_db_connection.cursor()
        config_id = str(uuid.uuid4())
        config_data = sample_alert_config.dict()
        config_data["id"] = config_id
        
        cursor.execute(
            "INSERT INTO alert_configs (id, config, enabled) VALUES (%s, %s, %s)",
            (config_id, json.dumps(config_data), True)
        )
        
        # Create a test event
        event_id = str(uuid.uuid4())
        timestamp = datetime.now()
        metric_value = 150.0
        threshold_value = 100.0
        details = {"source": "integration_test"}
        
        cursor.execute(
            """
            INSERT INTO alert_events 
            (id, config_id, timestamp, metric_value, threshold_value, details) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (event_id, config_id, timestamp, metric_value, threshold_value, json.dumps(details))
        )
        test_db_connection.commit()
        
        # Get events
        response = client.get(
            "/api/alerts/events",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        events = response.json()
        assert isinstance(events, list)
        assert len(events) > 0
        
        # Get specific event
        response = client.get(
            f"/api/alerts/events/{event_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        event = response.json()
        assert event["id"] == event_id
        assert event["alert_config_id"] == config_id
        assert event["metric_value"] == metric_value
        assert event["threshold_value"] == threshold_value
        
        # Resolve the event
        response = client.post(
            f"/api/alerts/events/{event_id}/resolve",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        resolved_event = response.json()
        assert resolved_event["id"] == event_id
        assert resolved_event["resolved_at"] is not None
