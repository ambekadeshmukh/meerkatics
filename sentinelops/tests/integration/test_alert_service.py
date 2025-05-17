import pytest
import json
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

from sentinelops.backend.api_server.services.alerts import AlertService
from sentinelops.backend.api_server.models.alerts import AlertConfig, AlertEvent, AlertThreshold, AlertType, AlertSeverity

class TestAlertService:
    """Integration tests for the AlertService."""
    
    def test_send_alert_all_channels(self, alert_service, mock_smtp_server, mock_slack_api, mock_twilio_api):
        """Test sending an alert through all channels."""
        # Send alert through all channels
        result = alert_service.send_alert(
            title="Critical System Alert",
            message="This is a test of all notification channels",
            severity="critical",
            metadata={
                "test": True,
                "source": "integration_test",
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Verify alert was sent successfully
        assert result is True
        
        # Verify email was sent
        mock_smtp_server.sendmail.assert_called_once()
        
        # Verify Slack notification was sent
        mock_slack_api.assert_called_once()
        
        # Verify SMS was sent
        assert mock_twilio_api.messages.create.called
        
        # Verify alert was added to history
        assert len(alert_service.alert_history) > 0
        latest_alert = alert_service.alert_history[-1]
        assert latest_alert["title"] == "Critical System Alert"
        assert latest_alert["severity"] == "critical"
        
    def test_alert_throttling(self, alert_service):
        """Test alert throttling to prevent alert fatigue."""
        # Configure throttling for testing
        alert_service.config["general"]["throttle_period_seconds"] = 60
        
        # Send first alert
        first_result = alert_service.send_alert(
            title="Throttle Test",
            message="This is the first alert",
            severity="warning"
        )
        assert first_result is True
        
        # Send second identical alert (should be throttled)
        second_result = alert_service.send_alert(
            title="Throttle Test",
            message="This is the second alert",
            severity="warning"
        )
        assert second_result is False
        
        # Send different alert (should not be throttled)
        third_result = alert_service.send_alert(
            title="Different Alert",
            message="This is a different alert",
            severity="warning"
        )
        assert third_result is True
        
        # Send critical alert (should not be throttled regardless)
        critical_result = alert_service.send_alert(
            title="Throttle Test",
            message="This is a critical alert that should bypass throttling",
            severity="critical"
        )
        assert critical_result is True
        
        # Reset throttling for other tests
        alert_service.config["general"]["throttle_period_seconds"] = 0
    
    def test_alert_config_crud(self, alert_service, sample_alert_config):
        """Test CRUD operations for alert configurations."""
        # Create alert config
        config_id = alert_service.create_alert_config(sample_alert_config)
        assert config_id is not None
        
        # Get the created config
        config = alert_service.get_alert_config(config_id)
        assert config is not None
        assert config.name == sample_alert_config.name
        assert config.alert_type == sample_alert_config.alert_type
        
        # Update the config
        config.description = "Updated description"
        updated_config = alert_service.update_alert_config(config)
        assert updated_config is not None
        assert updated_config.description == "Updated description"
        
        # Get all configs
        all_configs = alert_service.get_alert_configs()
        assert len(all_configs) > 0
        assert any(c.id == config_id for c in all_configs)
        
        # Get enabled configs only
        config.enabled = True
        alert_service.update_alert_config(config)
        enabled_configs = alert_service.get_alert_configs(enabled_only=True)
        assert all(c.enabled for c in enabled_configs)
        
        # Delete the config
        delete_result = alert_service.delete_alert_config(config_id)
        assert delete_result is True
        
        # Verify deletion
        deleted_config = alert_service.get_alert_config(config_id)
        assert deleted_config is None
    
    def test_alert_events(self, alert_service, sample_alert_config):
        """Test alert events creation and management."""
        # Create alert config
        config_id = alert_service.create_alert_config(sample_alert_config)
        
        # Create alert event
        event_id = alert_service.create_alert_event(
            config_id=config_id,
            metric_value=150.0,
            threshold_value=100.0,
            details={"source": "integration_test"}
        )
        assert event_id is not None
        
        # Get the created event
        event = alert_service.get_alert_event(event_id)
        assert event is not None
        assert event.alert_config_id == config_id
        assert event.metric_value == 150.0
        assert event.threshold_value == 100.0
        assert event.resolved_at is None
        
        # Get all events
        all_events = alert_service.get_alert_events()
        assert len(all_events) > 0
        assert any(e.id == event_id for e in all_events)
        
        # Filter events by config
        config_events = alert_service.get_alert_events(config_id=config_id)
        assert all(e.alert_config_id == config_id for e in config_events)
        
        # Filter by resolution status
        unresolved = alert_service.get_alert_events(resolved=False)
        assert all(e.resolved_at is None for e in unresolved)
        
        # Resolve the event
        resolved_event = alert_service.resolve_alert_event(event_id)
        assert resolved_event is not None
        assert resolved_event.resolved_at is not None
        
        # Get resolved events
        resolved = alert_service.get_alert_events(resolved=True)
        assert len(resolved) > 0
        assert any(e.id == event_id for e in resolved)
    
    def test_email_alert(self, alert_service, mock_smtp_server):
        """Test sending an alert via email."""
        # Send email alert
        alert_data = {
            "title": "Email Test Alert",
            "message": "This is a test email alert",
            "severity": "info",
            "timestamp": datetime.now().isoformat(),
            "metadata": {"test": True}
        }
        
        result = alert_service._send_email_alert(alert_data)
        assert result is True
        
        # Verify SMTP interactions
        mock_smtp_server.starttls.assert_called_once()
        mock_smtp_server.login.assert_called_once()
        mock_smtp_server.sendmail.assert_called_once()
        mock_smtp_server.quit.assert_called_once()
        
        # Verify email content
        args = mock_smtp_server.sendmail.call_args[0]
        assert args[0] == alert_service.config["email"]["from_address"]
        assert args[1] == alert_service.config["email"]["to_addresses"]
        assert "Email Test Alert" in args[2]
        assert "This is a test email alert" in args[2]
    
    def test_slack_alert(self, alert_service, mock_slack_api):
        """Test sending an alert via Slack."""
        # Send Slack alert
        alert_data = {
            "title": "Slack Test Alert",
            "message": "This is a test Slack alert",
            "severity": "warning",
            "timestamp": datetime.now().isoformat(),
            "metadata": {"test": True}
        }
        
        result = alert_service._send_slack_alert(alert_data)
        assert result is True
        
        # Verify Slack API call
        mock_slack_api.assert_called_once()
        
        # Verify payload
        args = mock_slack_api.call_args
        assert args[0][0] == alert_service.config["slack"]["webhook_url"]
        payload = args[1]["json"]
        assert payload["channel"] == alert_service.config["slack"]["channel"]
        assert "Slack Test Alert" in str(payload)
        assert "This is a test Slack alert" in str(payload)
    
    def test_webhook_alert(self, alert_service):
        """Test sending an alert via webhook."""
        # Mock requests.request
        with patch("requests.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response
            
            # Send webhook alert
            alert_data = {
                "title": "Webhook Test Alert",
                "message": "This is a test webhook alert",
                "severity": "error",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True}
            }
            
            result = alert_service._send_webhook_alert(alert_data)
            assert result is True
            
            # Verify webhook request
            mock_request.assert_called_once()
            
            # Verify payload
            args = mock_request.call_args
            assert args[0][0] == alert_service.config["webhook"]["method"]
            assert args[0][1] == alert_service.config["webhook"]["url"]
            payload = args[1]["json"]
            assert payload["title"] == "Webhook Test Alert"
            assert payload["message"] == "This is a test webhook alert"
            assert payload["severity"] == "error"
    
    def test_sms_alert(self, alert_service, mock_twilio_api):
        """Test sending an alert via SMS."""
        # Send SMS alert
        alert_data = {
            "title": "SMS Test Alert",
            "message": "This is a test SMS alert",
            "severity": "critical",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "test": True,
                "model": "gpt-4",
                "provider": "openai"
            }
        }
        
        result = alert_service._send_sms_alert(alert_data)
        assert result is True
        
        # Verify Twilio API call
        assert mock_twilio_api.messages.create.called
        
        # Verify message content
        args = mock_twilio_api.messages.create.call_args[1]
        assert args["from_"] == alert_service.config["sms"]["from_number"]
        assert args["to"] in alert_service.config["sms"]["to_numbers"]
        assert "SMS Test Alert" in args["body"]
        assert "This is a test SMS alert" in args["body"]
        assert "model: gpt-4" in args["body"]
