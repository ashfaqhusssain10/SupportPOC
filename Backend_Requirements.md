# Backend Logic Requirements
## Support-Led Ordering System

Based on your requirements documents, here are all the backend modules and logic needed:

---

## 🔷 Module 1: Incidence Management Service

The core system that replaces traditional "leads" with incidences.

### Data Model: `Incidence`
```
{
  incidenceId: string (UUID)
  userId: string
  orderId: string | null
  stage: "PRE_ORDER" | "POST_ORDER"
  channel: "IN_APP_CHAT" | "CALL" | "WHATSAPP"
  trigger: "USER_INITIATED" | "SYSTEM_INITIATED"
  outcome: "RESOLVED" | "DROPPED" | "CONVERTED"
  
  // Context
  appScreen: string
  userInputs: object
  selectedItems: array
  
  // Resolution
  issueCategory: string
  rootCause: string
  resolutionType: string
  timeToResolve: number (seconds)
  orderImpact: "PLACED" | "MODIFIED" | "LOST"
  
  // Timestamps
  createdAt: timestamp
  resolvedAt: timestamp
  agentId: string | null
}
```

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/incidences` | POST | Create new incidence |
| `/incidences/:id` | GET | Fetch incidence details |
| `/incidences/:id` | PATCH | Update incidence (resolution, outcome) |
| `/incidences/user/:userId` | GET | Get user's incidence history |
| `/incidences/order/:orderId` | GET | Get incidences linked to order |

---

## 🔷 Module 2: User Context Service

Provides real-time user context to support agents.

### Data Model: `UserContext`
```
{
  userId: string
  currentScreen: string
  lastActivity: timestamp
  sessionDuration: number
  
  // Order context
  cartItems: array
  selectedPlatter: object | null
  guestCount: number | null
  eventDate: date | null
  
  // User profile
  language: string
  tier: "GOLD" | "SILVER" | "BRONZE"
  pastOrderCount: number
  lastOrderDate: date | null
  
  // Behavior signals
  hesitationScore: number (0-100)
  backNavigationCount: number
  priceCheckCount: number
}
```

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/context/:userId` | GET | Get current user context |
| `/context/:userId/screen` | PUT | Update current screen |
| `/context/:userId/cart` | PUT | Update cart state |
| `/context/:userId/signals` | POST | Log behavior signal |

---

## 🔷 Module 3: Friction Detection Engine

Auto-detects when users need help.

### Friction Signals to Monitor
| Signal | Threshold | Action |
|--------|-----------|--------|
| Inactivity on checkout | > 60 seconds | Trigger help prompt |
| Back navigation loops | > 3 times on same flow | Trigger help prompt |
| Quantity changes | > 5 changes | Show "Need help with quantities?" |
| Payment retries | > 2 failures | Trigger call option |
| Menu comparison time | > 3 minutes | Show "Compare packages" help |
| Price calculator usage | > 5 calculations | Offer expert consultation |

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/friction/detect` | POST | Evaluate friction score |
| `/friction/signals` | POST | Log friction signal |
| `/friction/thresholds` | GET | Get current thresholds |
| `/friction/thresholds` | PUT | Update thresholds (admin) |

### Logic
```python
def calculate_friction_score(user_context):
    score = 0
    
    if user_context.inactivity_seconds > 60:
        score += 30
    
    if user_context.back_navigation_count > 3:
        score += 25
    
    if user_context.price_check_count > 5:
        score += 20
    
    if user_context.is_high_value_event:
        score += 15
    
    if user_context.is_first_time_user:
        score += 10
    
    return min(score, 100)
```

---

## 🔷 Module 4: Channel Router Service

Routes support requests to appropriate channel based on rules.

### Routing Rules
| Order Value | Allowed Channels | Auto-Escalation |
|-------------|------------------|-----------------|
| < ₹5,000 | ❌ No human support | Self-serve only |
| ₹5,000 - ₹25,000 | Chat only | After 10 min unresolved |
| > ₹25,000 | Chat + Call | Immediate call option |

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/channel/route` | POST | Determine allowed channels |
| `/channel/escalate` | POST | Escalate to higher channel |
| `/channel/rules` | GET | Get routing rules |
| `/channel/rules` | PUT | Update rules (admin) |

