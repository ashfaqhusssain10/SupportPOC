# 🤖 Agent Reply Setup Guide

Since we bypassed the native ticket creation (to make tickets redundant/fast), we need to manually tell Freshdesk to send replies back to the widget.

## 1. Get your Ngrok URL
Ensure `ngrok` is running. You need your public URL (e.g., `https://a1b2-106-200-xx-xx.ngrok-free.app`).
*   **Your URL:** `<YOUR_NGROK_URL>` (Replace this in steps below)

## 2. In Freshdesk Admin
1.  Go to **Admin** (Gear Icon) -> **Workflows** -> **Automations**.
2.  Select **"Ticket Updates"** tab.
3.  Click **"New Rule"**.

### Rule Config:
*   **Rule Name:** `Sync Agent Reply to Freshchat`
*   **When an action starts:** `Ticket is updated`
*   **Involved events:**
    *   `Note is added` -> `Public` (This covers Replies)
*   **On tickets with these properties:**
    *   `Source` is `Chat`
    *   **AND** `Freshchat Conversation ID` (Custom Field) is `Not Empty` (if available, otherwise skip)
*   **Perform these actions:**
    *   **Trigger Webhook**
    *   **Request Type:** `POST`
    *   **URL:** `<YOUR_NGROK_URL>/webhooks/freshdesk`
    *   **Encoding:** `JSON`
    *   **Content:** **Advanced** (Select custom payload)
    *   **Payload:**

```json
{
    "ticket_id": "{{ticket.id}}",
    "freshchat_conversation_id": "{{ticket.cf_freshchat_conversation_id}}",
    "action": "reply",
    "message": "{{ticket.latest_public_comment}}",
    "agent_name": "{{ticket.agent.name}}"
}
```

4.  Click **Preview and Save**.

## 3. Verification
1.  Reply to the Ticket #20 in Freshdesk.
2.  Check the Freshchat Widget.
3.  The message should appear!
