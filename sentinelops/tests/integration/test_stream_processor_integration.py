import pytest
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the necessary modules
from sentinelops.backend.stream_processor.processors.metrics_processor import MetricsProcessor
from sentinelops.backend.api_server.services.alerts import AlertService
from sentinelops.backend.api_server.models.alerts import AlertConfig, AlertThreshold, AlertType, AlertSeverity

class TestStreamProcessorIntegration:
    """
    Integration tests for the stream processor.
    These tests verify that data flows correctly from the stream processor to the database
    and that alerts are properly triggered when conditions are met.
    """
    
    @pytest.fixture
    def metrics_processor(self, test_db_connection):
        """Create a MetricsProcessor instance with a test database connection."""
        processor = MetricsProcessor(db_connection=test_db_connection)
        return processor
    
    @pytest.fixture
    def cost_alert_config(self, alert_service):
        """Create a cost alert configuration for testing."""
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
                    value=10.0,  # Low threshold for testing
                    duration_minutes=5
                )
            ],
            filters={"provider": "openai", "model": "gpt-4"},
            notify_emails=["admin@example.com"]
        )
        
        config_id = alert_service.create_alert_config(config)
        config.id = config_id
        return config
    
    @pytest.fixture
    def latency_alert_config(self, alert_service):
        """Create a latency alert configuration for testing."""
        config = AlertConfig(
            name="Test Latency Alert",
            description="Alert when latency exceeds threshold",
            enabled=True,
            alert_type=AlertType.PERFORMANCE,
            severity=AlertSeverity.HIGH,
            thresholds=[
                AlertThreshold(
                    metric="avg_latency",
                    operator=">",
                    value=2000.0,  # 2000ms threshold for testing
                    duration_minutes=5
                )
            ],
            filters={"provider": "openai", "model": "gpt-4"},
            notify_emails=["admin@example.com"]
        )
        
        config_id = alert_service.create_alert_config(config)
        config.id = config_id
        return config
    
    def test_process_events_to_database(self, metrics_processor, test_db_connection):
        """Test that events are correctly processed and stored in the database."""
        # Create sample events
        events = [
            {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 1200,
                "cost": 0.0075,
                "status": "success"
            },
            {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "application": "summarizer",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 200,
                "completion_tokens": 100,
                "total_tokens": 300,
                "latency_ms": 800,
                "cost": 0.0045,
                "status": "success"
            }
        ]
        
        # Process events
        metrics_processor.process_events(events)
        
        # Verify events were stored in the database
        cursor = test_db_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM request_metrics")
        count = cursor.fetchone()[0]
        assert count >= 2
        
        # Verify metrics were aggregated
        cursor.execute(
            """
            SELECT provider, model, COUNT(*) 
            FROM request_metrics 
            WHERE provider = 'openai' 
            GROUP BY provider, model
            """
        )
        results = cursor.fetchall()
        assert len(results) >= 2
        
        # Verify we can retrieve the events by model
        cursor.execute(
            """
            SELECT * FROM request_metrics 
            WHERE provider = 'openai' AND model = 'gpt-4'
            """
        )
        gpt4_events = cursor.fetchall()
        assert len(gpt4_events) >= 1
    
    def test_alert_triggering_on_cost(self, metrics_processor, test_db_connection, 
                                     cost_alert_config, alert_service, mock_smtp_server):
        """Test that cost alerts are triggered when thresholds are exceeded."""
        # Create high-cost events that should trigger the alert
        high_cost_events = []
        for i in range(5):
            high_cost_events.append({
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 1000,
                "completion_tokens": 500,
                "total_tokens": 1500,
                "latency_ms": 1200,
                "cost": 3.0,  # High cost to trigger alert
                "status": "success"
            })
        
        # Process events
        with patch.object(alert_service, 'send_alert') as mock_send_alert:
            # Set up the mock to return True
            mock_send_alert.return_value = True
            
            # Inject the alert service into the metrics processor
            metrics_processor.alert_service = alert_service
            
            # Process the events
            metrics_processor.process_events(high_cost_events)
            
            # Check if alert was triggered
            cursor = test_db_connection.cursor()
            cursor.execute(
                """
                SELECT SUM(cost) FROM request_metrics 
                WHERE provider = 'openai' AND model = 'gpt-4'
                """
            )
            total_cost = cursor.fetchone()[0]
            
            # Verify total cost exceeds threshold
            assert total_cost > cost_alert_config.thresholds[0].value
            
            # Verify alert was triggered
            mock_send_alert.assert_called()
            
            # Verify alert event was created
            cursor.execute(
                """
                SELECT COUNT(*) FROM alert_events 
                WHERE config_id = %s
                """,
                (cost_alert_config.id,)
            )
            alert_count = cursor.fetchone()[0]
            assert alert_count >= 1
    
    def test_alert_triggering_on_latency(self, metrics_processor, test_db_connection,
                                        latency_alert_config, alert_service, mock_smtp_server):
        """Test that latency alerts are triggered when thresholds are exceeded."""
        # Create high-latency events that should trigger the alert
        high_latency_events = []
        for i in range(5):
            high_latency_events.append({
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 3000,  # High latency to trigger alert
                "cost": 0.0075,
                "status": "success"
            })
        
        # Process events
        with patch.object(alert_service, 'send_alert') as mock_send_alert:
            # Set up the mock to return True
            mock_send_alert.return_value = True
            
            # Inject the alert service into the metrics processor
            metrics_processor.alert_service = alert_service
            
            # Process the events
            metrics_processor.process_events(high_latency_events)
            
            # Check if alert was triggered
            cursor = test_db_connection.cursor()
            cursor.execute(
                """
                SELECT AVG(latency_ms) FROM request_metrics 
                WHERE provider = 'openai' AND model = 'gpt-4'
                """
            )
            avg_latency = cursor.fetchone()[0]
            
            # Verify average latency exceeds threshold
            assert avg_latency > latency_alert_config.thresholds[0].value
            
            # Verify alert was triggered
            mock_send_alert.assert_called()
            
            # Verify alert event was created
            cursor.execute(
                """
                SELECT COUNT(*) FROM alert_events 
                WHERE config_id = %s
                """,
                (latency_alert_config.id,)
            )
            alert_count = cursor.fetchone()[0]
            assert alert_count >= 1
    
    def test_alert_not_triggered_below_threshold(self, metrics_processor, test_db_connection,
                                               cost_alert_config, alert_service):
        """Test that alerts are not triggered when metrics are below thresholds."""
        # Create low-cost events that should not trigger the alert
        low_cost_events = []
        for i in range(5):
            low_cost_events.append({
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "latency_ms": 500,
                "cost": 0.0005,  # Low cost, should not trigger alert
                "status": "success"
            })
        
        # Process events
        with patch.object(alert_service, 'send_alert') as mock_send_alert:
            # Inject the alert service into the metrics processor
            metrics_processor.alert_service = alert_service
            
            # Process the events
            metrics_processor.process_events(low_cost_events)
            
            # Check if alert was triggered
            cursor = test_db_connection.cursor()
            cursor.execute(
                """
                SELECT SUM(cost) FROM request_metrics 
                WHERE provider = 'openai' AND model = 'gpt-4' AND
                timestamp > %s
                """,
                (datetime.now() - timedelta(minutes=10),)
            )
            total_cost = cursor.fetchone()[0]
            
            # Verify total cost is below threshold
            assert total_cost < cost_alert_config.thresholds[0].value
            
            # Verify alert was not triggered
            mock_send_alert.assert_not_called()
    
    def test_error_rate_alert(self, metrics_processor, test_db_connection, alert_service):
        """Test that error rate alerts are triggered correctly."""
        # Create an error rate alert config
        error_config = AlertConfig(
            name="Test Error Rate Alert",
            description="Alert when error rate exceeds threshold",
            enabled=True,
            alert_type=AlertType.ERROR_RATE,
            severity=AlertSeverity.HIGH,
            thresholds=[
                AlertThreshold(
                    metric="error_rate",
                    operator=">",
                    value=20.0,  # 20% error rate threshold
                    duration_minutes=5
                )
            ],
            filters={"provider": "openai", "model": "gpt-4"},
            notify_emails=["admin@example.com"]
        )
        
        config_id = alert_service.create_alert_config(error_config)
        error_config.id = config_id
        
        # Create events with a high error rate
        events = []
        # Add 8 successful events
        for i in range(8):
            events.append({
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 1000,
                "cost": 0.0075,
                "status": "success"
            })
        
        # Add 2 error events (20% error rate)
        for i in range(2):
            events.append({
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": f"req-{uuid.uuid4()}",
                "user_id": "test-user",
                "prompt_tokens": 100,
                "completion_tokens": 0,
                "total_tokens": 100,
                "latency_ms": 500,
                "cost": 0.0025,
                "status": "error",
                "error": "rate_limit_exceeded"
            })
        
        # Process events
        with patch.object(alert_service, 'send_alert') as mock_send_alert:
            # Set up the mock to return True
            mock_send_alert.return_value = True
            
            # Inject the alert service into the metrics processor
            metrics_processor.alert_service = alert_service
            
            # Process the events
            metrics_processor.process_events(events)
            
            # Verify alert was triggered
            mock_send_alert.assert_called()
            
            # Verify alert event was created
            cursor = test_db_connection.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM alert_events 
                WHERE config_id = %s
                """,
                (error_config.id,)
            )
            alert_count = cursor.fetchone()[0]
            assert alert_count >= 1
