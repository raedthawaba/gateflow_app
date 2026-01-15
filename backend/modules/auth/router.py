"""
الملف: backend/modules/auth/router.py
الوصف: واجهة برمجة التطبيقات للمصادقة
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import (
    Token, TokenData,
    create_access_token, create_refresh_token,
    verify_password, get_password_hash,
    validate_password_strength,
    decode_token, decode_refresh_token,
    get_current_user, RoleChecker,
    LoginRequest, LoginResponse, RefreshTokenRequest,
    UserInToken
)
from database.session import get_db
from modules.users.repository import UsersRepository
from modules.users.models import User
from modules.audit.service import AuditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    تسجيل الدخول إلى النظام
    
    - **username**: اسم المستخدم
    - **password**: كلمة المرور
    """
    users_repo = UsersRepository(db)
    audit_service = AuditService(db)
    
    # البحث عن المستخدم
    user = await users_repo.get_by_username(request.username)
    
    if user is None:
        await audit_service.log(
            action="login_failed",
            entity="auth",
            description=f"محاولة دخول فاشلة - المستخدم غير موجود: {request.username}",
            ip_address=None  # يمكن الحصول عليها من request
        )
        return LoginResponse(
            success=False,
            message="اسم المستخدم أو كلمة المرور غير صحيحة"
        )
    
    # التحقق من قفل الحساب
    if user.is_locked:
        return LoginResponse(
            success=False,
            message="الحساب مقفل مؤقتاً بسبب محاولات دخول متكررة فاشلة"
        )
    
    # التحقق من كلمة المرور
    if not verify_password(request.password, user.password_hash):
        # زيادة عدد المحاولات الفاشلة
        await users_repo.increment_login_attempts(user.id)
        
        # قفل الحساب إذا تجاوز الحد
        if user.failed_login_attempts + 1 >= settings.MAX_LOGIN_ATTEMPTS:
            lockout_duration = timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            await users_repo.lock_user(user.id, lockout_duration)
            await audit_service.log(
                action="account_locked",
                entity="user",
                entity_id=user.id,
                description=f"قفل الحساب بسبب {settings.MAX_LOGIN_ATTEMPTS} محاولات دخول فاشلة"
            )
            return LoginResponse(
                success=False,
                message=f"الحساب مقفل مؤقتاً لمدة {settings.LOCKOUT_DURATION_MINUTES} دقيقة"
            )
        
        await audit_service.log(
            action="login_failed",
            entity="auth",
            entity_id=user.id,
            description=f"محاولة دخول فاشلة - كلمة مرور خاطئة"
        )
        return LoginResponse(
            success=False,
            message="اسم المستخدم أو كلمة المرور غير صحيحة"
        )
    
    # التحقق من حالة الحساب
    if not user.is_active:
        await audit_service.log(
            action="login_failed",
            entity="auth",
            entity_id=user.id,
            description="محاولة دخول بحساب غير نشط"
        )
        return LoginResponse(
            success=False,
            message="الحساب غير نشط، يرجى التواصل مع المسؤول"
        )
    
    # إعادة تعيين محاولات الدخول
    await users_repo.reset_login_attempts(user.id)
    
    # تحديث آخر دخول
    await users_repo.update_last_login(user.id)
    
    # إنشاء التوكنات
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        gate_id=user.gate_id
    )
    
    refresh_token = create_refresh_token(user.id)
    
    await audit_service.log(
        action="login_success",
        entity="auth",
        entity_id=user.id,
        description="تسجيل دخول ناجح"
    )
    
    logger.info(f"المستخدم {user.username} سجل دخول بنجاح")
    
    return LoginResponse(
        success=True,
        message="تم تسجيل الدخول بنجاح",
        data=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        user=UserInToken(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            gate_id=user.gate_id
        )
    )


@router.post("/login/form", response_model=LoginResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    تسجيل الدخول باستخدام نموذج OAuth2
    """
    return await login(
        LoginRequest(username=form_data.username, password=form_data.password),
        background_tasks,
        db
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    تحديث توكن الوصول باستخدام توكن التحديث
    """
    try:
        # فك تشفير توكن التحديث
        user_id = decode_refresh_token(request.refresh_token)
        
        # الحصول على المستخدم
        users_repo = UsersRepository(db)
        user = await users_repo.get_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="المستخدم غير موجود",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="الحساب غير نشط",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # إنشاء توكنات جديدة
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            gate_id=user.gate_id
        )
        
        refresh_token = create_refresh_token(user.id)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في تحديث التوكن: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="فشل تحديث التوكن",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    تسجيل الخروج من النظام
    """
    audit_service = AuditService(db)
    
    await audit_service.log(
        action="logout",
        entity="auth",
        entity_id=current_user.id,
        description="تسجيل خروج"
    )
    
    return {"success": True, "message": "تم تسجيل الخروج بنجاح"}


@router.get("/me", response_model=UserInToken)
async def get_current_user_info(
    current_user: UserInToken = Depends(get_current_user)
):
    """
    الحصول على معلومات المستخدم الحالي
    """
    return current_user


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: UserInToken = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    تغيير كلمة المرور
    """
    # التحقق من قوة كلمة المرور الجديدة
    is_valid, error_message = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # الحصول على المستخدم من قاعدة البيانات
    users_repo = UsersRepository(db)
    user = await users_repo.get_by_id(current_user.id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # التحقق من كلمة المرور القديمة
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="كلمة المرور الحالية غير صحيحة"
        )
    
    # تشفير كلمة المرور الجديدة وتحديثها
    new_password_hash = get_password_hash(new_password)
    await users_repo.update_password(user.id, new_password_hash)
    
    # إنشاء توكنات جديدة
    access_token = create_access_token(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        gate_id=user.gate_id
    )
    
    refresh_token = create_refresh_token(user.id)
    
    audit_service = AuditService(db)
    await audit_service.log(
        action="password_changed",
        entity="user",
        entity_id=user.id,
        description="تم تغيير كلمة المرور"
    )
    
    return {
        "success": True,
        "message": "تم تغيير كلمة المرور بنجاح",
        "data": Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    }


@router.post("/validate-token")
async def validate_token(
    current_user: UserInToken = Depends(get_current_user)
):
    """
    التحقق من صلاحية التوكن
    """
    return {
        "valid": True,
        "user": current_user
    }
