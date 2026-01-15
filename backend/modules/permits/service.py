"""
Module Service for Permits Management
Handles business logic for permit operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from database.models import (
    Permit, Traveler, User, Gate, City,
    PermitStatus, PermitType
)


class PermitsService:
    """Service class for permit-related business logic"""
    
    @staticmethod
    async def create_permit(
        db: AsyncSession,
        permit_type: str,
        traveler_id: str,
        issued_by_user_id: str,
        gate_id: Optional[str] = None,
        city_id: Optional[str] = None,
        valid_days: int = 30,
        notes: Optional[str] = None,
        **kwargs
    ) -> Permit:
        """
        Create a new permit for a traveler
        
        Args:
            db: Database session
            permit_type: Type of permit (TRANSIT, ENTRY, EXIT, TEMPORARY)
            traveler_id: ID of the traveler
            issued_by_user_id: ID of the user issuing the permit
            gate_id: Optional specific gate for the permit
            city_id: Optional specific city for the permit
            valid_days: Number of days the permit is valid
            notes: Additional notes
            
        Returns:
            Created Permit object
        """
        # Validate permit type
        try:
            permit_type_enum = PermitType(permit_type.upper())
        except ValueError:
            raise ValueError(f"Invalid permit type: {permit_type}")
        
        # Verify traveler exists
        traveler_result = await db.execute(
            select(Traveler).where(Traveler.id == traveler_id)
        )
        traveler = traveler_result.scalar_one_or_none()
        if not traveler:
            raise ValueError(f"Traveler with ID {traveler_id} not found")
        
        # Verify issuer exists
        issuer_result = await db.execute(
            select(User).where(User.id == issued_by_user_id)
        )
        issuer = issuer_result.scalar_one_or_none()
        if not issuer:
            raise ValueError(f"User with ID {issued_by_user_id} not found")
        
        # Verify gate if provided
        if gate_id:
            gate_result = await db.execute(
                select(Gate).where(Gate.id == gate_id)
            )
            gate = gate_result.scalar_one_or_none()
            if not gate:
                raise ValueError(f"Gate with ID {gate_id} not found")
        
        # Verify city if provided
        if city_id:
            city_result = await db.execute(
                select(City).where(City.id == city_id)
            )
            city = city_result.scalar_one_or_none()
            if not city:
                raise ValueError(f"City with ID {city_id} not found")
        
        # Generate permit number
        permit_number = f"PRMT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate validity period
        valid_from = datetime.now()
        valid_until = valid_from + timedelta(days=valid_days)
        
        # Create permit
        permit = Permit(
            permit_number=permit_number,
            permit_type=permit_type_enum,
            traveler_id=traveler_id,
            issued_by=issued_by_user_id,
            gate_id=gate_id,
            city_id=city_id,
            valid_from=valid_from,
            valid_until=valid_until,
            status=PermitStatus.ACTIVE,
            notes=notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(permit)
        await db.commit()
        await db.refresh(permit)
        
        return permit
    
    @staticmethod
    async def get_permit_by_id(db: AsyncSession, permit_id: str) -> Optional[Permit]:
        """
        Get a permit by its ID with all relationships
        
        Args:
            db: Database session
            permit_id: ID of the permit
            
        Returns:
            Permit object or None
        """
        result = await db.execute(
            select(Permit)
            .options(
                selectinload(Permit.traveler),
                selectinload(Permit.issuer),
                selectinload(Permit.gate),
                selectinload(Permit.city)
            )
            .where(Permit.id == permit_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_permit_by_number(db: AsyncSession, permit_number: str) -> Optional[Permit]:
        """
        Get a permit by its permit number
        
        Args:
            db: Database session
            permit_number: Permit number to search for
            
        Returns:
            Permit object or None
        """
        result = await db.execute(
            select(Permit)
            .options(
                selectinload(Permit.traveler),
                selectinload(Permit.issuer),
                selectinload(Permit.gate),
                selectinload(Permit.city)
            )
            .where(Permit.permit_number == permit_number)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_permits(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        permit_type: Optional[str] = None,
        traveler_id: Optional[str] = None
    ) -> List[Permit]:
        """
        Get all permits with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum records to return
            status: Filter by permit status
            permit_type: Filter by permit type
            traveler_id: Filter by traveler ID
            
        Returns:
            List of Permit objects
        """
        query = select(Permit).options(
            selectinload(Permit.traveler),
            selectinload(Permit.issuer),
            selectinload(Permit.gate),
            selectinload(Permit.city)
        )
        
        # Apply filters
        if status:
            try:
                query = query.where(Permit.status == PermitStatus(status.upper()))
            except ValueError:
                pass  # Invalid status, ignore filter
        
        if permit_type:
            try:
                query = query.where(Permit.permit_type == PermitType(permit_type.upper()))
            except ValueError:
                pass  # Invalid type, ignore filter
        
        if traveler_id:
            query = query.where(Permit.traveler_id == traveler_id)
        
        # Add pagination and ordering
        query = query.order_by(Permit.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_traveler_permits(db: AsyncSession, traveler_id: str) -> List[Permit]:
        """
        Get all permits for a specific traveler
        
        Args:
            db: Database session
            traveler_id: ID of the traveler
            
        Returns:
            List of Permit objects
        """
        result = await db.execute(
            select(Permit)
            .options(
                selectinload(Permit.issuer),
                selectinload(Permit.gate),
                selectinload(Permit.city)
            )
            .where(Permit.traveler_id == traveler_id)
            .order_by(Permit.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def validate_permit(
        db: AsyncSession,
        permit_number: str,
        gate_id: Optional[str] = None
    ) -> dict:
        """
        Validate if a permit is valid for use
        
        Args:
            db: Database session
            permit_number: Permit number to validate
            gate_id: Optional gate ID to validate against
            
        Returns:
            Dictionary with validation result
        """
        permit = await PermitsService.get_permit_by_number(db, permit_number)
        
        if not permit:
            return {
                "valid": False,
                "message": "Permit not found",
                "permit": None
            }
        
        # Check if permit is active
        if permit.status != PermitStatus.ACTIVE:
            return {
                "valid": False,
                "message": f"Permit is {permit.status.value}",
                "permit": permit
            }
        
        # Check if permit has expired
        if permit.valid_until and permit.valid_until < datetime.now():
            return {
                "valid": False,
                "message": "Permit has expired",
                "permit": permit
            }
        
        # Check if permit has started
        if permit.valid_from and permit.valid_from > datetime.now():
            return {
                "valid": False,
                "message": "Permit is not yet valid",
                "permit": permit
            }
        
        # Check if gate is specified and matches
        if gate_id and permit.gate_id and permit.gate_id != gate_id:
            return {
                "valid": False,
                "message": "Permit is not valid for this gate",
                "permit": permit
            }
        
        return {
            "valid": True,
            "message": "Permit is valid",
            "permit": permit
        }
    
    @staticmethod
    async def update_permit_status(
        db: AsyncSession,
        permit_id: str,
        new_status: str,
        updated_by: str,
        reason: Optional[str] = None
    ) -> Optional[Permit]:
        """
        Update the status of a permit
        
        Args:
            db: Database session
            permit_id: ID of the permit
            new_status: New status (ACTIVE, SUSPENDED, EXPIRED, REVOKED, USED)
            updated_by: ID of the user making the update
            reason: Reason for status change
            
        Returns:
            Updated Permit object or None
        """
        try:
            status_enum = PermitStatus(new_status.upper())
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")
        
        # Get permit
        result = await db.execute(
            select(Permit).where(Permit.id == permit_id)
        )
        permit = result.scalar_one_or_none()
        
        if not permit:
            return None
        
        # Update status
        old_status = permit.status
        permit.status = status_enum
        permit.updated_at = datetime.now()
        permit.updated_by = updated_by
        permit.status_change_reason = reason
        
        await db.commit()
        await db.refresh(permit)
        
        return permit
    
    @staticmethod
    async def revoke_permit(
        db: AsyncSession,
        permit_id: str,
        revoked_by: str,
        reason: str
    ) -> Optional[Permit]:
        """
        Revoke a permit
        
        Args:
            db: Database session
            permit_id: ID of the permit
            revoked_by: ID of the user revoking the permit
            reason: Reason for revocation
            
        Returns:
            Updated Permit object or None
        """
        return await PermitsService.update_permit_status(
            db, permit_id, "REVOKED", revoked_by, reason
        )
    
    @staticmethod
    async def suspend_permit(
        db: AsyncSession,
        permit_id: str,
        suspended_by: str,
        reason: str
    ) -> Optional[Permit]:
        """
        Suspend a permit temporarily
        
        Args:
            db: Database session
            permit_id: ID of the permit
            suspended_by: ID of the user suspending the permit
            reason: Reason for suspension
            
        Returns:
            Updated Permit object or None
        """
        return await PermitsService.update_permit_status(
            db, permit_id, "SUSPENDED", suspended_by, reason
        )
    
    @staticmethod
    async def renew_permit(
        db: AsyncSession,
        permit_id: str,
        renewed_by: str,
        additional_days: int = 30
    ) -> Optional[Permit]:
        """
        Renew an expired or expiring permit
        
        Args:
            db: Database session
            permit_id: ID of the permit
            renewed_by: ID of the user renewing the permit
            additional_days: Number of days to add to validity
            
        Returns:
            Updated Permit object or None
        """
        result = await db.execute(
            select(Permit).where(Permit.id == permit_id)
        )
        permit = result.scalar_one_or_none()
        
        if not permit:
            return None
        
        # Update validity period
        if permit.status == PermitStatus.EXPIRED:
            permit.valid_from = datetime.now()
        else:
            permit.valid_from = permit.valid_until or datetime.now()
        
        permit.valid_until = permit.valid_from + timedelta(days=additional_days)
        permit.status = PermitStatus.ACTIVE
        permit.updated_at = datetime.now()
        permit.updated_by = renewed_by
        permit.renewed = True
        permit.renewal_count = (permit.renewal_count or 0) + 1
        
        await db.commit()
        await db.refresh(permit)
        
        return permit
    
    @staticmethod
    async def get_expired_permits(db: AsyncSession) -> List[Permit]:
        """
        Get all expired permits
        
        Args:
            db: Database session
            
        Returns:
            List of expired Permit objects
        """
        result = await db.execute(
            select(Permit)
            .options(
                selectinload(Permit.traveler),
                selectinload(Permit.issuer)
            )
            .where(Permit.status == PermitStatus.ACTIVE)
            .where(Permit.valid_until < datetime.now())
            .order_by(Permit.valid_until.asc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_expiring_permits(
        db: AsyncSession,
        days_ahead: int = 7
    ) -> List[Permit]:
        """
        Get permits expiring within specified days
        
        Args:
            db: Database session
            days_ahead: Number of days to look ahead
            
        Returns:
            List of Permit objects expiring soon
        """
        expiry_threshold = datetime.now() + timedelta(days=days_ahead)
        
        result = await db.execute(
            select(Permit)
            .options(
                selectinload(Permit.traveler),
                selectinload(Permit.issuer)
            )
            .where(Permit.status == PermitStatus.ACTIVE)
            .where(Permit.valid_until <= expiry_threshold)
            .where(Permit.valid_until > datetime.now())
            .order_by(Permit.valid_until.asc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def delete_permit(db: AsyncSession, permit_id: str) -> bool:
        """
        Delete a permit (hard delete)
        
        Args:
            db: Database session
            permit_id: ID of the permit to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(Permit).where(Permit.id == permit_id)
        )
        permit = result.scalar_one_or_none()
        
        if not permit:
            return False
        
        await db.delete(permit)
        await db.commit()
        
        return True