### Logic
```python
def get_allowed_channels(order_value, event_type):
    # High-importance events always get call access
    if event_type in ["WEDDING", "CORPORATE", "RELIGIOUS"]:
        return ["CHAT", "CALL"]
    
    if order_value < 5000:
        return []  # No human support
    elif order_value < 25000:
        return ["CHAT"]
    else:
        return ["CHAT", "CALL"]
```

---

## 🔷 Module 5: Escalation Service

Handles escalation rules for CX team.

### Escalation Triggers
| Trigger | Escalation Level |
|---------|-----------------|
| High-value order (>₹50k) | Senior agent |
| System bug reported | Tech team |
| Policy exception request | Supervisor |
| Emotional/critical situation | Senior agent |
| Unresolved > 15 minutes | Supervisor |

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/escalation/trigger` | POST | Trigger escalation |
| `/escalation/rules` | GET | Get escalation rules |
| `/escalation/queue` | GET | Get escalation queue |

---

## 🔷 Module 6: Agent Dashboard Service

Provides agents with user context and tools.

### Agent View Requirements
```
{
  // User Info (instant view)
  userDetails: {
    name, phone, language, tier
  }
  
  // Order Context
  orderContext: {
    cartItems, guestCount, eventDate, 
    selectedPlatter, estimatedValue
  }
  
  // App State
  appState: {
    currentScreen, previousScreens,
    itemsViewed, itemsAdded
  }
  
  // Incidence History
  previousIncidences: array
  
  // Quick Actions
  actions: [
    "APPLY_DISCOUNT",
    "MODIFY_ORDER", 
    "REASSIGN",
    "ESCALATE",
    "CLOSE_RESOLVED",
    "CLOSE_DROPPED"
  ]
}
```

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agent/dashboard/:incidenceId` | GET | Get full context for incidence |
| `/agent/actions/:incidenceId` | POST | Perform agent action |
| `/agent/notes/:incidenceId` | POST | Add agent notes |

---

## 🔷 Module 7: Analytics & Feedback Loop Service

Powers product improvements and investor reporting.

### Metrics to Track
| Metric | Calculation | Purpose |
|--------|-------------|---------|
| Self-serve conversion % | Orders without help / Total orders | Primary KPI |
| Assisted conversion % | Orders with help / Total assisted | CX efficiency |
| Time to resolve | Avg(resolvedAt - createdAt) | CX performance |
| Cost per assisted order | CX cost / Assisted orders | Unit economics |
| Top friction reasons | Count by issueCategory | Product fixes |
| Repeat issues | Same issueCategory > 3/week | Priority fixes |

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/analytics/kpis` | GET | Get dashboard KPIs |
| `/analytics/friction-report` | GET | Weekly friction report |
| `/analytics/cost-analysis` | GET | Cost per order analysis |
| `/analytics/trend/:metric` | GET | Trend over time |

### Automated Reports
```python
def generate_weekly_report():
    return {
        "period": "last_7_days",
        "top_friction_reasons": get_top_issues(limit=10),
        "unresolved_repeats": get_repeat_issues(),
        "cost_per_order": calculate_cost_metrics(),
        "self_serve_rate": calculate_self_serve_rate(),
        "recommendations": generate_product_fixes()
    }
