"""
Channel Router Service - Routes users to appropriate support channels.
"""

from typing import Optional, List
from app.config import settings
from app.schemas.channel import ChannelRouteRequest, ChannelRouteResponse


class ChannelRouter:
    """
    Routes users to appropriate support channels based on order value and event type.
    Enforces cost boundaries to optimize support spend.
    
    Rules:
    - < ₹5,000: No human support (self-serve only)
    - ₹5,000 - ₹25,000: Chat only
    - > ₹25,000: Chat + Call
    - High-importance events: Always Chat + Call
    """
    
    # High importance event types that always get premium support
    HIGH_IMPORTANCE_EVENTS = ["WEDDING", "CORPORATE", "RELIGIOUS", "GOVERNMENT"]
    
    def get_allowed_channels(self, request: ChannelRouteRequest) -> ChannelRouteResponse:
        """
        Determine allowed channels for the given context.
        
        Args:
            request: Channel routing request with order value and context
            
        Returns:
            ChannelRouteResponse with allowed channels and routing info
        """
        order_value = request.order_value
        event_type = request.event_type
        
        # Rule 1: High-importance events always get full access
        if event_type and event_type.upper() in self.HIGH_IMPORTANCE_EVENTS:
            return ChannelRouteResponse(
                allowed_channels=["CHAT", "CALL"],
                show_help_button=True,
                priority="HIGH",
                help_trigger_text="Talk to our catering expert",
                route_to_group="premium_support",
                reason=f"High-importance event type: {event_type}"
            )
        
        # Rule 2: Apply order value thresholds
        if order_value < settings.THRESHOLD_LOW:
            # < ₹5,000: No human support
            return ChannelRouteResponse(
                allowed_channels=[],
                show_help_button=False,
                priority="LOW",
                help_trigger_text=None,
                route_to_group=None,
                reason=f"Order value ₹{order_value:,.0f} below ₹{settings.THRESHOLD_LOW:,.0f} threshold"
            )
        
        elif order_value < settings.THRESHOLD_HIGH:
            # ₹5,000 - ₹25,000: Chat only
            return ChannelRouteResponse(
                allowed_channels=["CHAT"],
                show_help_button=True,
                priority="NORMAL",
                help_trigger_text="Chat with us",
                route_to_group="general_support",
                reason=f"Order value ₹{order_value:,.0f} qualifies for chat support"
            )
        
        else:
            # > ₹25,000: Chat + Call
            return ChannelRouteResponse(
                allowed_channels=["CHAT", "CALL"],
                show_help_button=True,
                priority="HIGH",
                help_trigger_text="Talk to our catering expert",
                route_to_group="premium_support",
                reason=f"Order value ₹{order_value:,.0f} qualifies for premium support"
            )
    
    def should_show_help(self, order_value: float, event_type: Optional[str] = None) -> bool:
        """Quick check if help button should be shown."""
        if event_type and event_type.upper() in self.HIGH_IMPORTANCE_EVENTS:
            return True
        return order_value >= settings.THRESHOLD_LOW
    
    def get_priority(self, order_value: float, event_type: Optional[str] = None) -> str:
        """Get support priority level."""
        if event_type and event_type.upper() in self.HIGH_IMPORTANCE_EVENTS:
            return "HIGH"
        if order_value >= settings.THRESHOLD_HIGH:
            return "HIGH"
        if order_value >= settings.THRESHOLD_LOW:
            return "NORMAL"
        return "LOW"
