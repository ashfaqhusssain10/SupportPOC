"""
Pydantic schemas for Incidence-related operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class StageEnum(str, Enum):
    PRE_ORDER = "PRE_ORDER"
    POST_ORDER = "POST_ORDER"


class ChannelEnum(str, Enum):
    IN_APP_CHAT = "IN_APP_CHAT"
    CALL = "CALL"
    WHATSAPP = "WHATSAPP"


class TriggerEnum(str, Enum):
    USER_INITIATED = "USER_INITIATED"
    SYSTEM_INITIATED = "SYSTEM_INITIATED"


class OutcomeEnum(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    DROPPED = "DROPPED"
    CONVERTED = "CONVERTED"


class OrderImpactEnum(str, Enum):
    PLACED = "PLACED"
    MODIFIED = "MODIFIED"
    LOST = "LOST"
    NONE = "NONE"


class ActorEnum(str, Enum):
    USER = "USER"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


# Timeline Event Schemas
class TimelineEventCreate(BaseModel):
    """Schema for creating a timeline event."""
    event_type: str = Field(..., description="Type of event (MESSAGE, AGENT_ASSIGNED, etc.)")
    actor: ActorEnum = Field(..., description="Who performed the action")
    content: Optional[str] = Field(None, description="Event content/message")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class TimelineEventResponse(BaseModel):
    """Schema for timeline event response."""
    id: UUID
    incidence_id: UUID
    event_type: str
    actor: str
    content: Optional[str]
    event_metadata: Optional[dict] = None  # Changed from metadata
    created_at: datetime
    
    class Config:
        from_attributes = True


# Incidence Schemas
class IncidenceCreate(BaseModel):
    """Schema for creating a new incidence."""
    user_id: str = Field(..., description="User identifier")
    order_id: Optional[str] = Field(None, description="Order ID if applicable")
    conversation_id: Optional[str] = Field(None, description="Freshchat conversation ID")
    
    stage: StageEnum = Field(..., description="PRE_ORDER or POST_ORDER")
    channel: ChannelEnum = Field(default=ChannelEnum.IN_APP_CHAT, description="Support channel")
    trigger: TriggerEnum = Field(default=TriggerEnum.USER_INITIATED, description="Who initiated")
    
    app_screen: Optional[str] = Field(None, description="Screen user was on")
    cart_value: float = Field(default=0, description="Cart value in INR")
    guest_count: Optional[int] = Field(None, description="Number of guests")
    event_type: Optional[str] = Field(None, description="Event type (WEDDING, CORPORATE, etc.)")
    friction_score: float = Field(default=0, description="Friction score 0-100")
    user_phone: Optional[str] = Field(None, description="User phone for call callback")


class IncidenceUpdate(BaseModel):
    """Schema for updating an incidence."""
    outcome: Optional[OutcomeEnum] = None
    issue_category: Optional[str] = None
    root_cause: Optional[str] = None
    resolution_type: Optional[str] = None
    order_impact: Optional[OrderImpactEnum] = None
    agent_id: Optional[str] = None
    call_notes: Optional[str] = None


class IncidenceResponse(BaseModel):
    """Schema for incidence response."""
    id: UUID
    user_id: str
    order_id: Optional[str]
    conversation_id: Optional[str]
    
    stage: str
    channel: str
    trigger: str
    
    app_screen: Optional[str]
    cart_value: Optional[float] = 0
    guest_count: Optional[int]
    event_type: Optional[str]
    friction_score: Optional[float] = 0
    
    outcome: Optional[str]
    issue_category: Optional[str]
    root_cause: Optional[str]
    resolution_type: Optional[str]
    order_impact: Optional[str]
    
    agent_id: Optional[str] = None
    user_phone: Optional[str] = None
    call_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime]
    time_to_resolve_seconds: Optional[int]
    
    timeline: List[TimelineEventResponse] = []
    
    class Config:
        from_attributes = True
