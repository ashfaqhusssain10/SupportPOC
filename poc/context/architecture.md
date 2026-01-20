# System Architecture

**Status:** Draft
**Author:** Architect

## 1. High-Level Diagram

```mermaid
graph TD
    User[Customer (Browser/App)] -->|Chat/Call| FC[Freshchat Widget]
    FC -->|Webhook (message_create)| API[FastAPI Backend]
    
    subgraph "Backend Services"
        API --> WebhooksRouter[Webhooks Router]
        WebhooksRouter --> IncidenceService[Incidence Service]
        WebhooksRouter --> FDS[Freshdesk Service]
        WebhooksRouter --> FCS[Freshchat Service]
    end
    
    subgraph "Freshworks Ecosystem"
        FC -- Native (Disabled for Ticket) --> FD[Freshdesk]
        FDS -->|Create Ticket (API)| FD
        FD -->|Automation Webhook (Agent Reply)| API
        FCS -->|Send Message (API)| FC
    end
    
    subgraph "Database"
        IncidenceService --> DB[(PostgreSQL)]
        DB --> Tables[Incidences, Timeline, Analytics]
    end
```

## 2. Components

### 2.1 Backend (FastAPI)
*   **`main.py`**: Entry point.
*   **`routers/webhooks.py`**: Handles incoming events from Freshchat and Freshdesk.
*   **`services/freshchat_service.py`**: Wrapper for Freshchat V2 API.
*   **`services/freshdesk_ticket_service.py`**: Wrapper for Freshdesk V2 API.
*   **`models`**: SQLAlchemy models for `Incidence` (Internal record of support request).

### 2.2 Freshchat (Channels)
*   **API URL**: `https://api.in.freshchat.com/v2` (or Account Specific)
*   **Auth**: Bearer Token (JWS or API Key).

### 2.3 Freshdesk (Tickets)
*   **API URL**: `https://<domain>.freshdesk.com/api/v2`
*   **Auth**: Basic Auth (API Key).
*   **Automation**: "Ticket Update" rule triggers webhook on Agent Reply.

## 3. Data Flow

### 3.1 User Starts Chat
1.  User sends message in Widget.
2.  Freshchat sends `message_create` webhook to Backend.
3.  Backend (`webhooks.py`):
    *   Creates/Updates `Incidence` in DB.
    *   Calls `FreshchatService.get_user` to get email.
    *   Calls `FreshdeskTicketService.create_ticket` with `source=7` (Chat) and Custom Fields (Cart Value, Friction).
    *   **Result:** Ticket #123 created in Freshdesk immediately.

### 3.2 Agent Replies
1.  Agent sees Ticket #123 in Freshdesk (Source: Chat).
2.  Agent adds "Public Reply".
3.  Freshdesk Automation Rule fires because `Source == Chat` AND `Conversation ID != Empty`.
4.  Freshdesk causes Webhook POST to `/webhooks/freshdesk`.
5.  Backend:
    *   Receives payload (Message, Conversation ID).
    *   Calls `FreshchatService.send_message` (Actor: System/Bot).
6.  User sees reply in Widget.

## 4. Key Configuration
*   **Environment Variables**: `.env` (API Keys, Secrets).
*   **Database**: PostgreSQL (Store Incidences).
*   **Tunneling**: Ngrok (Exposes localhost to Freshworks Webhooks).
