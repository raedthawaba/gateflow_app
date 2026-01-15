"""
Module Service for Alerts Management
Handles business logic for security alerts and notifications
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from database.models import (
    Alert, User, Traveler, Gate, City,
    AlertType, AlertSeverity, AlertStatus
)


class AlertsService:
    """Service class for alert-related business logic"""
    
    @staticmethod
    async def create_alert(
        db: AsyncSession,
        alert_type: str,
        title: str,
        description: str,
        severity: str = "MEDIUM",
        created_by_user_id: Optional[str] = None,
        traveler_id: Optional[str] = None,
        gate_id: Optional[str] = None,
        city_id: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Alert:
        """
        Create a new security alert
        
        Args:
            db: Database session
            alert_type: Type of alert (INTRUSION, SUSPICIOUS_ACTIVITY, SYSTEM, PERMIT, WEAPON, etc.)
            title: Short title of the alert
            description: Detailed description of the alert
            severity: Alert severity level (LOW, MEDIUM, HIGH, CRITICAL)
            created_by_user_id: ID of the user who created the alert
            traveler_id: Optional related traveler ID
            gate_id: Optional related gate ID
            city_id: Optional related city ID
            source: Source of the alert (CAMERA, MANUAL, SYSTEM, GATE, etc.)
            metadata: Additional metadata as JSON
            
        Returns:
            Created Alert object
        """
        # Validate alert type
        try:
            alert_type_enum = AlertType(alert_type.upper())
        except ValueError:
            raise ValueError(f"Invalid alert type: {alert_type}")
        
        # Validate severity
        try:
            severity_enum = AlertSeverity(severity.upper())
        except ValueError:
            raise ValueError(f"Invalid severity level: {severity}")
        
        # Verify creator if provided
        if created_by_user_id:
            user_result = await db.execute(
                select(User).where(User.id == created_by_user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise ValueError(f"User with ID {created_by_user_id} not found")
        
        # Verify traveler if provided
        if traveler_id:
            traveler_result = await db.execute(
                select(Traveler).where(Traveler.id == traveler_id)
            )
            traveler = traveler_result.scalar_one_or_none()
            if not traveler:
                raise ValueError(f"Traveler with ID {traveler_id} not found")
        
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
        
        # Generate alert code
        alert_code = f"ALT-{datetime.now().strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:4].upper()}"
        
        # Create alert
        alert = Alert(
            alert_code=alert_code,
            alert_type=alert_type_enum,
            title=title,
            description=description,
            severity=severity_enum,
            status=AlertStatus.NEW,
            created_by=created_by_user_id,
            traveler_id=traveler_id,
            gate_id=gate_id,
            city_id=city_id,
            source=source,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        return alert
    
    @staticmethod
    async def get_alert_by_id(db: AsyncSession, alert_id: str) -> Optional[Alert]:
        """
        Get an alert by its ID with all relationships
        
        Args:
            db: Database session
            alert_id: ID of the alert
            
        Returns:
            Alert object or None
        """
        result = await db.execute(
            select(Alert)
            .options(
                selectinload(Alert.creator),
                selectinload(Alert.traveler),
                selectinload(Alert.gate),
                selectinload(Alert.city),
                selectinload(Alert.assignee),
                selectinload(Alert.resolved_by_user)
            )
            .where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_alerts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        assigned_to: Optional[str] = None,
        created_by: Optional[str] = None,
        city_id: Optional[str] = None,
        gate_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Alert]:
        """
        Get all alerts with optional filters
        
        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum records to return
            status: Filter by alert status
            severity: Filter by severity level
            alert_type: Filter by alert type
            assigned_to: Filter by assigned user ID
            created_by: Filter by creator user ID
            city_id: Filter by city ID
            gate_id: Filter by gate ID
            start_date: Filter by creation date start
            end_date: Filter by creation date end
            
        Returns:
            List of Alert objects
        """
        query = select(Alert).options(
            selectinload(Alert.creator),
            selectinload(Alert.traveler),
            selectinload(Alert.gate),
            selectinload(Alert.city),
            selectinload(Alert.assignee),
            selectinload(Alert.resolved_by_user)
        )
        
        # Apply filters
        conditions = []
        
        if status:
            try:
                conditions.append(Alert.status == AlertStatus(status.upper()))
            except ValueError:
                pass
        
        if severity:
            try:
                conditions.append(Alert.severity == AlertSeverity(severity.upper()))
            except ValueError:
                pass
        
        if alert_type:
            try:
                conditions.append(Alert.alert_type == AlertType(alert_type.upper()))
            except ValueError:
                pass
        
        if assigned_to:
            conditions.append(Alert.assigned_to == assigned_to)
        
        if created_by:
            conditions.append(Alert.created_by == created_by)
        
        if city_id:
            conditions.append(Alert.city_id == city_id)
        
        if gate_id:
            conditions.append(Alert.gate_id == gate_id)
        
        if start_date:
            conditions.append(Alert.created_at >= start_date)
        
        if end_date:
            conditions.append(Alert.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Add pagination and ordering
        query = query.order_by(
            Alert.severity.desc(),  # Higher severity first
            Alert.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def assign_alert(
        db: AsyncSession,
        alert_id: str,
        assignee_user_id: str,
        assigned_by: str
    ) -> Optional[Alert]:
        """
        Assign an alert to a user
        
        Args:
            db: Database session
            alert_id: ID of the alert
            assignee_user_id: ID of the user to assign
            assigned_by: ID of the user making the assignment
            
        Returns:
            Updated Alert object or None
        """
        # Verify assignee exists
        user_result = await db.execute(
            select(User).where(User.id == assignee_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User with ID {assignee_user_id} not found")
        
        # Get alert
        result = await db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        # Update assignment
        alert.assigned_to = assignee_user_id
        alert.assigned_at = datetime.now()
        alert.assigned_by = assigned_by
        if alert.status == AlertStatus.NEW:
            alert.status = AlertStatus.IN_PROGRESS
        alert.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(alert)
        
        return alert
    
    @staticmethod
    async def update_alert_status(
        db: AsyncSession,
        alert_id: str,
        new_status: str,
        updated_by: str,
        resolution_notes: Optional[str] = None
    ) -> Optional[Alert]:
        """
        Update the status of an alert
        
        Args:
            db: Database session
            alert_id: ID of the alert
            new_status: New status (NEW, IN_PROGRESS, RESOLVED, DISMISSED, ESCALATED)
            updated_by: ID of the user making the update
            resolution_notes: Notes about the resolution
            
        Returns:
            Updated Alert object or None
        """
        try:
            status_enum = AlertStatus(new_status.upper())
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")
        
        # Get alert
        result = await db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        # Update status
        alert.status = status_enum
        alert.updated_at = datetime.now()
        
        # Track resolution
        if status_enum == AlertStatus.RESOLVED:
            alert.resolved_at = datetime.now()
            alert.resolved_by = updated_by
            alert.resolution_notes = resolution_notes
        
        await db.commit()
        await db.refresh(alert)
        
        return alert
    
    @staticmethod
    async def resolve_alert(
        db: AsyncSession,
        alert_id: str,
        resolved_by: str,
        resolution_notes: str,
        resolution_type: Optional[str] = None
    ) -> Optional[Alert]:
        """
        Mark an alert as resolved
        
        Args:
            db: Database session
            alert_id: ID of the alert
            resolved_by: ID of the user resolving the alert
            resolution_notes: Detailed notes about the resolution
            resolution_type: Type of resolution (FALSE_POSITIVE, REAL_THREAT, etc.)
            
        Returns:
            Updated Alert object or None
        """
        # Get alert
        result = await db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        # Update resolution fields
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes
        alert.resolution_type = resolution_type
        alert.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(alert)
        
        return alert
    
    @staticmethod
    async def escalate_alert(
        db: AsyncSession,
        alert_id: str,
        escalated_to: str,
        escalated_by: str,
        reason: str
    ) -> Optional[Alert]:
        """
        Escalate an alert to higher authority
        
        Args:
            db: Database session
            alert_id: ID of the alert
            escalated_to: User ID or role to escalate to
            escalated_by: ID of the user escalating
            reason: Reason for escalation
            
        Returns:
            Updated Alert object or None
        """
        # Get alert
        result = await db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        # Update escalation fields
        alert.status = AlertStatus.ESCALATED
        alert.escalated_to = escalated_to
        alert.escalated_at = datetime.now()
        alert.escalated_by = escalated_by
        alert.escalation_reason = reason
        alert.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(alert)
        
        return alert
    
    @staticmethod
    async def dismiss_alert(
        db: AsyncSession,
        alert_id: str,
        dismissed_by: str,
        reason: str
    ) -> Optional[Alert]:
        """
        Dismiss an alert (mark as false positive)
        
        Args:
            db: Database session
            alert_id: ID of the alert
            dismissed_by: ID of the user dismissing
            reason: Reason for dismissal
            
        Returns:
            Updated Alert object or None
        """
        return await AlertsService.update_alert_status(
            db, alert_id, "DISMISSED", dismissed_by, reason
        )
    
    @staticmethod
    async def get_active_alerts(
        db: AsyncSession,
        severity: Optional[str] = None
    ) -> List[Alert]:
        """
        Get all active (non-resolved, non-dismissed) alerts
        
        Args:
            db: Database session
            severity: Optional severity filter
            
        Returns:
            List of active Alert objects
        """
        query = select(Alert).options(
            selectinload(Alert.creator),
            selectinload(Alert.traveler),
            selectinload(Alert.gate),
            selectinload(Alert.city),
            selectinload(Alert.assignee)
        ).where(
            Alert.status.in_([AlertStatus.NEW, AlertStatus.IN_PROGRESS, AlertStatus.ESCALATED])
        )
        
        if severity:
            try:
                query = query.where(Alert.severity == AlertSeverity(severity.upper()))
            except ValueError:
                pass
        
        query = query.order_by(
            Alert.severity.desc(),
            Alert.created_at.desc()
        )
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_critical_alerts(db: AsyncSession) -> List[Alert]:
        """
        Get all critical and high severity active alerts
        
        Args:
            db: Database session
            
        Returns:
            List of critical Alert objects
        """
        result = await db.execute(
            select(Alert).options(
                selectinload(Alert.creator),
                selectinload(Alert.traveler),
                selectinload(Alert.gate),
                selectinload(Alert.city),
                selectinload(Alert.assignee)
            )
            .where(
                Alert.status.in_([AlertStatus.NEW, AlertStatus.IN_PROGRESS, AlertStatus.ESCALATED])
            )
            .where(
                Alert.severity.in_([AlertSeverity.CRITICAL, AlertSeverity.HIGH])
            )
            .order_by(
                Alert.severity.desc(),
                Alert.created_at.desc()
            )
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_alerts_summary(db: AsyncSession) -> dict:
        """
        Get summary statistics for alerts
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with alert statistics
        """
        # Get counts by status
        status_counts = {}
        for status in AlertStatus:
            result = await db.execute(
                select(Alert).where(Alert.status == status)
            )
            status_counts[status.value] = len(result.scalars().all())
        
        # Get counts by severity
        severity_counts = {}
        for severity in AlertSeverity:
            result = await db.execute(
                select(Alert).where(Alert.severity == severity)
            )
            severity_counts[severity.value] = len(result.scalars().all())
        
        # Get active alerts count
        active_result = await db.execute(
            select(Alert).where(
                Alert.status.in_([AlertStatus.NEW, AlertStatus.IN_PROGRESS, AlertStatus.ESCALATED])
            )
        )
        active_count = len(active_result.scalars().all())
        
        # Get critical alerts count
        critical_result = await db.execute(
            select(Alert).where(
                Alert.status.in_([AlertStatus.NEW, AlertStatus.IN_PROGRESS, AlertStatus.ESCALATED])
            ).where(
                Alert.severity.in_([AlertSeverity.CRITICAL, AlertSeverity.HIGH])
            )
        )
        critical_count = len(critical_result.scalars().all())
        
        return {
            "total_alerts": sum(status_counts.values()),
            "active_alerts": active_count,
            "critical_alerts": critical_count,
            "by_status": status_counts,
            "by_severity": severity_counts
        }
    
    @staticmethod
    async def create_automatic_alert(
        db: AsyncSession,
        alert_type: str,
        title: str,
        description: str,
        severity: str,
        source: str,
        metadata: Optional[dict] = None
    ) -> Alert:
        """
        Create an alert automatically from system events
        
        Args:
            db: Database session
            alert_type: Type of alert
            title: Alert title
            description: Alert description
            severity: Alert severity
            source: Source system
            metadata: Additional metadata
            
        Returns:
            Created Alert object
        """
        return await AlertsService.create_alert(
            db=db,
            alert_type=alert_type,
            title=title,
            description=description,
            severity=severity,
            source=source,
            metadata=metadata
        )
    
    @staticmethod
    async def get_user_assigned_alerts(
        db: AsyncSession,
        user_id: str
    ) -> List[Alert]:
        """
        Get all alerts assigned to a specific user
        
        Args:
            db: Database session
            user_id: ID of the user
            
        Returns:
            List of Alert objects
        """
        result = await db.execute(
            select(Alert).options(
                selectinload(Alert.creator),
                selectinload(Alert.traveler),
                selectinload(Alert.gate),
                selectinload(Alert.city)
            )
            .where(Alert.assigned_to == user_id)
            .where(
                Alert.status.in_([AlertStatus.NEW, AlertStatus.IN_PROGRESS, AlertStatus.ESCALATED])
            )
            .order_by(
                Alert.severity.desc(),
                Alert.created_at.desc()
            )
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_recent_alerts(
        db: AsyncSession,
        hours: int = 24
    ) -> List[Alert]:
        """
        Get alerts created within the specified hours
        
        Args:
            db: Database session
            hours: Number of hours to look back
            
        Returns:
            List of recent Alert objects
        """
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        result = await db.execute(
            select(Alert).options(
                selectinload(Alert.creator),
                selectinload(Alert.traveler),
                selectinload(Alert.gate),
                selectinload(Alert.city)
            )
            .where(Alert.created_at >= time_threshold)
            .order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def delete_alert(db: AsyncSession, alert_id: str) -> bool:
        """
        Delete an alert (hard delete)
        
        Args:
            db: Database session
            alert_id: ID of the alert to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        await db.delete(alert)
        await db.commit()
        
        return True
