# Support-Led Ordering System - POC Documentation

## Overview

The Support-Led Ordering System is a customer support integration platform designed for **CraftMyPlate**, a catering company. It enables intelligent routing of customer support requests based on order value, detects user friction, and tracks all support interactions as "Incidences" (tickets).

---

## Table of Contents

1. [Architecture](#architecture)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Channel Routing Logic](#channel-routing-logic)
5. [Friction Detection](#friction-detection)
6. [Incidence Lifecycle](#incidence-lifecycle)
7. [Freshchat Integration](#freshchat-integration)
8. [Agent Console](#agent-console)
9. [Analytics Dashboard](#analytics-dashboard)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│  Demo UI (demo.html)     │  Agent Console    │  Analytics Dashboard │
│  - User simulation       │  (agent.html)     │  (analytics.html)    │
│  - Behavior tracking     │  - Ticket queue   │  - KPI cards         │
│  - Freshchat widget      │  - Timeline view  │  - Charts            │
│                          │  - Customer ctx   │  - Incidence table   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          BACKEND LAYER (FastAPI)                    │
├─────────────────────────────────────────────────────────────────────┤
│  /api/v1/channel/route    │  Channel Router - decides support type  │
│  /api/v1/friction/detect  │  Friction Service - calculates scores   │
│  /api/v1/incidences       │  Incidence CRUD - ticket management     │
│  /api/v1/context          │  Context API - user session data        │
│  /api/v1/analytics        │  Analytics - KPIs and reports           │
│  /webhooks/freshchat      │  Webhook Handler - Freshchat events     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  PostgreSQL (port 5433)       │  Redis (port 6379)                  │
│  - incidences                 │  - User context cache               │
│  - incidence_timeline         │  - Session data                     │
│  - friction_signals           │                                     │
│  - analytics_daily            │                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker Desktop
- Node.js (for ngrok)

### Setup Steps

```bash
# 1. Navigate to POC directory
cd poc

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Docker containers
docker-compose up -d

# 5. Create .env file
copy .env.example .env

# 6. Start the server
uvicorn app.main:app --reload
```

### Access Points

| Service | URL | Purpose |
|---------|-----|----------|
| API Documentation | http://localhost:8000/docs | Swagger API explorer |
| Demo UI | http://localhost:8000/demo | Customer-facing simulation |
| Agent Console | http://localhost:8000/agent | Agent ticket management |
| Analytics Dashboard | http://localhost:8000/analytics | Business metrics |
| Health Check | http://localhost:8000/health | System status |

---

## API Endpoints

### Channel Router

**POST** `/api/v1/channel/route`

Determines which support channels are available based on order value and event type.

```json
// Request
{
  "order_value": 55000,
  "event_type": "WEDDING",
  "user_type": "first_time",
  "current_screen": "checkout"
}

// Response
{
  "chat_allowed": true,
  "call_allowed": true,
  "whatsapp_allowed": false,
  "reason": "Premium support: Order value ₹55,000 qualifies for full support",
  "priority": "high"
}
```

### Friction Detection

**POST** `/api/v1/friction/detect`

Calculates user friction score based on behavior signals.

```json
// Request
{
  "inactivity_seconds": 45,
  "price_checks": 5,
  "payment_retries": 2,
  "is_first_time_user": true,
  "current_screen": "checkout"
}

// Response
{
  "friction_score": 75,
  "factors": [
    {"name": "first_time_user", "points": 10},
    {"name": "checkout_screen", "points": 20},
    {"name": "price_checks", "points": 25}
  ],
  "help_message": "Need help with your order?",
  "suggested_action": "SHOW_CHAT"
}
```

### Incidences (Tickets)

**POST** `/api/v1/incidences/` - Create incidence
**GET** `/api/v1/incidences/{id}` - Get incidence
**PATCH** `/api/v1/incidences/{id}` - Update incidence
**POST** `/api/v1/incidences/{id}/close` - Close incidence
**POST** `/api/v1/incidences/{id}/timeline` - Add timeline event

```json
// Create Incidence Request
{
  "user_id": "user_123",
  "stage": "PRE_ORDER",
  "channel": "IN_APP_CHAT",
  "trigger": "USER_INITIATED",
  "cart_value": 55000,
  "event_type": "WEDDING",
  "friction_score": 75
}

// Response
{
  "id": "uuid-here",
  "user_id": "user_123",
  "outcome": "IN_PROGRESS",
  "timeline": []
}
```

---

## Channel Routing Logic

### Thresholds (Configurable in `.env`)

| Order Value | Chat | Call | Priority |
|-------------|------|------|----------|
| < ₹5,000 | ❌ | ❌ | Self-serve only |
| ₹5,000 - ₹25,000 | ✅ | ❌ | Standard |
| > ₹25,000 | ✅ | ✅ | Premium |

### Event Type Multipliers

| Event Type | Multiplier | Effect |
|------------|------------|--------|
| Wedding | 1.5x | Increases priority |
| Corporate | 1.3x | Increases priority |
| Birthday | 1.0x | Standard |
| Casual | 0.8x | Decreases priority |

### Example

```
Order Value: ₹20,000
Event Type: Wedding
Effective Value: ₹20,000 × 1.5 = ₹30,000
Result: Premium Support (Chat + Call)
```

---

## Friction Detection

### Scoring Factors

| Factor | Points | Trigger |
|--------|--------|---------|
| First-time user | +10 | `is_first_time_user = true` |
| Checkout screen | +20 | `current_screen = "checkout"` |
| Payment screen | +30 | `current_screen = "payment"` |
| Inactivity (30-60s) | +15 | 30-60 seconds idle |
| Inactivity (60s+) | +25 | >60 seconds idle |
| Price checks (3-5) | +15 | Checking prices multiple times |
| Price checks (5+) | +25 | Excessive price checking |
| Payment retries | +20 per retry | Failed payment attempts |

### Suggested Actions

| Score | Action |
|-------|--------|
| 0-30 | No action needed |
| 31-50 | Show subtle help option |
| 51-70 | Show proactive help message |
| 71-100 | Trigger live chat option |

---

## Incidence Lifecycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CREATED   │────▶│ IN_PROGRESS │────▶│  RESOLVED   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │                    │
                          │                    │
                          ▼                    ▼
                   ┌─────────────┐     ┌─────────────┐
                   │  ESCALATED  │     │  CONVERTED  │
                   └─────────────┘     └─────────────┘
```

### Outcome Types

| Outcome | Description |
|---------|-------------|
| `IN_PROGRESS` | Active, being worked on |
| `RESOLVED` | Issue resolved, no order |
| `CONVERTED` | User placed an order |
| `DROPPED` | User abandoned |

### Order Impact Types

| Impact | Description |
|--------|-------------|
| `PLACED` | New order placed |
| `MODIFIED` | Existing order modified |
| `LOST` | Order was lost |
| `NONE` | No order impact |

---

## Freshchat Integration

### Widget Integration

The Freshchat widget is embedded in `demo.html`:

```html
<script
  src='//in.fw-cdn.com/32682765/1503844.js'
  chat='true'>
</script>
```

### User Context Passing

When opening chat, user context is passed to agents:

```javascript
window.fcWidget.user.setProperties({
    firstName: "Customer",
    cf_cart_value: 55000,
    cf_event_type: "WEDDING",
    cf_friction_score: 75,
    cf_current_screen: "checkout",
    cf_priority: "high"
});
```

### Webhook Configuration

1. Start ngrok:
   ```bash
   ngrok http 8000
   ```

2. Configure in Freshchat:
   - URL: `https://your-ngrok-url/webhooks/freshchat`
   - Events: `message_create`, `conversation_resolution`

### Webhook Events Handled

| Event | Action |
|-------|--------|
| `message_create` | Logs to incidence timeline |
| `conversation_assignment` | Updates agent_id |
| `conversation_resolution` | Closes incidence |

---

## Agent Console

### Available at: `http://localhost:8000/agent`

The Agent Console is a unified dashboard where support agents can manage all customer tickets in one place.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎧 Agent Console                                  │
├──────────────┬───────────────────────────────┬──────────────────────┤
│              │                               │                      │
│  INCIDENCES  │      CONVERSATION             │  CUSTOMER CONTEXT    │
│  (Left)      │      (Center)                 │  (Right)             │
│              │                               │                      │
│ ⚡ Sneha S.  │  System: Incidence created    │  👤 User ID          │
│   ₹95,000    │  Agent: Hello! How can I     │  📦 Cart Value       │
│   Wedding    │  help with your order?        │  💒 Event Type       │
│              │                               │  🔥 Friction Score   │
│ ○ Rahul K.   │  System: Assigned to agent   │  📱 Channel          │
│   ₹55,000    │  System: Resolved             │  ✅ Status           │
│              │                               │                      │
│              │  [Reply via Freshchat]        │  [Actions]           │
└──────────────┴───────────────────────────────┴──────────────────────┘
```

### Features

| Panel | Content |
|-------|----------|
| **Left Panel** | List of all incidences with user, cart value, event type, friction score, status |
| **Center Panel** | Full timeline of the selected incidence (system events, agent messages, user messages) |
| **Right Panel** | Rich customer context card with all metadata |
| **Actions** | Mark as Converted, Resolved, or Dropped |

### Header Stats

| Metric | Description |
|--------|-------------|
| Active | Count of IN_PROGRESS tickets |
| Resolved Today | Count of closed tickets |
| Avg Time | Average resolution time |

### Auto-Refresh

The incidences list auto-refreshes every 30 seconds to show new tickets.

### Reply via Freshchat

Clicking "Reply via Freshchat" opens the Freshchat inbox where agents can respond to customer messages in real-time.

---

## Analytics Dashboard

### Available at: `http://localhost:8000/analytics`

### KPI Cards

| Metric | Description |
|--------|-------------|
| Total Incidences | Count of all support tickets |
| Resolution Rate | % of resolved tickets |
| Avg Resolution Time | Time to resolve in minutes |
| Conversion Rate | % of tickets that converted to orders |
| Self-Serve Rate | % of orders without support |
| Avg Friction Score | Average friction across users |

### Charts

1. **Daily Incidences & Resolutions** - Line chart showing trends
2. **Channel Distribution** - Doughnut chart (Self-Serve / Chat / Call)
3. **Outcomes Distribution** - Bar chart (Converted / Resolved / Abandoned)

---

## Configuration

### Environment Variables (`.env`)

```ini
# Database (Docker PostgreSQL on port 5433)
DATABASE_URL=postgresql+asyncpg://poc_user:poc_password@localhost:5433/support_system

# Redis
REDIS_URL=redis://localhost:6379/0

# Freshchat
FRESHCHAT_APP_ID=your_app_id
FRESHCHAT_APP_KEY=your_app_key
FRESHCHAT_WEBHOOK_SECRET=your_webhook_secret

# Application
DEBUG=true
```

### Routing Thresholds (`app/config.py`)

```python
THRESHOLD_LOW: float = 5000.0    # Below this: self-serve
THRESHOLD_HIGH: float = 25000.0  # Above this: premium support
FRICTION_THRESHOLD: float = 50.0 # Above this: show help
```

---

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Failed

**Symptom:** `password authentication failed for user "poc_user"`

**Cause:** Local PostgreSQL installation on port 5432 conflicting with Docker.

**Solution:** We use port **5433** for Docker PostgreSQL. Ensure `.env` has:
```
DATABASE_URL=postgresql+asyncpg://poc_user:poc_password@localhost:5433/support_system
```

#### 2. Freshchat Widget Not Loading

**Symptom:** Widget doesn't appear when opening `demo.html` directly.

**Cause:** File:// protocol doesn't support Freshchat.

**Solution:** Access via server: `http://localhost:8000/demo`

#### 3. Database Tables Not Created

**Symptom:** Relations don't exist errors.

**Solution:**
```bash
docker-compose down -v
docker-compose up -d
# Wait 5 seconds for init.sql to run
```

#### 4. ngrok Not Working

**Symptom:** `authtoken required` error.

**Solution:**
```bash
npx ngrok config add-authtoken YOUR_TOKEN
npx ngrok http 8000
```

---

## File Structure

```
poc/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── database.py            # PostgreSQL & Redis connections
│   ├── main.py                # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── incidence.py       # SQLAlchemy models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── analytics.py       # Analytics endpoints
│   │   ├── channel.py         # Channel routing endpoint
│   │   ├── context.py         # User context endpoint
│   │   ├── friction.py        # Friction detection endpoint
│   │   ├── incidences.py      # Incidence CRUD endpoints
│   │   └── webhooks.py        # Freshchat webhook handler
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analytics.py       # Pydantic schemas
│   │   ├── channel.py
│   │   ├── context.py
│   │   └── incidence.py
│   └── services/
│       ├── __init__.py
│       ├── analytics_service.py
│       ├── channel_router.py
│       ├── friction_service.py
│       └── incidence_service.py
├── agent.html                 # Agent console dashboard
├── analytics.html             # Analytics dashboard
├── demo.html                  # Demo UI (customer simulation)
├── docker-compose.yml         # PostgreSQL & Redis
├── init.sql                   # Database schema
├── requirements.txt           # Python dependencies
├── DOCUMENTATION.md           # This documentation file
├── .env                       # Environment variables
└── .env.example               # Environment template
```

---

## Testing Summary

### Tested Components

| Component | Test | Result |
|-----------|------|--------|
| Channel Router | ₹30K Wedding → Chat+Call | ✅ Pass |
| Channel Router | ₹3K Casual → Self-serve | ✅ Pass |
| Friction Detection | First-time + Checkout → 30pts | ✅ Pass |
| Demo UI | Full user simulation | ✅ Pass |
| Freshchat Widget | Opens real chat | ✅ Pass |
| Webhooks | Receives message_create | ✅ Pass |
| Analytics Dashboard | KPIs and charts display | ✅ Pass |
| Incidence Create | POST creates record | ✅ Pass |
| Incidence Get | GET retrieves record | ✅ Pass |
| Incidence Update | PATCH assigns agent | ✅ Pass |
| Incidence Timeline | POST adds events | ✅ Pass |
| Incidence Close | POST closes with outcome | ✅ Pass |
| Agent Console | Displays tickets with context | ✅ Pass |
| Agent Console | Actions (resolve/convert/drop) | ✅ Pass |

---

## Next Steps for Production

1. **Authentication** - Add JWT/OAuth authentication
2. **Rate Limiting** - Protect APIs from abuse
3. **Logging** - Structured logging with ELK stack
4. **Monitoring** - Prometheus + Grafana
5. **CI/CD** - Automated deployment pipeline
6. **Database Migrations** - Use Alembic
7. **Unit Tests** - Add pytest coverage
8. **Load Testing** - Verify performance under load

---

## Support

For issues or questions, contact the development team.

**Last Updated:** January 16, 2026
