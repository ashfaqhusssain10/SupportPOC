"""
Freshchat Webhook Handler - Receives events from Freshchat.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib

from app.database import get_db
from app.config import settings
from app.services.incidence_service import IncidenceService
from app.schemas.incidence import IncidenceCreate, TimelineEventCreate, StageEnum, ChannelEnum, TriggerEnum, ActorEnum

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


async def verify_signature(request: Request, body: bytes) -> bool:
    """Verify Freshchat webhook signature."""
    signature = request.headers.get("X-Freshchat-Signature")
    if not signature:
        return settings.DEBUG  # Allow in debug mode without signature
    
    expected = hmac.new(
        settings.FRESHCHAT_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


@router.post("/freshchat")
async def handle_freshchat_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle incoming Freshchat webhooks.
    
    Supported events:
    - message_create: Create incidence, log to timeline
    - conversation_assignment: Update agent assignment
    - conversation_resolution: Close incidence
    - conversation_reopen: Reopen incidence
    """
    body = await request.body()
    print(f"📨 WEBHOOK RECEIVED: {len(body)} bytes")
    print(f"📄 RAW BODY: {body.decode('utf-8')}")
    
    # Verify signature (skip in debug mode)
    # if not settings.DEBUG:
    #     if not await verify_signature(request, body):
    #         print("❌ Signature verification failed")
    #         raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    action = payload.get("action", payload.get("event"))
    
    print(f"🔔 ACTION: {action}")
    
    service = IncidenceService(db)
    
    # Route to appropriate handler
    if action == "message_create":
        await handle_message_create(payload, service)
    elif action == "conversation_assignment":
        await handle_assignment(payload, service)
    elif action == "conversation_resolution":
        await handle_resolution(payload, service)
    elif action == "conversation_reopen":
        await handle_reopen(payload, service)
    
    return {"status": "ok", "action": action}


