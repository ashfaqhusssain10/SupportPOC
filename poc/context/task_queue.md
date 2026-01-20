# Task Queue

**Status:** Active
**Owner:** Junior Agent / Team

## 🔴 High Priority (Immediate)

- [ ] **Verify Bidirectional Sync (Final)**
    - [ ] Run full end-to-end test: Chat -> Ticket -> Reply -> Widget.
    - [ ] Confirm `freshchat_conversation_id` is populating correctly in Freshdesk.

- [ ] **Enable Freshcaller (Telephony)**
    - [ ] Verify "Call Us" option appears in the widget.
    - [ ] Test a call flow (simulate if necessary).
    - [ ] Ensure call logs/tickets appear in Freshdesk (if applicable).

## 🟡 Medium Priority (Refinement)

- [ ] **Error Handling**
    - [ ] Add retry logic for Freshchat/Freshdesk API calls in `webhooks.py`.
    - [ ] Handle duplicate webhook events (idempotency).

- [ ] **Code Cleanup**
    - [ ] Remove commented-out "Native Integration" code from `webhooks.py` once custom flow is stable.
    - [ ] Standardize logging across all services.

## 🟢 Low Priority (Future)

- [ ] **Analytics Dashboard**
    - [ ] Build a view to show "Friction Score" trends over time.
    - [ ] Track "Chat to Order" conversion rates.

- [ ] **Production Deployment**
    - [ ] Replace Ngrok with stable domain (AWS/Heroku).
    - [ ] Set up production Database.
