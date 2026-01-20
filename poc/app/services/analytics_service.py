"""
Analytics Service - Generates reports and KPIs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date, timedelta
from typing import List, Dict

from app.models.incidence import Incidence, AnalyticsDaily
from app.schemas.analytics import KPIResponse, WeeklyReportResponse


class AnalyticsService:
    """
    Generates analytics, reports, and KPIs for the dashboard.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_kpis(self) -> KPIResponse:
        """Get current KPIs for dashboard."""
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Get today's incidences
        today_query = select(Incidence).where(Incidence.created_at >= today_start)
        result = await self.db.execute(today_query)
        today_incidences = result.scalars().all()
        
        total_today = len(today_incidences)
        
        # Count by outcome
        converted = sum(1 for i in today_incidences if i.outcome == "CONVERTED")
        resolved = sum(1 for i in today_incidences if i.outcome == "RESOLVED")
        dropped = sum(1 for i in today_incidences if i.outcome == "DROPPED")
        open_count = sum(1 for i in today_incidences if i.outcome == "IN_PROGRESS")
        
        # Calculate average resolution time
        resolved_incidences = [i for i in today_incidences if i.time_to_resolve_seconds]
        avg_resolution = 0
        if resolved_incidences:
            avg_resolution = sum(i.time_to_resolve_seconds for i in resolved_incidences) // len(resolved_incidences)
        
        # Get top friction screens
        screen_counts: Dict[str, int] = {}
        for i in today_incidences:
            if i.app_screen:
                screen_counts[i.app_screen] = screen_counts.get(i.app_screen, 0) + 1
        
        top_screens = sorted(screen_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get top issue categories
        category_counts: Dict[str, int] = {}
        for i in today_incidences:
            if i.issue_category:
                category_counts[i.issue_category] = category_counts.get(i.issue_category, 0) + 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate rates (mock self-serve data for POC)
        self_serve_count = max(0, total_today * 3)  # Assume 3x self-serve vs assisted
        total_orders = total_today + self_serve_count
        
        return KPIResponse(
            total_orders_today=total_orders,
            self_serve_count=self_serve_count,
            assisted_count=total_today,
            self_serve_rate=round((self_serve_count / total_orders * 100) if total_orders > 0 else 0, 1),
            total_incidences_today=total_today,
            open_incidences=open_count,
            avg_resolution_time_seconds=avg_resolution,
            assisted_conversion_rate=round((converted / total_today * 100) if total_today > 0 else 0, 1),
            top_friction_screens=[{s[0]: s[1]} for s in top_screens],
            top_issue_categories=[{c[0]: c[1]} for c in top_categories]
        )
    
    async def get_weekly_report(self) -> WeeklyReportResponse:
        """Generate weekly analytics report."""
        today = date.today()
        week_ago = today - timedelta(days=7)
        week_start = datetime.combine(week_ago, datetime.min.time())
        
        # Get week's incidences
        query = select(Incidence).where(Incidence.created_at >= week_start)
        result = await self.db.execute(query)
        incidences = result.scalars().all()
        
        total_incidences = len(incidences)
        
        # Calculate average resolution time
        resolved = [i for i in incidences if i.time_to_resolve_seconds]
        avg_resolution_mins = 0
        if resolved:
            avg_resolution_mins = sum(i.time_to_resolve_seconds for i in resolved) / len(resolved) / 60
        
        # Get top friction reasons
        reason_counts: Dict[str, int] = {}
        for i in incidences:
            if i.issue_category:
                reason_counts[i.issue_category] = reason_counts.get(i.issue_category, 0) + 1
        
        top_reasons = [
            {"category": k, "count": v, "percentage": round(v / total_incidences * 100, 1)}
            for k, v in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(top_reasons, avg_resolution_mins)
        
        # Mock self-serve rate for POC
        self_serve_rate = 72.5
        
        return WeeklyReportResponse(
            period_start=week_ago,
            period_end=today,
            total_orders=total_incidences * 4,  # Mock: assume 4x assisted
            self_serve_rate=self_serve_rate,
            total_incidences=total_incidences,
            avg_resolution_time_minutes=round(avg_resolution_mins, 1),
            top_friction_reasons=top_reasons,
            product_recommendations=recommendations
        )
    
    def _generate_recommendations(self, top_reasons: List[Dict], avg_resolution: float) -> List[str]:
        """Generate product recommendations based on data."""
        recommendations = []
        
        if avg_resolution > 10:
            recommendations.append("Average resolution time >10 min. Consider adding FAQs for common issues.")
        
        for reason in top_reasons[:3]:
            cat = reason.get("category", "").lower()
            if "price" in cat or "cost" in cat:
                recommendations.append("Pricing-related friction detected. Consider clearer price breakdown in UI.")
            elif "menu" in cat or "item" in cat:
                recommendations.append("Menu confusion detected. Consider improving item descriptions.")
            elif "delivery" in cat:
                recommendations.append("Delivery questions common. Add delivery info to checkout page.")
            elif "payment" in cat:
                recommendations.append("Payment issues detected. Review payment flow UX.")
        
        if not recommendations:
            recommendations.append("No critical friction patterns detected this week.")
        
        return recommendations[:5]
