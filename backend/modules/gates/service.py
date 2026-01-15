"""
Module Service for Gates Management
Handles business logic for gate operations and control
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List, Optional
import uuid

from database.models import (
    Gate, City, User,
    GateType, GateStatus, GateDirection
)


class GatesService:
    """Service class for gate-related business logic"""
    
    @staticmethod
    async def create_gate(
        db: AsyncSession,
        gate_name: str,
        gate_code: str,
        gate_type: str,
        city_id: str,
        direction: str = "BIDIRECTIONAL",
        created_by_user_id: Optional[str] = None,
        location_coordinates: Optional[str] = None,
        max_capacity: Optional[int] = None,
        operating_hours: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Gate:
        """
        Create a new gate
        
        Args:
            db: Database session
            gate_name: Name of the gate
            gate_code: Unique code for the gate
            gate_type: Type of gate (LAND, SEA, AIR, RAIL, CHECKPOINT)
            city_id: ID of the city where the gate is located
            direction: Gate direction (ENTRY, EXIT, BIDIRECTIONAL)
            created_by_user_id: ID of the user creating the gate
            location_coordinates: GPS coordinates
            max_capacity: Maximum capacity at the gate
            operating_hours: Operating hours in JSON format
            notes: Additional notes
            
        Returns:
            Created Gate object
        """
        # Validate gate type
        try:
            gate_type_enum = GateType(gate_type.upper())
        except ValueError:
            raise ValueError(f"Invalid gate type: {gate_type}")
        
        # Validate direction
        try:
            direction_enum = GateDirection(direction.upper())
        except ValueError:
            raise ValueError(f"Invalid direction: {direction}")
        
        # Verify city exists
        city_result = await db.execute(
            select(City).where(City.id == city_id)
        )
        city = city_result.scalar_one_or_none()
        if not city:
            raise ValueError(f"City with ID {city_id} not found")
        
        # Check if gate code already exists
        existing_result = await db.execute(
            select(Gate).where(Gate.gate_code == gate_code)
        )
        existing_gate = existing_result.scalar_one_or_none()
        if existing_gate:
            raise ValueError(f"Gate with code {gate_code} already exists")
        
        # Create gate
        gate = Gate(
            gate_name=gate_name,
            gate_code=gate_code,
            gate_type=gate_type_enum,
            city_id=city_id,
            direction=direction_enum,
            status=GateStatus.OPEN,
            created_by=created_by_user_id,
            location_coordinates=location_coordinates,
            max_capacity=max_capacity,
            operating_hours=operating_hours,
            notes=notes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(gate)
        await db.commit()
        await db.refresh(gate)
        
        return gate
    
    @staticmethod
    async def get_gate_by_id(db: AsyncSession, gate_id: str) -> Optional[Gate]:
        """
        Get a gate by its ID with relationships
        
        Args:
            db: Database session
            gate_id: ID of the gate
            
        Returns:
            Gate object or None
        """
        result = await db.execute(
            select(Gate)
            .options(
                selectinload(Gate.city),
                selectinload(Gate.created_by_user)
            )
            .where(Gate.id == gate_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_gate_by_code(db: AsyncSession, gate_code: str) -> Optional[Gate]:
        """
        Get a gate by its code
        
        Args:
            db: Database session
            gate_code: Code of the gate
            
        Returns:
            Gate object or None
        """
        result = await db.execute(
            select(Gate)
            .options(
                selectinload(Gate.city),
                selectinload(Gate.created_by_user)
            )
            .where(Gate.gate_code == gate_code)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_gates(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        city_id: Optional[str] = None,
        gate_type: Optional[str] = None,
        status: Optional[str] = None,
        direction: Optional[str] = None
    ) -> List[Gate]:
        """
        Get all gates with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            city_id: Filter by city ID
            gate_type: Filter by gate type
            status: Filter by gate status
            direction: Filter by direction
            
        Returns:
            List of Gate objects
        """
        query = select(Gate).options(
            selectinload(Gate.city),
            selectinload(Gate.created_by_user)
        )
        
        # Apply filters
        conditions = []
        
        if city_id:
            conditions.append(Gate.city_id == city_id)
        
        if gate_type:
            try:
                conditions.append(Gate.gate_type == GateType(gate_type.upper()))
            except ValueError:
                pass
        
        if status:
            try:
                conditions.append(Gate.status == GateStatus(status.upper()))
            except ValueError:
                pass
        
        if direction:
            try:
                conditions.append(Gate.direction == GateDirection(direction.upper()))
            except ValueError:
                pass
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Add pagination and ordering
        query = query.order_by(Gate.gate_name.asc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_gates_by_city(db: AsyncSession, city_id: str) -> List[Gate]:
        """
        Get all gates in a specific city
        
        Args:
            db: Database session
            city_id: ID of the city
            
        Returns:
            List of Gate objects
        """
        result = await db.execute(
            select(Gate)
            .options(selectinload(Gate.created_by_user))
            .where(Gate.city_id == city_id)
            .order_by(Gate.gate_name.asc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_gate_status(
        db: AsyncSession,
        gate_id: str,
        new_status: str,
        updated_by: str,
        reason: Optional[str] = None
    ) -> Optional[Gate]:
        """
        Update the status of a gate
        
        Args:
            db: Database session
            gate_id: ID of the gate
            new_status: New status (OPEN, CLOSED, MAINTENANCE, EMERGENCY)
            updated_by: ID of the user making the update
            reason: Reason for status change
            
        Returns:
            Updated Gate object or None
        """
        try:
            status_enum = GateStatus(new_status.upper())
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")
        
        # Get gate
        result = await db.execute(
            select(Gate).where(Gate.id == gate_id)
        )
        gate = result.scalar_one_or_none()
        
        if not gate:
            return None
        
        # Update status
        old_status = gate.status
        gate.status = status_enum
        gate.updated_at = datetime.now()
        gate.updated_by = updated_by
        gate.status_change_reason = reason
        
        await db.commit()
        await db.refresh(gate)
        
        return gate
    
    @staticmethod
    async def open_gate(
        db: AsyncSession,
        gate_id: str,
        opened_by: str,
        reason: Optional[str] = None
    ) -> Optional[Gate]:
        """
        Open a gate
        
        Args:
            db: Database session
            gate_id: ID of the gate
            opened_by: ID of the user opening the gate
            reason: Reason for opening
            
        Returns:
            Updated Gate object or None
        """
        return await GatesService.update_gate_status(
            db, gate_id, "OPEN", opened_by, reason
        )
    
    @staticmethod
    async def close_gate(
        db: AsyncSession,
        gate_id: str,
        closed_by: str,
        reason: Optional[str] = None
    ) -> Optional[Gate]:
        """
        Close a gate
        
        Args:
            db: Database session
            gate_id: ID of the gate
            closed_by: ID of the user closing the gate
            reason: Reason for closing
            
        Returns:
            Updated Gate object or None
        """
        return await GatesService.update_gate_status(
            db, gate_id, "CLOSED", closed_by, reason
        )
    
    @staticmethod
    async def set_maintenance(
        db: AsyncSession,
        gate_id: str,
        maintenance_by: str,
        reason: Optional[str] = None
    ) -> Optional[Gate]:
        """
        Set a gate to maintenance mode
        
        Args:
            db: Database session
            gate_id: ID of the gate
            maintenance_by: ID of the user setting maintenance
            reason: Reason for maintenance
            
        Returns:
            Updated Gate object or None
        """
        return await GatesService.update_gate_status(
            db, gate_id, "MAINTENANCE", maintenance_by, reason
        )
    
    @staticmethod
    async def set_emergency(
        db: AsyncSession,
        gate_id: str,
        emergency_by: str,
        reason: str
    ) -> Optional[Gate]:
        """
        Set a gate to emergency status
        
        Args:
            db: Database session
            gate_id: ID of the gate
            emergency_by: ID of the user setting emergency
            reason: Emergency reason (required)
            
        Returns:
            Updated Gate object or None
        """
        return await GatesService.update_gate_status(
            db, gate_id, "EMERGENCY", emergency_by, reason
        )
    
    @staticmethod
    async def update_gate(
        db: AsyncSession,
        gate_id: str,
        gate_name: Optional[str] = None,
        location_coordinates: Optional[str] = None,
        max_capacity: Optional[int] = None,
        operating_hours: Optional[str] = None,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> Optional[Gate]:
        """
        Update gate details
        
        Args:
            db: Database session
            gate_id: ID of the gate
            gate_name: New gate name
            location_coordinates: New GPS coordinates
            max_capacity: New maximum capacity
            operating_hours: New operating hours
            notes: New notes
            updated_by: ID of the user making the update
            
        Returns:
            Updated Gate object or None
        """
        result = await db.execute(
            select(Gate).where(Gate.id == gate_id)
        )
        gate = result.scalar_one_or_none()
        
        if not gate:
            return None
        
        # Update fields
        if gate_name is not None:
            gate.gate_name = gate_name
        if location_coordinates is not None:
            gate.location_coordinates = location_coordinates
        if max_capacity is not None:
            gate.max_capacity = max_capacity
        if operating_hours is not None:
            gate.operating_hours = operating_hours
        if notes is not None:
            gate.notes = notes
        
        gate.updated_at = datetime.now()
        if updated_by:
            gate.updated_by = updated_by
        
        await db.commit()
        await db.refresh(gate)
        
        return gate
    
    @staticmethod
    async def get_open_gates(
        db: AsyncSession,
        city_id: Optional[str] = None,
        gate_type: Optional[str] = None
    ) -> List[Gate]:
        """
        Get all open gates
        
        Args:
            db: Database session
            city_id: Optional city filter
            gate_type: Optional gate type filter
            
        Returns:
            List of open Gate objects
        """
        query = select(Gate).options(
            selectinload(Gate.city)
        ).where(Gate.status == GateStatus.OPEN)
        
        if city_id:
            query = query.where(Gate.city_id == city_id)
        
        if gate_type:
            try:
                query = query.where(Gate.gate_type == GateType(gate_type.upper()))
            except ValueError:
                pass
        
        query = query.order_by(Gate.gate_name.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_gates_summary(db: AsyncSession) -> dict:
        """
        Get summary statistics for gates
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with gate statistics
        """
        # Get counts by status
        status_counts = {}
        for status in GateStatus:
            result = await db.execute(
                select(Gate).where(Gate.status == status)
            )
            status_counts[status.value] = len(result.scalars().all())
        
        # Get counts by type
        type_counts = {}
        for gate_type in GateType:
            result = await db.execute(
                select(Gate).where(Gate.gate_type == gate_type)
            )
            type_counts[gate_type.value] = len(result.scalars().all())
        
        return {
            "total_gates": sum(status_counts.values()),
            "by_status": status_counts,
            "by_type": type_counts
        }
    
    @staticmethod
    async def get_gate_statistics(
        db: AsyncSession,
        gate_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Get statistics for a specific gate
        
        Args:
            db: Database session
            gate_id: ID of the gate
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with gate statistics
        """
        # Get gate
        gate = await GatesService.get_gate_by_id(db, gate_id)
        
        if not gate:
            return {}
        
        # Get movement counts would go here
        # This would integrate with MovementLog model
        
        return {
            "gate_id": gate_id,
            "gate_name": gate.gate_name,
            "gate_code": gate.gate_code,
            "current_status": gate.status.value if hasattr(gate.status, 'value') else str(gate.status),
            "statistics": {
                # Movement statistics would be populated here
                "total_movements": 0,
                "entry_count": 0,
                "exit_count": 0
            }
        }
    
    @staticmethod
    async def check_gate_access(
        db: AsyncSession,
        gate_id: str,
        user_id: str
    ) -> dict:
        """
        Check if a user has access to operate a gate
        
        Args:
            db: Database session
            gate_id: ID of the gate
            user_id: ID of the user
            
        Returns:
            Dictionary with access check result
        """
        gate = await GatesService.get_gate_by_id(db, gate_id)
        
        if not gate:
            return {
                "has_access": False,
                "message": "Gate not found"
            }
        
        # Check if gate is operational
        if gate.status == GateStatus.MAINTENANCE:
            return {
                "has_access": False,
                "message": "Gate is under maintenance"
            }
        
        if gate.status == GateStatus.CLOSED:
            return {
                "has_access": False,
                "message": "Gate is currently closed"
            }
        
        # In a real implementation, we would check user permissions
        # against gate-specific access controls
        
        return {
            "has_access": True,
            "message": "Access granted",
            "gate_status": gate.status.value if hasattr(gate.status, 'value') else str(gate.status)
        }
    
    @staticmethod
    async def delete_gate(db: AsyncSession, gate_id: str) -> bool:
        """
        Delete a gate (hard delete)
        
        Args:
            db: Database session
            gate_id: ID of the gate to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(Gate).where(Gate.id == gate_id)
        )
        gate = result.scalar_one_or_none()
        
        if not gate:
            return False
        
        await db.delete(gate)
        await db.commit()
        
        return True
