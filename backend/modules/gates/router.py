"""
Router for Gates Management
Defines API endpoints for gate operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from core.database import get_db
from core.security import get_current_user, require_permissions
from modules.gates.service import GatesService


router = APIRouter(prefix="/gates", tags=["Gates Management"])


# Pydantic Models for Request/Response
class GateCreateRequest(BaseModel):
    """Request model for creating a new gate"""
    gate_name: str = Field(..., min_length=2, max_length=100, description="Name of the gate")
    gate_code: str = Field(..., min_length=2, max_length=20, description="Unique code for the gate")
    gate_type: str = Field(..., description="Type of gate (LAND, SEA, AIR, RAIL, CHECKPOINT)")
    city_id: str = Field(..., description="ID of the city where the gate is located")
    direction: str = Field("BIDIRECTIONAL", description="Gate direction (ENTRY, EXIT, BIDIRECTIONAL)")
    location_coordinates: Optional[str] = Field(None, description="GPS coordinates")
    max_capacity: Optional[int] = Field(None, ge=1, description="Maximum capacity")
    operating_hours: Optional[str] = Field(None, description="Operating hours in JSON format")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class GateUpdateRequest(BaseModel):
    """Request model for updating a gate"""
    gate_name: Optional[str] = Field(None, min_length=2, max_length=100)
    location_coordinates: Optional[str] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    operating_hours: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)


class GateStatusRequest(BaseModel):
    """Request model for updating gate status"""
    status: str = Field(..., description="New gate status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class GateResponse(BaseModel):
    """Response model for gate data"""
    id: str
    gate_name: str
    gate_code: str
    gate_type: str
    city_id: str
    city_name: Optional[str] = None
    direction: str
    status: str
    location_coordinates: Optional[str] = None
    max_capacity: Optional[int] = None
    operating_hours: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GateSummaryResponse(BaseModel):
    """Response model for gate summary statistics"""
    total_gates: int
    by_status: dict
    by_type: dict


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None


def format_gate_response(gate) -> dict:
    """Format gate object for response"""
    return {
        "id": gate.id,
        "gate_name": gate.gate_name,
        "gate_code": gate.gate_code,
        "gate_type": gate.gate_type.value if hasattr(gate.gate_type, 'value') else str(gate.gate_type),
        "city_id": gate.city_id,
        "city_name": gate.city.city_name if gate.city else None,
        "direction": gate.direction.value if hasattr(gate.direction, 'value') else str(gate.direction),
        "status": gate.status.value if hasattr(gate.status, 'value') else str(gate.status),
        "location_coordinates": gate.location_coordinates,
        "max_capacity": gate.max_capacity,
        "operating_hours": gate.operating_hours,
        "notes": gate.notes,
        "created_by": gate.created_by,
        "created_at": gate.created_at.isoformat() if gate.created_at else None,
        "updated_at": gate.updated_at.isoformat() if gate.updated_at else None
    }


@router.post("/", response_model=GateResponse, status_code=status.HTTP_201_CREATED)
async def create_gate(
    request: GateCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new gate
    
    Requires: Create Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:create", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create gates"
        )
    
    try:
        gate = await GatesService.create_gate(
            db=db,
            gate_name=request.gate_name,
            gate_code=request.gate_code,
            gate_type=request.gate_type,
            city_id=request.city_id,
            direction=request.direction,
            created_by_user_id=current_user["user_id"],
            location_coordinates=request.location_coordinates,
            max_capacity=request.max_capacity,
            operating_hours=request.operating_hours,
            notes=request.notes
        )
        
        return format_gate_response(gate)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating gate: {str(e)}"
        )


@router.get("/", response_model=List[GateResponse])
async def get_all_gates(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    city_id: Optional[str] = Query(None, description="Filter by city ID"),
    gate_type: Optional[str] = Query(None, description="Filter by gate type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    direction: Optional[str] = Query(None, description="Filter by direction"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all gates with optional filters
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gates"
        )
    
    try:
        gates = await GatesService.get_all_gates(
            db=db,
            skip=skip,
            limit=limit,
            city_id=city_id,
            gate_type=gate_type,
            status=status_filter,
            direction=direction
        )
        
        return [format_gate_response(gate) for gate in gates]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching gates: {str(e)}"
        )


@router.get("/{gate_id}", response_model=GateResponse)
async def get_gate_by_id(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific gate by ID
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gates"
        )
    
    gate = await GatesService.get_gate_by_id(db, gate_id)
    
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return format_gate_response(gate)


@router.get("/code/{gate_code}", response_model=GateResponse)
async def get_gate_by_code(
    gate_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a gate by its code
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gates"
        )
    
    gate = await GatesService.get_gate_by_code(db, gate_code)
    
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with code {gate_code} not found"
        )
    
    return format_gate_response(gate)


@router.put("/{gate_id}", response_model=GateResponse)
async def update_gate(
    gate_id: str,
    request: GateUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update gate details
    
    Requires: Update Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:update", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update gates"
        )
    
    try:
        gate = await GatesService.update_gate(
            db=db,
            gate_id=gate_id,
            gate_name=request.gate_name,
            location_coordinates=request.location_coordinates,
            max_capacity=request.max_capacity,
            operating_hours=request.operating_hours,
            notes=request.notes,
            updated_by=current_user["user_id"]
        )
        
        if not gate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gate with ID {gate_id} not found"
            )
        
        return format_gate_response(gate)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating gate: {str(e)}"
        )


@router.put("/{gate_id}/status", response_model=GateResponse)
async def update_gate_status(
    gate_id: str,
    request: GateStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update the status of a gate
    
    Requires: Update Gate Status permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:status", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update gate status"
        )
    
    try:
        gate = await GatesService.update_gate_status(
            db=db,
            gate_id=gate_id,
            new_status=request.status,
            updated_by=current_user["user_id"],
            reason=request.reason
        )
        
        if not gate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Gate with ID {gate_id} not found"
            )
        
        return format_gate_response(gate)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating gate status: {str(e)}"
        )


@router.post("/{gate_id}/open", response_model=GateResponse)
async def open_gate(
    gate_id: str,
    reason: Optional[str] = Field(None, max_length=500, description="Reason for opening"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Open a gate
    
    Requires: Open/Close Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:operate", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to operate gates"
        )
    
    gate = await GatesService.open_gate(
        db=db,
        gate_id=gate_id,
        opened_by=current_user["user_id"],
        reason=reason
    )
    
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return format_gate_response(gate)


@router.post("/{gate_id}/close", response_model=GateResponse)
async def close_gate(
    gate_id: str,
    reason: Optional[str] = Field(None, max_length=500, description="Reason for closing"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Close a gate
    
    Requires: Open/Close Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:operate", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to operate gates"
        )
    
    gate = await GatesService.close_gate(
        db=db,
        gate_id=gate_id,
        closed_by=current_user["user_id"],
        reason=reason
    )
    
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return format_gate_response(gate)


@router.post("/{gate_id}/maintenance", response_model=GateResponse)
async def set_maintenance(
    gate_id: str,
    reason: Optional[str] = Field(None, max_length=500, description="Reason for maintenance"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Set a gate to maintenance mode
    
    Requires: Set Maintenance permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:maintenance", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to set maintenance"
        )
    
    gate = await GatesService.set_maintenance(
        db=db,
        gate_id=gate_id,
        maintenance_by=current_user["user_id"],
        reason=reason
    )
    
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return format_gate_response(gate)


@router.post("/{gate_id}/emergency", response_model=GateResponse)
async def set_emergency(
    gate_id: str,
    reason: str = Field(..., max_length=500, description="Emergency reason"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Set a gate to emergency status
    
    Requires: Emergency Control permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:emergency", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to set emergency status"
        )
    
    gate = await GatesService.set_emergency(
        db=db,
        gate_id=gate_id,
        emergency_by=current_user["user_id"],
        reason=reason
    )
    
    if not gate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return format_gate_response(gate)


@router.get("/city/{city_id}", response_model=List[GateResponse])
async def get_gates_by_city(
    city_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all gates in a specific city
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gates"
        )
    
    gates = await GatesService.get_gates_by_city(db, city_id)
    
    return [format_gate_response(gate) for gate in gates]


@router.get("/active/open", response_model=List[GateResponse])
async def get_open_gates(
    city_id: Optional[str] = Query(None, description="Filter by city ID"),
    gate_type: Optional[str] = Query(None, description="Filter by gate type"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all open gates
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gates"
        )
    
    gates = await GatesService.get_open_gates(db, city_id, gate_type)
    
    return [format_gate_response(gate) for gate in gates]


@router.get("/summary/stats", response_model=GateSummaryResponse)
async def get_gates_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary statistics for gates
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gate statistics"
        )
    
    summary = await GatesService.get_gates_summary(db)
    
    return GateSummaryResponse(**summary)


@router.get("/{gate_id}/statistics", response_model=dict)
async def get_gate_statistics(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics for a specific gate
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view gate statistics"
        )
    
    statistics = await GatesService.get_gate_statistics(db, gate_id)
    
    if not statistics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return statistics


@router.get("/{gate_id}/check-access", response_model=dict)
async def check_gate_access(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check if current user has access to operate a gate
    
    Requires: Read Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:read", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to check gate access"
        )
    
    access_result = await GatesService.check_gate_access(
        db=db,
        gate_id=gate_id,
        user_id=current_user["user_id"]
    )
    
    return access_result


@router.delete("/{gate_id}", response_model=MessageResponse)
async def delete_gate(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a gate (hard delete)
    
    Requires: Delete Gate permission
    """
    # Check permissions
    if not require_permissions(current_user, ["gates:delete", "gates:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete gates"
        )
    
    deleted = await GatesService.delete_gate(db, gate_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gate with ID {gate_id} not found"
        )
    
    return {
        "message": f"Gate with ID {gate_id} has been deleted",
        "details": {"gate_id": gate_id}
    }
