# Platform Comparison Summary
## Support-Led Ordering System - Chat Platform Selection

---

## Quick Comparison Matrix

| Feature | Tawk.to | Freshchat | Intercom |
|---------|---------|-----------|----------|
| **Monthly Cost (5 agents)** | **₹0 (free)** | ~₹8,000 | ~₹43,800 |
| **Native Mobile SDK** | ❌ WebView | ✅ Full SDK | ✅ Full SDK |
| **REST API** | ⚠️ By request | ✅ Full | ✅ Full |
| **Webhooks** | ✅ | ✅ | ✅ |
| **Custom Attributes** | ✅ | ✅ | ✅ |
| **Agent Custom Actions** | ❌ | ⚠️ Limited | ✅ Full |
| **Push Notifications** | ⚠️ Limited | ✅ | ✅ |
| **WhatsApp Integration** | ✅ | ✅ | ✅ |
| **Branding Removal** | ₹2,400/mo | Included | Included |

---

## Detailed Cost Breakdown

### Total Monthly Cost (5 Agents + Backend)

| Platform | Platform Cost | Backend Infra | Total |
|----------|---------------|---------------|-------|
| **Tawk.to** | ₹0-2,400 | ₹8,500-18,500 | **₹8,500-21,000** |
| **Freshchat** | ₹8,000 | ₹8,500-18,500 | **₹16,500-26,500** |
| **Intercom** | ₹43,800 | ₹8,500-18,500 | **₹52,300-62,300** |

---

## Technical Capability Comparison

### SDK & Integration Depth

| Capability | Tawk.to | Freshchat | Intercom |
|------------|---------|-----------|----------|
| **iOS Native SDK** | ❌ | ✅ iOS 14+ | ✅ iOS 13+ |
| **Android Native SDK** | ❌ | ✅ Android 6+ | ✅ API 21+ |
| **React Native SDK** | ❌ | ✅ Official | ✅ Official |
| **Flutter SDK** | ❌ | ⚠️ Community | ✅ Official |
| **Real-time Context Update** | ✅ JS API | ✅ SDK Methods | ✅ SDK Methods |
| **Event Tracking** | ⚠️ Basic | ⚠️ Basic | ✅ Advanced |

### Webhook Events

| Event | Tawk.to | Freshchat | Intercom |
|-------|---------|-----------|----------|
| Chat Started | ✅ | ✅ | ✅ |
| Message Sent | ✅ | ✅ | ✅ |
| Chat Ended | ✅ | ✅ | ✅ |
| Agent Assigned | ❌ | ✅ | ✅ |
| Transcript | ✅ | ✅ | ✅ |
| Custom Events | ❌ | ⚠️ | ✅ |

---

## Fit for Your Requirements

### Requirement Matching

| Your Requirement | Tawk.to | Freshchat | Intercom |
|------------------|---------|-----------|----------|
| **Pass user context to agents** | ✅ via setAttributes | ✅ via SDK | ✅ via SDK + Custom Objects |
| **See current app screen** | ✅ | ✅ | ✅ |
| **Incidence logging** | ✅ via webhooks | ✅ via webhooks | ✅ via webhooks |
| **Cost boundary rules** | ✅ in your backend | ✅ in your backend | ✅ in your backend |
| **Friction detection triggers** | ✅ in your backend | ✅ in your backend | ✅ in your backend |
| **Channel routing (chat/call)** | ⚠️ Manual | ✅ Routing rules | ✅ Routing + Workflows |
| **Agent action guardrails** | ❌ Build yourself | ⚠️ Limited | ✅ Custom Actions |
| **Weekly analytics reports** | ✅ Build yourself | ✅ Built-in + Custom | ✅ Built-in + Custom |

---

## Recommendation by Stage

### Stage 1: MVP/POC (0-3 months)
**Recommended: Tawk.to**

| Aspect | Details |
|--------|---------|
| **Why** | Zero cost, validate Incidence model |
| **Risk** | WebView UX slightly less native |
| **Cost** | ~₹8,500-18,500/mo (backend only) |
| **Effort** | Medium (WebView integration) |

