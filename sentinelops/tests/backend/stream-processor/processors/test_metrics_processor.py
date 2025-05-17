import unittest
from unittest.mock import patch, MagicMock, call
import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add the parent directory to the path to import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from sentinelops.backend.stream_processor.processors.metrics_processor import MetricsProcessor

class TestMetricsProcessor(unittest.TestCase):
    """Test suite for the MetricsProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the database connection
        self.db_conn_mock = MagicMock()
        self.cursor_mock = MagicMock()
        self.db_conn_mock.cursor.return_value = self.cursor_mock
        
        # Create sample events
        self.sample_events = [
            {
                "event_id": "event1",
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-4",
                "application": "chatbot",
                "request_id": "req1",
                "user_id": "user1",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "latency_ms": 1200,
                "cost": 0.0075,
                "status": "success"
            },
            {
                "event_id": "event2",
                "timestamp": datetime.now().isoformat(),
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "application": "summarizer",
                "request_id": "req2",
                "user_id": "user2",
                "prompt_tokens": 200,
                "completion_tokens": 100,
                "total_tokens": 300,
                "latency_ms": 800,
                "cost": 0.0045,
                "status": "success"
            },
            {
                "event_id": "event3",
                "timestamp": datetime.now().isoformat(),
                "provider": "anthropic",
                "model": "claude-2",
                "application": "chatbot",
                "request_id": "req3",
                "user_id": "user1",
                "prompt_tokens": 300,
                "completion_tokens": 150,
                "total_tokens": 450,
                "latency_ms": 1500,
                "cost": 0.0135,
                "status": "error"
            }
        ]
        
        # Initialize the processor with the mock DB connection
        self.processor = MetricsProcessor(db_conn=self.db_conn_mock)

    def test_init(self):
        """Test initialization of the MetricsProcessor."""
        self.assertEqual(self.processor.db_conn, self.db_conn_mock)
        self.assertIsNotNone(self.processor.metrics_cache)
        self.assertIsNotNone(self.processor.time_windows)

    def test_process_event(self):
        """Test processing a single event."""
        event = self.sample_events[0]
        
        # Mock the database operations
        self.cursor_mock.execute.return_value = None
        self.cursor_mock.fetchone.return_value = None
        
        # Process the event
        result = self.processor.process_event(event)
        
        # Check that the event was stored in the database
        self.cursor_mock.execute.assert_called()
        self.db_conn_mock.commit.assert_called_once()
        
        # Check the result
        self.assertTrue(result)
        
        # Check that metrics were updated in the cache
        cache_key = f"{event['provider']}:{event['model']}:{event['application']}"
        self.assertIn(cache_key, self.processor.metrics_cache)
        
        metrics = self.processor.metrics_cache[cache_key]
        self.assertEqual(metrics["request_count"], 1)
        self.assertEqual(metrics["total_tokens"], event["total_tokens"])
        self.assertEqual(metrics["prompt_tokens"], event["prompt_tokens"])
        self.assertEqual(metrics["completion_tokens"], event["completion_tokens"])
        self.assertEqual(metrics["total_cost"], event["cost"])
        self.assertEqual(metrics["success_count"], 1)
        self.assertEqual(metrics["error_count"], 0)
        self.assertEqual(metrics["latency_sum"], event["latency_ms"])

    def test_process_event_with_error(self):
        """Test processing an event with error status."""
        event = self.sample_events[2]  # This is an error event
        
        # Mock the database operations
        self.cursor_mock.execute.return_value = None
        self.cursor_mock.fetchone.return_value = None
        
        # Process the event
        result = self.processor.process_event(event)
        
        # Check the result
        self.assertTrue(result)
        
        # Check that metrics were updated correctly for an error event
        cache_key = f"{event['provider']}:{event['model']}:{event['application']}"
        metrics = self.processor.metrics_cache[cache_key]
        self.assertEqual(metrics["request_count"], 1)
        self.assertEqual(metrics["error_count"], 1)
        self.assertEqual(metrics["success_count"], 0)

    def test_process_multiple_events(self):
        """Test processing multiple events."""
        # Mock the database operations
        self.cursor_mock.execute.return_value = None
        self.cursor_mock.fetchone.return_value = None
        
        # Process all sample events
        for event in self.sample_events:
            self.processor.process_event(event)
        
        # Check that metrics were aggregated correctly
        self.assertEqual(len(self.processor.metrics_cache), 3)  # 3 unique provider:model:application combinations
        
        # Check metrics for the chatbot application with OpenAI
        chatbot_openai_key = "openai:gpt-4:chatbot"
        chatbot_metrics = self.processor.metrics_cache[chatbot_openai_key]
        self.assertEqual(chatbot_metrics["request_count"], 1)
        self.assertEqual(chatbot_metrics["total_tokens"], 150)
        self.assertEqual(chatbot_metrics["total_cost"], 0.0075)
        
        # Check metrics for the summarizer application
        summarizer_key = "openai:gpt-3.5-turbo:summarizer"
        summarizer_metrics = self.processor.metrics_cache[summarizer_key]
        self.assertEqual(summarizer_metrics["request_count"], 1)
        self.assertEqual(summarizer_metrics["total_tokens"], 300)
        self.assertEqual(summarizer_metrics["total_cost"], 0.0045)
        
        # Check metrics for the chatbot application with Anthropic
        chatbot_anthropic_key = "anthropic:claude-2:chatbot"
        chatbot_anthropic_metrics = self.processor.metrics_cache[chatbot_anthropic_key]
        self.assertEqual(chatbot_anthropic_metrics["request_count"], 1)
        self.assertEqual(chatbot_anthropic_metrics["total_tokens"], 450)
        self.assertEqual(chatbot_anthropic_metrics["error_count"], 1)

    def test_calculate_time_window_metrics(self):
        """Test calculating metrics for a specific time window."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            (100, 50, 150, 1200, 0.0075, "success", "2023-01-01T12:00:00"),
            (200, 100, 300, 800, 0.0045, "success", "2023-01-01T12:05:00"),
            (300, 150, 450, 1500, 0.0135, "error", "2023-01-01T12:10:00")
        ]
        
        # Calculate metrics for the last hour
        window = "1h"
        provider = "openai"
        model = "gpt-4"
        application = "chatbot"
        
        metrics = self.processor.calculate_time_window_metrics(window, provider, model, application)
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the calculated metrics
        self.assertEqual(metrics["request_count"], 3)
        self.assertEqual(metrics["total_tokens"], 900)
        self.assertEqual(metrics["prompt_tokens"], 600)
        self.assertEqual(metrics["completion_tokens"], 300)
        self.assertEqual(metrics["total_cost"], 0.0255)
        self.assertEqual(metrics["success_count"], 2)
        self.assertEqual(metrics["error_count"], 1)
        self.assertEqual(metrics["error_rate"], 1/3)
        self.assertEqual(metrics["avg_latency"], 1166.67)
        self.assertEqual(metrics["avg_tokens_per_request"], 300)

    def test_get_top_models_by_usage(self):
        """Test getting top models by usage."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            ("openai", "gpt-4", 1000),
            ("openai", "gpt-3.5-turbo", 800),
            ("anthropic", "claude-2", 600),
            ("anthropic", "claude-instant-1", 400),
            ("cohere", "command", 200)
        ]
        
        # Get top 3 models
        top_models = self.processor.get_top_models_by_usage(limit=3)
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the result
        self.assertEqual(len(top_models), 3)
        self.assertEqual(top_models[0]["provider"], "openai")
        self.assertEqual(top_models[0]["model"], "gpt-4")
        self.assertEqual(top_models[0]["total_tokens"], 1000)
        self.assertEqual(top_models[1]["provider"], "openai")
        self.assertEqual(top_models[1]["model"], "gpt-3.5-turbo")
        self.assertEqual(top_models[2]["provider"], "anthropic")
        self.assertEqual(top_models[2]["model"], "claude-2")

    def test_get_top_applications_by_cost(self):
        """Test getting top applications by cost."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            ("chatbot", 0.0500),
            ("summarizer", 0.0300),
            ("translator", 0.0200),
            ("code-assistant", 0.0100),
            ("image-generator", 0.0050)
        ]
        
        # Get top 3 applications
        top_apps = self.processor.get_top_applications_by_cost(limit=3)
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the result
        self.assertEqual(len(top_apps), 3)
        self.assertEqual(top_apps[0]["application"], "chatbot")
        self.assertEqual(top_apps[0]["total_cost"], 0.0500)
        self.assertEqual(top_apps[1]["application"], "summarizer")
        self.assertEqual(top_apps[2]["application"], "translator")

    def test_get_error_rate_by_model(self):
        """Test getting error rates by model."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            ("openai", "gpt-4", 100, 5),
            ("openai", "gpt-3.5-turbo", 200, 10),
            ("anthropic", "claude-2", 150, 15)
        ]
        
        # Get error rates
        error_rates = self.processor.get_error_rate_by_model()
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the result
        self.assertEqual(len(error_rates), 3)
        self.assertEqual(error_rates[0]["provider"], "openai")
        self.assertEqual(error_rates[0]["model"], "gpt-4")
        self.assertEqual(error_rates[0]["error_rate"], 0.05)
        self.assertEqual(error_rates[1]["provider"], "openai")
        self.assertEqual(error_rates[1]["model"], "gpt-3.5-turbo")
        self.assertEqual(error_rates[1]["error_rate"], 0.05)
        self.assertEqual(error_rates[2]["provider"], "anthropic")
        self.assertEqual(error_rates[2]["model"], "claude-2")
        self.assertEqual(error_rates[2]["error_rate"], 0.10)

    def test_get_usage_over_time(self):
        """Test getting usage over time."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            ("2023-01-01", 1000),
            ("2023-01-02", 1200),
            ("2023-01-03", 900),
            ("2023-01-04", 1500),
            ("2023-01-05", 1300)
        ]
        
        # Get usage over time
        usage = self.processor.get_usage_over_time(
            interval="day",
            start_date="2023-01-01",
            end_date="2023-01-05"
        )
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the result
        self.assertEqual(len(usage), 5)
        self.assertEqual(usage[0]["date"], "2023-01-01")
        self.assertEqual(usage[0]["total_tokens"], 1000)
        self.assertEqual(usage[3]["date"], "2023-01-04")
        self.assertEqual(usage[3]["total_tokens"], 1500)

    def test_get_cost_over_time(self):
        """Test getting cost over time."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            ("2023-01-01", 0.0100),
            ("2023-01-02", 0.0120),
            ("2023-01-03", 0.0090),
            ("2023-01-04", 0.0150),
            ("2023-01-05", 0.0130)
        ]
        
        # Get cost over time
        cost = self.processor.get_cost_over_time(
            interval="day",
            start_date="2023-01-01",
            end_date="2023-01-05"
        )
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the result
        self.assertEqual(len(cost), 5)
        self.assertEqual(cost[0]["date"], "2023-01-01")
        self.assertEqual(cost[0]["total_cost"], 0.0100)
        self.assertEqual(cost[3]["date"], "2023-01-04")
        self.assertEqual(cost[3]["total_cost"], 0.0150)

    def test_get_latency_statistics(self):
        """Test getting latency statistics."""
        # Mock the database query results
        self.cursor_mock.fetchall.return_value = [
            (800, 1500, 1100, 200)
        ]
        
        # Get latency statistics
        stats = self.processor.get_latency_statistics(
            provider="openai",
            model="gpt-4",
            application="chatbot"
        )
        
        # Check that the correct query was executed
        self.cursor_mock.execute.assert_called()
        
        # Check the result
        self.assertEqual(stats["min_latency"], 800)
        self.assertEqual(stats["max_latency"], 1500)
        self.assertEqual(stats["avg_latency"], 1100)
        self.assertEqual(stats["std_latency"], 200)

    def test_get_summary_metrics(self):
        """Test getting summary metrics."""
        # Mock the metrics calculation methods
        with patch.object(self.processor, 'calculate_time_window_metrics') as mock_calc:
            mock_calc.return_value = {
                "request_count": 1000,
                "total_tokens": 150000,
                "prompt_tokens": 50000,
                "completion_tokens": 100000,
                "total_cost": 2.25,
                "success_count": 950,
                "error_count": 50,
                "error_rate": 0.05,
                "avg_latency": 1200,
                "avg_tokens_per_request": 150
            }
            
            # Get summary metrics
            summary = self.processor.get_summary_metrics()
            
            # Check that the calculation method was called with the right parameters
            mock_calc.assert_called_with("24h", None, None, None)
            
            # Check the result
            self.assertEqual(summary["request_count"], 1000)
            self.assertEqual(summary["total_tokens"], 150000)
            self.assertEqual(summary["total_cost"], 2.25)
            self.assertEqual(summary["error_rate"], 0.05)
            self.assertEqual(summary["avg_latency"], 1200)

    def test_get_dashboard_metrics(self):
        """Test getting dashboard metrics."""
        # Mock the methods that get_dashboard_metrics calls
        with patch.multiple(
            self.processor,
            get_summary_metrics=MagicMock(return_value={
                "request_count": 1000,
                "total_tokens": 150000,
                "total_cost": 2.25,
                "error_rate": 0.05,
                "avg_latency": 1200
            }),
            get_top_models_by_usage=MagicMock(return_value=[
                {"provider": "openai", "model": "gpt-4", "total_tokens": 80000},
                {"provider": "openai", "model": "gpt-3.5-turbo", "total_tokens": 50000},
                {"provider": "anthropic", "model": "claude-2", "total_tokens": 20000}
            ]),
            get_top_applications_by_cost=MagicMock(return_value=[
                {"application": "chatbot", "total_cost": 1.50},
                {"application": "summarizer", "total_cost": 0.50},
                {"application": "translator", "total_cost": 0.25}
            ]),
            get_error_rate_by_model=MagicMock(return_value=[
                {"provider": "openai", "model": "gpt-4", "error_rate": 0.03},
                {"provider": "openai", "model": "gpt-3.5-turbo", "error_rate": 0.05},
                {"provider": "anthropic", "model": "claude-2", "error_rate": 0.07}
            ]),
            get_usage_over_time=MagicMock(return_value=[
                {"date": "2023-01-01", "total_tokens": 30000},
                {"date": "2023-01-02", "total_tokens": 35000},
                {"date": "2023-01-03", "total_tokens": 40000},
                {"date": "2023-01-04", "total_tokens": 45000}
            ]),
            get_cost_over_time=MagicMock(return_value=[
                {"date": "2023-01-01", "total_cost": 0.45},
                {"date": "2023-01-02", "total_cost": 0.52},
                {"date": "2023-01-03", "total_cost": 0.60},
                {"date": "2023-01-04", "total_cost": 0.68}
            ])
        ):
            # Get dashboard metrics
            dashboard = self.processor.get_dashboard_metrics()
            
            # Check that all the methods were called
            self.processor.get_summary_metrics.assert_called_once()
            self.processor.get_top_models_by_usage.assert_called_once()
            self.processor.get_top_applications_by_cost.assert_called_once()
            self.processor.get_error_rate_by_model.assert_called_once()
            self.processor.get_usage_over_time.assert_called_once()
            self.processor.get_cost_over_time.assert_called_once()
            
            # Check the structure of the result
            self.assertIn("summary", dashboard)
            self.assertIn("top_models", dashboard)
            self.assertIn("top_applications", dashboard)
            self.assertIn("error_rates", dashboard)
            self.assertIn("usage_over_time", dashboard)
            self.assertIn("cost_over_time", dashboard)
            
            # Check some values
            self.assertEqual(dashboard["summary"]["request_count"], 1000)
            self.assertEqual(len(dashboard["top_models"]), 3)
            self.assertEqual(dashboard["top_models"][0]["model"], "gpt-4")
            self.assertEqual(len(dashboard["usage_over_time"]), 4)

if __name__ == '__main__':
    unittest.main()
