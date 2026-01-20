"""
Call Request API - Handle call-back requests from Freshchat widget.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.services.incidence_service import IncidenceService
from app.schemas.incidence import IncidenceCreate, TimelineEventCreate, ActorEnum, StageEnum, ChannelEnum, TriggerEnum

router = APIRouter(prefix="/api/v1/call", tags=["Call"])


class CallRequestPayload(BaseModel):
    """Request body for call-back request."""
    user_id: str
    phone: str
    incidence_id: Optional[str] = None  # Link to existing incidence if available
    cart_value: Optional[float] = 0
    event_type: Optional[str] = None
    friction_score: Optional[float] = 0
    app_screen: Optional[str] = None


class CallRequestResponse(BaseModel):
    """Response for call request."""
    success: bool
    message: str
    incidence_id: str
    phone: str


@router.post("/request", response_model=CallRequestResponse)
async def request_call(
    data: CallRequestPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle a call-back request from the Freshchat widget.
    Creates or updates an incidence with call channel.
    """
    service = IncidenceService(db)
    incidence = None
    
    # If incidence_id provided, update existing incidence
    if data.incidence_id:
        try:
            incidence = await service.get_by_id(UUID(data.incidence_id))
            if incidence:
                # Update to call channel
                incidence.channel = "CALL"
                incidence.user_phone = data.phone
                await service.db.flush()
                
                # Log timeline event
                timeline_event = TimelineEventCreate(
                    event_type="CALL_REQUESTED",
                    actor=ActorEnum.USER,
                    content=f"User requested a call back to {data.phone}",
                    metadata={"phone": data.phone, "source": "freshchat_widget"}
                )
                await service.log_timeline(incidence.id, timeline_event)
                print(f"📞 Call request added to incidence {incidence.id}")
        except Exception as e:
            print(f"⚠️ Error updating incidence: {e}")
            incidence = None
    
    # Create new incidence if none found
    if not incidence:
        incidence_data = IncidenceCreate(
            user_id=data.user_id,
            stage=StageEnum.PRE_ORDER,
            channel=ChannelEnum.CALL,
            trigger=TriggerEnum.USER_INITIATED,
            app_screen=data.app_screen,
            cart_value=data.cart_value or 0,
            event_type=data.event_type,
            friction_score=data.friction_score or 0,
            user_phone=data.phone
        )
        incidence = await service.create(incidence_data)
        
        # Log call request event
        timeline_event = TimelineEventCreate(
            event_type="CALL_REQUESTED",
            actor=ActorEnum.USER,
            content=f"User requested a call back to {data.phone}",
            metadata={"phone": data.phone, "source": "freshchat_widget"}
        )
        await service.log_timeline(incidence.id, timeline_event)
        print(f"📞 Created new call request incidence {incidence.id}")
    
    await service.db.commit()
    
    return CallRequestResponse(
        success=True,
        message="Call request submitted successfully! An agent will call you within 5 minutes.",
        incidence_id=str(incidence.id),
        phone=data.phone
    )


@router.get("/pending")
async def get_pending_calls(
    db: AsyncSession = Depends(get_db),
    limit: int = 20
):
    """Get list of pending call requests for agent dashboard."""
    from sqlalchemy import select, and_
    from app.models.incidence import Incidence
    
    query = (
        select(Incidence)
        .where(
            and_(
                Incidence.channel == "CALL",
                Incidence.outcome == "IN_PROGRESS",
                Incidence.user_phone.isnot(None)
            )
        )
        .order_by(Incidence.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    incidences = result.scalars().all()
    
    return [
        {
            "id": str(inc.id),
            "user_id": inc.user_id,
            "phone": inc.user_phone,
            "cart_value": inc.cart_value,
            "event_type": inc.event_type,
            "created_at": inc.created_at.isoformat(),
            "friction_score": inc.friction_score
        }
        for inc in incidences
    ]
