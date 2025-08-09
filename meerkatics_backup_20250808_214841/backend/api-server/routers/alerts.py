# meerkatics/backend/api-server/routers/alerts.py

from fastapi import APIRouter, HTTPException, Depends, status, Body, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ..models.alerts import AlertConfig, AlertEvent, AlertSeverity, AlertType
from ..services.alerts import AlertService
from ..middleware.auth import require_permissions, get_current_user

# Create a unified router with standardized prefix
router = APIRouter(
    prefix="/api/alerts",
    tags=["alerts"],
    dependencies=[Depends(require_permissions(["read:alerts"]))]
)

# Models for the simplified alert API
class AlertRequest(BaseModel):
    title: str
    message: str
    severity: str = "warning"
    metadata: Optional[Dict[str, Any]] = None
    channels: Optional[List[str]] = None

class AlertResponse(BaseModel):
    success: bool
    message: str
    alert_id: Optional[str] = None

class AlertHistoryItem(BaseModel):
    title: str
    message: str
    severity: str
    timestamp: str
    metadata: Dict[str, Any]

# Initialize alert service
alert_service = AlertService()

# Routes from the original alerts.py in routes directory
@router.post("/", response_model=AlertResponse)
async def send_alert(
    request: AlertRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send an alert through configured channels.
    """
    # Add user info to metadata
    if request.metadata is None:
        request.metadata = {}
    
    request.metadata["triggered_by"] = current_user.get("username", "system")
    
    # Send alert
    success = alert_service.send_alert(
        title=request.title,
        message=request.message,
        severity=request.severity,
        metadata=request.metadata,
        channels=request.channels
    )
    
    if success:
        return {
            "success": True,
            "message": "Alert sent successfully",
            "alert_id": None  # We don't have IDs for alerts yet
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send alert through any channel"
        )

@router.get("/history", response_model=List[AlertHistoryItem])
async def get_alert_history(
    limit: int = Query(50, ge=1, le=1000),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get alert history.
    """
    # Get history
    history = alert_service.alert_history
    
    # Apply filters
    if severity:
        history = [alert for alert in history if alert["severity"] == severity]
    
    # Sort by timestamp (newest first)
    history = sorted(
        history,
        key=lambda x: datetime.fromisoformat(x["timestamp"]),
        reverse=True
    )
    
    # Apply limit
    history = history[:limit]
    
    return history

@router.post("/test", response_model=AlertResponse)
async def test_alert(
    channel: str = Query(..., description="Channel to test (email, slack, webhook, sms)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a test alert to verify channel configuration.
    """
    # Validate channel
    if channel not in ["email", "slack", "webhook", "sms"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid channel: {channel}"
        )
    
    # Check if channel is enabled
    if not alert_service.config.get(channel, {}).get("enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Channel {channel} is not enabled"
        )
    
    # Send test alert
    success = alert_service.send_alert(
        title="Test Alert",
        message=f"This is a test alert sent to the {channel} channel.",
        severity="info",
        metadata={
            "test": True,
            "triggered_by": current_user.get("username", "system"),
            "timestamp": datetime.now().isoformat()
        },
        channels=[channel]
    )
    
    if success:
        return {
            "success": True,
            "message": f"Test alert sent successfully to {channel}",
            "alert_id": None
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test alert to {channel}"
        )

@router.get("/config")
async def get_alert_config(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current alert configuration (without sensitive information).
    """
    # Create a copy of the config
    config = {
        "email": {
            "enabled": alert_service.config["email"]["enabled"],
            "smtp_server": alert_service.config["email"]["smtp_server"],
            "smtp_port": alert_service.config["email"]["smtp_port"],
            "from_address": alert_service.config["email"]["from_address"],
            "to_addresses": alert_service.config["email"]["to_addresses"],
            "use_tls": alert_service.config["email"]["use_tls"]
        },
        "slack": {
            "enabled": alert_service.config["slack"]["enabled"],
            "channel": alert_service.config["slack"]["channel"]
        },
        "webhook": {
            "enabled": alert_service.config["webhook"]["enabled"],
            "url": alert_service.config["webhook"]["url"],
            "method": alert_service.config["webhook"]["method"]
        },
        "sms": {
            "enabled": alert_service.config["sms"]["enabled"],
            "from_number": alert_service.config["sms"]["from_number"],
            "to_numbers": alert_service.config["sms"]["to_numbers"]
        },
        "general": alert_service.config["general"]
    }
    
    return config

# Routes from the original routers/alerts.py
@router.get("/configs", response_model=List[AlertConfig])
async def get_alert_configs(enabled_only: bool = False):
    """Get all alert configurations."""
    return alert_service.get_alert_configs(enabled_only=enabled_only)

@router.get("/configs/{alert_id}", response_model=AlertConfig)
async def get_alert_config(alert_id: str):
    """Get alert configuration by ID."""
    config = alert_service.get_alert_config(alert_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert configuration with ID {alert_id} not found"
        )
    
    return config

@router.post("/configs", response_model=str, dependencies=[Depends(require_permissions(["write:alerts"]))])
async def create_alert_config(config: AlertConfig):
    """Create a new alert configuration."""
    try:
        alert_id = alert_service.create_alert_config(config)
        return alert_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert configuration: {str(e)}"
        )

@router.put("/configs/{alert_id}", dependencies=[Depends(require_permissions(["write:alerts"]))])
async def update_alert_config(alert_id: str, config: AlertConfig):
    """Update an existing alert configuration."""
    # Ensure ID matches
    if config.id and config.id != alert_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert ID in path and body do not match"
        )
    
    # Set ID if not present
    if not config.id:
        config.id = alert_id
    
    # Check if exists
    existing = alert_service.get_alert_config(alert_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert configuration with ID {alert_id} not found"
        )
    
    # Update
    success = alert_service.update_alert_config(config)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update alert configuration"
        )
    
    return {"success": True}

