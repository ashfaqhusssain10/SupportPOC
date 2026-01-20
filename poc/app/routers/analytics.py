"""
Analytics API - Dashboard KPIs and reports.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import KPIResponse, WeeklyReportResponse

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(db: AsyncSession = Depends(get_db)):
    """Get current dashboard KPIs."""
    service = AnalyticsService(db)
    return await service.get_kpis()


@router.get("/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(db: AsyncSession = Depends(get_db)):
    """Get weekly analytics report."""
    service = AnalyticsService(db)
    return await service.get_weekly_report()


@router.get("/health")
async def analytics_health():
    """Analytics service health check."""
    return {
        "status": "healthy",
        "service": "analytics",
        "metrics_available": [
            "total_orders_today",
            "self_serve_rate",
            "assisted_count",
            "avg_resolution_time",
            "top_friction_screens",
            "top_issue_categories"
        ]
    }
