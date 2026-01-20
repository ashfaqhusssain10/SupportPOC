# Technical PRD: Support-Led Ordering System
## Customer Support Backend with Freshchat Integration

**Version**: 1.0  
**Date**: January 14, 2026  
**Status**: Draft  
**Author**: Engineering Team

---

## 1. Overview

### 1.1 Problem Statement

Current catering order flow relies heavily on human sales intervention. Users abandon orders due to:
- Trust issues and uncertainty
- Menu/quantity confusion
- High cognitive load with choices

### 1.2 Solution

Build a **Support-Led Ordering System** where:
- App is the primary interface
- Human support is contextual (triggered only when needed)
- Every interaction is logged as an "Incidence" for product improvement

### 1.3 Selected Platform

**Freshchat Growth** — chosen based on:
- Native React Native SDK support
- Budget fit (₹9,600/mo for 6 agents)
- Robust webhooks and REST API
- 2-week implementation timeline

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           MOBILE APP                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  React Native Application                                    │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │   │
│  │  │ Freshchat   │  │ Context      │  │ Friction          │   │   │
│  │  │ SDK         │  │ Tracker      │  │ Detector          │   │   │
│  │  └──────┬──────┘  └──────┬───────┘  └─────────┬─────────┘   │   │
│  │         │                │                    │              │   │
│  └─────────┼────────────────┼────────────────────┼──────────────┘   │
└────────────┼────────────────┼────────────────────┼──────────────────┘
             │                │                    │
             │ Chat           │ API calls          │ Behavior signals
             ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FRESHCHAT CLOUD                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐    │
│  │ Agent Inbox    │  │ User Context   │  │ Conversation       │    │
│  │ (Dashboard)    │  │ (Attributes)   │  │ Storage            │    │
│  └────────────────┘  └────────────────┘  └─────────┬──────────┘    │
│                                                     │ Webhooks     │
└─────────────────────────────────────────────────────┼───────────────┘
                                                      │
                                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVICES                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     API Gateway (FastAPI)                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         │              │              │              │              │
│         ▼              ▼              ▼              ▼              │
│  ┌──────────┐  ┌──────────────┐  ┌─────────┐  ┌─────────────┐      │
│  │ Webhook  │  │ Incidence    │  │ Channel │  │ Analytics   │      │
│  │ Handler  │  │ Service      │  │ Router  │  │ Service     │      │
│  └──────────┘  └──────────────┘  └─────────┘  └─────────────┘      │
│         │              │              │              │              │
│         └──────────────┴──────────────┴──────────────┘              │
│                                 │                                   │
│                                 ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      PostgreSQL + Redis                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| Mobile App | React Native | User-facing app with Freshchat SDK |
| API Gateway | FastAPI (Python) | REST API, webhook handling |
| Database | PostgreSQL | Persistent storage |
| Cache | Redis | Real-time context, session data |
| Queue | Celery + Redis | Async webhook processing |

---

## 3. Data Models

### 3.1 Incidence

The core entity representing every support interaction.

```python
# models/incidence.py

from enum import Enum
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class Stage(str, Enum):
    PRE_ORDER = "PRE_ORDER"
    POST_ORDER = "POST_ORDER"

class Channel(str, Enum):
    IN_APP_CHAT = "IN_APP_CHAT"
    CALL = "CALL"
    WHATSAPP = "WHATSAPP"

class Trigger(str, Enum):
    USER_INITIATED = "USER_INITIATED"
    SYSTEM_INITIATED = "SYSTEM_INITIATED"

class Outcome(str, Enum):
    RESOLVED = "RESOLVED"
    DROPPED = "DROPPED"
    CONVERTED = "CONVERTED"
    IN_PROGRESS = "IN_PROGRESS"

class OrderImpact(str, Enum):
    PLACED = "PLACED"
    MODIFIED = "MODIFIED"
    LOST = "LOST"
    NONE = "NONE"


class Incidence(BaseModel):
    """
    Core entity for tracking support interactions.
    
    Every customer support interaction is logged as an Incidence,
    replacing the traditional "lead" concept.
    
    @docz
    category: Core Models
    """
    id: str                              # UUID
    user_id: str                         # Reference to user
    order_id: Optional[str]              # Reference to order (if exists)
    conversation_id: str                 # Freshchat conversation ID
    
    # Classification
    stage: Stage                         # PRE_ORDER or POST_ORDER
    channel: Channel                     # How user reached support
    trigger: Trigger                     # Who initiated
    
    # Context (captured at creation)
    app_screen: str                      # Screen user was on
    cart_value: float                    # Cart value at time of incidence
    guest_count: Optional[int]           # Number of guests
    event_type: Optional[str]            # WEDDING, CORPORATE, etc.
    friction_score: float                # 0-100 friction score
    
    # Resolution
    outcome: Outcome                     # Final outcome
    issue_category: Optional[str]        # Categorized issue
    root_cause: Optional[str]            # Why user needed help
    resolution_type: Optional[str]       # How it was resolved
    order_impact: OrderImpact            # Impact on order
    
    # Metadata
    agent_id: Optional[str]              # Assigned agent
    created_at: datetime
    resolved_at: Optional[datetime]
    time_to_resolve_seconds: Optional[int]
```

