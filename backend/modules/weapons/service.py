"""
Module Service for Weapons Management
Handles business logic for weapon registration and tracking
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List, Optional
import uuid

from database.models import (
    Weapon, WeaponRegistration, Traveler, User, City, Gate,
    WeaponType, WeaponStatus, WeaponRegistrationStatus
)


class WeaponsService:
    """Service class for weapon-related business logic"""
    
    @staticmethod
    async def register_weapon(
        db: AsyncSession,
        weapon_type: str,
        serial_number: str,
        description: str,
        registered_by_user_id: str,
        owner_name: str,
        owner_national_id: Optional[str] = None,
        city_id: Optional[str] = None,
        permit_id: Optional[str] = None,
        license_number: Optional[str] = None,
        license_expiry: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> WeaponRegistration:
        """
        Register a new weapon
        
        Args:
            db: Database session
            weapon_type: Type of weapon (FIREARM, KNIFE, EXPLOSIVE, CHEMICAL, OTHER)
            serial_number: Serial number of the weapon
            description: Description of the weapon
            registered_by_user_id: ID of the user registering the weapon
            owner_name: Name of the weapon owner
            owner_national_id: National ID of the owner
            city_id: City where weapon is registered
            permit_id: Associated permit ID
            license_number: License number
            license_expiry: License expiry date
            notes: Additional notes
            
        Returns:
            Created WeaponRegistration object
        """
        # Validate weapon type
        try:
            weapon_type_enum = WeaponType(weapon_type.upper())
        except ValueError:
            raise ValueError(f"Invalid weapon type: {weapon_type}")
        
        # Check if serial number already exists
        existing_result = await db.execute(
            select(Weapon).where(Weapon.serial_number == serial_number)
        )
        existing_weapon = existing_result.scalar_one_or_none()
        if existing_weapon:
            raise ValueError(f"Weapon with serial number {serial_number} already exists")
        
        # Verify registrar exists
        user_result = await db.execute(
            select(User).where(User.id == registered_by_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with ID {registered_by_user_id} not found")
        
        # Verify city if provided
        if city_id:
            city_result = await db.execute(
                select(City).where(City.id == city_id)
            )
            city = city_result.scalar_one_or_none()
            if not city:
                raise ValueError(f"City with ID {city_id} not found")
        
        # Create weapon
        weapon = Weapon(
            serial_number=serial_number,
            weapon_type=weapon_type_enum,
            description=description,
            status=WeaponStatus.REGISTERED,
            registered_by=registered_by_user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(weapon)
        await db.flush()  # Get the weapon ID
        
        # Create registration record
        registration = WeaponRegistration(
            weapon_id=weapon.id,
            owner_name=owner_name,
            owner_national_id=owner_national_id,
            city_id=city_id,
            permit_id=permit_id,
            license_number=license_number,
            license_expiry=license_expiry,
            registration_status=WeaponRegistrationStatus.ACTIVE,
            registered_by=registered_by_user_id,
            registration_date=datetime.now(),
            notes=notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(registration)
        await db.commit()
        await db.refresh(registration)
        
        return registration
    
    @staticmethod
    async def get_weapon_by_id(db: AsyncSession, weapon_id: str) -> Optional[Weapon]:
        """
        Get a weapon by its ID with relationships
        
        Args:
            db: Database session
            weapon_id: ID of the weapon
            
        Returns:
            Weapon object or None
        """
        result = await db.execute(
            select(Weapon)
            .options(
                selectinload(Weapon.registrations).selectinload(WeaponRegistration.city),
                selectinload(Weapon.registered_by_user)
            )
            .where(Weapon.id == weapon_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_weapon_by_serial(db: AsyncSession, serial_number: str) -> Optional[Weapon]:
        """
        Get a weapon by its serial number
        
        Args:
            db: Database session
            serial_number: Serial number of the weapon
            
        Returns:
            Weapon object or None
        """
        result = await db.execute(
            select(Weapon)
            .options(
                selectinload(Weapon.registrations).selectinload(WeaponRegistration.city),
                selectinload(Weapon.registered_by_user)
            )
            .where(Weapon.serial_number == serial_number)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_weapons(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        weapon_type: Optional[str] = None,
        status: Optional[str] = None,
        city_id: Optional[str] = None,
        owner_national_id: Optional[str] = None
    ) -> List[Weapon]:
        """
        Get all weapons with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            weapon_type: Filter by weapon type
            status: Filter by weapon status
            city_id: Filter by registration city
            owner_national_id: Filter by owner national ID
            
        Returns:
            List of Weapon objects
        """
        query = select(Weapon).options(
            selectinload(Weapon.registrations).selectinload(WeaponRegistration.city),
            selectinload(Weapon.registered_by_user)
        )
        
        # Apply filters
        conditions = []
        
        if weapon_type:
            try:
                conditions.append(Weapon.weapon_type == WeaponType(weapon_type.upper()))
            except ValueError:
                pass
        
        if status:
            try:
                conditions.append(Weapon.status == WeaponStatus(status.upper()))
            except ValueError:
                pass
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Add pagination and ordering
        query = query.order_by(Weapon.serial_number.asc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_weapon_status(
        db: AsyncSession,
        weapon_id: str,
        new_status: str,
        updated_by: str,
        reason: Optional[str] = None
    ) -> Optional[Weapon]:
        """
        Update the status of a weapon
        
        Args:
            db: Database session
            weapon_id: ID of the weapon
            new_status: New status (REGISTERED, CONFISCATED, LOST, STOLEN, DESTROYED)
            updated_by: ID of the user making the update
            reason: Reason for status change
            
        Returns:
            Updated Weapon object or None
        """
        try:
            status_enum = WeaponStatus(new_status.upper())
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")
        
        # Get weapon
        result = await db.execute(
            select(Weapon).where(Weapon.id == weapon_id)
        )
        weapon = result.scalar_one_or_none()
        
        if not weapon:
            return None
        
        # Update status
        weapon.status = status_enum
        weapon.updated_at = datetime.now()
        weapon.updated_by = updated_by
        weapon.status_change_reason = reason
        
        await db.commit()
        await db.refresh(weapon)
        
        return weapon
    
    @staticmethod
    async def confiscate_weapon(
        db: AsyncSession,
        weapon_id: str,
        confiscated_by: str,
        reason: str,
        location_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Weapon]:
        """
        Confiscate a weapon
        
        Args:
            db: Database session
            weapon_id: ID of the weapon
            confiscated_by: ID of the user confiscating
            reason: Reason for confiscation
            location_id: Location where confiscated
            notes: Additional notes
            
        Returns:
            Updated Weapon object or None
        """
        return await WeaponsService.update_weapon_status(
            db, weapon_id, "CONFISCATED", confiscated_by, reason
        )
    
    @staticmethod
    async def report_lost_weapon(
        db: AsyncSession,
        weapon_id: str,
        reported_by: str,
        reason: str
    ) -> Optional[Weapon]:
        """
        Report a weapon as lost
        
        Args:
            db: Database session
            weapon_id: ID of the weapon
            reported_by: ID of the user reporting
            reason: Description of how it was lost
            
        Returns:
            Updated Weapon object or None
        """
        return await WeaponsService.update_weapon_status(
            db, weapon_id, "LOST", reported_by, reason
        )
    
    @staticmethod
    async def report_stolen_weapon(
        db: AsyncSession,
        weapon_id: str,
        reported_by: str,
        reason: str,
        police_report_number: Optional[str] = None
    ) -> Optional[Weapon]:
        """
        Report a weapon as stolen
        
        Args:
            db: Database session
            weapon_id: ID of the weapon
            reported_by: ID of the user reporting
            reason: Description of the theft
            police_report_number: Police report number
            
        Returns:
            Updated Weapon object or None
        """
        weapon = await WeaponsService.update_weapon_status(
            db, weapon_id, "STOLEN", reported_by, reason
        )
        
        if weapon and police_report_number:
            # Create alert for stolen weapon
            from modules.alerts.service import AlertsService
            await AlertsService.create_alert(
                db=db,
                alert_type="WEAPON",
                title=f"Stolen Weapon Reported: {weapon.serial_number}",
                description=f"Weapon with serial number {weapon.serial_number} reported stolen. {reason}",
                severity="CRITICAL",
                created_by_user_id=reported_by,
                metadata={
                    "weapon_id": weapon_id,
                    "serial_number": weapon.serial_number,
                    "police_report_number": police_report_number
                }
            )
        
        return weapon
    
    @staticmethod
    async def check_weapon_status(
        db: AsyncSession,
        serial_number: str
    ) -> dict:
        """
        Check the status of a weapon by serial number
        
        Args:
            db: Database session
            serial_number: Serial number to check
            
        Returns:
            Dictionary with weapon status
        """
        weapon = await WeaponsService.get_weapon_by_serial(db, serial_number)
        
        if not weapon:
            return {
                "found": False,
                "message": "Weapon not found in registry"
            }
        
        # Get latest registration
        registration = None
        if weapon.registrations:
            registration = max(weapon.registrations, key=lambda r: r.registration_date)
        
        return {
            "found": True,
            "weapon_id": weapon.id,
            "serial_number": weapon.serial_number,
            "weapon_type": weapon.weapon_type.value if hasattr(weapon.weapon_type, 'value') else str(weapon.weapon_type),
            "status": weapon.status.value if hasattr(weapon.status, 'value') else str(weapon.status),
            "description": weapon.description,
            "owner_name": registration.owner_name if registration else None,
            "owner_national_id": registration.owner_national_id if registration else None,
            "is_confiscated": weapon.status == WeaponStatus.CONFISCATED,
            "is_stolen": weapon.status == WeaponStatus.STOLEN,
            "is_lost": weapon.status == WeaponStatus.LOST,
            "requires_alert": weapon.status in [WeaponStatus.CONFISCATED, WeaponStatus.STOLEN, WeaponStatus.LOST]
        }
    
    @staticmethod
    async def get_weapons_by_owner(
        db: AsyncSession,
        owner_national_id: str
    ) -> List[Weapon]:
        """
        Get all weapons registered to a specific owner
        
        Args:
            db: Database session
            owner_national_id: National ID of the owner
            
        Returns:
            List of Weapon objects
        """
        # This would require a more complex query in real implementation
        # For now, return all weapons and filter
        result = await db.execute(
            select(Weapon)
            .options(
                selectinload(Weapon.registrations)
            )
            .order_by(Weapon.serial_number.asc())
        )
        
        weapons = result.scalars().all()
        
        # Filter by owner (in real implementation, this would be done at database level)
        filtered_weapons = []
        for weapon in weapons:
            for reg in weapon.registrations:
                if reg.owner_national_id == owner_national_id:
                    filtered_weapons.append(weapon)
                    break
        
        return filtered_weapons
    
    @staticmethod
    async def get_confiscated_weapons(db: AsyncSession) -> List[Weapon]:
        """
        Get all confiscated weapons
        
        Args:
            db: Database session
            
        Returns:
            List of confiscated Weapon objects
        """
        result = await db.execute(
            select(Weapon)
            .options(
                selectinload(Weapon.registrations).selectinload(WeaponRegistration.city)
            )
            .where(Weapon.status == WeaponStatus.CONFISCATED)
            .order_by(Weapon.updated_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_stolen_weapons(db: AsyncSession) -> List[Weapon]:
        """
        Get all stolen weapons
        
        Args:
            db: Database session
            
        Returns:
            List of stolen Weapon objects
        """
        result = await db.execute(
            select(Weapon)
            .options(
                selectinload(Weapon.registrations).selectinload(WeaponRegistration.city)
            )
            .where(Weapon.status == WeaponStatus.STOLEN)
            .order_by(Weapon.updated_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_weapons_summary(db: AsyncSession) -> dict:
        """
        Get summary statistics for weapons
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with weapon statistics
        """
        # Get counts by status
        status_counts = {}
        for status in WeaponStatus:
            result = await db.execute(
                select(Weapon).where(Weapon.status == status)
            )
            status_counts[status.value] = len(result.scalars().all())
        
        # Get counts by type
        type_counts = {}
        for weapon_type in WeaponType:
            result = await db.execute(
                select(Weapon).where(Weapon.weapon_type == weapon_type)
            )
            type_counts[weapon_type.value] = len(result.scalars().all())
        
        # Get counts for dangerous weapons
        dangerous_result = await db.execute(
            select(Weapon).where(
                Weapon.weapon_type.in_([WeaponType.FIREARM, WeaponType.EXPLOSIVE, WeaponType.CHEMICAL])
            )
        )
        dangerous_count = len(dangerous_result.scalars().all())
        
        return {
            "total_weapons": sum(status_counts.values()),
            "confiscated": status_counts.get(WeaponStatus.CONFISCATED.value, 0),
            "stolen": status_counts.get(WeaponStatus.STOLEN.value, 0),
            "lost": status_counts.get(WeaponStatus.LOST.value, 0),
            "dangerous_weapons": dangerous_count,
            "by_status": status_counts,
            "by_type": type_counts
        }
    
    @staticmethod
    async def get_weapon_registration_history(
        db: AsyncSession,
        weapon_id: str
    ) -> List[WeaponRegistration]:
        """
        Get the registration history for a weapon
        
        Args:
            db: Database session
            weapon_id: ID of the weapon
            
        Returns:
            List of WeaponRegistration objects
        """
        result = await db.execute(
            select(WeaponRegistration)
            .options(
                selectinload(WeaponRegistration.city),
                selectinload(WeaponRegistration.registered_by_user)
            )
            .where(WeaponRegistration.weapon_id == weapon_id)
            .order_by(WeaponRegistration.registration_date.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def renew_weapon_license(
        db: AsyncSession,
        registration_id: str,
        new_expiry: datetime,
        renewed_by: str
    ) -> Optional[WeaponRegistration]:
        """
        Renew a weapon license
        
        Args:
            db: Database session
            registration_id: ID of the registration
            new_expiry: New license expiry date
            renewed_by: ID of the user renewing
            
        Returns:
            Updated WeaponRegistration object or None
        """
        result = await db.execute(
            select(WeaponRegistration).where(WeaponRegistration.id == registration_id)
        )
        registration = result.scalar_one_or_none()
        
        if not registration:
            return None
        
        registration.license_expiry = new_expiry
        registration.updated_at = datetime.now()
        registration.updated_by = renewed_by
        
        await db.commit()
        await db.refresh(registration)
        
        return registration
    
    @staticmethod
    async def delete_weapon(db: AsyncSession, weapon_id: str) -> bool:
        """
        Delete a weapon (hard delete)
        
        Args:
            db: Database session
            weapon_id: ID of the weapon to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(Weapon).where(Weapon.id == weapon_id)
        )
        weapon = result.scalar_one_or_none()
        
        if not weapon:
            return False
        
        await db.delete(weapon)
        await db.commit()
        
        return True
