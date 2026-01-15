"""
Router for Alerts Management
Defines API endpoints for alert operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from core.database import get_db
from core.security import get_current_user, require_permissions
from modules.alerts.service import AlertsService


router = APIRouter(prefix="/alerts", tags=["Alerts Management"])


# Pydantic Models for Request/Response
class AlertCreateRequest(BaseModel):
    """Request model for creating a new alert"""
    alert_type: str = Field(..., description="Type of alert (INTRUSION, SUSPICIOUS_ACTIVITY, SYSTEM, PERMIT, WEAPON)")
    title: str = Field(..., min_length=3, max_length=200, description="Short title of the alert")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed description")
    severity: str = Field("MEDIUM", description="Alert severity (LOW, MEDIUM, HIGH, CRITICAL)")
    traveler_id: Optional[str] = Field(None, description="Optional related traveler ID")
    gate_id: Optional[str] = Field(None, description="Optional related gate ID")
    city_id: Optional[str] = Field(None, description="Optional related city ID")
    source: Optional[str] = Field(None, description="Source of the alert (CAMERA, MANUAL, SYSTEM, GATE)")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class AlertUpdateRequest(BaseModel):
    """Request model for updating an alert"""
    status: Optional[str] = Field(None, description="New alert status")
    assigned_to: Optional[str] = Field(None, description="User ID to assign the alert to")


class AlertAssignRequest(BaseModel):
    """Request model for assigning an alert"""
    assignee_user_id: str = Field(..., description="ID of the user to assign")


class AlertResolveRequest(BaseModel):
    """Request model for resolving an alert"""
    resolution_notes: str = Field(..., min_length=10, description="Detailed notes about the resolution")
    resolution_type: Optional[str] = Field(None, description="Type of resolution")


class AlertEscalateRequest(BaseModel):
    """Request model for escalating an alert"""
    escalated_to: str = Field(..., description="User ID or role to escalate to")
    reason: str = Field(..., min_length=10, description="Reason for escalation")


class AlertDismissRequest(BaseModel):
    """Request model for dismissing an alert"""
    reason: str = Field(..., min_length=10, description="Reason for dismissal")


class AlertResponse(BaseModel):
    """Response model for alert data"""
    id: str
    alert_code: str
    alert_type: str
    title: str
    description: str
    severity: str
    status: str
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    traveler_id: Optional[str] = None
    traveler_name: Optional[str] = None
    gate_id: Optional[str] = None
    gate_name: Optional[str] = None
    city_id: Optional[str] = None
    city_name: Optional[str] = None
    assigned_to: Optional[str] = None
    assignee_name: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class AlertSummaryResponse(BaseModel):
    """Response model for alert summary statistics"""
    total_alerts: int
    active_alerts: int
    critical_alerts: int
    by_status: dict
    by_severity: dict


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None


def format_alert_response(alert) -> dict:
    """Format alert object for response"""
    return {
        "id": alert.id,
        "alert_code": alert.alert_code,
        "alert_type": alert.alert_type.value if hasattr(alert.alert_type, 'value') else str(alert.alert_type),
        "title": alert.title,
        "description": alert.description,
        "severity": alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity),
        "status": alert.status.value if hasattr(alert.status, 'value') else str(alert.status),
        "creator_id": alert.created_by,
        "creator_name": f"{alert.creator.first_name} {alert.creator.last_name}" if alert.creator else None,
        "traveler_id": alert.traveler_id,
        "traveler_name": f"{alert.traveler.first_name} {alert.traveler.last_name}" if alert.traveler else None,
        "gate_id": alert.gate_id,
        "gate_name": alert.gate.gate_name if alert.gate else None,
        "city_id": alert.city_id,
        "city_name": alert.city.city_name if alert.city else None,
        "assigned_to": alert.assigned_to,
        "assignee_name": f"{alert.assignee.first_name} {alert.assignee.last_name}" if alert.assignee else None,
        "source": alert.source,
        "metadata": alert.metadata,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
        "assigned_at": alert.assigned_at.isoformat() if alert.assigned_at else None,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "resolved_by": alert.resolved_by,
        "resolution_notes": alert.resolution_notes
    }


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    request: AlertCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new security alert
    
    Requires: Create Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:create", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create alerts"
        )
    
    try:
        alert = await AlertsService.create_alert(
            db=db,
            alert_type=request.alert_type,
            title=request.title,
            description=request.description,
            severity=request.severity,
            created_by_user_id=current_user["user_id"],
            traveler_id=request.traveler_id,
            gate_id=request.gate_id,
            city_id=request.city_id,
            source=request.source,
            metadata=request.metadata
        )
        
        return format_alert_response(alert)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating alert: {str(e)}"
        )


@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned user ID"),
    city_id: Optional[str] = Query(None, description="Filter by city ID"),
    gate_id: Optional[str] = Query(None, description="Filter by gate ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all alerts with optional filters
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alerts"
        )
    
    try:
        alerts = await AlertsService.get_all_alerts(
            db=db,
            skip=skip,
            limit=limit,
            status=status_filter,
            severity=severity,
            alert_type=alert_type,
            assigned_to=assigned_to,
            city_id=city_id,
            gate_id=gate_id
        )
        
        return [format_alert_response(alert) for alert in alerts]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching alerts: {str(e)}"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert_by_id(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific alert by ID
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alerts"
        )
    
    alert = await AlertsService.get_alert_by_id(db, alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return format_alert_response(alert)


@router.put("/{alert_id}/assign", response_model=AlertResponse)
async def assign_alert(
    alert_id: str,
    request: AlertAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Assign an alert to a user
    
    Requires: Update Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:update", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to assign alerts"
        )
    
    try:
        alert = await AlertsService.assign_alert(
            db=db,
            alert_id=alert_id,
            assignee_user_id=request.assignee_user_id,
            assigned_by=current_user["user_id"]
        )
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found"
            )
        
        return format_alert_response(alert)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning alert: {str(e)}"
        )


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    request: AlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark an alert as resolved
    
    Requires: Resolve Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:resolve", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to resolve alerts"
        )
    
    alert = await AlertsService.resolve_alert(
        db=db,
        alert_id=alert_id,
        resolved_by=current_user["user_id"],
        resolution_notes=request.resolution_notes,
        resolution_type=request.resolution_type
    )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return format_alert_response(alert)


@router.post("/{alert_id}/escalate", response_model=AlertResponse)
async def escalate_alert(
    alert_id: str,
    request: AlertEscalateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Escalate an alert to higher authority
    
    Requires: Escalate Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:escalate", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to escalate alerts"
        )
    
    alert = await AlertsService.escalate_alert(
        db=db,
        alert_id=alert_id,
        escalated_to=request.escalated_to,
        escalated_by=current_user["user_id"],
        reason=request.reason
    )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return format_alert_response(alert)


@router.post("/{alert_id}/dismiss", response_model=AlertResponse)
async def dismiss_alert(
    alert_id: str,
    request: AlertDismissRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Dismiss an alert (mark as false positive)
    
    Requires: Dismiss Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:dismiss", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to dismiss alerts"
        )
    
    alert = await AlertsService.dismiss_alert(
        db=db,
        alert_id=alert_id,
        dismissed_by=current_user["user_id"],
        reason=request.reason
    )
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return format_alert_response(alert)


@router.get("/active/all", response_model=List[AlertResponse])
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all active (non-resolved) alerts
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alerts"
        )
    
    alerts = await AlertsService.get_active_alerts(db, severity)
    
    return [format_alert_response(alert) for alert in alerts]


@router.get("/critical/all", response_model=List[AlertResponse])
async def get_critical_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all critical and high severity active alerts
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alerts"
        )
    
    alerts = await AlertsService.get_critical_alerts(db)
    
    return [format_alert_response(alert) for alert in alerts]


@router.get("/summary/stats", response_model=AlertSummaryResponse)
async def get_alerts_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary statistics for alerts
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alert statistics"
        )
    
    summary = await AlertsService.get_alerts_summary(db)
    
    return AlertSummaryResponse(**summary)


@router.get("/my/assigned", response_model=List[AlertResponse])
async def get_my_assigned_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get alerts assigned to the current user
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alerts"
        )
    
    alerts = await AlertsService.get_user_assigned_alerts(db, current_user["user_id"])
    
    return [format_alert_response(alert) for alert in alerts]


@router.get("/recent/{hours}", response_model=List[AlertResponse])
async def get_recent_alerts(
    hours: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get alerts created within the specified hours
    
    Requires: Read Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:read", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view alerts"
        )
    
    alerts = await AlertsService.get_recent_alerts(db, hours)
    
    return [format_alert_response(alert) for alert in alerts]


@router.delete("/{alert_id}", response_model=MessageResponse)
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an alert (hard delete)
    
    Requires: Delete Alert permission
    """
    # Check permissions
    if not require_permissions(current_user, ["alerts:delete", "alerts:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete alerts"
        )
    
    deleted = await AlertsService.delete_alert(db, alert_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    return {
        "message": f"Alert with ID {alert_id} has been deleted",
        "details": {"alert_id": alert_id}
    }
