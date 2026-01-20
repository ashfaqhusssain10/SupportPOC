"""
Freshdesk sync router - API endpoints to sync incidence data to Freshdesk tickets.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.incidence import Incidence
from app.services.freshdesk_ticket_service import freshdesk_ticket_service

router = APIRouter(prefix="/api/v1/freshdesk", tags=["Freshdesk"])


class SyncRequest(BaseModel):
    """Request to sync an incidence to Freshdesk."""
    incidence_id: UUID
    ticket_id: Optional[int] = None  # If known, update this ticket; otherwise search by email


class SyncResponse(BaseModel):
    """Response from sync operation."""
    success: bool
    message: str
    ticket_id: Optional[int] = None


@router.post("/sync", response_model=SyncResponse)
async def sync_incidence_to_freshdesk(
    request: SyncRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Sync an incidence's data to a Freshdesk ticket's custom fields.
    
    If ticket_id is provided, updates that ticket directly.
    Otherwise, searches for an open ticket by the user's email.
    If no ticket is found, creates a new one.
    """
    # 1. Fetch the incidence
    result = await db.execute(
        select(Incidence).where(Incidence.id == request.incidence_id)
    )
    incidence = result.scalar_one_or_none()
    
    if not incidence:
        raise HTTPException(status_code=404, detail="Incidence not found")
    
    # 2. Extract data for Freshdesk
    user_email = incidence.user_id  # Assuming user_id is email; adjust if needed
    friction_score = incidence.friction_score or 0
    cart_value = incidence.cart_value or 0
    stage = incidence.stage.value if incidence.stage else "unknown"
    guest_count = incidence.guest_count or 0
    
    # 3. If ticket_id provided, update directly
    if request.ticket_id:
        success = await freshdesk_ticket_service.update_ticket_custom_fields(
            ticket_id=request.ticket_id,
            friction_score=friction_score,
            cart_value=cart_value,
            stage=stage,
            guest_count=guest_count
        )
        if success:
            return SyncResponse(
                success=True,
                message=f"Ticket #{request.ticket_id} updated with incidence data",
                ticket_id=request.ticket_id
            )
        else:
            return SyncResponse(success=False, message="Failed to update ticket")
    
    # 4. Search for existing ticket by email
    existing_ticket = await freshdesk_ticket_service.find_ticket_by_email(user_email)
    
    if existing_ticket:
        ticket_id = existing_ticket.get("id")
        success = await freshdesk_ticket_service.update_ticket_custom_fields(
            ticket_id=ticket_id,
            friction_score=friction_score,
            cart_value=cart_value,
            stage=stage,
            guest_count=guest_count
        )
        if success:
            return SyncResponse(
                success=True,
                message=f"Existing ticket #{ticket_id} updated",
                ticket_id=ticket_id
            )
    
    # 5. No existing ticket found - create one
    new_ticket = await freshdesk_ticket_service.create_ticket(
        email=user_email,
        subject=f"Support Request - {stage}",
        description=f"User has an active support incidence with friction score: {friction_score}",
        friction_score=friction_score,
        cart_value=cart_value,
        stage=stage,
        guest_count=guest_count
    )
    
    if new_ticket:
        return SyncResponse(
            success=True,
            message=f"New ticket #{new_ticket.get('id')} created",
            ticket_id=new_ticket.get("id")
        )
    
    return SyncResponse(success=False, message="Failed to create or update ticket")


@router.post("/sync-all")
async def sync_all_active_incidences(db: AsyncSession = Depends(get_db)):
    """
    Sync ALL active (non-resolved) incidences to Freshdesk.
    Useful for bulk initial sync.
    """
    from app.schemas.incidence import StatusEnum
    
    result = await db.execute(
        select(Incidence).where(Incidence.status != StatusEnum.RESOLVED)
    )
    incidences = result.scalars().all()
    
    synced = 0
    failed = 0
    
    for inc in incidences:
        try:
            # Create sync request for each
            sync_result = await sync_incidence_to_freshdesk(
                SyncRequest(incidence_id=inc.id),
                db=db
            )
            if sync_result.success:
                synced += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Failed to sync incidence {inc.id}: {e}")
            failed += 1
    
    return {
        "total": len(incidences),
        "synced": synced,
        "failed": failed
    }
