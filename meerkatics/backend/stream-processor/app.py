# stream-processor/app.py
import os
import json
import time
import logging
from typing import Dict, Any, List
import sqlite3
import os.path
import json as json_lib
from kafka import KafkaConsumer
import minio
import uuid
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("stream-processor")

# Configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "llm-monitoring")
SQLITE_DB_PATH = os.environ.get("SQLITE_DB_PATH", "./meerkatics.db")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "llm-requests")

class StreamProcessor:
    """Process LLM monitoring events from Kafka in real-time."""
    
    def __init__(self):
        self.connect_kafka()
        self.connect_postgres()
        self.connect_minio()
        
        # In-memory state for anomaly detection
        self.metrics_buffer = {
            "inference_time": [],
            "prompt_tokens": [],
            "completion_tokens": [],
            "total_tokens": [],
            "errors": []
        }
        self.max_buffer_size = 1000
        self.anomaly_thresholds = {
            "inference_time": 5.0,  # 5 seconds
            "error_rate": 0.1       # 10% error rate
        }
        
    def connect_kafka(self):
        """Connect to Kafka broker."""
        logger.info(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='llm-stream-processor',
            enable_auto_commit=True,
            auto_commit_interval_ms=5000
        )
        logger.info("Connected to Kafka")
        
    def connect_postgres(self):
        """Connect to SQLite database."""
        logger.info(f"Connecting to SQLite database at {SQLITE_DB_PATH}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        
        self.conn = sqlite3.connect(SQLITE_DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            provider TEXT,
            model TEXT,
            application TEXT,
            environment TEXT,
            total_tokens INTEGER,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            inference_time REAL,
            cost REAL,
            status TEXT,
            error_message TEXT,
            metadata TEXT
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            anomaly_type TEXT,
            provider TEXT,
            model TEXT,
            application TEXT,
            description TEXT,
            severity TEXT
        )
        ''')
        
        self.conn.commit()
        logger.info("Connected to SQLite database")
        
    def connect_minio(self):
        """Connect to MinIO object storage."""
        logger.info(f"Connecting to MinIO at {MINIO_ENDPOINT}")
        self.minio_client = minio.Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False  # Set to True if using HTTPS
        )
        
        # Create bucket if it doesn't exist
        if not self.minio_client.bucket_exists(MINIO_BUCKET):
            self.minio_client.make_bucket(MINIO_BUCKET)
            logger.info(f"Created MinIO bucket: {MINIO_BUCKET}")
        
        logger.info("Connected to MinIO")
        
    def store_request_response(self, data: Dict[str, Any]) -> str:
        """Store full request/response in MinIO and return the object ID."""
        # Only store if prompt or completion is included
        if "prompt" not in data and "completion" not in data:
            return None
            
        object_id = f"{data['request_id']}.json"
        
        # Create a filtered copy with just the request/response data
        storage_data = {
            "request_id": data["request_id"],
            "timestamp": data["timestamp"],
            "provider": data["provider"],
            "model": data["model"]
        }
        
        if "prompt" in data:
            storage_data["prompt"] = data["prompt"]
            
        if "completion" in data:
            storage_data["completion"] = data["completion"]
        
        # Convert to JSON and store in MinIO
        json_data = json.dumps(storage_data).encode('utf-8')
        self.minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_id,
            data=json.dumps(storage_data).encode('utf-8'),
            length=len(json_data),
            content_type="application/json"
        )
        
        return object_id
        
    def process_event(self, data: Dict[str, Any]):
        """Process a single monitoring event."""
        try:
            # Store request/response data if present
            object_id = self.store_request_response(data)
            
            # Extract metrics for storage and analysis
            metrics = {
                "request_id": data["request_id"],
                "timestamp": datetime.fromtimestamp(data["timestamp"]),
                "provider": data["provider"],
                "model": data["model"],
                "application": data["application"],
                "environment": data["environment"],
                "inference_time": data["inference_time"],
                "success": data["success"],
                "prompt_tokens": data["prompt_tokens"],
                "memory_used": data.get("memory_used", 0),
                "storage_object_id": object_id
            }
            
            # Add completion tokens if successful
            if data["success"] and "completion_tokens" in data:
                metrics["completion_tokens"] = data["completion_tokens"] 
                metrics["total_tokens"] = data["total_tokens"]
                metrics["estimated_cost"] = data["estimated_cost"]
            
            # Add error info if failed
            if not data["success"] and "error" in data:
                metrics["error"] = data["error"]
            
            # Insert metrics into database
            self.store_metrics(metrics)
            
            # Update in-memory state for anomaly detection
            self.update_metrics_buffer(metrics)
            
            # Check for anomalies
            anomalies = self.detect_anomalies(metrics)
            if anomalies:
                self.report_anomalies(metrics, anomalies)
                
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}", exc_info=True)
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in SQLite database."""
        columns = list(metrics.keys())
        values = [metrics[col] for col in columns]
        placeholders = ["?"] * len(columns)
        
        # Convert any complex objects to JSON strings
        for i, val in enumerate(values):
            if isinstance(val, dict) or isinstance(val, list):
                values[i] = json_lib.dumps(val)
        
        query = f"""
        INSERT INTO request_metrics ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        """
        
        self.cursor.execute(query, values)
        self.conn.commit()
    
    def update_metrics_buffer(self, metrics: Dict[str, Any]):
        """Update in-memory metrics buffer for anomaly detection."""
        # Add new metrics to buffer
        self.metrics_buffer["inference_time"].append(metrics["inference_time"])
        self.metrics_buffer["prompt_tokens"].append(metrics["prompt_tokens"])
        
        if "completion_tokens" in metrics:
            self.metrics_buffer["completion_tokens"].append(metrics["completion_tokens"])
            self.metrics_buffer["total_tokens"].append(metrics["total_tokens"])
        
        if not metrics["success"]:
            self.metrics_buffer["errors"].append(metrics)
            
        # Trim buffer if it gets too large
        if len(self.metrics_buffer["inference_time"]) > self.max_buffer_size:
            for key in self.metrics_buffer:
                if isinstance(self.metrics_buffer[key], list) and len(self.metrics_buffer[key]) > self.max_buffer_size:
                    self.metrics_buffer[key] = self.metrics_buffer[key][-self.max_buffer_size:]
    
    def detect_anomalies(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics."""
        anomalies = []
        
        # Need at least 30 data points for meaningful anomaly detection
        if len(self.metrics_buffer["inference_time"]) < 30:
            return anomalies
            
        # Check for inference time anomalies (using simple Z-score method)
        inference_times = np.array(self.metrics_buffer["inference_time"])
        mean_time = np.mean(inference_times)
        std_time = np.std(inference_times)
        
        if std_time > 0:
            z_score = (current_metrics["inference_time"] - mean_time) / std_time
            if z_score > 3:  # More than 3 standard deviations
                anomalies.append({
                    "type": "inference_time_spike",
                    "value": current_metrics["inference_time"],
                    "mean": mean_time,
                    "threshold": mean_time + 3 * std_time,
                    "z_score": z_score
                })
                
        # Check error rate over last 5 minutes
        recent_errors = [
            e for e in self.metrics_buffer["errors"] 
            if e.get("timestamp", datetime.now()) > datetime.now() - timedelta(minutes=5)
        ]
        
        if len(recent_errors) >= 5:  # At least 5 errors in 5 minutes
            anomalies.append({
                "type": "error_rate_spike",
                "count": len(recent_errors),
                "errors": [e.get("error", "unknown") for e in recent_errors[:5]]
            })
            
        return anomalies
    
    def report_anomalies(self, metrics: Dict[str, Any], anomalies: List[Dict[str, Any]]):
        """Report detected anomalies to the database."""
        for anomaly in anomalies:
            anomaly_id = str(uuid.uuid4())
            
            # Convert anomaly to JSON string for storage
            anomaly_json = json_lib.dumps(anomaly)
            
            # Store anomaly in database
            self.cursor.execute(
                """
                INSERT INTO anomalies 
                (request_id, anomaly_type, provider, model, application, description, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metrics["request_id"],
                    anomaly["type"],
                    metrics["provider"],
                    metrics["model"],
                    metrics["application"],
                    anomaly_json,
                    "high" if anomaly["type"] == "error_rate_spike" else "medium"
                )
            )
            self.conn.commit()
            
            logger.warning(f"Anomaly detected: {anomaly['type']} for request {metrics['request_id']}")
    
    def run(self):
        """Main processing loop."""
        logger.info("Starting stream processing loop")
        
        try:
            for message in self.consumer:
                data = message.value
                self.process_event(data)
        except KeyboardInterrupt:
            logger.info("Shutting down stream processor")
        except Exception as e:
            logger.error(f"Error in processing loop: {str(e)}", exc_info=True)
        finally:
            self.close()
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        if hasattr(self, 'consumer') and self.consumer:
            self.consumer.close()

if __name__ == "__main__":
    processor = StreamProcessor()
    processor.run()