"""
الملف: backend/main.py
الوصف: نقطة الدخول الرئيسية لتطبيق FastAPI
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.config import settings
from core.database import engine, Base
from core.logging_config import setup_logging
from modules.auth.router import router as auth_router
from modules.users.router import router as users_router
from modules.cities.router import router as cities_router
from modules.gates.router import router as gates_router
from modules.devices.router import router as devices_router
from modules.travelers.router import router as travelers_router
from modules.wanted.router import router as wanted_router
from modules.weapons.router import router as weapons_router
from modules.permits.router import router as permits_router
from modules.movement.router import router as movement_router
from modules.cameras.router import router as cameras_router
from modules.alerts.router import router as alerts_router
from modules.reports.router import router as reports_router
from modules.audit.router import router as audit_router
from modules.sync.router import router as sync_router
from scheduler import start_scheduler, stop_scheduler
from services.websocket_service import ws_manager

# إعداد التسجيل
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    إدارة دورة حياة التطبيق
    """
    # بدء التشغيل
    logger.info("=" * 60)
    logger.info("بدء تشغيل نظام GateFlow...")
    logger.info(f"الوضع: {'تطوير' if settings.DEBUG else 'إنتاج'}")
    logger.info("=" * 60)
    
    try:
        # إنشاء جداول قاعدة البيانات
        logger.info("جاري إنشاء جداول قاعدة البيانات...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
        
        # بدء المجدول
        logger.info("جاري تشغيل المهام المجدولة...")
        await start_scheduler()
        logger.info("تم تشغيل المهام المجدولة")
        
        # بدء WebSocket Manager
        await ws_manager.start()
        logger.info("تم تشغيل خدمة WebSocket")
        
        logger.info("=" * 60)
        logger.info("✅ تم بدء تشغيل النظام بنجاح")
        logger.info("=" * 60)
        
        yield
        
    finally:
        # إيقاف التشغيل
        logger.info("جاري إيقاف النظام...")
        
        # إيقاف المجدول
        await stop_scheduler()
        
        # إيقاف WebSocket Manager
        await ws_manager.stop()
        
        # إغلاق قاعدة البيانات
        await engine.dispose()
        
        logger.info("✅ تم إيقاف النظام بنجاح")


# إنشاء تطبيق FastAPI
app = FastAPI(
    title="نظام GateFlow - API",
    description="""
    نظام متكامل لإدارة حركة المسافرين والسندات الزمنية
    
    ## الميزات الرئيسية:
    - إدارة المدن والنقاط متعددة
    - إصدار السندات الزمنية الرقمية
    - التحقق الآلي من قائمة المطلوبين
    - التكامل مع كاميرات المراقبة
    - نظام التنبيهات الذكي
    - دعم العمل دون اتصال
    
    ## الأدوار:
    - **Admin**: إدارة كاملة للنظام
    - **Supervisor**: مراقبة وتقارير
    - **Entry Officer**: إدخال وإصدار سندات
    - **Exit Officer**: تسجيل خروج
    - **Viewer**: عرض فقط
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# معالج الاستثناءات العام
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    معالج للاستثناءات غير المتوقعة
    """
    logger.error(f"استثناء غير متوقع: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "حدث خطأ داخلي في الخادم",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )


# تضمين Routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["المصادقة"])
app.include_router(users_router, prefix="/api/v1/users", tags=["المستخدمون"])
app.include_router(cities_router, prefix="/api/v1/cities", tags=["المدن"])
app.include_router(gates_router, prefix="/api/v1/gates", tags=["النقاط"])
app.include_router(devices_router, prefix="/api/v1/devices", tags=["الأجهزة"])
app.include_router(travelers_router, prefix="/api/v1/travelers", tags=["المسافرين"])
app.include_router(wanted_router, prefix="/api/v1/wanted", tags=["المطلوبين"])
app.include_router(weapons_router, prefix="/api/v1/weapons", tags=["الأسلحة"])
app.include_router(permits_router, prefix="/api/v1/permits", tags=["السندات"])
app.include_router(movement_router, prefix="/api/v1/movement", tags=["الحركة"])
app.include_router(cameras_router, prefix="/api/v1/cameras", tags=["الكاميرات"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["التنبيهات"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["التقارير"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["التدقيق"])
app.include_router(sync_router, prefix="/api/v1/sync", tags=["المزامنة"])


# نقطة الفحص الصحية
@app.get("/health", tags=["الصحة"])
async def health_check():
    """
    فحص حالة الخادم
    """
    return {
        "status": "healthy",
        "service": "GateFlow API",
        "version": "1.0.0",
        "environment": "development" if settings.DEBUG else "production",
        "timestamp": asyncio.datetime.now().isoformat()
    }


@app.get("/health/detailed", tags=["الصحة"])
async def detailed_health_check():
    """
    فحص تفصيلي لحالة الخادم
    """
    try:
        # فحص قاعدة البيانات
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "scheduler": "running",
            "websocket": "connected"
        },
        "version": "1.0.0"
    }


# نقطة الوصول الرئيسية
@app.get("/", tags=["الرئيسية"])
async def root():
    """
    الصفحة الرئيسية
    """
    return {
        "service": "نظام GateFlow",
        "full_name": "نظام إدارة حركة المسافرين والسندات الزمنية",
        "version": "1.0.0",
        "api_docs": "/api/docs",
        "re_docs": "/api/redoc",
        "github": "https://github.com/raedthawaba/gateflow_app"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level="debug" if settings.DEBUG else "info",
    )
