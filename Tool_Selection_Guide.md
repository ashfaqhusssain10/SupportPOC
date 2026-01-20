# Chat Platform Selection Guide
## Support-Led Ordering System

**Purpose**: This document helps you decide which chat platform to use based on your specific requirements, constraints, and growth stage.

---

## Step 1: Answer These Questions

Mark each that applies to your current situation:

### Budget Constraints
- [ ] **A1**: Budget is tight, need to minimize cost → +Tawk.to
- [ ] **A2**: Can invest ₹15-30k/month → +Freshchat
- [ ] **A3**: Premium experience worth ₹50k+/month → +Intercom

### Current Stage
- [ ] **B1**: Building MVP / validating concept → +Tawk.to
- [ ] **B2**: Have product-market fit, growing team → +Freshchat
- [ ] **B3**: Scaling, 10+ support agents → +Intercom

### Mobile App Priority
- [ ] **C1**: Web-first, mobile is secondary → +Tawk.to
- [ ] **C2**: Mobile is important, need good SDK → +Freshchat, +Intercom
- [ ] **C3**: Mobile is primary, need premium UX → +Intercom

### Engineering Capacity
- [ ] **D1**: Small team, want simple integration → +Tawk.to, +Freshchat
- [ ] **D2**: Medium team, can build custom features → +Freshchat
- [ ] **D3**: Large team, want extensibility → +Intercom

### Timeline
- [ ] **E1**: Need to launch in <2 weeks → +Tawk.to
- [ ] **E2**: Have 1-2 months for integration → +Freshchat
- [ ] **E3**: Can invest time for premium setup → +Intercom

---

## Step 2: Score Your Answers

Count how many times each platform was selected:

| Platform | Your Count | Recommended If |
|----------|------------|----------------|
| **Tawk.to** | ___ | 3+ selections |
| **Freshchat** | ___ | 2+ selections |
| **Intercom** | ___ | 2+ selections |

**Your Recommended Platform**: ________________________

---

## Step 3: Platform Decision Matrix

### Choose TAWK.TO If:

| Criteria | Check |
|----------|-------|
| Monthly platform budget < ₹5,000 | ☐ |
| Building MVP to validate concept | ☐ |
| Web app is primary focus | ☐ |
| Team size < 3 engineers | ☐ |
| Can accept WebView-based mobile chat | ☐ |

**Total Cost**: ~₹8,500-21,000/month (mostly backend infra)

**Key Trade-offs**:
- ❌ No native mobile SDK (uses WebView)
- ❌ REST API requires approval
- ❌ Less customizable agent experience
- ✅ Zero platform cost
- ✅ Unlimited agents

---

### Choose FRESHCHAT If:

| Criteria | Check |
|----------|-------|
| Monthly platform budget ₹8,000-15,000 | ☐ |
| Need native iOS/Android SDK | ☐ |
| 3-15 support agents | ☐ |
| Want balance of features vs cost | ☐ |
| Already using Freshworks products | ☐ |

**Total Cost**: ~₹16,500-26,500/month

**Key Trade-offs**:
- ❌ Limited custom agent actions
- ❌ Bot sessions charged separately
- ✅ Full native SDKs
- ✅ Good webhook support
- ✅ Solid documentation

---

### Choose INTERCOM If:

| Criteria | Check |
|----------|-------|
| Monthly platform budget ₹40,000+ | ☐ |
| Premium user experience is priority | ☐ |
| 10+ support agents | ☐ |
| Need custom agent actions | ☐ |
| Want advanced event tracking | ☐ |

**Total Cost**: ~₹52,300-62,300/month

**Key Trade-offs**:
- ❌ Higher cost
- ❌ Complex pricing with add-ons
- ✅ Best-in-class UX
- ✅ Custom actions for agents
- ✅ Advanced analytics

---

## Step 4: Feature Requirements Checklist

Check which features are **MUST HAVE** for your system:

| Feature | Must Have? | Tawk.to | Freshchat | Intercom |
|---------|------------|---------|-----------|----------|
| Pass user context to agents | ☐ | ✅ | ✅ | ✅ |
| See user's current screen | ☐ | ✅ | ✅ | ✅ |
| Webhook for incidence logging | ☐ | ✅ | ✅ | ✅ |
| Native iOS SDK | ☐ | ❌ | ✅ | ✅ |
| Native Android SDK | ☐ | ❌ | ✅ | ✅ |
| React Native SDK | ☐ | ❌ | ✅ | ✅ |
| WhatsApp integration | ☐ | ✅ | ✅ | ✅ |
| Custom agent actions | ☐ | ❌ | ⚠️ | ✅ |
| Push notifications | ☐ | ⚠️ | ✅ | ✅ |
| No branding | ☐ | 💰 | ✅ | ✅ |
| Built-in analytics | ☐ | ⚠️ | ✅ | ✅ |

