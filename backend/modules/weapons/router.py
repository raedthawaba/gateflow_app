"""
Router for Weapons Management
Defines API endpoints for weapon operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from core.database import get_db
from core.security import get_current_user, require_permissions
from modules.weapons.service import WeaponsService


router = APIRouter(prefix="/weapons", tags=["Weapons Management"])


# Pydantic Models for Request/Response
class WeaponCreateRequest(BaseModel):
    """Request model for registering a new weapon"""
    weapon_type: str = Field(..., description="Type of weapon (FIREARM, KNIFE, EXPLOSIVE, CHEMICAL, OTHER)")
    serial_number: str = Field(..., min_length=3, max_length=50, description="Serial number of the weapon")
    description: str = Field(..., min_length=10, max_length=500, description="Description of the weapon")
    owner_name: str = Field(..., min_length=2, max_length=200, description="Name of the weapon owner")
    owner_national_id: Optional[str] = Field(None, description="National ID of the owner")
    city_id: Optional[str] = Field(None, description="City where weapon is registered")
    permit_id: Optional[str] = Field(None, description="Associated permit ID")
    license_number: Optional[str] = Field(None, description="License number")
    license_expiry: Optional[datetime] = Field(None, description="License expiry date")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class WeaponStatusRequest(BaseModel):
    """Request model for updating weapon status"""
    status: str = Field(..., description="New weapon status")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")


class WeaponConfiscateRequest(BaseModel):
    """Request model for confiscating a weapon"""
    reason: str = Field(..., min_length=10, description="Reason for confiscation")
    location_id: Optional[str] = Field(None, description="Location where confiscated")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class WeaponReportRequest(BaseModel):
    """Request model for reporting lost/stolen weapon"""
    reason: str = Field(..., min_length=10, description="Description of incident")
    police_report_number: Optional[str] = Field(None, description="Police report number")


class WeaponRenewRequest(BaseModel):
    """Request model for renewing weapon license"""
    new_expiry: datetime = Field(..., description="New license expiry date")


class WeaponResponse(BaseModel):
    """Response model for weapon data"""
    id: str
    serial_number: str
    weapon_type: str
    description: str
    status: str
    owner_name: Optional[str] = None
    owner_national_id: Optional[str] = None
    city_id: Optional[str] = None
    city_name: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    registered_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WeaponCheckResponse(BaseModel):
    """Response model for weapon status check"""
    found: bool
    message: str
    weapon_id: Optional[str] = None
    serial_number: Optional[str] = None
    weapon_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    owner_name: Optional[str] = None
    owner_national_id: Optional[str] = None
    is_confiscated: bool = False
    is_stolen: bool = False
    is_lost: bool = False
    requires_alert: bool = False


class WeaponSummaryResponse(BaseModel):
    """Response model for weapon summary statistics"""
    total_weapons: int
    confiscated: int
    stolen: int
    lost: int
    dangerous_weapons: int
    by_status: dict
    by_type: dict


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    details: Optional[dict] = None


def format_weapon_response(weapon, registration=None) -> dict:
    """Format weapon object for response"""
    if registration is None and weapon.registrations:
        registration = max(weapon.registrations, key=lambda r: r.registration_date)
    
    return {
        "id": weapon.id,
        "serial_number": weapon.serial_number,
        "weapon_type": weapon.weapon_type.value if hasattr(weapon.weapon_type, 'value') else str(weapon.weapon_type),
        "description": weapon.description,
        "status": weapon.status.value if hasattr(weapon.status, 'value') else str(weapon.status),
        "owner_name": registration.owner_name if registration else None,
        "owner_national_id": registration.owner_national_id if registration else None,
        "city_id": registration.city_id if registration else None,
        "city_name": registration.city.city_name if registration and registration.city else None,
        "license_number": registration.license_number if registration else None,
        "license_expiry": registration.license_expiry.isoformat() if registration and registration.license_expiry else None,
        "registered_by": weapon.registered_by,
        "created_at": weapon.created_at.isoformat() if weapon.created_at else None,
        "updated_at": weapon.updated_at.isoformat() if weapon.updated_at else None
    }


@router.post("/register", response_model=WeaponResponse, status_code=status.HTTP_201_CREATED)
async def register_weapon(
    request: WeaponCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Register a new weapon
    
    Requires: Register Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:register", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to register weapons"
        )
    
    try:
        registration = await WeaponsService.register_weapon(
            db=db,
            weapon_type=request.weapon_type,
            serial_number=request.serial_number,
            description=request.description,
            registered_by_user_id=current_user["user_id"],
            owner_name=request.owner_name,
            owner_national_id=request.owner_national_id,
            city_id=request.city_id,
            permit_id=request.permit_id,
            license_number=request.license_number,
            license_expiry=request.license_expiry,
            notes=request.notes
        )
        
        # Get the weapon with relationships
        weapon = await WeaponsService.get_weapon_by_id(db, registration.weapon_id)
        
        return format_weapon_response(weapon, registration)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering weapon: {str(e)}"
        )


@router.get("/", response_model=List[WeaponResponse])
async def get_all_weapons(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    weapon_type: Optional[str] = Query(None, description="Filter by weapon type"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    city_id: Optional[str] = Query(None, description="Filter by city ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all weapons with optional filters
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapons"
        )
    
    try:
        weapons = await WeaponsService.get_all_weapons(
            db=db,
            skip=skip,
            limit=limit,
            weapon_type=weapon_type,
            status=status_filter,
            city_id=city_id
        )
        
        return [format_weapon_response(weapon) for weapon in weapons]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching weapons: {str(e)}"
        )


@router.get("/{weapon_id}", response_model=WeaponResponse)
async def get_weapon_by_id(
    weapon_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific weapon by ID
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapons"
        )
    
    weapon = await WeaponsService.get_weapon_by_id(db, weapon_id)
    
    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with ID {weapon_id} not found"
        )
    
    return format_weapon_response(weapon)


@router.get("/serial/{serial_number}", response_model=WeaponResponse)
async def get_weapon_by_serial(
    serial_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a weapon by its serial number
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapons"
        )
    
    weapon = await WeaponsService.get_weapon_by_serial(db, serial_number)
    
    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with serial number {serial_number} not found"
        )
    
    return format_weapon_response(weapon)


@router.post("/check-status", response_model=WeaponCheckResponse)
async def check_weapon_status(
    serial_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check the status of a weapon by serial number
    
    This endpoint can be used at checkpoints to verify weapons
    Requires: Check Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:check", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to check weapon status"
        )
    
    result = await WeaponsService.check_weapon_status(db, serial_number)
    
    return WeaponCheckResponse(**result)


@router.put("/{weapon_id}/status", response_model=WeaponResponse)
async def update_weapon_status(
    weapon_id: str,
    request: WeaponStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update the status of a weapon
    
    Requires: Update Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:update", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update weapon status"
        )
    
    try:
        weapon = await WeaponsService.update_weapon_status(
            db=db,
            weapon_id=weapon_id,
            new_status=request.status,
            updated_by=current_user["user_id"],
            reason=request.reason
        )
        
        if not weapon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Weapon with ID {weapon_id} not found"
            )
        
        return format_weapon_response(weapon)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating weapon status: {str(e)}"
        )


@router.post("/{weapon_id}/confiscate", response_model=WeaponResponse)
async def confiscate_weapon(
    weapon_id: str,
    request: WeaponConfiscateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Confiscate a weapon
    
    Requires: Confiscate Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:confiscate", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to confiscate weapons"
        )
    
    weapon = await WeaponsService.confiscate_weapon(
        db=db,
        weapon_id=weapon_id,
        confiscated_by=current_user["user_id"],
        reason=request.reason,
        location_id=request.location_id,
        notes=request.notes
    )
    
    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with ID {weapon_id} not found"
        )
    
    return format_weapon_response(weapon)


@router.post("/{weapon_id}/report-lost", response_model=WeaponResponse)
async def report_lost_weapon(
    weapon_id: str,
    request: WeaponReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Report a weapon as lost
    
    Requires: Report Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:report", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to report weapons"
        )
    
    weapon = await WeaponsService.report_lost_weapon(
        db=db,
        weapon_id=weapon_id,
        reported_by=current_user["user_id"],
        reason=request.reason
    )
    
    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with ID {weapon_id} not found"
        )
    
    return format_weapon_response(weapon)


@router.post("/{weapon_id}/report-stolen", response_model=WeaponResponse)
async def report_stolen_weapon(
    weapon_id: str,
    request: WeaponReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Report a weapon as stolen
    
    Requires: Report Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:report", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to report weapons"
        )
    
    weapon = await WeaponsService.report_stolen_weapon(
        db=db,
        weapon_id=weapon_id,
        reported_by=current_user["user_id"],
        reason=request.reason,
        police_report_number=request.police_report_number
    )
    
    if not weapon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with ID {weapon_id} not found"
        )
    
    return format_weapon_response(weapon)


@router.get("/owner/{owner_national_id}", response_model=List[WeaponResponse])
async def get_weapons_by_owner(
    owner_national_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all weapons registered to a specific owner
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapons"
        )
    
    weapons = await WeaponsService.get_weapons_by_owner(db, owner_national_id)
    
    return [format_weapon_response(weapon) for weapon in weapons]


@router.get("/confiscated/all", response_model=List[WeaponResponse])
async def get_confiscated_weapons(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all confiscated weapons
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapons"
        )
    
    weapons = await WeaponsService.get_confiscated_weapons(db)
    
    return [format_weapon_response(weapon) for weapon in weapons]


@router.get("/stolen/all", response_model=List[WeaponResponse])
async def get_stolen_weapons(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all stolen weapons
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapons"
        )
    
    weapons = await WeaponsService.get_stolen_weapons(db)
    
    return [format_weapon_response(weapon) for weapon in weapons]


@router.get("/summary/stats", response_model=WeaponSummaryResponse)
async def get_weapons_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get summary statistics for weapons
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapon statistics"
        )
    
    summary = await WeaponsService.get_weapons_summary(db)
    
    return WeaponSummaryResponse(**summary)


@router.get("/{weapon_id}/history", response_model=List[dict])
async def get_weapon_registration_history(
    weapon_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the registration history for a weapon
    
    Requires: Read Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:read", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view weapon history"
        )
    
    history = await WeaponsService.get_weapon_registration_history(db, weapon_id)
    
    return [
        {
            "id": reg.id,
            "owner_name": reg.owner_name,
            "owner_national_id": reg.owner_national_id,
            "city_name": reg.city.city_name if reg.city else None,
            "license_number": reg.license_number,
            "license_expiry": reg.license_expiry.isoformat() if reg.license_expiry else None,
            "status": reg.registration_status.value if hasattr(reg.registration_status, 'value') else str(reg.registration_status),
            "registration_date": reg.registration_date.isoformat() if reg.registration_date else None,
            "notes": reg.notes
        }
        for reg in history
    ]


@router.put("/registration/{registration_id}/renew", response_model=dict)
async def renew_weapon_license(
    registration_id: str,
    request: WeaponRenewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Renew a weapon license
    
    Requires: Renew Weapon License permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:license", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to renew weapon licenses"
        )
    
    registration = await WeaponsService.renew_weapon_license(
        db=db,
        registration_id=registration_id,
        new_expiry=request.new_expiry,
        renewed_by=current_user["user_id"]
    )
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration with ID {registration_id} not found"
        )
    
    return {
        "message": "Weapon license renewed successfully",
        "details": {
            "registration_id": registration_id,
            "new_expiry": request.new_expiry.isoformat()
        }
    }


@router.delete("/{weapon_id}", response_model=MessageResponse)
async def delete_weapon(
    weapon_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a weapon (hard delete)
    
    Requires: Delete Weapon permission
    """
    # Check permissions
    if not require_permissions(current_user, ["weapons:delete", "weapons:full_access"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete weapons"
        )
    
    deleted = await WeaponsService.delete_weapon(db, weapon_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weapon with ID {weapon_id} not found"
        )
    
    return {
        "message": f"Weapon with ID {weapon_id} has been deleted",
        "details": {"weapon_id": weapon_id}
    }