@router.post("/freshdesk")
async def handle_freshdesk_webhook(request: Request):
    """
    Handle incoming Freshdesk webhooks (e.g. Agent Reply).
    Expected Payload:
    {
        "ticket_id": 123,
        "freshchat_conversation_id": "uuid",
        "action": "reply",
        "message": "Hello...",
        "agent_name": "Agent Name"
    }
    """
    try:
        payload = await request.json()
        print(f"📨 FRESHDESK WEBHOOK RECEIVED: {payload}")
        
        conversation_id = payload.get("freshchat_conversation_id")
        message = payload.get("message")
        agent_name = payload.get("agent_name", "Support Agent")
        
        if not conversation_id or not message:
            print("❌ Missing conversation_id or message in payload")
            # Return 200 to satisfy Freshdesk webhook requirement even if invalid payload
            return {"status": "ignored", "reason": "missing_data"}
            
        # Clean up message (remove HTML tags if Freshdesk sends HTML)
        import re
        clean_message = re.sub('<[^<]+?>', '', message).strip()
        
        # Avoid infinite loop: Check if message is essentially identifying itself as a user message copy
        # (Though Freshdesk automation triggers usually distinguish public reply vs private note)
        
        from app.services.freshchat_service import freshchat_service
        
        # Send to Freshchat - try as 'system' first (doesn't require actor_id)
        # Note: 'agent' requires a valid agent actor_id
        response = await freshchat_service.send_message(
            conversation_id=conversation_id,
            message=f"[{agent_name}]: {clean_message}",
            actor_type="system",
            actor_id=None
        )
        
        if response.get("success"):
            print(f"✅ Forwarded Agent Reply to Freshchat Conversation {conversation_id}")
            return {"status": "ok", "forwarded": True}
        else:
            print(f"❌ Failed to forward to Freshchat: {response.get('error')}")
            return {"status": "error", "reason": "freshchat_api_error"}
            
    except Exception as e:
        print(f"⚠️ Error handling Freshdesk webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "reason": str(e)}


async def handle_message_create(payload: dict, service: IncidenceService):
    """Handle new message event - create incidence if not exists, log to timeline."""
    # Debug: Log the full payload structure
    print(f"🔔 Webhook received: {payload.get('action')}")
    
    # Freshchat payload has different structure - conversation and message at root level
    # or within a "data" wrapper depending on webhook version
    data = payload.get("data", payload)  # Fallback to root if no "data" key
    
    # Handle both nested and flat structures
    conversation = data.get("conversation", {}) if isinstance(data.get("conversation"), dict) else {}
    message = data.get("message", {}) if isinstance(data.get("message"), dict) else {}
    actor = data.get("actor", {}) if isinstance(data.get("actor"), dict) else {}
    user = data.get("user", {}) if isinstance(data.get("user"), dict) else {}
    
    # Get conversation_id - try multiple paths (Freshchat sends it in message.conversation_id)
    conversation_id = (
        message.get("conversation_id") or  # This is where Freshchat actually sends it!
        conversation.get("conversation_id") or 
        conversation.get("id") or 
        data.get("conversation_id") or
        payload.get("conversation_id")
    )
    
    print(f"📍 Conversation ID: {conversation_id}")
    
    if not conversation_id:
        print("❌ No conversation_id found in payload")
        print(f"   Available keys in message: {list(message.keys())}")
        return
    
    # Extract message text from message_parts array or direct text
    message_text = ""
    message_parts = message.get("message_parts", [])
    if message_parts:
        for part in message_parts:
            text_part = part.get("text", {})
            if isinstance(text_part, dict):
                message_text += text_part.get("content", "")
            elif isinstance(text_part, str):
                message_text += text_part
    else:
        message_text = message.get("text", "") or message.get("content", "")
    
    print(f"💬 Message text: {message_text[:100]}...")
    
    # Check if incidence exists by conversation_id
    incidence = await service.get_by_conversation(conversation_id)
    
    if not incidence:
        # Get user properties which may contain incidence_id from frontend
        custom_attrs = user.get("properties", {})
        
        # STRATEGY 1: Look for incidence_id passed from frontend (most reliable)
        incidence_id_str = (
            custom_attrs.get("incidence_id") or 
            custom_attrs.get("cf_incidence_id") or
            user.get("incidence_id")
        )
        
        if incidence_id_str:
            print(f"🔗 Found incidence_id from frontend: {incidence_id_str}")
            try:
                from uuid import UUID
                incidence = await service.get_by_id(UUID(incidence_id_str))
                if incidence:
                    # Link the conversation to this incidence
                    incidence.conversation_id = conversation_id
                    await service.db.flush()
                    print(f"✅ Linked incidence {incidence.id} to conversation {conversation_id}")
            except Exception as e:
                print(f"⚠️ Error looking up incidence_id: {e}")
                incidence = None
        
        # STRATEGY 2: Fallback - find most recent incidence without conversation_id
        if not incidence:
            user_id = custom_attrs.get("user_id", user.get("id", actor.get("actor_id", "unknown")))
            print(f"👤 User ID: {user_id} - using fallback strategy")
            
            from sqlalchemy import select, and_
            from app.models.incidence import Incidence
            from datetime import datetime, timedelta
            
            # Look for ANY recent incidence without conversation_id (within 5 minutes)
            recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
            query = (
                select(Incidence)
                .where(
                    and_(
                        Incidence.conversation_id.is_(None),
                        Incidence.created_at >= recent_cutoff
                    )
                )
                .order_by(Incidence.created_at.desc())
                .limit(1)
            )
            result = await service.db.execute(query)
            incidence = result.scalar_one_or_none()
            
            if incidence:
                incidence.conversation_id = conversation_id
                await service.db.flush()
                print(f"✅ Linked most recent incidence {incidence.id} to conversation {conversation_id} (fallback)")
            else:
                # STRATEGY 3: Create new incidence if nothing found
                incidence_data = IncidenceCreate(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    stage=StageEnum.PRE_ORDER if not custom_attrs.get("order_id") else StageEnum.POST_ORDER,
                    channel=ChannelEnum.IN_APP_CHAT,
                    trigger=TriggerEnum.USER_INITIATED,
                    app_screen=custom_attrs.get("cf_current_screen"),
                    cart_value=float(custom_attrs.get("cf_cart_value", "0").replace("₹", "").replace(",", "") or 0),
                    guest_count=int(custom_attrs.get("cf_guest_count")) if custom_attrs.get("cf_guest_count") else None,
                    event_type=custom_attrs.get("cf_event_type"),
                    friction_score=float(custom_attrs.get("cf_friction_score", 0) or 0)
                )
                incidence = await service.create(incidence_data)
                print(f"✅ Created new incidence {incidence.id} for conversation {conversation_id}")
    
    # Log message to timeline
    actor_type = actor.get("actor_type", "user").upper()
    timeline_actor = ActorEnum.USER if actor_type == "USER" else ActorEnum.AGENT
    
    timeline_event = TimelineEventCreate(
        event_type="MESSAGE",
        actor=timeline_actor,
        content=message_text if message_text else "[No message content]",
        metadata={"message_id": message.get("message_id") or message.get("id")}
    )
    await service.log_timeline(incidence.id, timeline_event)
    await service.db.commit()  # Ensure changes are committed
    print(f"📝 Logged message to incidence {incidence.id}: {message_text[:50]}...")
    # ========== AUTO-SYNC TO FRESHDESK ==========
    # Create/update Freshdesk ticket with customer context
    import sys
    print(f"🔄 Starting Freshdesk sync for actor_type: {actor_type}")
    sys.stdout.flush()
    
    try:
        from app.services.freshdesk_ticket_service import freshdesk_ticket_service
        from app.services.freshchat_service import freshchat_service
        
        # Only sync if this is a new conversation (first message from user)
        if actor_type == "USER":
            # Check if we have a ticket_id already stored (to avoid duplicates)
            # For now, we'll try to find an existing ticket or create a new one
            
            # Fetch real user email from Freshchat API
            # The user_id is in the message object, not a separate user dict
            freshchat_user_id = message.get("user_id") or message.get("actor_id") or user.get("actor_id")
            print(f"🔑 Freshchat User ID for API: {freshchat_user_id}")
            user_email = None
            
            # Fetch real user email from Freshchat API
            if freshchat_user_id:
                user_result = await freshchat_service.get_user(freshchat_user_id)
                if user_result.get("success"):
                    user_data = user_result.get("data", {})
                    user_email = user_data.get("email")
                    print(f"📧 Got email from Freshchat API: {user_email}")
            
            # Fallback to constructed email if API fails
            if not user_email:
                user_email = f"{incidence.user_id}@customer.craftmyplate.com"
                print(f"⚠️ Using fallback email: {user_email}")
            
            print(f"📧 User email for Freshdesk: {user_email}")
            sys.stdout.flush()
            
            # Try to find existing ticket
            print(f"🔍 Searching for existing ticket...")
            sys.stdout.flush()
            existing_ticket = await freshdesk_ticket_service.find_ticket_by_email(user_email)
            
            if existing_ticket:
                # Update existing ticket with latest context
                ticket_id = existing_ticket.get("id")
                print(f"📝 Found existing ticket #{ticket_id}, updating...")
                sys.stdout.flush()
                await freshdesk_ticket_service.update_ticket_custom_fields(
                    ticket_id=ticket_id,
                    friction_score=incidence.friction_score or 0,
                    cart_value=incidence.cart_value or 0,
                    stage=incidence.stage.value if hasattr(incidence.stage, "value") else incidence.stage if incidence.stage else "unknown",
                    guest_count=incidence.guest_count or 0,
                    conversation_id=conversation_id
                )
                print(f"✅ Updated Freshdesk ticket #{ticket_id} with incidence data")
                sys.stdout.flush()
            else:
                # Create new ticket
                print(f"➕ No existing ticket found, creating new ticket...")
                sys.stdout.flush()
                new_ticket = await freshdesk_ticket_service.create_ticket(
                    email=user_email,
                    subject=f"Support Request - {incidence.event_type or 'General'} Order",
                    description=f"""
Customer has initiated a support chat.

**Customer Context:**
- Cart Value: ₹{incidence.cart_value or 0:,.0f}
- Guest Count: {incidence.guest_count or 'Not specified'}
- Event Type: {incidence.event_type or 'Not specified'}
- Friction Score: {incidence.friction_score or 0}
- Current Screen: {incidence.app_screen or 'Unknown'}

**First Message:** {message_text[:200] if message_text else 'No message'}

[Auto-created from Freshchat conversation]
                    """.strip(),
                    friction_score=incidence.friction_score or 0,
                    cart_value=incidence.cart_value or 0,
                    stage=incidence.stage.value if hasattr(incidence.stage, "value") else incidence.stage if incidence.stage else "unknown",
                    guest_count=incidence.guest_count or 0,
                    conversation_id=conversation_id,
                    source=7  # <--- FORCE CHAT SOURCE (7)
                )
                if new_ticket:
                    print(f"✅ Created Freshdesk ticket #{new_ticket.get('id')} with SOURCE=7 (Chat)")
                    sys.stdout.flush()
                else:
                    print(f"⚠️ Failed to create Freshdesk ticket for conversation {conversation_id}")
                    sys.stdout.flush()
        else:
            print(f"⏭️ Skipping Freshdesk sync - actor_type is {actor_type} (not USER)")
            sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ Freshdesk sync error (non-blocking): {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()


async def handle_assignment(payload: dict, service: IncidenceService):
    """Handle agent assignment event."""
    data = payload.get("data", {})
    conversation = data.get("conversation", {})
    agent = data.get("agent", {})
    
    conversation_id = conversation.get("id")
    if not conversation_id:
        return
    
    incidence = await service.get_by_conversation(conversation_id)
    if incidence:
        from app.schemas.incidence import IncidenceUpdate
        await service.update(incidence.id, IncidenceUpdate(agent_id=agent.get("id")))
        
        # Log assignment to timeline
        timeline_event = TimelineEventCreate(
            event_type="AGENT_ASSIGNED",
            actor=ActorEnum.SYSTEM,
            content=f"Assigned to agent: {agent.get('name', agent.get('id'))}",
            metadata={"agent_id": agent.get("id"), "agent_name": agent.get("name")}
        )
        await service.log_timeline(incidence.id, timeline_event)


async def handle_resolution(payload: dict, service: IncidenceService):
    """Handle conversation resolved event."""
    data = payload.get("data", {})
    conversation = data.get("conversation", {})
    
    conversation_id = conversation.get("id")
    if not conversation_id:
        return
    
    incidence = await service.get_by_conversation(conversation_id)
    if not incidence:
        return
    
    # Determine outcome from tags
    tags = conversation.get("tags", [])
    tag_names = [t.get("name", "").lower() for t in tags]
    
    if "order_placed" in tag_names:
        outcome = "CONVERTED"
        order_impact = "PLACED"
    elif "dropped" in tag_names or "lost" in tag_names:
        outcome = "DROPPED"
        order_impact = "LOST"
    else:
        outcome = "RESOLVED"
        order_impact = "NONE"
    
    issue_category = tags[0].get("name") if tags else None
    
    await service.close(
        incidence_id=incidence.id,
        outcome=outcome,
        order_impact=order_impact,
        issue_category=issue_category
    )
    
    # Log resolution to timeline
    timeline_event = TimelineEventCreate(
        event_type="RESOLVED",
        actor=ActorEnum.SYSTEM,
        content=f"Conversation resolved with outcome: {outcome}",
        metadata={"outcome": outcome, "order_impact": order_impact}
    )
    await service.log_timeline(incidence.id, timeline_event)


async def handle_reopen(payload: dict, service: IncidenceService):
    """Handle conversation reopened event."""
    data = payload.get("data", {})
    conversation = data.get("conversation", {})
    
    conversation_id = conversation.get("id")
    if not conversation_id:
        return
    
    incidence = await service.get_by_conversation(conversation_id)
    if incidence:
        from app.schemas.incidence import IncidenceUpdate
        await service.update(incidence.id, IncidenceUpdate(outcome="IN_PROGRESS"))
        
        timeline_event = TimelineEventCreate(
            event_type="REOPENED",
            actor=ActorEnum.SYSTEM,
            content="Conversation reopened"
        )
        await service.log_timeline(incidence.id, timeline_event)