### 3.2 User Context

Real-time user state visible to agents.

```python
# models/user_context.py

class UserContext(BaseModel):
    """
    Real-time user context for support agents.
    
    Stored in Redis for fast access. Updated on every
    screen navigation and cart change.
    
    @docz
    category: Core Models
    """
    user_id: str
    
    # User profile
    name: str
    email: str
    phone: str
    language: str                        # en, hi, ta, etc.
    tier: str                            # GOLD, SILVER, BRONZE
    past_order_count: int
    lifetime_value: float
    
    # Current session
    current_screen: str
    session_start: datetime
    session_duration_seconds: int
    
    # Cart state
    cart_items: List[CartItem]
    cart_value: float
    selected_platter: Optional[str]
    guest_count: Optional[int]
    event_date: Optional[date]
    event_type: Optional[str]
    
    # Behavior signals
    friction_score: float                # 0-100
    back_navigation_count: int
    price_check_count: int
    time_on_checkout_seconds: int
    payment_retry_count: int
    
    # Last updated
    updated_at: datetime
```

### 3.3 Database Schema (SQL)

```sql
-- migrations/001_create_tables.sql

-- Incidences table
CREATE TABLE incidences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    order_id VARCHAR(255),
    conversation_id VARCHAR(255) NOT NULL UNIQUE,
    
    stage VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    trigger VARCHAR(20) NOT NULL,
    
    app_screen VARCHAR(100),
    cart_value DECIMAL(10,2),
    guest_count INTEGER,
    event_type VARCHAR(50),
    friction_score DECIMAL(5,2),
    
    outcome VARCHAR(20) DEFAULT 'IN_PROGRESS',
    issue_category VARCHAR(100),
    root_cause TEXT,
    resolution_type VARCHAR(100),
    order_impact VARCHAR(20),
    
    agent_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    time_to_resolve_seconds INTEGER,
    
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_outcome (outcome)
);

-- Incidence timeline (chat history)
CREATE TABLE incidence_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incidence_id UUID REFERENCES incidences(id),
    
    event_type VARCHAR(50) NOT NULL,     -- MESSAGE, AGENT_ASSIGNED, etc.
    actor VARCHAR(20) NOT NULL,          -- USER, AGENT, SYSTEM
    content TEXT,
    metadata JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_incidence_id (incidence_id)
);

-- Friction signals
CREATE TABLE friction_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    
    signal_type VARCHAR(50) NOT NULL,    -- INACTIVITY, BACK_NAV, etc.
    value DECIMAL(10,2),
    screen VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_session (user_id, session_id)
);

-- Daily analytics (pre-computed)
CREATE TABLE analytics_daily (
    date DATE PRIMARY KEY,
    
    total_orders INTEGER,
    orders_without_help INTEGER,
    orders_with_help INTEGER,
    
    total_incidences INTEGER,
    avg_time_to_resolve_seconds INTEGER,
    
    top_issue_categories JSONB,
    top_friction_screens JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 4. API Specifications

### 4.1 Webhook Handler

Receives events from Freshchat.

```python
# api/webhooks/freshchat.py

"""
Freshchat Webhook Handler

Receives real-time events from Freshchat and processes them
to create/update Incidences in our system.

@docz
category: API Endpoints
path: POST /webhooks/freshchat
authentication: HMAC signature verification
"""

from fastapi import APIRouter, Request, HTTPException
from services.incidence_service import IncidenceService
import hmac
import hashlib

router = APIRouter()
incidence_service = IncidenceService()

FRESHCHAT_WEBHOOK_SECRET = config.FRESHCHAT_WEBHOOK_SECRET


