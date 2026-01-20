# Technical Implementation Guide: Freshchat
## Support-Led Ordering System Integration

---

## 1. Platform Overview

| Aspect | Details |
|--------|---------|
| **Platform** | Freshchat (Freshworks) |
| **Pricing Tier** | Growth (~₹1,600/agent/mo) recommended |
| **SDK Support** | iOS, Android, React Native, Web |
| **Custom Backend** | REST API + Webhooks |
| **Documentation** | [developers.freshchat.com](https://developers.freshchat.com) |

---

## 2. SDK Integration

### 2.1 React Native Setup

```bash
# Install SDK
npm install react-native-freshchat-sdk

# iOS Setup
cd ios && pod install
```

```javascript
// Initialize Freshchat
import Freshchat from 'react-native-freshchat-sdk';

Freshchat.init({
  appId: 'YOUR_APP_ID',
  appKey: 'YOUR_APP_KEY',
  domain: 'YOUR_DOMAIN' // e.g., msdk.freshchat.com
});
```

### 2.2 Android Setup

```gradle
// build.gradle (project level)
allprojects {
    repositories {
        maven { url "https://jitpack.io" }
    }
}

// build.gradle (app level)
dependencies {
    implementation 'com.github.nickclaw:react-native-freshchat-sdk:latest-version'
}
```

### 2.3 iOS Setup

```ruby
# Podfile
pod 'FreshchatSDK'
```

---

## 3. Passing User Context to Agents

This is critical for your "Support sees full context" requirement.

### 3.1 Set User Properties

```javascript
// When user logs in
Freshchat.setUser({
  firstName: 'John',
  lastName: 'Doe',
  email: 'john@example.com',
  phone: '+919876543210',
  phoneCountryCode: '+91'
});

// Set custom properties (your Incidence context)
Freshchat.setUserProperties({
  'user_tier': 'GOLD',
  'past_orders': '15',
  'preferred_language': 'Hindi',
  'registered_date': '2024-01-15'
});
```

### 3.2 Pass Order Context

```javascript
// When user enters checkout or needs help
Freshchat.setUserProperties({
  'current_screen': 'CHECKOUT',
  'cart_value': '25000',
  'guest_count': '100',
  'event_type': 'WEDDING',
  'event_date': '2026-02-15',
  'selected_platter': 'Premium Veg Thali',
  'items_in_cart': 'Paneer Tikka, Dal Makhani, Biryani'
});
```

### 3.3 Dynamic Context Updates

```javascript
// Update context in real-time as user navigates
function updateSupportContext(screen, data) {
  Freshchat.setUserProperties({
    'current_screen': screen,
    'last_action': data.action,
    'session_duration_mins': data.sessionMinutes,
    'friction_score': data.frictionScore
  });
}
```

---

## 4. Webhook Integration (Backend)

### 4.1 Webhook Events

| Event | Trigger | Your Action |
|-------|---------|-------------|
| `message_create` | New message sent | Log to Incidence timeline |
| `conversation_assignment` | Agent assigned | Update Incidence with agentId |
| `conversation_resolution` | Chat resolved | Close Incidence, log outcome |
| `conversation_reopen` | Chat reopened | Reopen Incidence |

### 4.2 Webhook Setup

**Enable webhooks**: Admin → Settings → Webhooks

**Webhook endpoint** (your backend):
```
POST https://your-api.com/webhooks/freshchat
```

### 4.3 Backend Webhook Handler

```python
# Python/FastAPI example
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()

FRESHCHAT_SECRET = "your_webhook_secret"

@app.post("/webhooks/freshchat")
async def handle_freshchat_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-Freshchat-Signature")
    body = await request.body()
    
    expected_sig = hmac.new(
        FRESHCHAT_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=401)
    
    payload = await request.json()
    event_type = payload.get("action")
    
    if event_type == "message_create":
        await handle_message_create(payload)
    elif event_type == "conversation_resolution":
        await handle_conversation_resolved(payload)
    
    return {"status": "ok"}

async def handle_message_create(payload):
    """Log message to Incidence timeline"""
    conversation_id = payload["data"]["conversation"]["id"]
    user_id = payload["data"]["user"]["id"]
    message = payload["data"]["message"]
    
    # Create or update Incidence in your database
    await incidence_service.log_timeline_event(
        conversation_id=conversation_id,
        user_id=user_id,
        event_type="MESSAGE",
        content=message["text"],
        sender=message["actor_type"]  # "user" or "agent"
    )

async def handle_conversation_resolved(payload):
    """Close Incidence when chat resolved"""
    conversation_id = payload["data"]["conversation"]["id"]
    
    await incidence_service.close_incidence(
        conversation_id=conversation_id,
        outcome="RESOLVED",
        resolved_at=datetime.now()
    )
```

---

## 5. REST API Integration

### 5.1 Authentication

```python
import requests

# Get access token (OAuth 2.0)
def get_freshchat_token():
    response = requests.post(
        "https://api.freshchat.com/v2/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "YOUR_APP_ID",
            "client_secret": "YOUR_APP_KEY"
        }
    )
    return response.json()["access_token"]
```

### 5.2 Fetch Conversation Details

```python
def get_conversation(conversation_id):
    token = get_freshchat_token()
    response = requests.get(
        f"https://api.freshchat.com/v2/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### 5.3 Send Message from Backend

```python
def send_system_message(conversation_id, message):
    """Send automated message (e.g., order confirmation)"""
    token = get_freshchat_token()
    response = requests.post(
        f"https://api.freshchat.com/v2/conversations/{conversation_id}/messages",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "message_parts": [{
                "text": {"content": message}
            }],
            "actor_type": "system"
        }
    )
    return response.json()
