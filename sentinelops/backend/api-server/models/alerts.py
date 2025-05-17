# sentinelops/backend/api-server/models/alerts.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    COST = "cost"
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    QUALITY = "quality"
    HALLUCINATION = "hallucination"
    SYSTEM = "system"

class AlertThreshold(BaseModel):
    metric: str
    operator: str = ">"  # >, <, >=, <=, ==, !=
    value: float
    duration_minutes: int = 5  # Duration the condition must be met

class AlertConfig(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    enabled: bool = True
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    thresholds: List[AlertThreshold]
    filters: Dict[str, Any] = {}  # provider, model, application, etc.
    notify_emails: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AlertEvent(BaseModel):
    id: str
    alert_config_id: str
    timestamp: datetime
    resolved_at: Optional[datetime] = None
    metric_value: float
    threshold_value: float
    details: Dict[str, Any] = {}