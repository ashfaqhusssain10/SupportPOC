# Technical Decisions & ADRs

**Status:** Active
**Author:** Senior Agent

## ADR-001: Bypassing Native Freshchat-Freshdesk Sync
*   **Context:** The native integration creates tickets only when a conversation is *resolved*. The client requires *immediate* ticket creation upon the first message to enable "Sales-like" follow-up.
*   **Decision:** Disable native ticket creation. Implement **Custom Ticket Creation** via Webhook.
*   **Consequence:** We lose the native "Reply" functionality. We must re-implement reply syncing using Freshdesk Automation Rules and a custom webhook endpoint.

## ADR-002: Freshchat API Authentication Source
*   **Context:** We encountered `400 Signed JWSs are not supported` errors using one key, and `404` errors using the generic API URL.
*   **Decision:**
    *   **URL:** Use the Account-Specific URL (`https://craftmyplate-....freshchat.com/v2`) found in "API Settings".
    *   **Key:** Use the JWS Token provided in the same settings.
    *   **Verification:** `test_freshchat.py` confirmed this combination works.

## ADR-003: Ticket Source Workaround
*   **Context:** Custom tickets created via API usually default to "Email" or "API" source.
*   **Decision:** Explicitly set `source=7` (Chat) in the `create_ticket` payload.
*   **Reasoning:** This makes the ticket look like a native chat ticket in the UI, enabling better agent experience (though it still requires the manual reply sync hook).

## ADR-004: Freshdesk Automation for Replies
*   **Context:** Freshdesk API does not support creating Automation Rules.
*   **Decision:** This step is **Manual Configuration**. The user must create a "Ticket Update" rule in Freshdesk Admin.
*   **Conditions:** `Source is Chat` AND `Freshchat Conversation ID is Not Empty` AND `Note is Public`.