```

---

## 6. Channel Router Implementation

Based on your cost boundary rules:

```python
def determine_support_channel(order_value: float, event_type: str) -> dict:
    """
    Returns allowed channels based on order value and event type.
    Integrates with Freshchat routing.
    """
    
    # High-importance events always get full access
    if event_type in ["WEDDING", "CORPORATE", "RELIGIOUS"]:
        return {
            "allowed_channels": ["CHAT", "CALL"],
            "priority": "HIGH",
            "route_to_group": "premium_support"
        }
    
    # Apply cost boundaries
    if order_value < 5000:
        return {
            "allowed_channels": [],  # No human support
            "show_faq": True,
            "show_self_serve": True
        }
    elif order_value < 25000:
        return {
            "allowed_channels": ["CHAT"],
            "priority": "NORMAL",
            "route_to_group": "general_support"
        }
    else:
        return {
            "allowed_channels": ["CHAT", "CALL"],
            "priority": "HIGH",
            "route_to_group": "premium_support"
        }
```

---

## 7. Recommended Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python/FastAPI or Node.js/Express | API server, webhook handler |
| **Database** | PostgreSQL | Incidences, users, analytics |
| **Cache** | Redis | Real-time user context |
| **Queue** | RabbitMQ/SQS | Async webhook processing |
| **Frontend** | React Native | Mobile app with Freshchat SDK |
| **Analytics** | Metabase/Grafana | Dashboard for KPIs |

---

## 8. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         MOBILE APP                              │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ Freshchat SDK    │◄──►│ Context Tracker (your code)      │  │
│  │ (Chat UI)        │    │ - Tracks screen, cart, behavior  │  │
│  └────────┬─────────┘    │ - Calls setUserProperties()      │  │
│           │              └──────────────────────────────────┘  │
└───────────┼─────────────────────────────────────────────────────┘
            │
            │ Chat messages, context
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRESHCHAT CLOUD                              │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ Agent Dashboard  │    │ Conversation Storage             │  │
│  │ (sees context)   │    │ Routing Engine                   │  │
│  └──────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ Webhooks
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR BACKEND                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Webhook      │  │ Incidence    │  │ Channel Router       │  │
│  │ Handler      │─►│ Service      │  │ (cost rules)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                 │                    │               │
│         ▼                 ▼                    ▼               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL                            │  │
│  │  incidences | users | analytics | friction_signals       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Cost Estimation

| Item | Monthly Cost |
|------|-------------|
| Freshchat Growth (5 agents) | ~₹8,000 ($95) |
| AWS/GCP Backend | ~₹5,000 - ₹15,000 |
| PostgreSQL (managed) | ~₹2,000 |
| Redis (managed) | ~₹1,500 |
| **Total** | **~₹16,500 - ₹26,500/mo** |

---

## 10. Implementation Checklist

- [ ] Create Freshchat account, get API credentials
- [ ] Integrate SDK in React Native app
- [ ] Set up context tracking (setUserProperties)
- [ ] Build backend webhook handler
- [ ] Implement Incidence Service
- [ ] Set up channel routing rules
- [ ] Configure agent dashboard with custom fields
- [ ] Build analytics dashboard
- [ ] Test end-to-end flow
