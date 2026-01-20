"""
Pydantic schemas for user context and friction signals.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CartItem(BaseModel):
    """Schema for cart item."""
    item_id: str
    name: str
    quantity: int
    price: float


class ContextUpdate(BaseModel):
    """Schema for updating user context."""
    user_id: str = Field(..., description="User identifier")
    
    # Session info
    current_screen: Optional[str] = Field(None, description="Current app screen")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Cart state
    cart_items: Optional[List[CartItem]] = Field(None, description="Items in cart")
    cart_value: Optional[float] = Field(None, description="Total cart value")
    guest_count: Optional[int] = Field(None, description="Number of guests")
    event_date: Optional[str] = Field(None, description="Event date")
    event_type: Optional[str] = Field(None, description="Event type")
    selected_platter: Optional[str] = Field(None, description="Selected platter name")
    
    # Behavior signals
    inactivity_seconds: Optional[int] = Field(None, description="Seconds of inactivity")
    back_nav_count: Optional[int] = Field(None, description="Back navigation count")
    price_check_count: Optional[int] = Field(None, description="Price check count")
    payment_retry_count: Optional[int] = Field(None, description="Payment retry count")


class FrictionSignalCreate(BaseModel):
    """Schema for logging a friction signal."""
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    signal_type: str = Field(..., description="Type of friction signal")
    value: Optional[float] = Field(None, description="Signal value")
    screen: Optional[str] = Field(None, description="Current screen")


class FrictionDetectRequest(BaseModel):
    """Schema for friction detection request."""
    user_id: str = Field(..., description="User identifier")
    
    # Behavior signals
    inactivity_seconds: int = Field(default=0, description="Seconds of inactivity")
    back_nav_count: int = Field(default=0, description="Back navigation count")
    price_check_count: int = Field(default=0, description="Price check count")
    payment_retry_count: int = Field(default=0, description="Payment retry count")
    
    # Context
    cart_value: float = Field(default=0, description="Cart value")
    is_first_time_user: bool = Field(default=False, description="First time user flag")
    event_type: Optional[str] = Field(None, description="Event type")
    current_screen: Optional[str] = Field(None, description="Current screen")


class FrictionDetectResponse(BaseModel):
    """Schema for friction detection response."""
    friction_score: float = Field(..., description="Calculated friction score (0-100)")
    should_show_help: bool = Field(..., description="Whether to show help prompt")
    help_message: Optional[str] = Field(None, description="Suggested help message")
    breakdown: dict = Field(..., description="Score breakdown by signal")