```

---

## 🔷 Module 8: Webhook Integration Service

Connects with chat platform (Freshchat/Intercom).

### Incoming Webhooks (from Chat Platform)
| Event | Handler |
|-------|---------|
| `chat.started` | Create incidence |
| `chat.message.received` | Update incidence timeline |
| `chat.resolved` | Close incidence |
| `chat.agent.assigned` | Update agentId |

### Outgoing API Calls (to Chat Platform)
| Action | Purpose |
|--------|---------|
| `sendUserContext` | Push context when chat starts |
| `updateConversation` | Add order details |
| `routeToAgent` | Route based on rules |
| `closeConversation` | Auto-close when order placed |

---

## 🔷 Module 9: CX Rules Engine

Enforces "what CX can and cannot do."

### Allowed Actions
- ✅ Clarify menu options
- ✅ Reassure on quality/delivery
- ✅ Compare platters/packages
- ✅ Help complete order (same as app flow)
- ✅ Apply pre-approved discounts

### Blocked Actions
- ❌ Push or upsell
- ❌ Restart user's journey
- ❌ Override app pricing
- ❌ Make off-system promises
- ❌ Offer custom items not in catalog

### Implementation
```python
def validate_agent_action(action, incidence):
    blocked_actions = [
        "CUSTOM_PRICING",
        "OFF_CATALOG_ITEM",
        "MANUAL_DISCOUNT_OVER_LIMIT"
    ]
    
    if action.type in blocked_actions:
        return {
            "allowed": False,
            "reason": "This action requires supervisor approval"
        }
    
    return {"allowed": True}
```

---

## 🔷 Module 10: Notification Service

Triggers proactive help at right moments.

### Trigger Points
| App Screen | Trigger Condition | Notification |
|------------|-------------------|--------------|
| Guest count | Inactivity > 45s | "Need help deciding portions?" |
| Menu comparison | > 3 platters viewed | "Want expert recommendation?" |
| Customization | > 5 changes | "Let us help customize" |
| Checkout | Cart > ₹25k | "Talk to catering expert" |
| Payment fail | > 1 retry | "Need payment help?" |

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/notifications/trigger` | POST | Trigger help notification |
| `/notifications/suppress/:userId` | POST | User dismissed help |
| `/notifications/rules` | GET | Get trigger rules |

---

## 📊 Database Schema Summary

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `incidences` | Core incidence data | id, userId, orderId, stage, outcome |
| `incidence_timeline` | Chat/action history | incidenceId, eventType, timestamp |
| `user_context` | Real-time user state | userId, currentScreen, cartItems |
| `friction_signals` | Behavior tracking | userId, signalType, value, timestamp |
| `escalation_log` | Escalation history | incidenceId, level, reason |
| `agent_actions` | Audit trail | incidenceId, agentId, action |
| `analytics_daily` | Pre-computed metrics | date, metric, value |
| `routing_rules` | Channel routing config | orderValueMin, orderValueMax, channels |

---

## 🔄 System Flow Summary

```
User opens app
      │
      ▼
┌─────────────────┐
│ Context Service │ ◄── Tracks screen, cart, behavior
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Friction Engine │ ◄── Monitors signals, calculates score
└────────┬────────┘
         │
    Score > 50?
         │
    ┌────┴────┐
    │ YES     │ NO
    ▼         ▼
┌───────┐  Continue
│Trigger│  self-serve
│ Help  │
└───┬───┘
    │
    ▼
┌─────────────────┐
│ Channel Router  │ ◄── Applies cost rules
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Incidence│ ◄── Logs everything
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Agent Dashboard │ ◄── Full context visible
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Resolution      │ ◄── Outcome logged
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Analytics Loop  │ ◄── Feeds product improvements
└─────────────────┘
```

---

## 📋 Implementation Priority

| Priority | Module | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Incidence Management | Medium | High |
| P0 | User Context Service | Medium | High |
| P0 | Channel Router | Low | High |
| P1 | Friction Detection | High | High |
| P1 | Agent Dashboard | Medium | High |
| P1 | Webhook Integration | Medium | Medium |
| P2 | Analytics Service | Medium | Medium |
| P2 | Escalation Service | Low | Medium |
| P3 | CX Rules Engine | Low | Low |
| P3 | Notification Service | Medium | Medium |
