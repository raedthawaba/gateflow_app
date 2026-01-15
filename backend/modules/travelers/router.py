"""
الملف: backend/modules/travelers/router.py
الوصف: واجهة برمجة تطبيقات إدارة المسافرين
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr

from core.security import get_current_user, require_admin, require_supervisor, RoleChecker
from core.security import UserInToken
from database.session import get_db
from modules.travelers.service import TravelersService
from modules.travelers.repository import TravelersRepository
from modules.wanted.service import WantedService
from modules.audit.service import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# نماذج Pydantic
# ============================================

class TravelerCreateRequest(BaseModel):
    """طلب إنشاء مسافر جديد"""
    full_name: str = Field(..., min_length=3, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    national_id: str = Field(..., min_length=7, max_length=20)
    passport_number: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, min_length=9, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    nationality: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class TravelerUpdateRequest(BaseModel):
    """طلب تحديث بيانات مسافر"""
    full_name: Optional[str] = Field(None, min_length=3, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, min_length=9, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    nationality: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class TravelerResponse(BaseModel):
    """استجابة بيانات مسافر"""
    id: int
    full_name: str
    national_id: str
    passport_number: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    is_flagged: bool
    flag_reason: Optional[str]
    created_at: datetime
    # حقول إضافية
    permits_count: Optional[int] = 0
    last_permit: Optional[datetime] = None


class TravelerWithCheckResponse(BaseModel):
    """استجابة المسافر مع نتيجة التحقق من المطلوبين"""
    traveler: TravelerResponse
    wanted_check: dict
    alert: Optional[dict] = None


class TravelerListResponse(BaseModel):
    """استجابة قائمة المسافرين"""
    success: bool
    data: List[TravelerResponse]
    pagination: dict
    filters: Optional[dict] = None


# ============================================
# نقاط النهاية
# ============================================

@router.get("", response_model=TravelerListResponse)
async def get_travelers(
    page: int = Query(1, ge=1, description="رقم الصفحة"),
    limit: int = Query(20, ge=1, le=100, description="عدد العناصر بالصفحة"),
    search: Optional[str] = Query(None, description="البحث بالاسم أو الرقم الوطني"),
    national_id: Optional[str] = Query(None, description="البحث بالرقم الوطني"),
    is_flagged: Optional[bool] = Query(None, description="تصفية بالمُعلمين فقط"),
    sort_by: str = Query("created_at", description="حقل الترتيب"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على قائمة المسافرين مع إمكانية التصفية والبحث
    """
    service = TravelersService(db)
    
    # حساب الإزاحة
    offset = (page - 1) * limit
    
    # الحصول على المسافرين
    travelers, total = await service.get_travelers(
        search=search,
        national_id=national_id,
        is_flagged=is_flagged,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    
    # تحويل النماذج
    data = [
        TravelerResponse(
            id=t.id,
            full_name=t.full_name,
            national_id=t.national_id,
            passport_number=t.passport_number,
            phone=t.phone,
            address=t.address,
            is_flagged=t.is_flagged,
            flag_reason=t.flag_reason,
            created_at=t.created_at,
            permits_count=len(t.permits) if hasattr(t, 'permits') else 0
        )
        for t in travelers
    ]
    
    return TravelerListResponse(
        success=True,
        data=data,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        },
        filters={
            "search": search,
            "national_id": national_id,
            "is_flagged": is_flagged
        }
    )