async def verify_signature(request: Request, body: bytes) -> bool:
    """
    Verify Freshchat webhook signature.
    
    Pseudocode:
    1. Get X-Freshchat-Signature header
    2. Compute HMAC-SHA256 of body with secret
    3. Compare signatures
    """
    signature = request.headers.get("X-Freshchat-Signature")
    if not signature:
        return False
    
    expected = hmac.new(
        FRESHCHAT_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


@router.post("/webhooks/freshchat")
async def handle_webhook(request: Request):
    """
    Main webhook endpoint.
    
    Pseudocode:
    1. Verify signature
    2. Parse event type
    3. Route to appropriate handler
    4. Return 200 OK (or Freshchat will retry)
    
    @docz
    method: POST
    request_body: Freshchat webhook payload
    responses:
      200: Event processed successfully
      401: Invalid signature
      500: Processing error
    """
    body = await request.body()
    
    # Step 1: Verify signature
    if not await verify_signature(request, body):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    action = payload.get("action")
    
    # Step 2: Route to handler
    handlers = {
        "message_create": handle_message_create,
        "conversation_assignment": handle_assignment,
        "conversation_resolution": handle_resolution,
        "conversation_reopen": handle_reopen,
    }
    
    handler = handlers.get(action)
    if handler:
        await handler(payload)
    
    return {"status": "ok"}


async def handle_message_create(payload: dict):
    """
    Handle new message event.
    
    Pseudocode:
    1. Extract conversation_id and user info
    2. Check if Incidence exists for this conversation
    3. If not, create new Incidence with context
    4. Log message to timeline
    """
    conversation = payload["data"]["conversation"]
    user = payload["data"]["user"]
    message = payload["data"]["message"]
    
    conversation_id = conversation["id"]
    
    # Check if incidence exists
    incidence = await incidence_service.get_by_conversation(conversation_id)
    
    if not incidence:
        # Create new incidence (first message)
        custom_attrs = user.get("properties", {})
        incidence = await incidence_service.create(
            user_id=custom_attrs.get("user_id"),
            conversation_id=conversation_id,
            stage="PRE_ORDER" if not custom_attrs.get("order_id") else "POST_ORDER",
            channel="IN_APP_CHAT",
            trigger="USER_INITIATED",
            app_screen=custom_attrs.get("current_screen"),
            cart_value=float(custom_attrs.get("cart_value", 0)),
            guest_count=custom_attrs.get("guest_count"),
            event_type=custom_attrs.get("event_type"),
            friction_score=float(custom_attrs.get("friction_score", 0))
        )
    
    # Log message to timeline
    await incidence_service.log_timeline(
        incidence_id=incidence.id,
        event_type="MESSAGE",
        actor=message["actor_type"],  # "user" or "agent"
        content=message.get("text")
    )


async def handle_resolution(payload: dict):
    """
    Handle conversation resolved event.
    
    Pseudocode:
    1. Get incidence by conversation_id
    2. Determine outcome from tags/notes
    3. Calculate time_to_resolve
    4. Update incidence with resolution data
    """
    conversation = payload["data"]["conversation"]
    conversation_id = conversation["id"]
    
    incidence = await incidence_service.get_by_conversation(conversation_id)
    if not incidence:
        return
    
    # Determine outcome from tags
    tags = conversation.get("tags", [])
    tag_names = [t["name"].lower() for t in tags]
    
    if "order_placed" in tag_names:
        outcome = "CONVERTED"
        order_impact = "PLACED"
    elif "dropped" in tag_names or "lost" in tag_names:
        outcome = "DROPPED"
        order_impact = "LOST"
    else:
        outcome = "RESOLVED"
        order_impact = "NONE"
    
    await incidence_service.close(
        incidence_id=incidence.id,
        outcome=outcome,
        order_impact=order_impact,
        issue_category=tags[0]["name"] if tags else None
    )
```

### 4.2 Context API

Endpoints for mobile app to update user context.

```python
# api/context.py

"""
User Context API

Endpoints for mobile app to update real-time user context.
Context is stored in Redis for fast access by agents.

@docz
category: API Endpoints
base_path: /api/v1/context
"""

from fastapi import APIRouter, Depends
from services.context_service import ContextService
from models.user_context import UserContext

router = APIRouter(prefix="/api/v1/context")
context_service = ContextService()


@router.put("/{user_id}/screen")
async def update_screen(
    user_id: str,
    screen_name: str,
    metadata: dict = None
):
    """
    Update user's current screen.
    
    Called by mobile app on every navigation.
    
    Pseudocode:
    1. Get current context from Redis
    2. Update current_screen field
    3. Check friction triggers
    4. Sync to Freshchat (setUserProperties)
    5. Save back to Redis
    
    @docz
    method: PUT
    path_params:
      user_id: User identifier
    query_params:
      screen_name: Current screen name
    """
    await context_service.update_screen(user_id, screen_name, metadata)
    return {"status": "updated"}


@router.put("/{user_id}/cart")
async def update_cart(
    user_id: str,
    cart_data: CartUpdateRequest
):
    """
    Update user's cart state.
    
    Pseudocode:
    1. Update cart fields in context
    2. Recalculate friction score
    3. Check if channel routing rules changed
    4. Sync to Freshchat
    
    @docz
    method: PUT
    """
    await context_service.update_cart(
        user_id=user_id,
        cart_value=cart_data.cart_value,
        items=cart_data.items,
        guest_count=cart_data.guest_count
    )
    return {"status": "updated"}


@router.post("/{user_id}/friction-signal")
async def log_friction_signal(
    user_id: str,
    signal: FrictionSignalRequest
):
    """
    Log a friction signal.
    
    Called when user exhibits friction behavior
    (inactivity, back navigation, etc.)
    
    Pseudocode:
    1. Log signal to database
    2. Recalculate friction score
    3. If score > threshold, trigger help prompt
    4. Update context
    
    @docz
    method: POST
    """
    result = await context_service.log_friction_signal(
        user_id=user_id,
        signal_type=signal.type,
        value=signal.value,
        screen=signal.screen
    )
    
    return {
        "friction_score": result.new_friction_score,
        "should_show_help": result.should_trigger_help
    }
```

### 4.3 Channel Router API

Determines allowed support channels.

```python
# api/channel.py

"""
Channel Router API

Determines which support channels (chat, call) are available
based on order value and event type.

@docz
category: API Endpoints
base_path: /api/v1/channel
"""

from fastapi import APIRouter
from services.channel_service import ChannelService

router = APIRouter(prefix="/api/v1/channel")
channel_service = ChannelService()


@router.post("/route")
async def get_allowed_channels(request: ChannelRouteRequest):
    """
    Get allowed channels for current order context.
    
    Business Rules:
    - < ₹5,000: No human support
    - ₹5,000 - ₹25,000: Chat only
    - > ₹25,000: Chat + Call
    - High-importance events: Always Chat + Call
    
    Pseudocode:
    1. Check if event_type is high-importance
    2. Apply order value rules
    3. Return allowed channels
    
    @docz
    method: POST
    request_body:
      order_value: float
      event_type: string (optional)
    response:
      allowed_channels: string[]
      show_help_button: boolean
      help_trigger_text: string
    """
    result = await channel_service.get_allowed_channels(
        order_value=request.order_value,
        event_type=request.event_type
    )
    
    return result
```

---

## 5. Service Layer

### 5.1 Incidence Service

Core business logic for incidences.

```python
# services/incidence_service.py

"""
Incidence Service

Core service for managing support incidences.
Replaces traditional "lead" tracking with rich
contextual data for product improvement.

@docz
category: Services
"""

from datetime import datetime
from typing import Optional
from models.incidence import Incidence, Outcome, OrderImpact
from repositories.incidence_repository import IncidenceRepository


class IncidenceService:
    """
    Manages the lifecycle of support incidences.
    
    @docz
    methods:
      create: Create new incidence
      close: Close incidence with resolution
      get_by_conversation: Lookup by Freshchat conversation ID
      log_timeline: Add event to incidence timeline
    """
    
    def __init__(self):
        self.repo = IncidenceRepository()
    
    async def create(
        self,
        user_id: str,
        conversation_id: str,
        stage: str,
        channel: str,
        trigger: str,
        app_screen: str,
        cart_value: float,
        guest_count: Optional[int] = None,
        event_type: Optional[str] = None,
        friction_score: float = 0
    ) -> Incidence:
        """
        Create a new incidence.
        
        Pseudocode:
        1. Generate UUID for incidence
        2. Set created_at timestamp
        3. Set outcome to IN_PROGRESS
        4. Save to database
        5. Emit event for analytics
        6. Return created incidence
        
        @docz
        params:
          user_id: User who initiated support
          conversation_id: Freshchat conversation ID
          stage: PRE_ORDER or POST_ORDER
          channel: IN_APP_CHAT, CALL, or WHATSAPP
          trigger: USER_INITIATED or SYSTEM_INITIATED
          app_screen: Screen user was on when help requested
          cart_value: Cart value at time of incidence
          guest_count: Number of guests (if applicable)
          event_type: Event category (WEDDING, CORPORATE, etc.)
          friction_score: Calculated friction score (0-100)
        returns: Created Incidence object
        """
        incidence = Incidence(
            id=generate_uuid(),
            user_id=user_id,
            conversation_id=conversation_id,
            stage=stage,
            channel=channel,
            trigger=trigger,
            app_screen=app_screen,
            cart_value=cart_value,
            guest_count=guest_count,
            event_type=event_type,
            friction_score=friction_score,
            outcome=Outcome.IN_PROGRESS,
            created_at=datetime.now()
        )
        
        await self.repo.save(incidence)
        await emit_event("incidence.created", incidence)
        
        return incidence
    
    async def close(
        self,
        incidence_id: str,
        outcome: Outcome,
        order_impact: OrderImpact,
        issue_category: Optional[str] = None,
        root_cause: Optional[str] = None,
        resolution_type: Optional[str] = None
    ) -> Incidence:
        """
        Close an incidence with resolution details.
        
        Pseudocode:
        1. Get incidence by ID
        2. Set resolved_at timestamp
        3. Calculate time_to_resolve
        4. Update outcome and resolution fields
        5. Save to database
        6. Emit event for analytics
        7. Trigger weekly report update (async)
        
        @docz
        params:
          incidence_id: ID of incidence to close
          outcome: RESOLVED, DROPPED, or CONVERTED
          order_impact: PLACED, MODIFIED, LOST, or NONE
          issue_category: Category of the issue
          root_cause: Why user needed help
          resolution_type: How it was resolved
        """
        incidence = await self.repo.get(incidence_id)
        
        incidence.resolved_at = datetime.now()
        incidence.time_to_resolve_seconds = (
            incidence.resolved_at - incidence.created_at
        ).seconds
        
        incidence.outcome = outcome
        incidence.order_impact = order_impact
        incidence.issue_category = issue_category
        incidence.root_cause = root_cause
        incidence.resolution_type = resolution_type
        
        await self.repo.update(incidence)
        await emit_event("incidence.closed", incidence)
        
        # Async: Update weekly report
        await trigger_task("update_weekly_report")
        
        return incidence
    
    async def log_timeline(
        self,
        incidence_id: str,
        event_type: str,
        actor: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """
        Add event to incidence timeline.
        
        Pseudocode:
        1. Create timeline event
        2. Save to incidence_timeline table
        3. Update incidence.last_activity timestamp
        
        @docz
        params:
          incidence_id: ID of incidence
          event_type: MESSAGE, AGENT_ASSIGNED, ESCALATED, etc.
          actor: USER, AGENT, or SYSTEM
          content: Message content (for MESSAGE events)
          metadata: Additional data
        """
        await self.repo.add_timeline_event(
            incidence_id=incidence_id,
            event_type=event_type,
            actor=actor,
            content=content,
            metadata=metadata
        )
```

### 5.2 Friction Detection Service

```python
# services/friction_service.py

"""
Friction Detection Service

Monitors user behavior and calculates friction score.
Triggers help prompts when friction exceeds threshold.

@docz
category: Services
"""

from typing import Tuple


class FrictionService:
    """
    Detects user friction and triggers support.
    
    Friction is calculated based on:
    - Inactivity time
    - Back navigation patterns
    - Price checking behavior
    - Payment failures
    - User profile (first-time vs returning)
    
    @docz
    threshold: 60 (0-100 scale)
    """
    
    # Friction weights
    WEIGHTS = {
        "inactivity_checkout": 30,      # >60s on checkout
        "back_navigation": 25,          # >3 back navs
        "price_checks": 20,             # >5 price calculations
        "high_value_event": 15,         # Wedding, corporate, etc.
        "first_time_user": 10,          # No past orders
        "payment_failure": 40,          # Payment failed
    }
    
    THRESHOLD = 60
    
    async def calculate_friction_score(
        self,
        user_context: UserContext
    ) -> Tuple[float, bool]:
        """
        Calculate friction score from user context.
        
        Pseudocode:
        1. Start with score = 0
        2. Add weight for each friction signal present
        3. Cap at 100
        4. Compare with threshold
        5. Return (score, should_trigger_help)
        
        @docz
        params:
          user_context: Current user context
        returns:
          Tuple of (friction_score, should_show_help)
        """
        score = 0
        
        # Inactivity on checkout
        if (user_context.current_screen == "CHECKOUT" and 
            user_context.time_on_checkout_seconds > 60):
            score += self.WEIGHTS["inactivity_checkout"]
        
        # Back navigation loops
        if user_context.back_navigation_count > 3:
            score += self.WEIGHTS["back_navigation"]
        
        # Excessive price checking
        if user_context.price_check_count > 5:
            score += self.WEIGHTS["price_checks"]
        
        # High-importance event
        if user_context.event_type in ["WEDDING", "CORPORATE", "RELIGIOUS"]:
            score += self.WEIGHTS["high_value_event"]
        
        # First-time user
        if user_context.past_order_count == 0:
            score += self.WEIGHTS["first_time_user"]
        
        # Payment failure
        if user_context.payment_retry_count > 0:
            score += self.WEIGHTS["payment_failure"]
        
        score = min(score, 100)
        should_trigger = score >= self.THRESHOLD
        
        return score, should_trigger
    
    async def get_help_trigger_message(
        self,
        user_context: UserContext,
        friction_score: float
    ) -> str:
        """
        Get appropriate help prompt message.
        
        Pseudocode:
        1. Identify highest friction signal
        2. Return contextual message
        
        @docz
        returns: Localized help prompt message
        """
        screen = user_context.current_screen
        
        messages = {
            "GUEST_COUNT": "Need help deciding portions?",
            "MENU_BROWSE": "Want a personalized recommendation?",
            "CHECKOUT": "Need help completing your order?",
            "PAYMENT": "Having trouble with payment?",
        }
        
        return messages.get(screen, "Need help?")
```

### 5.3 Channel Router Service

```python
# services/channel_service.py

"""
Channel Router Service

Determines allowed support channels based on
order value and event type.

@docz
category: Services
"""


class ChannelService:
    """
    Routes users to appropriate support channels.
    
    Business Rules:
    - < ₹5,000: Self-serve only (no human support)
    - ₹5,000 - ₹25,000: Chat only
    - > ₹25,000: Chat + Call
    - High-importance events: Always full access
    
    @docz
    config:
      low_threshold: 5000
      high_threshold: 25000
      high_importance_events: [WEDDING, CORPORATE, RELIGIOUS]
    """
    
    LOW_THRESHOLD = 5000
    HIGH_THRESHOLD = 25000
    HIGH_IMPORTANCE_EVENTS = ["WEDDING", "CORPORATE", "RELIGIOUS"]
    
    async def get_allowed_channels(
        self,
        order_value: float,
        event_type: Optional[str] = None
    ) -> ChannelRouteResult:
        """
        Get allowed channels for order context.
        
        Pseudocode:
        1. Check if high-importance event -> full access
        2. Check order value against thresholds
        3. Return allowed channels list
        
        @docz
        params:
          order_value: Current cart/order value
          event_type: Event category (optional)
        returns:
          ChannelRouteResult with:
            - allowed_channels: list
            - show_help_button: bool
            - priority: str
        """
        # High-importance events always get full access
        if event_type in self.HIGH_IMPORTANCE_EVENTS:
            return ChannelRouteResult(
                allowed_channels=["CHAT", "CALL"],
                show_help_button=True,
                priority="HIGH"
            )
        
        # Apply order value rules
        if order_value < self.LOW_THRESHOLD:
            return ChannelRouteResult(
                allowed_channels=[],
                show_help_button=False,
                show_faq=True,
                priority="NONE"
            )
        
        if order_value < self.HIGH_THRESHOLD:
            return ChannelRouteResult(
                allowed_channels=["CHAT"],
                show_help_button=True,
                priority="NORMAL"
            )
        
        return ChannelRouteResult(
            allowed_channels=["CHAT", "CALL"],
            show_help_button=True,
            priority="HIGH"
        )
```

---

## 6. Mobile Integration

### 6.1 Freshchat SDK Setup

```typescript
// mobile/services/FreshchatService.ts

/**
 * Freshchat SDK Integration Service
 * 
 * Handles:
 * - SDK initialization
 * - User identification
 * - Context synchronization
 * - Chat widget control
 * 
 * @docz
 * category: Mobile Services
 */

import Freshchat from 'react-native-freshchat-sdk';
import { ContextService } from './ContextService';

export class FreshchatService {
  
  /**
   * Initialize Freshchat SDK
   * 
   * Pseudocode:
   * 1. Call Freshchat.init with credentials
   * 2. Set up event listeners
   * 3. Configure push notifications
   * 
   * @docz
   * called_from: App startup
   */
  static async initialize(): Promise<void> {
    await Freshchat.init({
      appId: Config.FRESHCHAT_APP_ID,
      appKey: Config.FRESHCHAT_APP_KEY,
      domain: Config.FRESHCHAT_DOMAIN,
    });
    
    // Set up restore ID listener
    Freshchat.setRestoreIdListener((restoreId) => {
      // Save for user restoration
      AsyncStorage.setItem('freshchat_restore_id', restoreId);
    });
  }
  
  /**
   * Set user identity and properties
   * 
   * Pseudocode:
   * 1. Set basic user info (name, email, phone)
   * 2. Set custom properties for agent context
   * 3. Restore previous conversations if returning user
   * 
   * @docz
   * called_from: After user login
   */
  static async identifyUser(user: User): Promise<void> {
    // Basic identity
    await Freshchat.setUser({
      firstName: user.firstName,
      lastName: user.lastName,
      email: user.email,
      phone: user.phone,
      phoneCountryCode: '+91',
    });
    
    // Custom properties (visible to agents)
    await Freshchat.setUserProperties({
      user_id: user.id,
      user_tier: user.tier,
      past_order_count: String(user.orderCount),
      lifetime_value: String(user.lifetimeValue),
      language: user.preferredLanguage,
    });
    
    // Restore if returning user
    const restoreId = await AsyncStorage.getItem('freshchat_restore_id');
    if (restoreId) {
      await Freshchat.restoreUser(user.email, restoreId);
    }
  }
  
  /**
   * Update real-time context for agents
   * 
   * Pseudocode:
   * 1. Get current context from ContextService
   * 2. Send to Freshchat via setUserProperties
   * 3. Also sync to backend API
   * 
   * @docz
   * called_from: Screen navigation, cart updates
   */
  static async syncContext(context: PartialContext): Promise<void> {
    await Freshchat.setUserProperties({
      current_screen: context.screen,
      cart_value: String(context.cartValue || 0),
      guest_count: String(context.guestCount || ''),
      event_type: context.eventType || '',
      event_date: context.eventDate || '',
      selected_platter: context.selectedPlatter || '',
      friction_score: String(context.frictionScore || 0),
    });
    
    // Also sync to our backend
    await ContextService.updateContext(context);
  }
  
  /**
   * Show chat based on channel rules
   * 
   * Pseudocode:
   * 1. Call backend for allowed channels
   * 2. If chat allowed, show messenger
   * 3. If not allowed, show FAQ/self-serve
   * 
   * @docz
   * called_from: Help button tap
   */
  static async showSupportIfAllowed(
    orderValue: number,
    eventType?: string
  ): Promise<boolean> {
    // Get routing decision from backend
    const result = await ChannelAPI.getRoute(orderValue, eventType);
    
    if (result.allowed_channels.includes('CHAT')) {
      await Freshchat.displayMessenger();
      return true;
    }
    
    if (result.show_faq) {
      await Freshchat.displayFAQs();
      return false;
    }
    
    return false;
  }
}
```

### 6.2 Context Tracker

```typescript
// mobile/services/ContextTracker.ts

/**
 * Context Tracker
 * 
 * Tracks user behavior and maintains real-time context.
 * Syncs with Freshchat and backend.
 * 
 * @docz
 * category: Mobile Services
 */

export class ContextTracker {
  private static currentContext: UserContext = {};
  private static screenStartTime: number = 0;
  
  /**
   * Track screen navigation
   * 
   * Pseudocode:
   * 1. Calculate time on previous screen
   * 2. Check for back navigation
   * 3. Update current screen
   * 4. Sync to Freshchat
   * 5. Log friction signal if needed
   */
  static async trackScreen(
    screenName: string,
    isBackNavigation: boolean = false
  ): Promise<void> {
    const previousScreen = this.currentContext.currentScreen;
    const timeOnPrevious = Date.now() - this.screenStartTime;
    
    // Update context
    this.currentContext.currentScreen = screenName;
    this.screenStartTime = Date.now();
    
    if (isBackNavigation) {
      this.currentContext.backNavigationCount = 
        (this.currentContext.backNavigationCount || 0) + 1;
    }
    
    // Sync to Freshchat and backend
    await FreshchatService.syncContext({
      screen: screenName,
      ...this.currentContext
    });
    
    // Log to backend for analytics
    await ContextAPI.updateScreen(screenName, {
      previousScreen,
      timeOnPrevious,
      isBackNavigation
    });
  }
  
  /**
   * Track cart updates
   */
  static async trackCart(cart: Cart): Promise<void> {
    this.currentContext.cartValue = cart.total;
    this.currentContext.itemCount = cart.items.length;
    this.currentContext.guestCount = cart.guestCount;
    
    await FreshchatService.syncContext(this.currentContext);
    await ContextAPI.updateCart(cart);
  }
  
  /**
   * Calculate and report friction score
   */
  static async checkFriction(): Promise<FrictionResult> {
    const result = await FrictionAPI.logSignal({
      ...this.currentContext,
      timeOnCheckout: this.getTimeOnScreen('CHECKOUT')
    });
    
    if (result.should_show_help) {
      // Show contextual help prompt
      await this.showHelpPrompt(result.help_message);
    }
    
    return result;
  }
}
```

---

## 7. Analytics & Reporting

### 7.1 Weekly Report Generator

```python
# services/analytics_service.py

"""
Analytics Service

Generates reports and KPIs for product improvement
and investor visibility.

@docz
category: Services
"""


class AnalyticsService:
    """
    Computes analytics from incidence data.
    
    Key Metrics:
    - Self-serve conversion rate
    - Assisted conversion rate
    - Average time to resolve
    - Cost per assisted order
    - Top friction reasons
    
    @docz
    schedule: Weekly (Mondays), Daily aggregation
    """
    
    async def generate_weekly_report(self) -> WeeklyReport:
        """
        Generate weekly analytics report.
        
        Pseudocode:
        1. Query incidences from last 7 days
        2. Calculate primary metrics
        3. Identify top friction reasons
        4. Compute cost analysis
        5. Generate recommendations
        
        @docz
        output: WeeklyReport object + email to stakeholders
        """
        start_date = get_last_monday()
        end_date = get_last_sunday()
        
        incidences = await self.repo.get_range(start_date, end_date)
        orders = await self.order_repo.get_range(start_date, end_date)
        
        # Primary metrics
        total_orders = len(orders)
        orders_without_help = len([o for o in orders if not o.has_incidence])
        orders_with_help = len([o for o in orders if o.has_incidence])
        
        self_serve_rate = orders_without_help / total_orders * 100
        
        # Resolution metrics
        resolved = [i for i in incidences if i.outcome != "IN_PROGRESS"]
        avg_time_to_resolve = mean([i.time_to_resolve_seconds for i in resolved])
        
        # Cost analysis (assuming ₹X per agent hour)
        total_support_time = sum([i.time_to_resolve_seconds for i in resolved])
        support_cost = (total_support_time / 3600) * AGENT_HOURLY_RATE
        cost_per_assisted_order = support_cost / orders_with_help
        
        # Top friction reasons
        issue_counts = Counter([i.issue_category for i in incidences])
        top_issues = issue_counts.most_common(10)
        
        # Recommendations
        recommendations = await self.generate_recommendations(
            top_issues, self_serve_rate
        )
        
        return WeeklyReport(
            period=f"{start_date} to {end_date}",
            total_orders=total_orders,
            self_serve_rate=self_serve_rate,
            assisted_orders=orders_with_help,
            avg_time_to_resolve_minutes=avg_time_to_resolve / 60,
            cost_per_assisted_order=cost_per_assisted_order,
            top_friction_reasons=top_issues,
            recommendations=recommendations
        )
```

---

## 8. Deployment

### 8.1 Infrastructure Requirements

| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| API Server | 2 vCPU, 4GB RAM | ~₹3,000 |
| PostgreSQL | 2 vCPU, 4GB RAM, 50GB | ~₹2,500 |
| Redis | 1GB | ~₹1,000 |
| Celery Workers | 1 vCPU, 2GB RAM | ~₹1,500 |
| **Total Infra** | | **~₹8,000** |

### 8.2 Environment Variables

```bash
# .env.example

# Freshchat
FRESHCHAT_APP_ID=your_app_id
FRESHCHAT_APP_KEY=your_app_key
FRESHCHAT_DOMAIN=msdk.freshchat.com
FRESHCHAT_WEBHOOK_SECRET=your_webhook_secret

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# Analytics
AGENT_HOURLY_RATE=150  # ₹150/hour

# Feature Flags
FRICTION_DETECTION_ENABLED=true
CHANNEL_ROUTING_ENABLED=true
```

---

## 9. Implementation Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| **Week 1** | Freshchat setup, SDK integration, context passing | Chat working in app |
| **Week 2** | Webhook handler, Incidence Service, database | Incidences being logged |
| **Week 3** | Channel Router, Friction Detection | Smart routing active |
| **Week 4** | Analytics Service, Agent Dashboard config | Weekly reports |

---

## 10. Success Metrics

| Metric | Target (Month 1) | Target (Month 3) |
|--------|------------------|------------------|
| Self-serve conversion | 60% | 75% |
| Avg. time to resolve | <10 min | <5 min |
| Cost per assisted order | <₹50 | <₹30 |
| Repeat friction issues | Track | -30% |

---

## 11. References

| Document | Purpose |
|----------|---------|
| [Backend_Requirements.md](./Backend_Requirements.md) | Module specifications |
| [Tech_Stack_Freshchat.md](./Tech_Stack_Freshchat.md) | Integration details |
| [Tool_Selection_Guide.md](./Tool_Selection_Guide.md) | Platform decision |
| [Freshchat Docs](https://developers.freshchat.com) | Official SDK/API docs |

---

**Document Status**: Ready for Engineering Review  
**Next Steps**: Review with team → Sprint planning → Implementation
