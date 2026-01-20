# Support-Led Ordering System (Omnichannel POC) - PRD

**Status:** In Progress
**Version:** 1.0 (Reflected from Conversation History)
**Authors:** PRD Agent, User

## 1. Executive Summary
The goal is to implement a **Support-Led Ordering System** that integrates **Freshworks Omnichannel Suite** (Freshchat, Freshdesk, Freshcaller) with a custom **FastAPI Backend**. The system enables support agents to assist customers in real-time, accessing rich customer context (cart value, friction scores) and managing tickets seamlessly so effectively that "Support becomes Sales".

## 2. Objectives
*   **Real-time Context:** Agents must see customer details (Cart Value, Friction Score, Screen) immediately when a chat starts.
*   **Immediate Ticket Creation:** Every chat conversation must generate a Freshdesk Ticket *instantly* (not upon resolution) to ensure no lead is lost.
*   **Bidirectional Sync:** 
    *   User Chat -> Freshdesk Ticket (Synced)
    *   Agent Reply (Freshdesk) -> User Chat Widget (Synced)
*   **Telephony:** Freshcaller integration for voice support within the same widget.

## 3. User Stories
### 3.1 Customer
*   As a customer, I want to chat with support from the mobile app/web.
*   As a customer, I want to see agent replies instantly without refreshing.
*   As a customer, I want to call support from the same widget.

### 3.2 Support Agent
*   As an agent, I want to see the customer's "Friction Score" and "Cart Value" in Freshdesk.
*   As an agent, I want to reply to tickets in Freshdesk and have them sent as chat messages.
*   As an agent, I want to know if a user is a "High Value" lead immediately with visual indicators (Priority).

## 4. Functional Requirements

### 4.1 Chat Integration (Freshchat)
*   **Widget:** Embed Freshchat widget in the frontend.
*   **Context Passing:** Custom User Properties (friction_score, cart_value) passed via `window.fcWidget.user.setProperties`.
*   **Webhook:** Receive `message_create` events to backend.

### 4.2 Ticket Management (Freshdesk)
*   **Creation:** Create a ticket immediately upon first user message.
*   **Source:** Must be marked as Source 7 (Chat).
*   **Linking:** Store `freshchat_conversation_id` in a Ticket Custom Field.
*   **Sync:** Agent replies in Freshdesk must trigger a webhook to send the message back to Freshchat.

### 4.3 Telephony (Freshcaller)
*   **Integration:** Enable Freshcaller within the Freshchat widget.
*   **Visibility:** "Call Us" icon visible to customer.

## 5. Non-Functional Requirements
*   **Latency:** Message sync should be near real-time (< 2 seconds).
*   **Reliability:** Webhooks must handle retries or failures gracefully.
*   **Security:** API Keys must be secured; Signatures should be verified for webhooks.

## 6. Constraints
*   **Native Limitation:** Native Freshchat-Freshdesk integration only creates tickets upon *resolution*. This is unacceptable for this use case.
*   **Workaround:** We must bypass native sync for ticket creation but rebuild the reply sync manually.
