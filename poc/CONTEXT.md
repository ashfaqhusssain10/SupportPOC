# Support System Integration - Context & Walkthrough

## Project Overview
**Goal:** Integrate customer support tools (Freshchat/Freshdesk) with the Catering App to give agents real-time visibility into user behavior (Cart Value, Friction Score, Order Stage).

---

## Journey Summary

### Phase 1: Freshchat Widget Integration (Partially Working)
- Embedded Freshchat widget in `demo.html`
- Configured webhook to receive `message_create` events
- **Issue:** Bidirectional messaging failed due to:
  - Data Center mismatch (US vs India API URLs)
  - Multiple server instances causing webhook confusion
  - Browser cookie blocking in admin UI

### Phase 2: Freshdesk Sidebar App (Abandoned)
- Attempted to create a sidebar widget using iframe approach
- **Issue:** Freshdesk Admin UI blocked by Chrome third-party cookie settings
- FDK (Freshworks Developer Kit) approach required too much setup

### Phase 3: Freshdesk Custom Fields (SUCCESS ✅)
- Push incidence data directly INTO Freshdesk ticket fields via API
- No sidebar app needed - data appears natively in Freshdesk
- **Result:** Ticket #4 created with all custom fields populated

---

## Files Created/Modified

### New Services
| File | Purpose |
|------|---------|
| `app/services/freshchat_service.py` | Send messages TO Freshchat widget |
| `app/services/freshdesk_ticket_service.py` | Create/Update Freshdesk tickets with custom fields |

### New Routers
| File | Endpoints |
|------|-----------|
| `app/routers/messages.py` | `POST /api/v1/messages/send` |
| `app/routers/call.py` | `POST /api/v1/call/request`, `GET /api/v1/call/pending` |
| `app/routers/freshdesk.py` | `GET /freshdesk/sidebar` (HTML widget) |
| `app/routers/freshdesk_sync.py` | `POST /api/v1/freshdesk/sync`, `POST /api/v1/freshdesk/sync-all` |

### Modified Files
| File | Changes |
|------|---------|
| `app/config.py` | Added `FRESHCHAT_API_URL`, `FRESHDESK_DOMAIN`, `FRESHDESK_API_KEY` |
| `app/routers/webhooks.py` | Enhanced logging, incidence linking strategies |
| `app/main.py` | Registered all new routers |
| `demo.html` | Added floating call button, `requestCallFromChat()` function |
| `agent.html` | Fixed timezone parsing, added Freshchat message sending |

---

## Environment Variables (.env)
```
DATABASE_URL=postgresql+asyncpg://poc_user:poc_password@localhost:5433/support_system
REDIS_URL=redis://localhost:6379/0
FRESHCHAT_APP_ID=your_app_id
FRESHCHAT_APP_KEY=<JWT Token>
FRESHCHAT_WEBHOOK_SECRET=your_webhook_secret
FRESHDESK_DOMAIN=test2288
FRESHDESK_API_KEY=ilZzuny3l4EXd7PFf3K3
DEBUG=true
```

---

## Freshdesk Custom Fields (Created in Admin)
| Field Label | API Name | Type |
|-------------|----------|------|
| Friction Score | `cf_friction_score` | Number |
| Cart Value | `cf_cart_value` | Number |
| Guest Count | `cf_guest_count` | Number |
| Order Stage | `cf_order_stage` | Text |

---

## API Usage Examples

### Sync an Incidence to Freshdesk
```bash
curl -X POST http://localhost:8000/api/v1/freshdesk/sync \
  -H "Content-Type: application/json" \
  -d '{"incidence_id": "uuid-here"}'
```

### Bulk Sync All Active Incidences
```bash
curl -X POST http://localhost:8000/api/v1/freshdesk/sync-all
```

---

## Key Learnings
1. **Freshchat Data Centers matter** - Use `api.in.freshchat.com` for India accounts
2. **Browser privacy blocks iframe content** - Third-party cookie settings can break admin UIs
3. **Custom Fields > Sidebar Apps** - Native fields are simpler and more reliable
4. **Freshdesk expects integers** - Number fields must receive `int`, not `float`

---

## Next Steps (Optional Enhancements)
- [ ] Auto-sync on incidence creation (add to webhook handler)
- [ ] Two-way sync: Update local incidence when Freshdesk ticket changes
- [ ] Add more custom fields (Event Type, Occasion, etc.)
