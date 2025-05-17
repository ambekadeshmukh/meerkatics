import pytest
import json
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the application
from sentinelops.backend.api_server.app_enhanced import app

class TestFrontendBackendIntegration:
    """
    Integration tests for frontend-backend interaction.
    These tests simulate frontend component interactions with the backend API.
    """
    
    @pytest.fixture
    def mock_frontend_fetch(self):
        """Mock the frontend fetch API calls."""
        with patch("requests.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response
            yield mock_request
    
    def test_alerts_panel_data_loading(self, client):
        """
        Test that the AlertsPanel component can load alert data from the API.
        This simulates the frontend component fetching alert history.
        """
        # Create some test alerts first
        alert_data = {
            "title": "Frontend Test Alert",
            "message": "This is a test alert for frontend integration",
            "severity": "warning",
            "metadata": {"source": "frontend_test"}
        }
        
        # Send alerts to have data in history
        for i in range(3):
            client.post(
                "/api/alerts/",
                json=alert_data,
                headers={"X-API-Key": "test-api-key"}
            )
        
        # Simulate the frontend component fetching alert history
        response = client.get(
            "/api/alerts/history?limit=10",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify the response format matches what the frontend expects
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        
        # Verify each alert has the expected structure for the frontend
        for alert in data:
            assert "title" in alert
            assert "message" in alert
            assert "severity" in alert
            assert "timestamp" in alert
            assert "metadata" in alert
    
    def test_alert_config_management(self, client, sample_alert_config):
        """
        Test that alert configurations can be managed through the API.
        This simulates the frontend component for managing alert configurations.
        """
        # Simulate creating a new alert config from the frontend
        config_data = sample_alert_config.dict()
        create_response = client.post(
            "/api/alerts/configs",
            json=config_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert create_response.status_code in [200, 201]
        create_data = create_response.json()
        assert "id" in create_data
        config_id = create_data["id"]
        
        # Simulate fetching the config list for display in the frontend
        list_response = client.get(
            "/api/alerts/configs",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert list_response.status_code == 200
        configs = list_response.json()
        assert isinstance(configs, list)
        assert any(c["id"] == config_id for c in configs)
        
        # Simulate updating a config from the frontend
        config = next(c for c in configs if c["id"] == config_id)
        config["description"] = "Updated from frontend test"
        
        update_response = client.put(
            f"/api/alerts/configs/{config_id}",
            json=config,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert update_response.status_code == 200
        
        # Simulate fetching the updated config for display
        get_response = client.get(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert get_response.status_code == 200
        updated_config = get_response.json()
        assert updated_config["description"] == "Updated from frontend test"
        
        # Simulate deleting the config from the frontend
        delete_response = client.delete(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert delete_response.status_code == 200
        
        # Verify it's gone
        verify_response = client.get(
            f"/api/alerts/configs/{config_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert verify_response.status_code == 404
    
    def test_alert_channel_testing(self, client, mock_smtp_server):
        """
        Test the alert channel testing functionality.
        This simulates the frontend component for testing alert channels.
        """
        # Simulate testing the email channel from the frontend
        response = client.post(
            "/api/alerts/test?channel=email",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Test alert sent successfully to email" in data["message"]
        
        # Verify the email was sent
        mock_smtp_server.sendmail.assert_called()
    
    def test_alert_config_form_validation(self, client):
        """
        Test form validation for alert configurations.
        This simulates frontend form validation for creating alert configs.
        """
        # Test with missing required fields
        invalid_config = {
            # Missing name
            "description": "This should fail validation",
            "enabled": True,
            "alert_type": "cost",
            "severity": "medium",
            # Missing thresholds
            "filters": {"provider": "openai"}
        }
        
        response = client.post(
            "/api/alerts/configs",
            json=invalid_config,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Should return validation error
        assert response.status_code in [400, 422]
        
        # Test with valid data
        valid_config = {
            "name": "Valid Test Config",
            "description": "This should pass validation",
            "enabled": True,
            "alert_type": "cost",
            "severity": "medium",
            "thresholds": [
                {
                    "metric": "total_cost",
                    "operator": ">",
                    "value": 100.0,
                    "duration_minutes": 5
                }
            ],
            "filters": {"provider": "openai"},
            "notify_emails": ["test@example.com"]
        }
        
        response = client.post(
            "/api/alerts/configs",
            json=valid_config,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Should succeed
        assert response.status_code in [200, 201]
    
    def test_alert_events_pagination(self, client, test_db_connection, sample_alert_config):
        """
        Test pagination for alert events.
        This simulates the frontend component for browsing alert events with pagination.
        """
        # Create a test config
        cursor = test_db_connection.cursor()
        config_id = str(sample_alert_config.id or "test-config-id")
        config_data = sample_alert_config.dict()
        config_data["id"] = config_id
        
        cursor.execute(
            "INSERT INTO alert_configs (id, config, enabled) VALUES (%s, %s, %s)",
            (config_id, json.dumps(config_data), True)
        )
        
        # Create multiple test events
        for i in range(25):  # Create enough events to test pagination
            event_id = f"test-event-{i}"
            timestamp = datetime.now()
            metric_value = 100.0 + i
            threshold_value = 100.0
            details = {"index": i, "source": "pagination_test"}
            
            cursor.execute(
                """
                INSERT INTO alert_events 
                (id, config_id, timestamp, metric_value, threshold_value, details) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (event_id, config_id, timestamp, metric_value, threshold_value, json.dumps(details))
            )
        
        test_db_connection.commit()
        
        # Test first page (default limit is 100)
        response = client.get(
            "/api/alerts/events",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        all_events = response.json()
        assert isinstance(all_events, list)
        assert len(all_events) >= 25
        
        # Test with smaller limit
        response = client.get(
            "/api/alerts/events?limit=10",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        page1_events = response.json()
        assert isinstance(page1_events, list)
        assert len(page1_events) == 10
        
        # Test second page
        response = client.get(
            "/api/alerts/events?limit=10&offset=10",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 200
        page2_events = response.json()
        assert isinstance(page2_events, list)
        assert len(page2_events) >= 10
        
        # Verify pages don't overlap
        page1_ids = [e["id"] for e in page1_events]
        page2_ids = [e["id"] for e in page2_events]
        assert not any(id in page1_ids for id in page2_ids)