@router.get("/{traveler_id}", response_model=TravelerWithCheckResponse)
async def get_traveler(
    traveler_id: int,
    include_permits: bool = Query(False, description="تضمين السندات"),
    include_weapons: bool = Query(False, description="تضمين الأسلحة"),
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    الحصول على بيانات مسافر محدد مع التحقق من المطلوبين
    """
    travelers_service = TravelersService(db)
    wanted_service = WantedService(db)
    audit_service = AuditService(db)
    
    # الحصول على المسافر
    traveler = await travelers_service.get_by_id(traveler_id)
    
    if traveler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المسافر غير موجود"
        )
    
    # التحقق من المطلوبين
    wanted_check = await wanted_service.check_traveler(traveler)
    
    # إنشاء التنبيه إذا وُجد تطابق
    alert = None
    if wanted_check["is_match"]:
        # تسجيل في التدقيق
        await audit_service.log(
            action="wanted_match_detected",
            entity="traveler",
            entity_id=traveler.id,
            description=f"اكتشاف تطابق مع مطلوب: {wanted_check['matched_person']}"
        )
        
        alert = {
            "type": "wanted_match",
            "severity": wanted_check["risk_level"],
            "message": f"تطابق محتمل مع شخص مطلوب ({wanted_check['risk_level']})"
        }
    
    # تحويل الاستجابة
    traveler_response = TravelerResponse(
        id=traveler.id,
        full_name=traveler.full_name,
        national_id=traveler.national_id,
        passport_number=traveler.passport_number,
        phone=traveler.phone,
        address=traveler.address,
        is_flagged=traveler.is_flagged,
        flag_reason=traveler.flag_reason,
        created_at=traveler.created_at,
        permits_count=len(traveler.permits) if hasattr(traveler, 'permits') else 0
    )
    
    return TravelerWithCheckResponse(
        traveler=traveler_response,
        wanted_check=wanted_check,
        alert=alert
    )


@router.post("", response_model=TravelerWithCheckResponse)
async def create_traveler(
    request: TravelerCreateRequest,
    check_wanted: bool = Query(True, description="التحقق من قائمة المطلوبين"),
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    إنشاء مسافر جديد مع التحقق من قائمة المطلوبين
    """
    travelers_service = TravelersService(db)
    wanted_service = WantedService(db)
    audit_service = AuditService(db)
    
    # التحقق من عدم وجود مسافر بنفس الرقم الوطني
    existing = await travelers_service.get_by_national_id(request.national_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يوجد مسافر مسجل بهذا الرقم الوطني"
        )
    
    # إنشاء المسافر
    traveler = await travelers_service.create(request, current_user.id)
    
    # التحقق من المطلوبين
    wanted_check = {"is_match": False}
    alert = None
    
    if check_wanted:
        wanted_check = await wanted_service.check_traveler(traveler)
        
        if wanted_check["is_match"]:
            # وضع علامة على المسافر
            await travelers_service.flag(
                traveler.id,
                reason=f"تطابق مع مطلوب: {wanted_check['matched_person']}",
                user_id=current_user.id
            )
            
            alert = {
                "type": "wanted_match",
                "severity": wanted_check["risk_level"],
                "message": f"تم اكتشاف تطابق مع شخص مطلوب - {wanted_check['matched_person']}"
            }
            
            # تسجيل في التدقيق
            await audit_service.log(
                action="wanted_match_on_create",
                entity="traveler",
                entity_id=traveler.id,
                description=f"اكتشاف تطابق عند إنشاء مسافر: {wanted_check['matched_person']}"
            )
    
    # تسجيل في التدقيق
    await audit_service.log(
        action="create",
        entity="traveler",
        entity_id=traveler.id,
        description=f"إنشاء مسافر جديد: {traveler.full_name}"
    )
    
    logger.info(f"تم إنشاء المسافر {traveler.id} - {traveler.full_name} بواسطة {current_user.username}")
    
    # تحويل الاستجابة
    traveler_response = TravelerResponse(
        id=traveler.id,
        full_name=traveler.full_name,
        national_id=traveler.national_id,
        passport_number=traveler.passport_number,
        phone=traveler.phone,
        address=traveler.address,
        is_flagged=traveler.is_flagged,
        flag_reason=traveler.flag_reason,
        created_at=traveler.created_at
    )
    
    return TravelerWithCheckResponse(
        traveler=traveler_response,
        wanted_check=wanted_check,
        alert=alert
    )


@router.put("/{traveler_id}")
async def update_traveler(
    traveler_id: int,
    request: TravelerUpdateRequest,
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    تحديث بيانات مسافر
    """
    travelers_service = TravelersService(db)
    audit_service = AuditService(db)
    
    # التحقق من وجود المسافر
    traveler = await travelers_service.get_by_id(traveler_id)
    if traveler is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المسافر غير موجود"
        )
    
    # التحقق من الصلاحيات
    if current_user.role in ["entry_officer", "exit_officer", "viewer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ليس لديك صلاحية لتعديل بيانات المسافرين"
        )
    
    # تحديث البيانات
    updated_traveler = await travelers_service.update(traveler_id, request)
    
    # تسجيل في التدقيق
    await audit_service.log(
        action="update",
        entity="traveler",
        entity_id=traveler_id,
        description=f"تحديث بيانات مسافر: {updated_traveler.full_name}"
    )
    
    return {
        "success": True,
        "message": "تم تحديث بيانات المسافر بنجاح",
        "data": {
            "id": updated_traveler.id,
            "full_name": updated_traveler.full_name,
            "national_id": updated_traveler.national_id,
            "updated_at": updated_traveler.updated_at
        }
    }


@router.post("/{traveler_id}/flag")
async def flag_traveler(
    traveler_id: int,
    reason: str = Query(..., min_length=1, description="سبب التفعيل"),
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    تفعيل علامة على مسافر
    """
    travelers_service = TravelersService(db)
    audit_service = AuditService(db)
    
    # تفعيل العلامة
    traveler = await travelers_service.flag(traveler_id, reason, current_user.id)
    
    # تسجيل في التدقيق
    await audit_service.log(
        action="flag",
        entity="traveler",
        entity_id=traveler_id,
        description=f"تفعيل علامة على مسافر: {reason}"
    )
    
    return {
        "success": True,
        "message": "تم تفعيل العلامة بنجاح",
        "data": {
            "id": traveler.id,
            "is_flagged": True,
            "flag_reason": reason
        }
    }


@router.post("/{traveler_id}/unflag")
async def unflag_traveler(
    traveler_id: int,
    reason: Optional[str] = Query(None, description="سبب إلغاء التفعيل"),
    current_user: UserInToken = Depends(require_supervisor),
    db: AsyncSession = Depends(get_db)
):
    """
    إلغاء علامة على مسافر (يتطلب دور مشرف أو أعلى)
    """
    travelers_service = TravelersService(db)
    audit_service = AuditService(db)
    
    # إلغاء العلامة
    traveler = await travelers_service.unflag(traveler_id, current_user.id)
    
    # تسجيل في التدقيق
    await audit_service.log(
        action="unflag",
        entity="traveler",
        entity_id=traveler_id,
        description=f"إلغاء علامة على مسافر: {reason or 'لا يوجد سبب'}"
    )
    
    return {
        "success": True,
        "message": "تم إلغاء العلامة بنجاح",
        "data": {
            "id": traveler.id,
            "is_flagged": False,
            "flag_reason": None
        }
    }


@router.get("/search/quick")
async def quick_search(
    q: str = Query(..., min_length=2, description="نص البحث"),
    limit: int = Query(10, ge=1, le=50, description="عدد النتائج"),
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    بحث سريع عن مسافر
    """
    travelers_service = TravelersService(db)
    
    travelers = await travelers_service.quick_search(q, limit)
    
    return {
        "success": True,
        "data": [
            {
                "id": t.id,
                "full_name": t.full_name,
                "national_id": t.national_id,
                "phone": t.phone,
                "is_flagged": t.is_flagged
            }
            for t in travelers
        ]
    }


@router.get("/check-national-id/{national_id}")
async def check_national_id(
    national_id: str,
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    التحقق من وجود مسافر بالرقم الوطني
    """
    travelers_service = TravelersService(db)
    
    traveler = await travelers_service.get_by_national_id(national_id)
    
    if traveler:
        return {
            "exists": True,
            "traveler_id": traveler.id,
            "full_name": traveler.full_name,
            "is_flagged": traveler.is_flagged
        }
    else:
        return {"exists": False}
