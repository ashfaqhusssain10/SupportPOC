"""
Incidences API - CRUD operations for incidences.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.services.incidence_service import IncidenceService
from app.schemas.incidence import (
    IncidenceCreate, IncidenceUpdate, IncidenceResponse,
    TimelineEventCreate, TimelineEventResponse
)

router = APIRouter(prefix="/api/v1/incidences", tags=["Incidences"])


@router.post("/", response_model=IncidenceResponse)
async def create_incidence(
    data: IncidenceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new incidence."""
    try:
        service = IncidenceService(db)
        incidence = await service.create(data)
        
        # Convert to response dict within async context to avoid greenlet issues
        timeline_events = [
            {
                "id": event.id,
                "incidence_id": event.incidence_id,
                "event_type": event.event_type,
                "actor": event.actor,
                "content": event.content,
                "event_metadata": event.event_metadata,
                "created_at": event.created_at
            }
            for event in incidence.timeline
        ]
        
        return {
            "id": incidence.id,
            "user_id": incidence.user_id,
            "order_id": incidence.order_id,
            "conversation_id": incidence.conversation_id,
            "stage": incidence.stage,
            "channel": incidence.channel,
            "trigger": incidence.trigger,
            "app_screen": incidence.app_screen,
            "cart_value": incidence.cart_value,
            "guest_count": incidence.guest_count,
            "event_type": incidence.event_type,
            "friction_score": incidence.friction_score,
            "outcome": incidence.outcome,
            "issue_category": incidence.issue_category,
            "root_cause": incidence.root_cause,
            "resolution_type": incidence.resolution_type,
            "order_impact": incidence.order_impact,
            "agent_id": incidence.agent_id,
            "created_at": incidence.created_at,
            "resolved_at": incidence.resolved_at,
            "time_to_resolve_seconds": incidence.time_to_resolve_seconds,
            "timeline": timeline_events
        }
    except Exception as e:
        import traceback
        print(f"ERROR creating incidence: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incidence_id}", response_model=IncidenceResponse)
async def get_incidence(
    incidence_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get incidence by ID with timeline."""
    service = IncidenceService(db)
    incidence = await service.get_by_id(incidence_id)
    
    if not incidence:
        raise HTTPException(status_code=404, detail="Incidence not found")
    
    return incidence


@router.patch("/{incidence_id}", response_model=IncidenceResponse)
async def update_incidence(
    incidence_id: UUID,
    data: IncidenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update incidence fields."""
    service = IncidenceService(db)
    incidence = await service.update(incidence_id, data)
    
    if not incidence:
        raise HTTPException(status_code=404, detail="Incidence not found")
    
    return incidence


@router.post("/{incidence_id}/close", response_model=IncidenceResponse)
async def close_incidence(
    incidence_id: UUID,
    outcome: str,
    order_impact: str,
    issue_category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Close incidence with resolution details."""
    service = IncidenceService(db)
    incidence = await service.close(
        incidence_id=incidence_id,
        outcome=outcome,
        order_impact=order_impact,
        issue_category=issue_category
    )
    
    if not incidence:
        raise HTTPException(status_code=404, detail="Incidence not found")
    
    return incidence


@router.get("/user/{user_id}", response_model=List[IncidenceResponse])
async def get_user_incidences(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get user's incidence history."""
    service = IncidenceService(db)
    incidences = await service.get_by_user(user_id, limit)
    return incidences


@router.get("/", response_model=List[IncidenceResponse])
async def get_open_incidences(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all open incidences."""
    service = IncidenceService(db)
    incidences = await service.get_open_incidences(limit)
    
    # Convert to dicts within async context to avoid greenlet issues
    result = []
    for inc in incidences:
        timeline_events = [
            {
                "id": event.id,
                "incidence_id": event.incidence_id,
                "event_type": event.event_type,
                "actor": event.actor,
                "content": event.content,
                "event_metadata": event.event_metadata,
                "created_at": event.created_at
            }
            for event in inc.timeline
        ]
        
        result.append({
            "id": inc.id,
            "user_id": inc.user_id,
            "order_id": inc.order_id,
            "conversation_id": inc.conversation_id,
            "stage": inc.stage,
            "channel": inc.channel,
            "trigger": inc.trigger,
            "app_screen": inc.app_screen,
            "cart_value": inc.cart_value,
            "guest_count": inc.guest_count,
            "event_type": inc.event_type,
            "friction_score": inc.friction_score,
            "outcome": inc.outcome,
            "issue_category": inc.issue_category,
            "root_cause": inc.root_cause,
            "resolution_type": inc.resolution_type,
            "order_impact": inc.order_impact,
            "agent_id": inc.agent_id,
            "created_at": inc.created_at,
            "resolved_at": inc.resolved_at,
            "time_to_resolve_seconds": inc.time_to_resolve_seconds,
            "timeline": timeline_events
        })
    
    return result


@router.post("/{incidence_id}/timeline", response_model=TimelineEventResponse)
async def add_timeline_event(
    incidence_id: UUID,
    event: TimelineEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add event to incidence timeline."""
    service = IncidenceService(db)
    
    # Verify incidence exists
    incidence = await service.get_by_id(incidence_id)
    if not incidence:
        raise HTTPException(status_code=404, detail="Incidence not found")
    
    timeline_event = await service.log_timeline(incidence_id, event)
    return timeline_event
