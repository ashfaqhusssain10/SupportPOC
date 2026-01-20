"""
Pydantic schemas for analytics.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date


class KPIResponse(BaseModel):
    """Response schema for dashboard KPIs."""
    # Order metrics
    total_orders_today: int = Field(default=0, description="Total orders today")
    self_serve_count: int = Field(default=0, description="Orders without support")
    assisted_count: int = Field(default=0, description="Orders with support")
    self_serve_rate: float = Field(default=0, description="Self-serve percentage")
    
    # Incidence metrics
    total_incidences_today: int = Field(default=0, description="New incidences today")
    open_incidences: int = Field(default=0, description="Currently open incidences")
    avg_resolution_time_seconds: int = Field(default=0, description="Average resolution time")
    
    # Conversion
    assisted_conversion_rate: float = Field(default=0, description="Assisted to order rate")
    
    # Trends
    top_friction_screens: List[Dict[str, int]] = Field(default=[], description="Top friction screens")
    top_issue_categories: List[Dict[str, int]] = Field(default=[], description="Top issue categories")


class WeeklyReportResponse(BaseModel):
    """Response schema for weekly analytics report."""
    period_start: date
    period_end: date
    
    # Summary
    total_orders: int
    self_serve_rate: float
    total_incidences: int
    avg_resolution_time_minutes: float
    
    # Top issues
    top_friction_reasons: List[Dict[str, Any]]  # Fixed: 'any' -> 'Any'
    
    # Recommendations
    product_recommendations: List[str]
