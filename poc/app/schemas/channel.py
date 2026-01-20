"""
Pydantic schemas for channel routing.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SupportChannel(str, Enum):
    CHAT = "CHAT"
    CALL = "CALL"


class ChannelRouteRequest(BaseModel):
    """Request schema for channel routing."""
    order_value: float = Field(..., description="Order value in INR")
    event_type: Optional[str] = Field(None, description="Event type (WEDDING, CORPORATE, etc.)")
    user_tier: Optional[str] = Field(None, description="User tier (GOLD, SILVER, BRONZE)")
    friction_score: Optional[float] = Field(None, description="Current friction score")


class ChannelRouteResponse(BaseModel):
    """Response schema for channel routing."""
    allowed_channels: List[str] = Field(..., description="List of allowed channels")
    show_help_button: bool = Field(..., description="Whether to show help button")
    priority: str = Field(..., description="Support priority (HIGH, NORMAL, LOW)")
    help_trigger_text: Optional[str] = Field(None, description="Text to show on help trigger")
    route_to_group: Optional[str] = Field(None, description="Agent group to route to")
    reason: str = Field(..., description="Reason for routing decision")
