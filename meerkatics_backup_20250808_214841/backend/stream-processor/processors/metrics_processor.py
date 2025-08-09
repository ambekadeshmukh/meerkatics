import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class MetricsProcessor:
    """
    Process and aggregate LLM monitoring metrics.
    
    This processor handles:
    - Aggregating metrics by time period
    - Calculating derived metrics
    - Generating time-series data
    - Providing statistical summaries
    """
    
    def __init__(self, max_history: int = 10000):
        """
        Initialize the metrics processor.
        
        Args:
            max_history: Maximum number of data points to keep in memory
        """
        self.max_history = max_history
        
        # Store metrics by type and provider/model/application
        self.metrics = defaultdict(lambda: defaultdict(list))
        
        # Track aggregated metrics by time period
        self.hourly_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.daily_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        # Track last aggregation time
        self.last_hourly_aggregation = datetime.now()
        self.last_daily_aggregation = datetime.now()
    
    def add_metric(
        self, 
        metric_type: str, 
        value: float, 
        timestamp: datetime,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add a new metric data point.
        
        Args:
            metric_type: Type of metric (inference_time, prompt_tokens, etc.)
            value: The metric value
            timestamp: Timestamp of the metric
            metadata: Additional metadata about the metric
        """
        # Create a key for this provider/model/application combination
        provider = metadata.get("provider", "unknown")
        model = metadata.get("model", "unknown")
        application = metadata.get("application", "unknown")
        key = f"{provider}:{model}:{application}"
        
        # Create a data point with all information
        data_point = {
            "value": value,
            "timestamp": timestamp,
            **metadata
        }
        
        # Add to the metrics store
        self.metrics[metric_type][key].append(data_point)
        
        # Trim if needed
        if len(self.metrics[metric_type][key]) > self.max_history:
            self.metrics[metric_type][key] = self.metrics[metric_type][key][-self.max_history:]
        
        # Check if we need to update aggregations
        self._check_aggregation_schedule()
    
    def _check_aggregation_schedule(self) -> None:
        """Check if it's time to update aggregations."""
        now = datetime.now()
        
        # Hourly aggregation every 10 minutes
        if (now - self.last_hourly_aggregation).total_seconds() > 600:  # 10 minutes
            self._aggregate_hourly_metrics()
            self.last_hourly_aggregation = now
        
        # Daily aggregation every hour
        if (now - self.last_daily_aggregation).total_seconds() > 3600:  # 1 hour
            self._aggregate_daily_metrics()
            self.last_daily_aggregation = now
    
    def _aggregate_hourly_metrics(self) -> None:
        """Aggregate metrics by hour."""
        logger.info("Aggregating hourly metrics")
        
        # Current time rounded to the hour
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # Process each metric type
        for metric_type, keys in self.metrics.items():
            for key, data_points in keys.items():
                # Group data points by hour
                hour_groups = defaultdict(list)
                
                for point in data_points:
                    # Skip points without timestamp
                    if "timestamp" not in point:
                        continue
                        
                    # Get the hour bucket
                    timestamp = point["timestamp"]
                    hour_bucket = timestamp.replace(minute=0, second=0, microsecond=0)
                    
                    # Only process recent data (last 48 hours)
                    if now - hour_bucket <= timedelta(hours=48):
                        hour_groups[hour_bucket].append(point["value"])
                
                # Calculate statistics for each hour
                for hour, values in hour_groups.items():
                    if not values:
                        continue
                        
                    stats = {
                        "mean": float(np.mean(values)),
                        "median": float(np.median(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "std": float(np.std(values)) if len(values) > 1 else 0.0,
                        "count": len(values),
                        "sum": float(np.sum(values))
                    }
                    
                    # Store in hourly metrics
                    self.hourly_metrics[metric_type][key][hour] = stats
    
    def _aggregate_daily_metrics(self) -> None:
        """Aggregate metrics by day."""
        logger.info("Aggregating daily metrics")
        
        # Current time rounded to the day
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Process each metric type
        for metric_type, keys in self.metrics.items():
            for key, data_points in keys.items():
                # Group data points by day
                day_groups = defaultdict(list)
                
                for point in data_points:
                    # Skip points without timestamp
                    if "timestamp" not in point:
                        continue
                        
                    # Get the day bucket
                    timestamp = point["timestamp"]
                    day_bucket = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Only process recent data (last 30 days)
                    if now - day_bucket <= timedelta(days=30):
                        day_groups[day_bucket].append(point["value"])
                
                # Calculate statistics for each day
                for day, values in day_groups.items():
                    if not values:
                        continue
                        
                    stats = {
                        "mean": float(np.mean(values)),
                        "median": float(np.median(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "std": float(np.std(values)) if len(values) > 1 else 0.0,
                        "count": len(values),
                        "sum": float(np.sum(values))
                    }
                    
                    # Store in daily metrics
                    self.daily_metrics[metric_type][key][day] = stats
    
    def get_timeseries(
        self, 
        metric_type: str, 
        provider: str, 
        model: str, 
        application: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        aggregation: str = "hourly"
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for a specific metric.
        
        Args:
            metric_type: Type of metric (inference_time, prompt_tokens, etc.)
            provider: LLM provider
            model: Model name
            application: Application name
            start_time: Start time for the time series
            end_time: End time for the time series
            aggregation: Aggregation level ("hourly" or "daily")
            
        Returns:
            List of time series data points
        """
        key = f"{provider}:{model}:{application}"
        
        # Set default time range if not provided
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            if aggregation == "hourly":
                start_time = end_time - timedelta(days=2)  # 48 hours
            else:
                start_time = end_time - timedelta(days=30)  # 30 days
        
        # Get the appropriate aggregation data
        if aggregation == "hourly":
            if metric_type not in self.hourly_metrics or key not in self.hourly_metrics[metric_type]:
                return []
                
            agg_data = self.hourly_metrics[metric_type][key]
        else:  # daily
            if metric_type not in self.daily_metrics or key not in self.daily_metrics[metric_type]:
                return []
                
            agg_data = self.daily_metrics[metric_type][key]
        
        # Filter by time range and convert to list
        result = []
        for timestamp, stats in agg_data.items():
            if start_time <= timestamp <= end_time:
                result.append({
                    "timestamp": timestamp,
                    **stats
                })
        
        # Sort by timestamp
        result.sort(key=lambda x: x["timestamp"])
        
        return result
    
    def get_summary(
        self, 
        metric_type: str, 
        provider: str, 
        model: str, 
        application: str,
        time_window: str = "1d"
    ) -> Dict[str, Any]:
        """
        Get a summary of a specific metric over a time window.
        
        Args:
            metric_type: Type of metric (inference_time, prompt_tokens, etc.)
            provider: LLM provider
            model: Model name
            application: Application name
            time_window: Time window for the summary (e.g., "1h", "1d", "7d", "30d")
            
        Returns:
            Summary statistics
        """
        key = f"{provider}:{model}:{application}"
        
        # Parse time window
        amount = int(time_window[:-1])
        unit = time_window[-1]
        
        if unit == "h":
            delta = timedelta(hours=amount)
        elif unit == "d":
            delta = timedelta(days=amount)
        else:
            raise ValueError(f"Invalid time window: {time_window}")
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - delta
        
        # Get raw data points in the time range
        if metric_type not in self.metrics or key not in self.metrics[metric_type]:
            return {
                "count": 0,
                "available": False
            }
            
        data_points = self.metrics[metric_type][key]
        values_in_range = []
        
        for point in data_points:
            if "timestamp" in point and start_time <= point["timestamp"] <= end_time:
                values_in_range.append(point["value"])
        
        # Calculate statistics
        if not values_in_range:
            return {
                "count": 0,
                "available": False
            }
            
        return {
            "mean": float(np.mean(values_in_range)),
            "median": float(np.median(values_in_range)),
            "min": float(np.min(values_in_range)),
            "max": float(np.max(values_in_range)),
            "std": float(np.std(values_in_range)) if len(values_in_range) > 1 else 0.0,
            "count": len(values_in_range),
            "sum": float(np.sum(values_in_range)),
            "available": True
        }
    
    def get_top_consumers(
        self, 
        metric_type: str,
        limit: int = 5,
        time_window: str = "1d"
    ) -> List[Dict[str, Any]]:
        """
        Get top consumers for a specific metric.
        
        Args:
            metric_type: Type of metric (inference_time, prompt_tokens, etc.)
            limit: Maximum number of results to return
            time_window: Time window for analysis (e.g., "1h", "1d", "7d", "30d")
            
        Returns:
            List of top consumers with their statistics
        """
        # Parse time window
        amount = int(time_window[:-1])
        unit = time_window[-1]
        
        if unit == "h":
            delta = timedelta(hours=amount)
        elif unit == "d":
            delta = timedelta(days=amount)
        else:
            raise ValueError(f"Invalid time window: {time_window}")
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - delta
        
        # Calculate sums for each key
        results = []
        
        if metric_type in self.metrics:
            for key, data_points in self.metrics[metric_type].items():
                # Split the key
                provider, model, application = key.split(":", 2)
                
                # Calculate sum in time range
                values_in_range = []
                for point in data_points:
                    if "timestamp" in point and start_time <= point["timestamp"] <= end_time:
                        values_in_range.append(point["value"])
                
                if values_in_range:
                    results.append({
                        "provider": provider,
                        "model": model,
                        "application": application,
                        "sum": float(np.sum(values_in_range)),
                        "count": len(values_in_range),
                        "mean": float(np.mean(values_in_range))
                    })
        
        # Sort by sum (descending) and take top N
        results.sort(key=lambda x: x["sum"], reverse=True)
        return results[:limit]