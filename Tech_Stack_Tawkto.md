# Technical Implementation Guide: Tawk.to
## Support-Led Ordering System Integration

---

## 1. Platform Overview

| Aspect | Details |
|--------|---------|
| **Platform** | Tawk.to |
| **Pricing** | **FREE** (core features) |
| **SDK Support** | JavaScript API, Mobile WebView |
| **Custom Backend** | REST API (by request) + Webhooks |
| **Documentation** | [developer.tawk.to](https://developer.tawk.to) |

---

## 2. Why Consider Tawk.to

| Advantage | Details |
|-----------|---------|
| **Cost** | 100% free core features |
| **Agents** | Unlimited agents, no per-seat fee |
| **Volume** | Unlimited chats |
| **Trade-off** | Less native mobile SDK, requires WebView approach |

**Best for**: MVP/POC phase, budget-conscious teams, validating Incidence model

---

## 3. Integration Approaches

### Option A: WebView Integration (Recommended for Mobile)

```javascript
// React Native - Using WebView
import { WebView } from 'react-native-webview';

const TawktoChat = ({ userContext }) => {
  const injectedJS = `
    var Tawk_API = Tawk_API || {};
    
    // Set visitor info
    Tawk_API.visitor = {
      name: '${userContext.name}',
      email: '${userContext.email}',
      hash: '${userContext.secureHash}' // HMAC-SHA256
    };
    
    // Set custom attributes
    Tawk_API.onLoad = function() {
      Tawk_API.setAttributes({
        'user_id': '${userContext.userId}',
        'user_tier': '${userContext.tier}',
        'current_screen': '${userContext.currentScreen}',
        'cart_value': '${userContext.cartValue}',
        'guest_count': '${userContext.guestCount}',
        'event_type': '${userContext.eventType}'
      });
      
      // Add tags
      Tawk_API.addTags(['order_value_${userContext.orderTier}']);
    };
    
    true;
  `;

  return (
    <WebView
      source={{ uri: 'https://your-domain.com/chat-page' }}
      injectedJavaScript={injectedJS}
      javaScriptEnabled={true}
    />
  );
};
```

### Option B: Web Integration (for Web App)

```html
<!-- Add to your HTML -->
<script type="text/javascript">
var Tawk_API = Tawk_API || {};
var Tawk_LoadStart = new Date();

// Pre-set visitor info before widget loads
Tawk_API.visitor = {
    name: 'John Doe',
    email: 'john@example.com',
    hash: 'HMAC_SHA256_HASH' // Required for secure mode
};

(function(){
    var s1 = document.createElement("script");
    s1.async = true;
    s1.src = 'https://embed.tawk.to/YOUR_PROPERTY_ID/YOUR_WIDGET_ID';
    s1.charset = 'UTF-8';
    document.head.appendChild(s1);
})();
</script>
```

---

## 4. JavaScript API - Context Passing

### 4.1 Set Visitor Attributes

```javascript
// Call after Tawk widget loads
Tawk_API.onLoad = function() {
    // Set custom attributes (visible to agents)
    Tawk_API.setAttributes({
        'user_id': 'user_12345',
        'user_tier': 'GOLD',
        'past_orders': '15',
        'lifetime_value': '150000',
        
        // Current session
        'current_screen': 'CHECKOUT',
        'cart_value': '25000',
        'guest_count': '100',
        'event_type': 'WEDDING',
        'event_date': '2026-02-15',
        'selected_platter': 'Premium Veg Thali'
    }, function(error) {
        if (error) console.error('Failed to set attributes:', error);
    });
    
    // Add tags for quick filtering
    Tawk_API.addTags([
        'tier_gold',
        'order_high',
        'event_wedding'
    ]);
};
```

### 4.2 Update Context in Real-time

```javascript
function updateSupportContext(screen, cartValue, frictionScore) {
    if (typeof Tawk_API !== 'undefined' && Tawk_API.setAttributes) {
        Tawk_API.setAttributes({
            'current_screen': screen,
            'cart_value': cartValue,
            'friction_score': frictionScore,
            'last_updated': new Date().toISOString()
        });
    }
}

// Call on navigation
navigation.addListener('state', (e) => {
    const screenName = getScreenName(e.state);
    updateSupportContext(screenName, cartTotal, calculateFriction());
});
```

### 4.3 Control Widget Display

```javascript
// Check if support should be available based on order value
function shouldShowSupport(orderValue) {
    if (orderValue < 5000) return false;
    return true;
}

// Show/hide widget based on rules
function toggleSupportWidget(orderValue) {
    if (shouldShowSupport(orderValue)) {
        Tawk_API.showWidget();
    } else {
        Tawk_API.hideWidget();
    }
}

// Maximize widget (open chat)
function openChat() {
    Tawk_API.maximize();
}

// Minimize widget
function minimizeChat() {
    Tawk_API.minimize();
}
```

---

## 5. Secure Mode (HMAC Verification)

**Critical for production** - prevents identity spoofing.

### 5.1 Backend Hash Generation

```python
# Python/FastAPI
import hmac
import hashlib

TAWK_API_KEY = "your_tawk_api_key"  # From Tawk.to dashboard

def generate_tawk_hash(user_email: str) -> str:
    """Generate HMAC-SHA256 hash for Tawk.to secure mode"""
    return hmac.new(
        TAWK_API_KEY.encode(),
        user_email.encode(),
        hashlib.sha256
    ).hexdigest()

# API endpoint
@app.get("/api/tawk-hash")
async def get_tawk_hash(user: User = Depends(get_current_user)):
    return {
        "hash": generate_tawk_hash(user.email),
        "email": user.email
    }
```

### 5.2 Frontend Usage

```javascript
// Fetch hash from your backend
async function initTawkSecure() {
    const response = await fetch('/api/tawk-hash');
    const { hash, email } = await response.json();
    
    Tawk_API.visitor = {
        name: userName,
        email: email,
        hash: hash  // HMAC-SHA256 hash
    };
}
```

---

## 6. Webhook Integration

### 6.1 Available Webhook Events

| Event | Trigger | Your Action |
|-------|---------|-------------|
| `chat:start` | New chat started | Create Incidence |
| `chat:end` | Chat ended | Close Incidence |
| `chat:transcript` | Full transcript available | Store for analytics |
| `ticket:create` | New ticket created | Create Post-Order Incidence |

### 6.2 Webhook Setup

**Enable**: Admin → Settings → Webhooks → Add Webhook

### 6.3 Backend Webhook Handler

```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib

app = FastAPI()

TAWK_WEBHOOK_SECRET = "your_webhook_secret"

@app.post("/webhooks/tawkto")
async def handle_tawkto_webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-Tawk-Signature")
    body = await request.body()
    
    expected_sig = hmac.new(
        TAWK_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha1
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    event = payload.get("event")
    
    if event == "chat:start":
        await handle_chat_start(payload)
    elif event == "chat:end":
        await handle_chat_end(payload)
    elif event == "chat:transcript":
        await handle_transcript(payload)
    
    return {"status": "ok"}

async def handle_chat_start(payload):
    """Create Incidence when chat starts"""
    chat = payload["chat"]
    visitor = payload["visitor"]
    
    # Extract custom attributes
    attrs = visitor.get("customAttributes", {})
    
    incidence = await incidence_service.create_incidence(
        user_id=attrs.get("user_id"),
        conversation_id=chat["id"],
        channel="IN_APP_CHAT",
        trigger="USER_INITIATED",
        stage="PRE_ORDER" if not attrs.get("order_id") else "POST_ORDER",
        app_screen=attrs.get("current_screen"),
        cart_value=float(attrs.get("cart_value", 0)),
        event_type=attrs.get("event_type"),
        friction_score=float(attrs.get("friction_score", 0))
    )
    
    return incidence

async def handle_chat_end(payload):
    """Close Incidence when chat ends"""
    chat = payload["chat"]
    
    await incidence_service.close_incidence(
        conversation_id=chat["id"],
        outcome="RESOLVED",  # Or determine from chat tags
        resolved_at=datetime.now()
    )

async def handle_transcript(payload):
    """Store full transcript for analytics"""
    chat = payload["chat"]
    messages = payload["messages"]
    
    await incidence_service.store_transcript(
        conversation_id=chat["id"],
        messages=messages,
        duration_seconds=chat.get("duration")
    )
```

---

## 7. REST API Integration

**Note**: Tawk.to REST API requires approval. Request access at developer.tawk.to

### 7.1 Authentication

```python
import requests
from requests.auth import HTTPBasicAuth

TAWK_API_KEY = "your_api_key"
TAWK_API_SECRET = "your_api_secret"

auth = HTTPBasicAuth(TAWK_API_KEY, TAWK_API_SECRET)
base_url = "https://api.tawk.to/v1"
```

### 7.2 Get Chat Statistics

```python
def get_chat_stats(property_id: str, start_date: str, end_date: str):
    """Get chat statistics for analytics"""
    response = requests.get(
        f"{base_url}/properties/{property_id}/chats/stats",
        auth=auth,
        params={
            "start": start_date,
            "end": end_date
        }
    )
    return response.json()
```

### 7.3 Get Chat History

```python
def get_chats(property_id: str, page: int = 1):
    """Get list of chats"""
    response = requests.get(
        f"{base_url}/properties/{property_id}/chats",
        auth=auth,
        params={"page": page}
    )
    return response.json()
```

---

## 8. Mobile Deep Integration (React Native)

For a more native feel, create a hybrid approach:

### 8.1 Chat Context Manager

```javascript
// ChatContextManager.js
class ChatContextManager {
    static currentContext = {};
    
    static updateContext(context) {
        this.currentContext = {
            ...this.currentContext,
            ...context,
            lastUpdated: new Date().toISOString()
        };
        
        // Update Tawk if widget is loaded
        if (typeof Tawk_API !== 'undefined') {
            Tawk_API.setAttributes(this.currentContext);
        }
    }
    
    static setScreen(screenName) {
        this.updateContext({ current_screen: screenName });
    }
    
    static setCart(cartValue, itemCount) {
        this.updateContext({
            cart_value: cartValue,
            items_in_cart: itemCount
        });
    }
    
    static setFriction(score) {
        this.updateContext({ friction_score: score });
    }
}
```

### 8.2 Integration with Navigation

```javascript
// App.js
import { NavigationContainer } from '@react-navigation/native';
import ChatContextManager from './ChatContextManager';

function App() {
    const onStateChange = (state) => {
        const currentRoute = state?.routes[state.index];
        ChatContextManager.setScreen(currentRoute?.name || 'unknown');
    };
    
    return (
        <NavigationContainer onStateChange={onStateChange}>
            {/* Your screens */}
        </NavigationContainer>
    );
}
```

---

## 9. Recommended Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python/FastAPI or Node.js | API server, webhooks |
| **Database** | PostgreSQL | Incidences, analytics |
| **Cache** | Redis | Session context |
| **Frontend** | React Native + WebView | Mobile app with Tawk chat |
| **Web** | React/Next.js | Web app with native Tawk widget |
| **Analytics** | Custom Dashboard | KPIs, friction analysis |

---

## 10. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         MOBILE APP                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ React Native App                                          │  │
│  │  ┌─────────────────┐  ┌───────────────────────────────┐  │  │
│  │  │ Native Screens  │  │ Chat Screen (WebView)         │  │  │
│  │  │                 │  │  ┌─────────────────────────┐  │  │  │
│  │  │ - Menu         │  │  │ Tawk.to Widget           │  │  │  │
│  │  │ - Cart         │  │  │ (JavaScript API)         │  │  │  │
│  │  │ - Checkout     │  │  └─────────────────────────┘  │  │  │
│  │  └─────────────────┘  └───────────────────────────────┘  │  │
│  │         │                           ▲                     │  │
│  │         │ setAttributes()           │                     │  │
│  │         └───────────────────────────┘                     │  │
│  │                                                            │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ ChatContextManager                                   │  │  │
│  │  │ - Tracks screen, cart, friction                      │  │  │
│  │  │ - Syncs context to Tawk widget                       │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
└──┼──────────────────────────────────────────────────────────────┘
   │
   │ Secure Hash Request
   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR BACKEND                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Auth API     │  │ Webhook      │  │ Incidence Service    │  │
│  │ (HMAC hash)  │  │ Handler      │─►│                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                           ▲                    │                │
│                           │                    ▼                │
│                    ┌──────┴─────┐   ┌───────────────────────┐  │
│                    │ Tawk.to    │   │ PostgreSQL            │  │
│                    │ Webhooks   │   │ incidences | analytics│ │
│                    └────────────┘   └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           ▲
                           │ Webhooks
┌──────────────────────────┴──────────────────────────────────────┐
│                    TAWK.TO CLOUD                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Agent Dashboard                                           │  │
│  │ - Sees custom attributes (user_id, cart_value, etc.)     │  │
│  │ - Sees tags (tier_gold, order_high)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Cost Estimation

| Item | Monthly Cost |
|------|-------------|
| Tawk.to (Core) | **₹0 (FREE)** |
| Remove Branding (optional) | ~₹2,400 ($29) |
| AI Assist (optional) | ~₹2,400 ($29) |
| AWS/GCP Backend | ~₹5,000 - ₹15,000 |
| PostgreSQL (managed) | ~₹2,000 |
| Redis (managed) | ~₹1,500 |
| **Total (Minimal)** | **~₹8,500 - ₹18,500/mo** |
| **Total (Full features)** | **~₹13,300 - ₹23,300/mo** |

---

## 12. Limitations & Trade-offs

| Limitation | Workaround |
|------------|------------|
| No native mobile SDK | Use WebView for chat |
| REST API requires approval | Request early in project |
| Less customizable than Intercom | Use JavaScript API for basic customization |
| No built-in custom actions | Build in your backend |

---

## 13. Best Use Cases

✅ **Good for**:
- MVP/POC phase
- Budget-conscious startups
- Validating your Incidence model before investing in premium platforms
- Web-first applications

⚠️ **Consider alternatives for**:
- Apps requiring deep native mobile experience
- Complex agent workflows
- Enterprise compliance requirements

---

## 14. Implementation Checklist

- [ ] Create Tawk.to account, get widget code
- [ ] Request REST API access (takes 1-2 days)
- [ ] Set up secure mode (HMAC generation in backend)
- [ ] Implement WebView chat screen in React Native
- [ ] Create ChatContextManager for context syncing
- [ ] Set up webhook endpoint
- [ ] Implement Incidence Service
- [ ] Configure channel visibility rules
- [ ] Test end-to-end flow
- [ ] Migrate to Freshchat/Intercom when scaling
