"""
الملف: backend/core/security.py
الوصف: وحدة الأمان والمصادقة (JWT, Password Hashing, Permissions)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from core.config import settings
from database.session import get_db
from modules.users.repository import UsersRepository


# إعداد خوارزمية تشفير كلمات المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# إعداد OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login", auto_error=False)


# ============================================
# نماذج Pydantic للأمان
# ============================================

class Token(BaseModel):
    """نموذج التوكن"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class TokenData(BaseModel):
    """بيانات داخل التوكن"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None


class UserInToken(BaseModel):
    """معلومات المستخدم داخل التوكن"""
    id: int
    username: str
    full_name: str
    role: str
    gate_id: Optional[int] = None


class LoginRequest(BaseModel):
    """طلب تسجيل الدخول"""
    username: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    """استجابة تسجيل الدخول"""
    success: bool
    message: str
    data: Optional[Token] = None
    user: Optional[UserInToken] = None


class RefreshTokenRequest(BaseModel):
    """طلب تحديث التوكن"""
    refresh_token: str


# ============================================
# دوال الأمان
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    التحقق من كلمة المرور
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    إنشاء تشفير كلمة المرور
    """
    return pwd_context.hash(password)


def create_access_token(
    user_id: int,
    username: str,
    full_name: str,
    role: str,
    gate_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    إنشاء توكن الوصول
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "full_name": full_name,
        "role": role,
        "gate_id": gate_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    إنشاء توكن التحديث
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    فك تشفير التوكن
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role")
        exp = payload.get("exp")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توكن غير صالح",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(
            user_id=int(user_id),
            username=username,
            role=role,
            exp=datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None
        )
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"فشل التحقق من التوكن: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_refresh_token(token: str) -> int:
    """
    فك تشفير توكن التحديث والحصول على معرف المستخدم
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="نوع التوكن غير صحيح",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توكن غير صالح",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return int(user_id)
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"فشل التحقق من التوكن: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================
# تبعيات FastAPI
# ============================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserInToken:
    """
    الحصول على المستخدم الحالي من التوكن
    """
    token_data = decode_token(token)
    
    users_repo = UsersRepository(db)
    user = await users_repo.get_by_id(token_data.user_id)
    
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
    
    return UserInToken(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        role=user.role.value,
        gate_id=user.gate_id
    )


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserInToken]:
    """
    الحصول على المستخدم الحالي (اختياري)
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


def require_roles(*allowed_roles: str):
    """
    decorator للتحقق من الأدوار المسموحة
    """
    async def role_checker(
        current_user: UserInToken = Depends(get_current_user)
    ) -> UserInToken:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ليس لديك صلاحية للوصول إلى هذا المورد",
            )
        return current_user
    
    return role_checker


# ============================================
# أدوار المستخدمين
# ============================================

class RoleChecker:
    """مُتحقق من الأدوار"""
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: UserInToken = Depends(get_current_user)) -> UserInToken:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ليس لديك صلاحية للوصول إلى هذا المورد",
            )
        return current_user


# تعريف أدوار الوصول
require_admin = RoleChecker([UserRole.ADMIN.value])
require_supervisor = RoleChecker([UserRole.ADMIN.value, UserRole.SUPERVISOR.value])
require_entry_officer = RoleChecker([UserRole.ADMIN.value, UserRole.ENTRY_OFFICER.value])
require_exit_officer = RoleChecker([UserRole.ADMIN.value, UserRole.EXIT_OFFICER.value])
require_viewer = RoleChecker([UserRole.ADMIN.value, UserRole.SUPERVISOR.value, UserRole.VIEWER.value])


# ============================================
# دوال مساعدة
# ============================================

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    التحقق من قوة كلمة المرور
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"كلمة المرور يجب أن تكون على الأقل {settings.PASSWORD_MIN_LENGTH} أحرف"
    
    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل"
    
    if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل"
    
    if settings.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "كلمة المرور يجب أن تحتوي على رقم واحد على الأقل"
    
    if settings.PASSWORD_REQUIRE_SPECIAL and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
        return False, "كلمة المرور يجب أن تحتوي على رمز خاص واحد على الأقل"
    
    return True, ""


def generate_random_password(length: int = 12) -> str:
    """
    توليد كلمة مرور عشوائية آمنة
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return password
