"""
الملف: backend/database/models.py
الوصف: نماذج قاعدة البيانات الرئيسية لنظام GateFlow
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Enum as SQLEnum, Numeric, JSON, Date,
    Index, UniqueConstraint, BigInteger
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# ============================================
# التعدادات (Enums)
# ============================================

class GateType(str, Enum):
    """نوع النقطة"""
    ENTRY = "entry"
    EXIT = "exit"


class UserRole(str, Enum):
    """أدوار المستخدمين"""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    ENTRY_OFFICER = "entry_officer"
    EXIT_OFFICER = "exit_officer"
    VIEWER = "viewer"


class PermitStatus(str, Enum):
    """حالة السند"""
    ACTIVE = "active"
    EXITED = "exited"
    EXPIRED = "expired"
    FLAGGED = "flagged"


class AlertSeverity(str, Enum):
    """مستوى خطورة التنبيه"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """نوع التنبيه"""
    WANTED_MATCH = "wanted_match"
    PERMIT_EXPIRED = "permit_expired"
    PERMIT_EXPIRING = "permit_expiring"
    CAMERA_OFFLINE = "camera_offline"
    OVERSTAY = "overstay"
    SYSTEM_ERROR = "system_error"
    SECURITY_BREACH = "security_breach"


class MovementAction(str, Enum):
    """نوع الحركة"""
    ENTRY = "entry"
    EXIT = "exit"
    EXPIRED = "expired"
    ALERT = "alert"
    SYNC = "sync"


class RiskLevel(str, Enum):
    """مستوى الخطر للمطلوبين"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DeviceType(str, Enum):
    """نوع الجهاز"""
    SCANNER = "scanner"
    CAMERA = "camera"
    TERMINAL = "terminal"
    PRINTER = "printer"


# ============================================
# النماذج الأساسية (Base Models)
# ============================================

class TimestampMixin:
    """مixin للطوابع الزمنية"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """مixin للحذف الناعم"""
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)


# ============================================
# نماذج الهيكل الإداري
# ============================================

class City(Base, TimestampMixin):
    """نموذج المدينة"""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # العلاقات
    gates = relationship("Gate", back_populates="city", cascade="all, delete-orphan")
    permits = relationship("Permit", back_populates="city")
    
    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}')>"


class Gate(Base, TimestampMixin):
    """نموذج نقطة الدخول/الخروج"""
    __tablename__ = "gates"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True, index=True)
    type = Column(SQLEnum(GateType), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # العلاقات
    city = relationship("City", back_populates="gates")
    devices = relationship("Device", back_populates="gate", cascade="all, delete-orphan")
    users = relationship("User", back_populates="gate")
    cameras = relationship("Camera", back_populates="gate", cascade="all, delete-orphan")
    entry_permits = relationship("Permit", foreign_keys="Permit.entry_gate_id", back_populates="entry_gate")
    exit_permits = relationship("Permit", foreign_keys="Permit.exit_gate_id", back_populates="exit_gate")
    movement_logs = relationship("MovementLog", back_populates="gate")
    
    __table_args__ = (
        Index("idx_gates_city_type", "city_id", "type"),
    )
    
    def __repr__(self):
        return f"<Gate(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class Device(Base, TimestampMixin):
    """نموذج الجهاز"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    gate_id = Column(Integer, ForeignKey("gates.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=True, index=True)
    type = Column(SQLEnum(DeviceType), nullable=False)
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(17), nullable=True)
    serial_number = Column(String(100), nullable=True)
    firmware_version = Column(String(50), nullable=True)
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    gate = relationship("Gate", back_populates="devices")
    
    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', type='{self.type.value}')>"


# ============================================
# نماذج المستخدمين والأدوار
# ============================================

class User(Base, TimestampMixin):
    """نموذج المستخدم"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    gate_id = Column(Integer, ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    preferences = Column(JSON, nullable=True)
    
    # العلاقات
    gate = relationship("Gate", back_populates="users")
    created_permits = relationship("Permit", back_populates="created_by")
    resolved_alerts = relationship("Alert", back_populates="resolved_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    movement_logs = relationship("MovementLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
    
    @property
    def is_locked(self) -> bool:
        """التحقق من قفل الحساب"""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until
    
    @property
    def can_login(self) -> bool:
        """التحقق من إمكانية تسجيل الدخول"""
        return self.is_active and not self.is_locked


class RolePermission(Base, TimestampMixin):
    """نموذج صلاحيات الأدوار"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(SQLEnum(UserRole), unique=True, nullable=False)
    permissions = Column(JSON, nullable=False)  # قائمة الصلاحيات
    
    def __repr__(self):
        return f"<RolePermission(role='{self.role.value}')>"


