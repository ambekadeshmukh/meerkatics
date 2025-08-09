import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Basic anomaly detection for LLM monitoring metrics.
    
    This detector uses simple statistical methods to identify anomalies in:
    - Inference time
    - Token usage
    - Error rates
    - Cost metrics
    """
    
    def __init__(
        self,
        window_size: int = 100,
        z_score_threshold: float = 3.0,
        min_data_points: int = 10
    ):
        """
        Initialize the anomaly detector.
        
        Args:
            window_size: Size of the window for moving statistics
            z_score_threshold: Z-score threshold for anomaly detection
            min_data_points: Minimum number of data points required for analysis
        """
        self.window_size = window_size
        self.z_score_threshold = z_score_threshold
        self.min_data_points = min_data_points
        
        # Metrics storage by type and provider/model
        self.metrics = {
            "inference_time": defaultdict(list),
            "prompt_tokens": defaultdict(list),
            "completion_tokens": defaultdict(list),
            "total_tokens": defaultdict(list),
            "error_rate": defaultdict(list),
            "cost": defaultdict(list)
        }
        
        # Store recent anomalies to prevent duplicate alerts
        self.recent_anomalies = []
        self.max_recent_anomalies = 100
    
    def add_metric(
        self, 
        metric_type: str, 
        value: float, 
        provider: str, 
        model: str, 
        application: str
    ) -> None:
        """
        Add a new metric data point.
        
        Args:
            metric_type: Type of metric (inference_time, prompt_tokens, etc.)
            value: The metric value
            provider: LLM provider (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-4", "claude-2")
            application: Application name
        """
        if metric_type not in self.metrics:
            logger.warning(f"Unknown metric type: {metric_type}")
            return
            
        # Create a key for this provider/model/application combination
        key = f"{provider}:{model}:{application}"
        
        # Add the data point
        self.metrics[metric_type][key].append(value)
        
        # Keep only the most recent window_size data points
        if len(self.metrics[metric_type][key]) > self.window_size:
            self.metrics[metric_type][key] = self.metrics[metric_type][key][-self.window_size:]
    
    def detect_anomalies(
        self, 
        metric_type: str, 
        value: float, 
        provider: str, 
        model: str, 
        application: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if a new data point is an anomaly.
        
        Args:
            metric_type: Type of metric (inference_time, prompt_tokens, etc.)
            value: The metric value to check
            provider: LLM provider (e.g., "openai", "anthropic")
            model: Model name (e.g., "gpt-4", "claude-2")
            application: Application name
            
        Returns:
            Anomaly information if detected, None otherwise
        """
        if metric_type not in self.metrics:
            return None
            
        # Create a key for this provider/model/application combination
        key = f"{provider}:{model}:{application}"
        
        # Get historical data
        history = self.metrics[metric_type][key]
        
        # Need enough data points for meaningful analysis
        if len(history) < self.min_data_points:
            return None
            
        # Calculate statistics
        mean = np.mean(history)
        std = np.std(history)
        
        # Avoid division by zero
        if std == 0:
            return None
            
        # Calculate z-score
        z_score = abs((value - mean) / std)
        
        # Check if this is an anomaly
        if z_score > self.z_score_threshold:
            anomaly = {
                "metric_type": metric_type,
                "value": value,
                "z_score": z_score,
                "mean": mean,
                "std": std,
                "provider": provider,
                "model": model,
                "application": application,
                "timestamp": datetime.now(),
                "anomaly_type": "high" if value > mean else "low"
            }
            
            # Check if this is a duplicate of a recent anomaly
            if not self._is_duplicate_anomaly(anomaly):
                self._add_recent_anomaly(anomaly)
                return anomaly
                
        return None
    
    def _is_duplicate_anomaly(self, anomaly: Dict[str, Any]) -> bool:
        """
        Check if an anomaly is a duplicate of a recent one.
        
        Args:
            anomaly: The anomaly to check
            
        Returns:
            True if this is a duplicate, False otherwise
        """
        # Create a key for comparison
        key = f"{anomaly['metric_type']}:{anomaly['provider']}:{anomaly['model']}:{anomaly['application']}:{anomaly['anomaly_type']}"
        
        # Check if we've seen this recently (within 5 minutes)
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        
        for recent in self.recent_anomalies:
            recent_key = f"{recent['metric_type']}:{recent['provider']}:{recent['model']}:{recent['application']}:{recent['anomaly_type']}"
            
            if key == recent_key and recent["timestamp"] > five_minutes_ago:
                return True
                
        return False
    
    def _add_recent_anomaly(self, anomaly: Dict[str, Any]) -> None:
        """
        Add an anomaly to the recent anomalies list.
        
        Args:
            anomaly: The anomaly to add
        """
        self.recent_anomalies.append(anomaly)
        
        # Keep only the most recent anomalies
        if len(self.recent_anomalies) > self.max_recent_anomalies:
            self.recent_anomalies = self.recent_anomalies[-self.max_recent_anomalies:]
    
    def get_metrics_summary(self, provider: str, model: str, application: str) -> Dict[str, Any]:
        """
        Get a summary of metrics for a specific provider/model/application.
        
        Args:
            provider: LLM provider
            model: Model name
            application: Application name
            
        Returns:
            Summary statistics for all metrics
        """
        key = f"{provider}:{model}:{application}"
        summary = {}
        
        for metric_type, data_by_key in self.metrics.items():
            if key in data_by_key and len(data_by_key[key]) > 0:
                data = data_by_key[key]
                summary[metric_type] = {
                    "mean": float(np.mean(data)),
                    "median": float(np.median(data)),
                    "min": float(np.min(data)),
                    "max": float(np.max(data)),
                    "std": float(np.std(data)),
                    "count": len(data)
                }
                
        return summary