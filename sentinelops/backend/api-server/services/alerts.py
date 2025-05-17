# sentinelops/backend/api-server/services/alerts.py

import logging
import uuid
import time
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

from ..models.alerts import AlertConfig, AlertEvent, AlertSeverity, AlertType, AlertThreshold

logger = logging.getLogger(__name__)

class AlertService:
    """
    Comprehensive service for managing and sending alerts.
    Supports alert configuration management and multiple notification channels:
    - Email
    - Slack
    - Webhook
    - SMS (via Twilio)
    """
    
    def __init__(self, db_connection=None, config: Dict[str, Any] = None):
        """
        Initialize the alert service.
        
        Args:
            db_connection: Database connection for persistent storage
            config: Configuration for alert channels
        """
        self.db_connection = db_connection
        self.config = config or {}
        
        # Load configuration from environment if not provided
        if not self.config:
            self._load_config_from_env()
            
        # Initialize notification channels
        self.channels = {
            "email": self._send_email_alert,
            "slack": self._send_slack_alert,
            "webhook": self._send_webhook_alert,
            "sms": self._send_sms_alert
        }
        
        # Alert history
        self.alert_history = []
        self.max_history = 1000
        
        logger.info("Alert service initialized")
    
    def _load_config_from_env(self):
        """Load alert configuration from environment variables."""
        self.config = {
            "email": {
                "enabled": os.environ.get("ALERT_EMAIL_ENABLED", "false").lower() == "true",
                "smtp_server": os.environ.get("ALERT_EMAIL_SMTP_SERVER", ""),
                "smtp_port": int(os.environ.get("ALERT_EMAIL_SMTP_PORT", "587")),
                "username": os.environ.get("ALERT_EMAIL_USERNAME", ""),
                "password": os.environ.get("ALERT_EMAIL_PASSWORD", ""),
                "from_address": os.environ.get("ALERT_EMAIL_FROM", ""),
                "to_addresses": os.environ.get("ALERT_EMAIL_TO", "").split(","),
                "use_tls": os.environ.get("ALERT_EMAIL_USE_TLS", "true").lower() == "true"
            },
            "slack": {
                "enabled": os.environ.get("ALERT_SLACK_ENABLED", "false").lower() == "true",
                "webhook_url": os.environ.get("ALERT_SLACK_WEBHOOK_URL", ""),
                "channel": os.environ.get("ALERT_SLACK_CHANNEL", "#alerts")
            },
            "webhook": {
                "enabled": os.environ.get("ALERT_WEBHOOK_ENABLED", "false").lower() == "true",
                "url": os.environ.get("ALERT_WEBHOOK_URL", ""),
                "headers": json.loads(os.environ.get("ALERT_WEBHOOK_HEADERS", "{}")),
                "method": os.environ.get("ALERT_WEBHOOK_METHOD", "POST")
            },
            "sms": {
                "enabled": os.environ.get("ALERT_SMS_ENABLED", "false").lower() == "true",
                "twilio_account_sid": os.environ.get("ALERT_SMS_TWILIO_ACCOUNT_SID", ""),
                "twilio_auth_token": os.environ.get("ALERT_SMS_TWILIO_AUTH_TOKEN", ""),
                "from_number": os.environ.get("ALERT_SMS_FROM_NUMBER", ""),
                "to_numbers": os.environ.get("ALERT_SMS_TO_NUMBERS", "").split(",")
            },
            "general": {
                "min_severity": os.environ.get("ALERT_MIN_SEVERITY", "warning"),
                "throttle_period_seconds": int(os.environ.get("ALERT_THROTTLE_PERIOD_SECONDS", "300"))
            }
        }
    
    # Alert Configuration Management Methods
    
    def get_alert_configs(self, enabled_only: bool = False) -> List[AlertConfig]:
        """
        Get all alert configurations.
        
        Args:
            enabled_only: If True, only return enabled configurations
            
        Returns:
            List of alert configurations
        """
        if not self.db_connection:
            return []
            
        cursor = self.db_connection.cursor()
        
        query = "SELECT id, config FROM alert_configs"
        if enabled_only:
            query += " WHERE enabled = TRUE"
            
        cursor.execute(query)
        
        configs = []
        for row in cursor.fetchall():
            config_data = json.loads(row[1])
            config = AlertConfig(**config_data)
            configs.append(config)
            
        return configs
    
    def get_alert_config(self, alert_id: str) -> Optional[AlertConfig]:
        """
        Get alert configuration by ID.
        
        Args:
            alert_id: ID of the alert configuration
            
        Returns:
            Alert configuration or None if not found
        """
        if not self.db_connection:
            return None
            
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            "SELECT config FROM alert_configs WHERE id = %s",
            (alert_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            return None
            
        config_data = json.loads(row[0])
        return AlertConfig(**config_data)
    
    def create_alert_config(self, config: AlertConfig) -> str:
        """
        Create a new alert configuration.
        
        Args:
            config: Alert configuration to create
            
        Returns:
            ID of the created configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.db_connection:
            raise ValueError("Database connection not available")
            
        # Validate configuration
        self._validate_alert_config(config)
        
        # Generate ID if not provided
        if not config.id:
            config.id = str(uuid.uuid4())
            
        # Set timestamps
        now = datetime.now()
        config.created_at = now
        config.updated_at = now
        
        # Insert into database
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            "INSERT INTO alert_configs (id, config, enabled) VALUES (%s, %s, %s)",
            (config.id, json.dumps(config.dict()), config.enabled)
        )
        
        self.db_connection.commit()
        
        return config.id
    
    def update_alert_config(self, config: AlertConfig) -> Optional[AlertConfig]:
        """
        Update an existing alert configuration.
        
        Args:
            config: Alert configuration to update
            
        Returns:
            Updated alert configuration or None if not found
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.db_connection:
            raise ValueError("Database connection not available")
            
        # Validate configuration
        self._validate_alert_config(config)
        
        # Check if exists
        existing = self.get_alert_config(config.id)
        if not existing:
            return None
            
        # Update timestamps
        config.created_at = existing.created_at
        config.updated_at = datetime.now()
        
        # Update in database
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            "UPDATE alert_configs SET config = %s, enabled = %s WHERE id = %s",
            (json.dumps(config.dict()), config.enabled, config.id)
        )
        
        self.db_connection.commit()
        
        return config
    
    def delete_alert_config(self, alert_id: str) -> bool:
        """
        Delete an alert configuration.
        
        Args:
            alert_id: ID of the alert configuration to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self.db_connection:
            raise ValueError("Database connection not available")
            
        # Check if exists
        existing = self.get_alert_config(alert_id)
        if not existing:
            return False
            
        # Delete from database
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            "DELETE FROM alert_configs WHERE id = %s",
            (alert_id,)
        )
        
        self.db_connection.commit()
        
        return True
    
    def _validate_alert_config(self, config: AlertConfig) -> None:
        """
        Validate alert configuration.
        
        Args:
            config: Alert configuration to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Check for required fields
        if not config.name:
            raise ValueError("Alert name is required")
            
        # Validate thresholds
        if not config.thresholds:
            raise ValueError("At least one threshold is required")
            
        # Additional validation could be added here
    
    # Alert Event Management Methods
    
    def get_alert_events(
        self,
        config_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        resolved: Optional[bool] = None
    ) -> List[AlertEvent]:
        """
        Get alert events.
        
        Args:
            config_id: Filter by alert configuration ID
            limit: Maximum number of events to return
            offset: Offset for pagination
            resolved: Filter by resolution status
            
        Returns:
            List of alert events
        """
        if not self.db_connection:
            return []
            
        cursor = self.db_connection.cursor()
        
        # Build query
        query = "SELECT id, config_id, timestamp, resolved_at, metric_value, threshold_value, details FROM alert_events WHERE 1=1"
        params = []
        
        if config_id:
            query += " AND config_id = %s"
            params.append(config_id)
            
        if resolved is not None:
            if resolved:
                query += " AND resolved_at IS NOT NULL"
            else:
                query += " AND resolved_at IS NULL"
                
        query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            event = AlertEvent(
                id=row[0],
                alert_config_id=row[1],
                timestamp=row[2],
                resolved_at=row[3],
                metric_value=row[4],
                threshold_value=row[5],
                details=json.loads(row[6]) if row[6] else {}
            )
            events.append(event)
            
        return events
    
    def get_alert_event(self, event_id: str) -> Optional[AlertEvent]:
        """
        Get alert event by ID.
        
        Args:
            event_id: ID of the alert event
            
        Returns:
            Alert event or None if not found
        """
        if not self.db_connection:
            return None
            
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            "SELECT id, config_id, timestamp, resolved_at, metric_value, threshold_value, details FROM alert_events WHERE id = %s",
            (event_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            return None
            
        return AlertEvent(
            id=row[0],
            alert_config_id=row[1],
            timestamp=row[2],
            resolved_at=row[3],
            metric_value=row[4],
            threshold_value=row[5],
            details=json.loads(row[6]) if row[6] else {}
        )
    
    def resolve_alert_event(self, event_id: str) -> Optional[AlertEvent]:
        """
        Resolve an alert event.
        
        Args:
            event_id: ID of the alert event to resolve
            
        Returns:
            Resolved alert event or None if not found
        """
        if not self.db_connection:
            raise ValueError("Database connection not available")
            
        # Check if exists and not already resolved
        event = self.get_alert_event(event_id)
        if not event:
            return None
            
        if event.resolved_at:
            # Already resolved
            return event
            
        # Resolve in database
        cursor = self.db_connection.cursor()
        
        now = datetime.now()
        cursor.execute(
            "UPDATE alert_events SET resolved_at = %s WHERE id = %s",
            (now, event_id)
        )
        
        self.db_connection.commit()
        
        # Update and return event
        event.resolved_at = now
        return event
    
    def create_alert_event(
        self,
        config_id: str,
        metric_value: float,
        threshold_value: float,
        details: Dict[str, Any] = {}
    ) -> str:
        """
        Create a new alert event.
        
        Args:
            config_id: ID of the alert configuration
            metric_value: Value of the metric that triggered the alert
            threshold_value: Threshold value that was exceeded
            details: Additional details about the alert
            
        Returns:
            ID of the created event
        """
        if not self.db_connection:
            raise ValueError("Database connection not available")
            
        # Generate ID
        event_id = str(uuid.uuid4())
        
        # Insert into database
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            "INSERT INTO alert_events (id, config_id, timestamp, metric_value, threshold_value, details) VALUES (%s, %s, %s, %s, %s, %s)",
            (event_id, config_id, datetime.now(), metric_value, threshold_value, json.dumps(details))
        )
        
        self.db_connection.commit()
        
        # Send notification for this event
        self._send_event_notification(event_id)
        
        return event_id
    
    def _send_event_notification(self, event_id: str) -> None:
        """
        Send notification for an alert event.
        
        Args:
            event_id: ID of the alert event
        """
        # Get event and config
        event = self.get_alert_event(event_id)
        if not event:
            logger.error(f"Cannot send notification for unknown event: {event_id}")
            return
            
        config = self.get_alert_config(event.alert_config_id)
        if not config:
            logger.error(f"Cannot send notification for unknown config: {event.alert_config_id}")
            return
            
        # Prepare notification
        title = f"{config.severity.upper()} Alert: {config.name}"
        message = f"Alert triggered for {config.alert_type} with value {event.metric_value} (threshold: {event.threshold_value})"
        
        # Send through appropriate channels
        self.send_alert(
            title=title,
            message=message,
            severity=config.severity.value,
            metadata={
                "alert_type": config.alert_type.value,
                "metric_value": event.metric_value,
                "threshold_value": event.threshold_value,
                "details": event.details
            }
        )
    
    # Alert Sending Methods (from alert_service.py)
    
    def send_alert(
        self, 
        title: str,
        message: str,
        severity: str = "warning",
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None
    ) -> bool:
        """
        Send an alert through configured channels.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error, critical)
            metadata: Additional metadata about the alert
            channels: Specific channels to use (defaults to all enabled)
            
        Returns:
            True if alert was sent successfully to at least one channel
        """
        # Check if severity meets minimum threshold
        severity_levels = {
            "info": 0,
            "warning": 1,
            "error": 2,
            "critical": 3
        }
        
        min_severity = self.config["general"]["min_severity"]
        if severity_levels.get(severity, 0) < severity_levels.get(min_severity, 0):
            logger.debug(f"Alert '{title}' skipped due to severity threshold ({severity} < {min_severity})")
            return False
        
        # Check if we should throttle this alert
        if self._should_throttle(title, severity, metadata):
            logger.debug(f"Alert '{title}' throttled to prevent alert fatigue")
            return False
        
        # Prepare alert data
        alert_data = {
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to history
        self.alert_history.append(alert_data)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        # Determine which channels to use
        if not channels:
            channels = [
                channel for channel, config in self.config.items()
                if channel != "general" and config.get("enabled", False)
            ]
        
        # Send through each channel
        success = False
        for channel in channels:
            if channel in self.channels and self.config.get(channel, {}).get("enabled", False):
                try:
                    self.channels[channel](alert_data)
                    success = True
                except Exception as e:
                    logger.error(f"Failed to send alert through {channel}: {str(e)}")
        
        return success
    
    def _should_throttle(
        self, 
        title: str, 
        severity: str,
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Check if an alert should be throttled to prevent alert fatigue.
        
        Args:
            title: Alert title
            severity: Alert severity
            metadata: Alert metadata
            
        Returns:
            True if the alert should be throttled
        """
        # Don't throttle critical alerts
        if severity == "critical":
            return False
            
        # Check if a similar alert was sent recently
        throttle_period = self.config["general"]["throttle_period_seconds"]
        now = datetime.now()
        
        for alert in reversed(self.alert_history):
            # Skip if different title
            if alert["title"] != title:
                continue
                
            # Skip if different severity
            if alert["severity"] != severity:
                continue
                
            # Check timestamp
            alert_time = datetime.fromisoformat(alert["timestamp"])
            seconds_diff = (now - alert_time).total_seconds()
            
            if seconds_diff < throttle_period:
                return True
                
        return False
    
    def _send_email_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send an alert via email."""
        config = self.config["email"]
        if not config["enabled"]:
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = config["from_address"]
            msg["To"] = ", ".join(config["to_addresses"])
            msg["Subject"] = f"[{alert_data['severity'].upper()}] {alert_data['title']}"
            
            # Create HTML body
            html = f"""
            <html>
                <body>
                    <h2>{alert_data['title']}</h2>
                    <p><strong>Severity:</strong> {alert_data['severity']}</p>
                    <p><strong>Time:</strong> {alert_data['timestamp']}</p>
                    <p>{alert_data['message']}</p>
                    
                    {self._format_metadata_html(alert_data['metadata'])}
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html, "html"))
            
            # Connect to SMTP server
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            if config["use_tls"]:
                server.starttls()
                
            # Login if credentials provided
            if config["username"] and config["password"]:
                server.login(config["username"], config["password"])
                
            # Send email
            server.sendmail(
                config["from_address"],
                config["to_addresses"],
                msg.as_string()
            )
            server.quit()
            
            logger.info(f"Email alert sent: {alert_data['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False
    
    def _send_slack_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send an alert via Slack webhook."""
        config = self.config["slack"]
        if not config["enabled"] or not config["webhook_url"]:
            return False
            
        try:
            # Set color based on severity
            color_map = {
                "info": "#2196F3",      # Blue
                "warning": "#FF9800",   # Orange
                "error": "#F44336",     # Red
                "critical": "#9C27B0"   # Purple
            }
            color = color_map.get(alert_data["severity"], "#757575")
            
            # Create payload
            payload = {
                "channel": config["channel"],
                "username": "SentinelOps Alert",
                "icon_emoji": ":bell:",
                "attachments": [
                    {
                        "fallback": f"{alert_data['severity'].upper()}: {alert_data['title']}",
                        "color": color,
                        "title": alert_data["title"],
                        "text": alert_data["message"],
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert_data["severity"].upper(),
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert_data["timestamp"],
                                "short": True
                            }
                        ],
                        "footer": "SentinelOps Monitoring"
                    }
                ]
            }
            
            # Add metadata fields
            for key, value in alert_data["metadata"].items():
                payload["attachments"][0]["fields"].append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })
            
            # Send request
            response = requests.post(
                config["webhook_url"],
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Slack alert sent: {alert_data['title']}")
                return True
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")
            return False
    
    def _send_webhook_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send an alert via custom webhook."""
        config = self.config["webhook"]
        if not config["enabled"] or not config["url"]:
            return False
            
        try:
            # Create payload
            payload = {
                "title": alert_data["title"],
                "message": alert_data["message"],
                "severity": alert_data["severity"],
                "timestamp": alert_data["timestamp"],
                "metadata": alert_data["metadata"]
            }
            
            # Send request
            method = config["method"].upper()
            headers = config["headers"] or {"Content-Type": "application/json"}
            
            if method == "GET":
                response = requests.get(
                    config["url"],
                    params=payload,
                    headers=headers
                )
            else:  # POST, PUT, etc.
                response = requests.request(
                    method,
                    config["url"],
                    json=payload,
                    headers=headers
                )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook alert sent: {alert_data['title']}")
                return True
            else:
                logger.error(f"Failed to send webhook alert: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {str(e)}")
            return False
    
    def _send_sms_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send an alert via SMS (Twilio)."""
        config = self.config["sms"]
        if not config["enabled"] or not config["twilio_account_sid"] or not config["twilio_auth_token"]:
            return False
            
        try:
            # Only import if needed
            from twilio.rest import Client
            
            # Create client
            client = Client(config["twilio_account_sid"], config["twilio_auth_token"])
            
            # Create message
            message_body = f"{alert_data['severity'].upper()}: {alert_data['title']}\n{alert_data['message']}"
            
            # Add key metadata
            if alert_data["metadata"]:
                message_body += "\n\n"
                for key, value in alert_data["metadata"].items():
                    if key in ["model", "provider", "application", "error"]:
                        message_body += f"{key}: {value}\n"
            
            # Send to all recipients
            success = False
            for to_number in config["to_numbers"]:
                if not to_number:
                    continue
                    
                message = client.messages.create(
                    body=message_body,
                    from_=config["from_number"],
                    to=to_number
                )
                
                logger.info(f"SMS alert sent to {to_number}: {message.sid}")
                success = True
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {str(e)}")
            return False
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as HTML for email alerts."""
        if not metadata:
            return ""
            
        html = "<h3>Additional Information</h3><table border='1' cellpadding='5' cellspacing='0'>"
        
        for key, value in metadata.items():
            html += f"<tr><td><strong>{key.replace('_', ' ').title()}</strong></td><td>{value}</td></tr>"
            
        html += "</table>"
        return html