# ============================================
# نماذج المسافرين والمطلوبين
# ============================================

class Traveler(Base, TimestampMixin):
    """نموذج المسافر"""
    __tablename__ = "travelers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    national_id = Column(String(20), unique=True, nullable=False, index=True)
    passport_number = Column(String(20), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    nationality = Column(String(100), nullable=True)
    photo_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)
    flag_created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    flag_created_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    weapons = relationship("Weapon", back_populates="traveler", cascade="all, delete-orphan")
    permits = relationship("Permit", back_populates="traveler")
    movement_logs = relationship("MovementLog", back_populates="traveler")
    
    def __repr__(self):
        return f"<Traveler(id={self.id}, name='{self.full_name}', national_id='{self.national_id}')>"


class WantedPerson(Base, TimestampMixin):
    """نموذج الشخص المطلوب"""
    __tablename__ = "wanted_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    national_id = Column(String(20), unique=True, nullable=True, index=True)
    passport_number = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    issued_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    issued_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships for fuzzy matching
    name_variants = relationship("WantedNameVariant", back_populates="wanted_person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WantedPerson(id={self.id}, name='{self.full_name}', risk='{self.risk_level.value}')>"


class WantedNameVariant(Base, TimestampMixin):
    """نموذج متغيرات اسم الشخص المطلوب (للمطابقة المرنة)"""
    __tablename__ = "wanted_name_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    wanted_person_id = Column(Integer, ForeignKey("wanted_persons.id", ondelete="CASCADE"), nullable=False)
    name_variant = Column(String(200), nullable=False, index=True)
    similarity_score = Column(Numeric(3, 2), default=1.0)
    
    # العلاقات
    wanted_person = relationship("WantedPerson", back_populates="name_variants")
    
    def __repr__(self):
        return f"<WantedNameVariant(id={self.id}, variant='{self.name_variant}')>"


# ============================================
# نموذج السلاح
# ============================================

class Weapon(Base, TimestampMixin):
    """نموذج السلاح الشخصي"""
    __tablename__ = "weapons"
    
    id = Column(Integer, primary_key=True, index=True)
    traveler_id = Column(Integer, ForeignKey("travelers.id", ondelete="CASCADE"), nullable=False)
    weapon_type = Column(String(50), nullable=False)
    serial_number = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    caliber = Column(String(50), nullable=True)
    license_number = Column(String(100), nullable=True)
    license_issued_by = Column(String(100), nullable=True)
    license_issued_date = Column(Date, nullable=True)
    license_expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    traveler = relationship("Traveler", back_populates="weapons")
    permits = relationship("Permit", back_populates="weapon")
    
    def __repr__(self):
        return f"<Weapon(id={self.id}, type='{self.weapon_type}', serial='{self.serial_number}')>"


# ============================================
# نموذج السند والحركة
# ============================================

class Permit(Base, TimestampMixin):
    """نموذج السند الزمني"""
    __tablename__ = "permits"
    
    id = Column(Integer, primary_key=True, index=True)
    permit_code = Column(String(50), unique=True, nullable=False, index=True)
    qr_code_data = Column(Text, nullable=True)
    traveler_id = Column(Integer, ForeignKey("travelers.id", ondelete="CASCADE"), nullable=False)
    weapon_id = Column(Integer, ForeignKey("weapons.id", ondelete="SET NULL"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True)
    entry_gate_id = Column(Integer, ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    exit_gate_id = Column(Integer, ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    allowed_duration_hours = Column(Integer, nullable=False)
    expiry_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(PermitStatus), default=PermitStatus.ACTIVE, index=True)
    notes = Column(Text, nullable=True)
    purpose = Column(String(200), nullable=True)
    destination = Column(String(200), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_synced = Column(Boolean, default=False)
    sync_attempts = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    traveler = relationship("Traveler", back_populates="permits")
    weapon = relationship("Weapon", back_populates="permits")
    city = relationship("City", back_populates="permits")
    entry_gate = relationship("Gate", foreign_keys=[entry_gate_id], back_populates="entry_permits")
    exit_gate = relationship("Gate", foreign_keys=[exit_gate_id], back_populates="exit_permits")
    created_by_user = relationship("User", back_populates="created_permits")
    movement_logs = relationship("MovementLog", back_populates="permit", cascade="all, delete-orphan")
    camera_events = relationship("CameraEvent", back_populates="permit", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_permits_status_expiry", "status", "expiry_time"),
        Index("idx_permits_traveler_created", "traveler_id", "created_at"),
    )
    
    def __repr__(self):
        return f"<Permit(id={self.id}, code='{self.permit_code}', status='{self.status.value}')>"
    
    @property
    def is_expired(self) -> bool:
        """التحقق من انتهاء صلاحية السند"""
        return datetime.now(timezone.utc) > self.expiry_time
    
    @property
    def remaining_minutes(self) -> int:
        """الحصول على الوقت المتبقي بالدقائق"""
        if self.status != PermitStatus.ACTIVE:
            return 0
        remaining = self.expiry_time - datetime.now(timezone.utc)
        return max(0, int(remaining.total_seconds() / 60))


class MovementLog(Base, TimestampMixin):
    """نموذج سجل الحركة"""
    __tablename__ = "movement_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    permit_id = Column(Integer, ForeignKey("permits.id", ondelete="CASCADE"), nullable=False)
    traveler_id = Column(Integer, ForeignKey("travelers.id", ondelete="CASCADE"), nullable=False)
    action = Column(SQLEnum(MovementAction), nullable=False)
    gate_id = Column(Integer, ForeignKey("gates.id", ondelete="SET NULL"), nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    camera_snapshot_path = Column(String(500), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_synced = Column(Boolean, default=False, index=True)
    sync_attempts = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    permit = relationship("Permit", back_populates="movement_logs")
    traveler = relationship("Traveler", back_populates="movement_logs")
    gate = relationship("Gate", back_populates="movement_logs")
    user = relationship("User", back_populates="movement_logs")
    
    __table_args__ = (
        Index("idx_movement_permit_timestamp", "permit_id", "timestamp"),
        Index("idx_movement_traveler_timestamp", "traveler_id", "timestamp"),
    )
    
    def __repr__(self):
        return f"<MovementLog(id={self.id}, action='{self.action.value}', timestamp='{self.timestamp}')>"


# ============================================
# نماذج الكاميرات والتنبيهات
# ============================================

class Camera(Base, TimestampMixin):
    """نموذج الكاميرا"""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    gate_id = Column(Integer, ForeignKey("gates.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=True, index=True)
    stream_url = Column(String(500), nullable=True)
    stream_type = Column(String(20), default="rtsp")  # rtsp, http, webrtc
    snapshot_url = Column(String(500), nullable=True)
    username = Column(String(100), nullable=True)
    password = Column(String(100), nullable=True)
    location_desc = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    direction = Column(String(50), nullable=True)  # entry, exit, overview
    resolution = Column(String(20), nullable=True)  # 720p, 1080p, 4k
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    gate = relationship("Gate", back_populates="cameras")
    events = relationship("CameraEvent", back_populates="camera", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Camera(id={self.id}, name='{self.name}')>"


class CameraEvent(Base, TimestampMixin):
    """نموذج حدث الكاميرا"""
    __tablename__ = "camera_events"
    
    id = Column(BigInteger, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    permit_id = Column(Integer, ForeignKey("permits.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=True)  # motion, entry, exit, manual
    snapshot_path = Column(String(500), nullable=True)
    video_clip_path = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=True)
    is_synced = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    camera = relationship("Camera", back_populates="events")
    permit = relationship("Permit", back_populates="camera_events")
    
    def __repr__(self):
        return f"<CameraEvent(id={self.id}, camera_id={self.camera_id}, timestamp='{self.timestamp}')>"


class Alert(Base, TimestampMixin):
    """نموذج التنبيه"""
    __tablename__ = "alerts"
    
    id = Column(BigInteger, primary_key=True, index=True)
    type = Column(SQLEnum(AlertType), nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    reference_type = Column(String(50), nullable=True)  # traveler, permit, camera, system
    reference_id = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    triggered_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    notifications_sent = Column(JSON, nullable=True)  # قائمة الإشعارات المرسلة
    metadata = Column(JSON, nullable=True)
    
    # العلاقات
    resolved_by_user = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_alerts")
    
    __table_args__ = (
        Index("idx_alerts_unresolved", "is_resolved", "severity", "created_at"),
        Index("idx_alerts_type_severity", "type", "severity"),
    )
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.type.value}', severity='{self.severity.value}')>"


# ============================================
# نموذج التدقيق
# ============================================

class AuditLog(Base):
    """نموذج سجل التدقيق"""
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity = Column(String(100), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    response_status = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    duration_ms = Column(Integer, nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index("idx_audit_entity_id", "entity", "entity_id"),
        Index("idx_audit_user_timestamp", "user_id", "timestamp"),
        Index("idx_audit_timestamp", "timestamp"),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', entity='{self.entity}')>"


# ============================================
# نموذج المزامنة
# ============================================

class SyncLog(Base, TimestampMixin):
    """نموذج سجل المزامنة"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), nullable=False, index=True)
    sync_type = Column(String(50), nullable=False)  # upload, download, full
    entity_type = Column(String(50), nullable=True)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<SyncLog(id={self.id}, device_id='{self.device_id}', status='{self.status}')>"
