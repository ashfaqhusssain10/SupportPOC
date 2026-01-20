"""
Incidence Service - Core business logic for managing support incidences.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.incidence import Incidence, IncidenceTimeline
from app.schemas.incidence import IncidenceCreate, IncidenceUpdate, TimelineEventCreate


class IncidenceService:
    """
    Manages the lifecycle of support incidences.
    Replaces traditional 'lead' tracking with rich contextual data.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: IncidenceCreate) -> Incidence:
        """
        Create a new incidence.
        
        Args:
            data: Incidence creation data
            
        Returns:
            Created Incidence object with timeline loaded
        """
        incidence = Incidence(
            user_id=data.user_id,
            order_id=data.order_id,
            conversation_id=data.conversation_id,
            stage=data.stage.value,
            channel=data.channel.value,
            trigger=data.trigger.value,
            app_screen=data.app_screen,
            cart_value=data.cart_value,
            guest_count=data.guest_count,
            event_type=data.event_type,
            friction_score=data.friction_score,
            user_phone=data.user_phone,
            outcome="IN_PROGRESS"
        )
        
        self.db.add(incidence)
        await self.db.flush()
        
        # Return with timeline eagerly loaded to avoid greenlet issues
        return await self.get_by_id(incidence.id)
    
    async def get_by_id(self, incidence_id: UUID) -> Optional[Incidence]:
        """Get incidence by ID with timeline."""
        query = (
            select(Incidence)
            .options(selectinload(Incidence.timeline))
            .where(Incidence.id == incidence_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_conversation(self, conversation_id: str) -> Optional[Incidence]:
        """Get incidence by Freshchat conversation ID."""
        query = (
            select(Incidence)
            .options(selectinload(Incidence.timeline))
            .where(Incidence.conversation_id == conversation_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: str, limit: int = 10) -> List[Incidence]:
        """Get user's incidence history."""
        query = (
            select(Incidence)
            .where(Incidence.user_id == user_id)
            .order_by(Incidence.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, incidence_id: UUID, data: IncidenceUpdate) -> Optional[Incidence]:
        """Update incidence fields."""
        update_data = data.model_dump(exclude_unset=True)
        
        if update_data:
            query = (
                update(Incidence)
                .where(Incidence.id == incidence_id)
                .values(**update_data)
            )
            await self.db.execute(query)
            await self.db.flush()
        
        return await self.get_by_id(incidence_id)
    
    async def close(
        self,
        incidence_id: UUID,
        outcome: str,
        order_impact: str,
        issue_category: Optional[str] = None,
        root_cause: Optional[str] = None,
        resolution_type: Optional[str] = None
    ) -> Optional[Incidence]:
        """
        Close an incidence with resolution details.
        Calculates time_to_resolve automatically.
        """
        incidence = await self.get_by_id(incidence_id)
        if not incidence:
            return None
        
        resolved_at = datetime.utcnow()
        time_to_resolve = int((resolved_at - incidence.created_at).total_seconds())
        
        query = (
            update(Incidence)
            .where(Incidence.id == incidence_id)
            .values(
                outcome=outcome,
                order_impact=order_impact,
                issue_category=issue_category,
                root_cause=root_cause,
                resolution_type=resolution_type,
                resolved_at=resolved_at,
                time_to_resolve_seconds=time_to_resolve
            )
        )
        await self.db.execute(query)
        await self.db.flush()
        
        return await self.get_by_id(incidence_id)
    
    async def log_timeline(
        self,
        incidence_id: UUID,
        event: TimelineEventCreate
    ) -> IncidenceTimeline:
        """Add event to incidence timeline."""
        timeline_event = IncidenceTimeline(
            incidence_id=incidence_id,
            event_type=event.event_type,
            actor=event.actor.value,
            content=event.content,
            event_metadata=event.metadata  # Changed from metadata
        )
        
        self.db.add(timeline_event)
        await self.db.flush()
        await self.db.refresh(timeline_event)
        
        return timeline_event
    
    async def get_open_incidences(self, limit: int = 50) -> List[Incidence]:
        """Get all incidences with timeline loaded."""
        query = (
            select(Incidence)
            .options(selectinload(Incidence.timeline))
            .order_by(Incidence.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
