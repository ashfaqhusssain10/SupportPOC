"""
Messages API - Send messages via Freshchat.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.freshchat_service import freshchat_service
from app.services.incidence_service import IncidenceService
from app.schemas.incidence import TimelineEventCreate, ActorEnum

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


class SendMessageRequest(BaseModel):
    """Request body for sending a message."""
    conversation_id: str
    content: str
    incidence_id: Optional[str] = None  # Optional: to log to timeline


@router.post("/send")
async def send_message(
    data: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message from agent to user via Freshchat.
    Also logs the message to the incidence timeline if incidence_id is provided.
    """
    # Send via Freshchat API
    result = await freshchat_service.send_message(
        conversation_id=data.conversation_id,
        message=data.content
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send message to Freshchat: {result.get('error')}"
        )
    
    # Log to timeline if incidence_id provided
    if data.incidence_id:
        try:
            from uuid import UUID
            service = IncidenceService(db)
            
            timeline_event = TimelineEventCreate(
                event_type="MESSAGE",
                actor=ActorEnum.AGENT,
                content=data.content,
                metadata={"sent_via": "freshchat_api"}
            )
            await service.log_timeline(UUID(data.incidence_id), timeline_event)
            print(f"📝 Logged agent message to incidence {data.incidence_id}")
        except Exception as e:
            print(f"⚠️ Failed to log to timeline: {e}")
    
    return {
        "success": True,
        "message": "Message sent successfully",
        "freshchat_response": result.get("data")
    }