@router.delete("/configs/{alert_id}", dependencies=[Depends(require_permissions(["write:alerts"]))])
async def delete_alert_config(alert_id: str):
    """Delete an alert configuration."""
    # Check if exists
    existing = alert_service.get_alert_config(alert_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert configuration with ID {alert_id} not found"
        )
    
    # Delete
    success = alert_service.delete_alert_config(alert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete alert configuration"
        )
    
    return {"success": True}

@router.get("/events", response_model=List[AlertEvent])
async def get_alert_events(
   config_id: Optional[str] = None,
   limit: int = 100,
   offset: int = 0,
   resolved: Optional[bool] = None
):
   """Get alert events, optionally filtered by config ID and resolution status."""
   db = alert_service.db_connection
   cursor = db.cursor()
   
   # Build query
   query = "SELECT id, alert_config_id, timestamp, resolved_at, metric_value, threshold_value, details FROM alert_events"
   where_clauses = []
   params = []
   
   if config_id:
       where_clauses.append("alert_config_id = %s")
       params.append(config_id)
   
   if resolved is not None:
       if resolved:
           where_clauses.append("resolved_at IS NOT NULL")
       else:
           where_clauses.append("resolved_at IS NULL")
   
   if where_clauses:
       query += " WHERE " + " AND ".join(where_clauses)
   
   query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
   params.extend([limit, offset])
   
   cursor.execute(query, params)
   results = cursor.fetchall()
   
   events = []
   for result in results:
       events.append(AlertEvent(
           id=result[0],
           alert_config_id=result[1],
           timestamp=result[2],
           resolved_at=result[3],
           metric_value=result[4],
           threshold_value=result[5],
           details=result[6]
       ))
   
   return events

@router.get("/events/{event_id}", response_model=AlertEvent)
async def get_alert_event(event_id: str):
   """Get alert event by ID."""
   db = alert_service.db_connection
   cursor = db.cursor()
   
   cursor.execute(
       "SELECT id, alert_config_id, timestamp, resolved_at, metric_value, threshold_value, details FROM alert_events WHERE id = %s",
       (event_id,)
   )
   result = cursor.fetchone()
   
   if not result:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=f"Alert event with ID {event_id} not found"
       )
   
   return AlertEvent(
       id=result[0],
       alert_config_id=result[1],
       timestamp=result[2],
       resolved_at=result[3],
       metric_value=result[4],
       threshold_value=result[5],
       details=result[6]
   )

@router.post("/events/{event_id}/resolve", dependencies=[Depends(require_permissions(["write:alerts"]))])
async def resolve_alert_event(event_id: str):
   """Manually resolve an alert event."""
   db = alert_service.db_connection
   cursor = db.cursor()
   
   # Check if event exists
   cursor.execute("SELECT id FROM alert_events WHERE id = %s", (event_id,))
   if not cursor.fetchone():
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail=f"Alert event with ID {event_id} not found"
       )
   
   # Check if already resolved
   cursor.execute("SELECT resolved_at FROM alert_events WHERE id = %s", (event_id,))
   result = cursor.fetchone()
   if result[0] is not None:
       return {"success": True, "message": "Alert event already resolved"}
   
   # Resolve event
   from datetime import datetime
   cursor.execute(
       "UPDATE alert_events SET resolved_at = %s WHERE id = %s",
       (datetime.now(), event_id)
   )
   db.commit()
   
   return {"success": True}