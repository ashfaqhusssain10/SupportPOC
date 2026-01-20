"""
SQLAlchemy models for the Support-Led Ordering System.
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class StageEnum(str, enum.Enum):
    PRE_ORDER = "PRE_ORDER"
    POST_ORDER = "POST_ORDER"


class ChannelEnum(str, enum.Enum):
    IN_APP_CHAT = "IN_APP_CHAT"
    CALL = "CALL"
    WHATSAPP = "WHATSAPP"


class TriggerEnum(str, enum.Enum):
    USER_INITIATED = "USER_INITIATED"
    SYSTEM_INITIATED = "SYSTEM_INITIATED"


class OutcomeEnum(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    DROPPED = "DROPPED"
    CONVERTED = "CONVERTED"


class OrderImpactEnum(str, enum.Enum):
    PLACED = "PLACED"
    MODIFIED = "MODIFIED"
    LOST = "LOST"
    NONE = "NONE"


class ActorEnum(str, enum.Enum):
    USER = "USER"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class Incidence(Base):
    """
    Core entity representing every support interaction.
    Replaces traditional 'lead' concept.
    """
    __tablename__ = "incidences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    order_id = Column(String(255), nullable=True)
    conversation_id = Column(String(255), unique=True, index=True)
    
    # Classification
    stage = Column(String(20), nullable=False)
    channel = Column(String(20), nullable=False)
    trigger = Column(String(20), nullable=False)
    
    # Context at creation
    app_screen = Column(String(100))
    cart_value = Column(Float, default=0)
    guest_count = Column(Integer)
    event_type = Column(String(50))
    friction_score = Column(Float, default=0)
    
    # Resolution
    outcome = Column(String(20), default="IN_PROGRESS")
    issue_category = Column(String(100))
    root_cause = Column(Text)
    resolution_type = Column(String(100))
    order_impact = Column(String(20))
    
    # Metadata
    agent_id = Column(String(255))
    user_phone = Column(String(20))  # For call callback feature
    call_notes = Column(Text)  # Agent notes after call
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    time_to_resolve_seconds = Column(Integer)
    
    # Relationships
    timeline = relationship("IncidenceTimeline", back_populates="incidence", cascade="all, delete-orphan")


class IncidenceTimeline(Base):
    """Timeline events for an incidence (chat history, actions)."""
    __tablename__ = "incidence_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incidence_id = Column(UUID(as_uuid=True), ForeignKey("incidences.id", ondelete="CASCADE"), index=True)
    
    event_type = Column(String(50), nullable=False)
    actor = Column(String(20), nullable=False)
    content = Column(Text)
    event_metadata = Column(JSON)  # Renamed from 'metadata' - reserved in SQLAlchemy
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    incidence = relationship("Incidence", back_populates="timeline")


class FrictionSignal(Base):
    """Tracked friction signals for users."""
    __tablename__ = "friction_signals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    session_id = Column(String(255), nullable=False)
    
    signal_type = Column(String(50), nullable=False)
    value = Column(Float)
    screen = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsDaily(Base):
    """Pre-computed daily analytics."""
    __tablename__ = "analytics_daily"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, unique=True, nullable=False, index=True)
    
    total_orders = Column(Integer, default=0)
    orders_without_help = Column(Integer, default=0)
    orders_with_help = Column(Integer, default=0)
    
    total_incidences = Column(Integer, default=0)
    avg_time_to_resolve_seconds = Column(Integer, default=0)
    
    top_issue_categories = Column(JSON)
    top_friction_screens = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