**If any ❌ is marked as "Must Have"**, that platform is disqualified.

---

## Step 5: Cost Calculator

Fill in your numbers:

| Item | Your Value |
|------|------------|
| Number of support agents | ___ agents |
| Expected monthly chat volume | ___ chats |
| Backend hosting budget | ₹ ___/month |

### Platform Costs:

**Tawk.to**:
```
Platform:               ₹0
Remove branding:        ₹2,400/month (optional)
Backend infra:          ₹8,500-18,500/month
─────────────────────────────────────
TOTAL:                  ₹8,500 - ₹21,000/month
```

**Freshchat** (Growth plan):
```
Platform:               ₹1,600 × ___ agents = ₹______/month
Bot sessions (if used): ₹4,100 per 100 extra sessions
Backend infra:          ₹8,500-18,500/month
─────────────────────────────────────
TOTAL:                  ₹______ /month
```

**Intercom** (Advanced plan):
```
Platform:               ₹7,100 × ___ agents = ₹______/month
Mobile add-on:          ₹8,300/month
Backend infra:          ₹8,500-18,500/month
─────────────────────────────────────
TOTAL:                  ₹______ /month
```

---

## Step 6: Risk Assessment

| Risk | Tawk.to | Freshchat | Intercom |
|------|---------|-----------|----------|
| **Vendor lock-in** | Low | Medium | High |
| **Migration difficulty** | Easy | Medium | Hard |
| **Pricing changes** | Low risk (free) | Medium | High |
| **Feature deprecation** | Medium | Low | Low |
| **Platform stability** | Medium | High | High |

---

## Step 7: Final Recommendation

Based on your answers, I recommend:

### For MVP/Early Stage (You):
```
┌─────────────────────────────────────────────────┐
│  RECOMMENDED: Tawk.to                           │
│                                                 │
│  • Start free, validate your Incidence model   │
│  • Build backend logic (platform-agnostic)     │
│  • Migrate to Freshchat when you have PMF      │
│  • Timeline: Launch in 2-3 weeks               │
└─────────────────────────────────────────────────┘
```

### For Growth Stage:
```
┌─────────────────────────────────────────────────┐
│  RECOMMENDED: Freshchat Growth                  │
│                                                 │
│  • Native SDKs for better mobile experience    │
│  • ~₹1,600/agent/month                         │
│  • Good webhook & API support                  │
│  • Timeline: 3-4 weeks integration             │
└─────────────────────────────────────────────────┘
```

### For Scale Stage:
```
┌─────────────────────────────────────────────────┐
│  RECOMMENDED: Intercom Advanced                 │
│                                                 │
│  • Premium UX for high-value customers         │
│  • Custom actions for agent workflows          │
│  • Advanced analytics & event tracking         │
│  • Timeline: 4-6 weeks full integration        │
└─────────────────────────────────────────────────┘
```

---

## Step 8: Migration Strategy

Your backend remains **platform-agnostic**:

```
          Your Custom Backend
    ┌─────────────────────────────┐
    │  • Incidence Service        │
    │  • Context Manager          │
    │  • Channel Router           │
    │  • Analytics Service        │
    └─────────────┬───────────────┘
                  │
    ┌─────────────┴───────────────┐
    │     Webhook Adapter         │
    │  (only this changes)        │
    └─────────────┬───────────────┘
                  │
         ┌───────┼───────┐
         ▼       ▼       ▼
    Tawk.to  Freshchat  Intercom
     (MVP)   (Growth)   (Scale)
```

**What changes when migrating**:
1. SDK integration in mobile app
2. Webhook endpoint parsing
3. Context-passing method names

**What stays the same**:
1. All 10 backend modules
2. Database schema
3. Business logic
4. Analytics calculations

---

## Quick Decision Summary

| Your Situation | Choose This |
|----------------|-------------|
| Budget is primary constraint | **Tawk.to** |
| Need native mobile SDK | **Freshchat** |
| Premium UX is non-negotiable | **Intercom** |
| Building MVP/POC | **Tawk.to** |
| Have product-market fit | **Freshchat** |
| High-value customers (>₹50k orders) | **Intercom** |
| Using Freshworks already | **Freshchat** |
| Want best agent tools | **Intercom** |

---

## Related Documents

For detailed implementation after you choose:
- [Tech_Stack_Freshchat.md](./Tech_Stack_Freshchat.md)
- [Tech_Stack_Intercom.md](./Tech_Stack_Intercom.md)
- [Tech_Stack_Tawkto.md](./Tech_Stack_Tawkto.md)
- [Backend_Requirements.md](./Backend_Requirements.md)
