"""
Channel Router API - Determine allowed support channels.
"""

from fastapi import APIRouter
from app.services.channel_router import ChannelRouter
from app.schemas.channel import ChannelRouteRequest, ChannelRouteResponse

router = APIRouter(prefix="/api/v1/channel", tags=["Channel Router"])

channel_router = ChannelRouter()


@router.post("/route", response_model=ChannelRouteResponse)
async def get_allowed_channels(request: ChannelRouteRequest):
    """
    Get allowed channels for the given order context.
    
    Rules:
    - < ₹5,000: No human support
    - ₹5,000 - ₹25,000: Chat only
    - > ₹25,000: Chat + Call
    - High-importance events: Always Chat + Call
    """
    return channel_router.get_allowed_channels(request)


@router.get("/rules")
async def get_routing_rules():
    """Get current channel routing rules."""
    from app.config import settings
    
    return {
        "thresholds": {
            "low": settings.THRESHOLD_LOW,
            "high": settings.THRESHOLD_HIGH
        },
        "rules": [
            {
                "condition": f"order_value < ₹{settings.THRESHOLD_LOW:,.0f}",
                "channels": [],
                "priority": "LOW",
                "description": "Self-serve only"
            },
            {
                "condition": f"₹{settings.THRESHOLD_LOW:,.0f} <= order_value < ₹{settings.THRESHOLD_HIGH:,.0f}",
                "channels": ["CHAT"],
                "priority": "NORMAL",
                "description": "Chat support"
            },
            {
                "condition": f"order_value >= ₹{settings.THRESHOLD_HIGH:,.0f}",
                "channels": ["CHAT", "CALL"],
                "priority": "HIGH",
                "description": "Premium support"
            },
            {
                "condition": "High-importance event (WEDDING, CORPORATE, RELIGIOUS)",
                "channels": ["CHAT", "CALL"],
                "priority": "HIGH",
                "description": "Premium support regardless of value"
            }
        ],
        "high_importance_events": channel_router.HIGH_IMPORTANCE_EVENTS
    }
