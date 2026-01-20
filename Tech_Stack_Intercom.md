# Technical Implementation Guide: Intercom
## Support-Led Ordering System Integration

---

## 1. Platform Overview

| Aspect | Details |
|--------|---------|
| **Platform** | Intercom |
| **Pricing Tier** | Advanced (~₹7,100/seat/mo) recommended |
| **SDK Support** | iOS, Android, React Native, Cordova, Flutter |
| **Custom Backend** | REST API + Webhooks + Custom Actions |
| **Documentation** | [developers.intercom.com](https://developers.intercom.com) |

---

## 2. SDK Integration

### 2.1 React Native Setup

```bash
npm install @intercom/intercom-react-native
```

### 2.2 iOS Configuration

```ruby
# Podfile
pod 'Intercom'
```

```swift
// AppDelegate.swift
import Intercom

func application(_ application: UIApplication, 
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    Intercom.setApiKey("YOUR_API_KEY", forAppId: "YOUR_APP_ID")
    return true
}
```

### 2.3 Android Configuration

```gradle
// build.gradle (app)
dependencies {
    implementation 'io.intercom.android:intercom-sdk:14.+'
}
```

```kotlin
// Application.kt
import io.intercom.android.sdk.Intercom

class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        Intercom.initialize(this, "YOUR_API_KEY", "YOUR_APP_ID")
    }
}
```

### 2.4 React Native Initialization

```javascript
import Intercom from '@intercom/intercom-react-native';

// Initialize
Intercom.setApiKey('YOUR_API_KEY', 'YOUR_APP_ID');

// For Android, also call in Application class
```

---

## 3. User Identification & Context

### 3.1 Register User

```javascript
// When user logs in
Intercom.registerIdentifiedUser({
  userId: 'user_12345',
  email: 'john@example.com'
});

// For logged out users
Intercom.registerUnidentifiedUser();
```

### 3.2 Update User Attributes

```javascript
// Set standard attributes
Intercom.updateUser({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+919876543210',
  languageOverride: 'hi', // Hindi
  signedUpAt: 1640995200, // Unix timestamp
});
```

### 3.3 Custom Data Attributes (Your Incidence Context)

```javascript
// Create custom attributes first in Intercom Settings → Data → People

// Then set them via SDK
Intercom.updateUser({
  customAttributes: {
    // User profile
    user_tier: 'GOLD',
    past_order_count: 15,
    lifetime_value: 150000,
    
    // Current session context
    current_screen: 'CHECKOUT',
    cart_value: 25000,
    guest_count: 100,
    event_type: 'WEDDING',
    event_date: '2026-02-15',
    selected_platter: 'Premium Veg Thali',
    
    // Friction indicators
    friction_score: 65,
    session_duration_mins: 12,
    price_checks: 5,
    back_navigations: 3,
    
    // For channel routing
    order_value_tier: 'HIGH' // >₹25k
  }
});
```

### 3.4 Track Events

```javascript
// Track user actions for behavior analysis
Intercom.logEvent('viewed_platter', {
  platter_id: 'premium_veg',
  platter_price: 350,
  guest_count: 100
});

Intercom.logEvent('added_to_cart', {
  item_name: 'Paneer Tikka',
  quantity: 100,
  total_price: 15000
});

Intercom.logEvent('checkout_started', {
  cart_value: 25000,
  items_count: 5
});

Intercom.logEvent('payment_failed', {
  error_code: 'TIMEOUT',
  attempt_number: 2
});
```

---

## 4. Controlling Chat Display

### 4.1 Show/Hide Messenger Based on Rules

```javascript
import Intercom from '@intercom/intercom-react-native';

function shouldShowSupport(orderValue, eventType) {
  // Apply your cost boundary rules
  if (orderValue < 5000) {
    return false; // No human support
  }
  return true;
}

// Show chat when allowed
if (shouldShowSupport(cartValue, eventType)) {
  Intercom.displayMessenger();
} else {
  // Show FAQ/self-serve instead
  Intercom.displayHelpCenter();
}
```

### 4.2 Open Chat with Pre-filled Context

```javascript
// Open messenger with specific context
Intercom.displayMessengerWithInitialMessage(
  `Hi! I need help with my order for ${guestCount} guests on ${eventDate}`
);
```

---

## 5. Webhook Integration (Backend)

### 5.1 Webhook Events

| Event | Trigger | Your Action |
|-------|---------|-------------|
| `conversation.user.created` | New conversation | Create Incidence |
| `conversation.user.replied` | User sent message | Log to timeline |
| `conversation.admin.replied` | Agent replied | Log to timeline |
| `conversation.admin.closed` | Conversation closed | Close Incidence |
| `conversation.admin.assigned` | Assigned to agent | Update agentId |

### 5.2 Webhook Setup

**Register webhook**: Settings → Developers → Your Apps → Webhooks

### 5.3 Backend Webhook Handler

```python
# Python/FastAPI example
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()

INTERCOM_CLIENT_SECRET = "your_client_secret"

@app.post("/webhooks/intercom")
async def handle_intercom_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-Hub-Signature")
    body = await request.body()
    
    expected_sig = "sha1=" + hmac.new(
        INTERCOM_CLIENT_SECRET.encode(),
        body,
        hashlib.sha1
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=401)
    
    payload = await request.json()
    topic = payload.get("topic")
    
    handlers = {
        "conversation.user.created": handle_conversation_created,
        "conversation.user.replied": handle_user_message,
        "conversation.admin.replied": handle_agent_message,
        "conversation.admin.closed": handle_conversation_closed,
    }
    
    handler = handlers.get(topic)
    if handler:
        await handler(payload)
    
    return {"status": "ok"}

async def handle_conversation_created(payload):
    """Create new Incidence when conversation starts"""
    data = payload["data"]["item"]
    
    # Extract user context from custom attributes
    user = data["user"]
    custom_attrs = user.get("custom_attributes", {})
    
    incidence = await incidence_service.create_incidence(
        user_id=user["id"],
        conversation_id=data["id"],
        stage="PRE_ORDER" if not custom_attrs.get("order_id") else "POST_ORDER",
        channel="IN_APP_CHAT",
        trigger="USER_INITIATED",
        app_screen=custom_attrs.get("current_screen"),
        cart_value=custom_attrs.get("cart_value"),
        event_type=custom_attrs.get("event_type"),
        friction_score=custom_attrs.get("friction_score")
    )
    
    return incidence

async def handle_conversation_closed(payload):
    """Close Incidence and log outcome"""
    data = payload["data"]["item"]
    conversation_id = data["id"]
    
    # Determine outcome based on conversation tags or admin notes
    tags = data.get("tags", [])
    outcome = "RESOLVED"
    order_impact = "PLACED"
    
    if "dropped" in [t["name"].lower() for t in tags]:
        outcome = "DROPPED"
        order_impact = "LOST"
    
    await incidence_service.close_incidence(
        conversation_id=conversation_id,
        outcome=outcome,
        order_impact=order_impact,
        resolved_at=datetime.now()
    )
```

---

## 6. REST API Integration

### 6.1 Authentication

```python
import requests

INTERCOM_ACCESS_TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {INTERCOM_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Intercom-Version": "2.10"
}
```

### 6.2 Create/Update Contact

```python
def update_contact(user_id: str, attributes: dict):
    """Update user with custom attributes"""
    response = requests.post(
        "https://api.intercom.io/contacts",
        headers=headers,
        json={
            "external_id": user_id,
            "custom_attributes": attributes
        }
    )
    return response.json()
```

### 6.3 Search Conversations

```python
def search_conversations(user_id: str):
    """Get all conversations for a user"""
    response = requests.post(
        "https://api.intercom.io/conversations/search",
        headers=headers,
        json={
            "query": {
                "field": "contact_ids",
                "operator": "=",
                "value": user_id
            }
        }
    )
    return response.json()
```

### 6.4 Send Message from Backend

```python
def send_admin_message(conversation_id: str, message: str, admin_id: str):
    """Send message as admin (e.g., order update)"""
    response = requests.post(
        f"https://api.intercom.io/conversations/{conversation_id}/reply",
        headers=headers,
        json={
            "type": "admin",
            "admin_id": admin_id,
            "message_type": "comment",
            "body": message
        }
    )
    return response.json()
```

---

## 7. Custom Actions (Intercom Apps)

Intercom allows building custom actions that agents can trigger.

### 7.1 Create Custom Action for Agents

```python
# Register action endpoint
@app.post("/intercom/actions/apply-discount")
async def apply_discount_action(request: Request):
    payload = await request.json()
    
    conversation_id = payload["conversation_id"]
    contact = payload["contact"]
    action_params = payload["canvas"]["content"]["components"]
    
    discount_percent = action_params.get("discount_percent", 10)
    
    # Apply discount in your system
    order_id = contact["custom_attributes"].get("current_order_id")
    await order_service.apply_discount(order_id, discount_percent)
    
    # Return confirmation canvas
    return {
        "canvas": {
            "content": {
                "components": [
                    {
                        "type": "text",
                        "text": f"✅ Applied {discount_percent}% discount to order {order_id}"
                    }
                ]
            }
        }
    }
```

---

## 8. Recommended Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Node.js/Express or Python/FastAPI | API server, webhook handler |
| **Database** | PostgreSQL | Incidences, users, analytics |
| **Cache** | Redis | Real-time user context, rate limiting |
| **Queue** | Bull (Redis) or SQS | Async webhook processing |
| **Frontend** | React Native | Mobile app with Intercom SDK |
| **Analytics** | Mixpanel + Custom Dashboard | Behavior analytics |

---

## 9. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         MOBILE APP                              │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ Intercom SDK     │    │ Context Manager                  │  │
│  │ (Messenger UI)   │◄──►│ - updateUser() with context      │  │
│  │                  │    │ - logEvent() for behavior        │  │
│  └────────┬─────────┘    └──────────────────────────────────┘  │
│           │                                                     │
│  ┌────────┴─────────────────────────────────────────────────┐  │
│  │ Channel Controller                                        │  │
│  │ - Checks order value against rules                        │  │
│  │ - Shows messenger or help center accordingly              │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTERCOM CLOUD                               │
│  ┌──────────────────┐    ┌──────────────────────────────────┐  │
│  │ Agent Inbox      │    │ Custom Attributes visible        │  │
│  │ - Full context   │    │ - current_screen, cart_value     │  │
│  │ - Custom actions │    │ - event_type, friction_score     │  │
│  └──────────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ Webhooks
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR BACKEND                                │
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Webhook    │  │ Incidence  │  │ Analytics  │  │ Custom   │ │
│  │ Handler    │─►│ Service    │─►│ Service    │  │ Actions  │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
│         │               │               │               │      │
│         └───────────────┴───────────────┴───────────────┘      │
│                                 │                              │
│                                 ▼                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      PostgreSQL                          │  │
│  │  incidences | timeline | analytics | agent_actions       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Cost Estimation

| Item | Monthly Cost |
|------|-------------|
| Intercom Advanced (5 seats) | ~₹35,500 ($425) |
| Mobile Add-on | ~₹8,300 ($99) |
| Fin AI (optional, per resolution) | Variable |
| AWS/GCP Backend | ~₹5,000 - ₹15,000 |
| PostgreSQL (managed) | ~₹2,000 |
| Redis (managed) | ~₹1,500 |
| **Total** | **~₹52,300 - ₹62,300/mo** |

---

## 11. Key Advantages Over Freshchat

| Feature | Intercom | Freshchat |
|---------|----------|-----------|
| Custom Actions for Agents | ✅ Built-in | ❌ Limited |
| Event Tracking | ✅ Powerful | ⚠️ Basic |
| Custom Objects | ✅ Yes | ❌ No |
| UX/Design | ✅ Premium | ⚠️ Standard |
| Price | 💰💰💰 Higher | 💰 Lower |

---

## 12. Implementation Checklist

- [ ] Create Intercom account, get API credentials
- [ ] Install SDK in React Native app
- [ ] Create custom attributes in Intercom dashboard
- [ ] Implement context tracking (updateUser, logEvent)
- [ ] Build channel routing logic in app
- [ ] Set up webhook endpoint
- [ ] Implement Incidence Service
- [ ] Build custom actions for agents (optional)
- [ ] Configure analytics dashboard
- [ ] Enable identity verification
- [ ] Test end-to-end flow
