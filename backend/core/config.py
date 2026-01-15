"""
الملف: backend/core/config.py
الوصف: إعدادات النظام المركزية
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from functools import lru_cache


class Settings(BaseSettings):
    """
    إعدادات النظام من متغيرات البيئة
    """
    
    # التطبيق
    APP_NAME: str = "GateFlow"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # قاعدة البيانات
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://gateflow:gateflow@localhost:5432/gateflow_db",
        env="DATABASE_URL"
    )
    SYNC_DATABASE_URL: str = Field(
        default="postgresql://gateflow:gateflow@localhost:5432/gateflow_db",
        env="SYNC_DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = 0
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:5000"],
        env="CORS_ORIGINS"
    )
    
    # Firebase (للتكامل المستقبلي)
    FIREBASE_PROJECT_ID: Optional[str] = Field(default=None, env="FIREBASE_PROJECT_ID")
    FIREBASE_API_KEY: Optional[SecretStr] = Field(default=None, env="FIREBASE_API_KEY")
    
    # SMTP (لإرسال الإشعارات)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[SecretStr] = Field(default=None, env="SMTP_PASSWORD")
    
    #_RATE Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # طلبات في الدقيقة
    RATE_LIMIT_WINDOW: int = 60  # ثانية
    
    # الامان
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # التخزين
    STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # الكاميرات
    CAMERA_SNAPSHOT_RETENTION_DAYS: int = 30
    RTSP_TIMEOUT_SECONDS: int = 5
    
    # السندات
    DEFAULT_PERMIT_DURATION_HOURS: int = 4
    MAX_PERMIT_DURATION_HOURS: int = 72
    PERMIT_CODE_PREFIX: str = "PMT"
    
    # التنبيهات
    EXPIRY_CHECK_INTERVAL_MINUTES: int = 15
    ALERT_EXPIRY_WARNING_MINUTES: int = 60
    
    # المزامنة
    SYNC_BATCH_SIZE: int = 100
    SYNC_MAX_RETRIES: int = 3
    SYNC_RETRY_DELAY_SECONDS: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    الحصول على إعدادات النظام (مع تخزين مؤقت)
    """
    return Settings()


settings = get_settings()
