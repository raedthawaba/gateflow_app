"""
Router for Permits Management
Defines API endpoints for permit operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from core.database import get_db
from core.security import get_current_user, require_permissions
from modules.permits.service import PermitsService


router = APIRouter(prefix="/permits", tags=["Permits Management"])


# Pydantic Models for Request/Response
class PermitCreateRequest(BaseModel):
    """Request model for creating a new permit"""
    permit_type: str = Field(..., description="Type of permit (TRANSIT, ENTRY, EXIT, TEMPORARY)")
    traveler_id: str = Field(..., description="ID of the traveler")
    gate_id: Optional[str] = Field(None, description="Optional specific gate ID")
    city_id: Optional[str] = Field(None, description="Optional specific city ID")
    valid_days: int = Field(30, ge=1, le=365, description="Number of days permit is valid")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class PermitUpdateRequest(BaseModel):
    """Request model for updating a permit"""
    status: Optional[str] = Field(None, description="New permit status")
    gate_id: Optional[str] = Field(None, description="Updated gate ID")
    city_id: Optional[str] = Field(None, description="Updated city ID")
    valid_days: Optional[int] = Field(None, ge=1, le=365, description="Updated validity days")
    notes: Optional[str] = Field(None, max_length=500, description="Updated notes")


class PermitValidateRequest(BaseModel):
    """Request model for validating a permit"""
    permit_number: str = Field(..., description="Permit number to validate")
    gate_id: Optional[str] = Field(None, description="Optional gate ID to validate against")


class PermitResponse(BaseModel):
    """Response model for permit data"""
    id: str
    permit_number: str
    permit_type: str
    traveler_id: str
    traveler_name: Optional[str] = None
    issued_by: str
    issuer_name: Optional[str] = None
    gate_id: Optional[str] = None
    gate_name: Optional[str] = None
    city_id: Optional[str] = None
    city_name: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermitValidationResponse(BaseModel):
    """Response model for permit validation"""
    valid: bool
    message: str
    permit: Optional[PermitResponse] = None


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None


def format_permit_response(permit) -> dict:
    """Format permit object for response"""
    return {
        "id": permit.id,
        "permit_number": permit.permit_number,
        "permit_type": permit.permit_type.value if hasattr(permit.permit_type, 'value') else str(permit.permit_type),
        "traveler_id": permit.traveler_id,
        "traveler_name": f"{permit.traveler.first_name} {permit.traveler.last_name}" if permit.traveler else None,
        "issued_by": permit.issued_by,
        "issuer_name": f"{permit.issuer.first_name} {permit.issuer.last_name}" if permit.issuer else None,
        "gate_id": permit.gate_id,
        "gate_name": permit.gate.gate_name if permit.gate else None,
        "city_id": permit.city_id,
        "city_name": permit.city.city_name if permit.city else None,
        "valid_from": permit.valid_from.isoformat() if permit.valid_from else None,
        "valid_until": permit.valid_until.isoformat() if permit.valid_until else None,
        "status": permit.status.value if hasattr(permit.status, 'value') else str(permit.status),
        "notes": permit.notes,
        "created_at": permit.created_at.isoformat() if permit.created_at else None,
        "updated_at": permit.updated_at.isoformat() if permit.updated_at else None
    }


@router.post("/", response_model=PermitResponse, status_code=status.HTTP_201_CREATED)
async def create_permit(
    request: PermitCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new permit for a traveler
    
    Requires: Create Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:create", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create permits"
        )
    
    try:
        permit = await PermitsService.create_permit(
            db=db,
            permit_type=request.permit_type,
            traveler_id=request.traveler_id,
            issued_by_user_id=current_user["user_id"],
            gate_id=request.gate_id,
            city_id=request.city_id,
            valid_days=request.valid_days,
            notes=request.notes
        )
        
        return format_permit_response(permit)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating permit: {str(e)}"
        )


@router.get("/", response_model=List[PermitResponse])
async def get_all_permits(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    permit_type: Optional[str] = Query(None, description="Filter by permit type"),
    traveler_id: Optional[str] = Query(None, description="Filter by traveler ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all permits with optional filters
    
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view permits"
        )
    
    try:
        permits = await PermitsService.get_all_permits(
            db=db,
            skip=skip,
            limit=limit,
            status=status_filter,
            permit_type=permit_type,
            traveler_id=traveler_id
        )
        
        return [format_permit_response(permit) for permit in permits]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching permits: {str(e)}"
        )


@router.get("/{permit_id}", response_model=PermitResponse)
async def get_permit_by_id(
    permit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific permit by ID
    
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view permits"
        )
    
    permit = await PermitsService.get_permit_by_id(db, permit_id)
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permit with ID {permit_id} not found"
        )
    
    return format_permit_response(permit)


@router.get("/number/{permit_number}", response_model=PermitResponse)
async def get_permit_by_number(
    permit_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a permit by its permit number
    
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view permits"
        )
    
    permit = await PermitsService.get_permit_by_number(db, permit_number)
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permit with number {permit_number} not found"
        )
    
    return format_permit_response(permit)


@router.post("/validate", response_model=PermitValidationResponse)
async def validate_permit(
    request: PermitValidateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Validate if a permit is valid for use
    
    This endpoint can be used at gate checkpoints to verify permits
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access", "gates:check"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to validate permits"
        )
    
    validation_result = await PermitsService.validate_permit(
        db=db,
        permit_number=request.permit_number,
        gate_id=request.gate_id
    )
    
    return {
        "valid": validation_result["valid"],
        "message": validation_result["message"],
        "permit": format_permit_response(validation_result["permit"]) if validation_result["permit"] else None
    }


@router.put("/{permit_id}", response_model=PermitResponse)
async def update_permit(
    permit_id: str,
    request: PermitUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a permit
    
    Requires: Update Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:update", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update permits"
        )
    
    try:
        # First get the current permit
        permit = await PermitsService.get_permit_by_id(db, permit_id)
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permit with ID {permit_id} not found"
            )
        
        # Update status if provided
        if request.status:
            permit = await PermitsService.update_permit_status(
                db=db,
                permit_id=permit_id,
                new_status=request.status,
                updated_by=current_user["user_id"]
            )
        
        # Note: Other updates would require additional service methods
        # For now, we just refresh and return
        await db.refresh(permit)
        
        return format_permit_response(permit)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating permit: {str(e)}"
        )


@router.post("/{permit_id}/revoke", response_model=PermitResponse)
async def revoke_permit(
    permit_id: str,
    reason: str = Field(..., description="Reason for revocation"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke a permit
    
    Requires: Revoke Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:revoke", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to revoke permits"
        )
    
    permit = await PermitsService.revoke_permit(
        db=db,
        permit_id=permit_id,
        revoked_by=current_user["user_id"],
        reason=reason
    )
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permit with ID {permit_id} not found"
        )
    
    return format_permit_response(permit)


@router.post("/{permit_id}/suspend", responseModel=PermitResponse)
async def suspend_permit(
    permit_id: str,
    reason: str = Field(..., description="Reason for suspension"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Suspend a permit temporarily
    
    Requires: Suspend Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:suspend", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to suspend permits"
        )
    
    permit = await PermitsService.suspend_permit(
        db=db,
        permit_id=permit_id,
        suspended_by=current_user["user_id"],
        reason=reason
    )
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permit with ID {permit_id} not found"
        )
    
    return format_permit_response(permit)


@router.post("/{permit_id}/renew", response_model=PermitResponse)
async def renew_permit(
    permit_id: str,
    additional_days: int = Field(30, ge=1, le=365, description="Number of days to extend validity"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Renew an expired or expiring permit
    
    Requires: Renew Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:renew", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to renew permits"
        )
    
    permit = await PermitsService.renew_permit(
        db=db,
        permit_id=permit_id,
        renewed_by=current_user["user_id"],
        additional_days=additional_days
    )
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permit with ID {permit_id} not found"
        )
    
    return format_permit_response(permit)


@router.get("/traveler/{traveler_id}", response_model=List[PermitResponse])
async def get_traveler_permits(
    traveler_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all permits for a specific traveler
    
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view permits"
        )
    
    permits = await PermitsService.get_traveler_permits(db, traveler_id)
    
    return [format_permit_response(permit) for permit in permits]


@router.get("/alerts/expired", response_model=List[PermitResponse])
async def get_expired_permits(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all expired permits
    
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access", "alerts:read"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view expired permits"
        )
    
    permits = await PermitsService.get_expired_permits(db)
    
    return [format_permit_response(permit) for permit in permits]


@router.get("/alerts/expiring", response_model=List[PermitResponse])
async def get_expiring_permits(
    days_ahead: int = Query(7, ge=1, le=90, description="Number of days to look ahead"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get permits expiring within specified days
    
    Requires: Read Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:read", "permits:full_access", "alerts:read"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view expiring permits"
        )
    
    permits = await PermitsService.get_expiring_permits(db, days_ahead)
    
    return [format_permit_response(permit) for permit in permits]


@router.delete("/{permit_id}", response_model=MessageResponse)
async def delete_permit(
    permit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a permit (hard delete)
    
    Requires: Delete Permit permission
    """
    # Check permissions
    if not require_permissions(current_user, ["permits:delete", "permits:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete permits"
        )
    
    deleted = await PermitsService.delete_permit(db, permit_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permit with ID {permit_id} not found"
        )
    
    return {
        "message": f"Permit with ID {permit_id} has been deleted",
        "details": {"permit_id": permit_id}
    }