### Stage 2: Growth (3-12 months)
**Recommended: Freshchat Growth**

| Aspect | Details |
|--------|---------|
| **Why** | Best value, native SDK, solid APIs |
| **Risk** | Limited custom actions |
| **Cost** | ~₹16,500-26,500/mo |
| **Effort** | Low (SDK straightforward) |

### Stage 3: Scale (12+ months)
**Recommended: Intercom Advanced**

| Aspect | Details |
|--------|---------|
| **Why** | Premium UX, full customization, custom actions |
| **Risk** | High cost |
| **Cost** | ~₹52,300-62,300/mo |
| **Effort** | Medium (more features to configure) |

---

## Recommended Backend Tech Stack

Common across all platforms:

| Layer | Technology | Why |
|-------|------------|-----|
| **API** | FastAPI (Python) or Express (Node.js) | Fast development, good async |
| **Database** | PostgreSQL | Relational for incidences |
| **Cache** | Redis | Real-time context storage |
| **Queue** | BullMQ or SQS | Async webhook processing |
| **Hosting** | AWS / GCP / Railway | Your preference |
| **Mobile** | React Native | Cross-platform + SDK support |

---

## Migration Path

```
┌────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   TAWK.TO      │────►│   FRESHCHAT     │────►│    INTERCOM      │
│   (MVP)        │     │   (Growth)      │     │    (Scale)       │
└────────────────┘     └─────────────────┘     └──────────────────┘
       │                       │                        │
       ▼                       ▼                        ▼
  Your Backend ─────────────────────────────────────────┘
  (Stays same)

Key: Backend logic is platform-agnostic. Only change:
- SDK integration in mobile app
- Webhook endpoints (minor changes)
```

---

## Decision Framework

### Choose Tawk.to if:
- [ ] Budget is primary constraint
- [ ] Building MVP to validate concept
- [ ] Web-first application
- [ ] Okay with WebView-based chat

### Choose Freshchat if:
- [ ] Need native mobile SDK
- [ ] Want balance of cost vs features
- [ ] 5-20 agents
- [ ] Part of Freshworks ecosystem

### Choose Intercom if:
- [ ] Premium UX is critical
- [ ] Need advanced custom actions
- [ ] Have budget (>₹50k/mo for platform)
- [ ] Want best-in-class agent tools

---

## Implementation Timeline Estimate

| Phase | Tawk.to | Freshchat | Intercom |
|-------|---------|-----------|----------|
| SDK Integration | 3-5 days | 2-3 days | 2-3 days |
| Context Passing | 2-3 days | 2 days | 2 days |
| Webhook Handler | 3-4 days | 3-4 days | 3-4 days |
| Incidence Service | 5-7 days | 5-7 days | 5-7 days |
| Analytics Dashboard | 3-5 days | 3-5 days | 3-5 days |
| Testing & Polish | 3-5 days | 3-5 days | 3-5 days |
| **Total** | **19-29 days** | **18-26 days** | **18-26 days** |

---

## Documents Created

| Document | Description |
|----------|-------------|
| [Tech_Stack_Freshchat.md](./Tech_Stack_Freshchat.md) | Full Freshchat implementation guide |
| [Tech_Stack_Intercom.md](./Tech_Stack_Intercom.md) | Full Intercom implementation guide |
| [Tech_Stack_Tawkto.md](./Tech_Stack_Tawkto.md) | Full Tawk.to implementation guide |
| [Backend_Requirements.md](./Backend_Requirements.md) | Backend modules specification |

---

## Next Steps

1. **Choose platform** based on current stage and budget
2. **Set up backend** infrastructure (PostgreSQL, Redis, API server)
3. **Integrate SDK** following platform-specific guide
4. **Implement Incidence Service** as first backend module
5. **Configure webhooks** to capture all events
6. **Build analytics dashboard** for weekly reviews
