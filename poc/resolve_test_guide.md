# 🕵️ How to Validate Native Integration (The "Resolve" Test)

Since your settings are configured to **"Create ticket upon resolution"**, we need to resolve a chat to prove the connection works.

### Step 1: In the Freshchat Dashboard
1.  Go to your **Freshworks CRM/Freshchat Dashboard**.
    *   URL usually looks like: `https://<your-domain>.myfreshworks.com/crm/sales`
2.  Click on the **Chat / Inbox icon** (left sidebar).
3.  Find the **"Testing Native Sync"** conversation you started earlier.
4.  Open it. (You should see your "testing" message).
5.  Look for a **"Resolve"** button (check-mark icon or "Close" button, usually top-right).
6.  **Click Resolve**.

### Step 2: In Freshdesk
1.  Go to **Freshdesk Tickets** (`https://test2288.freshdesk.com/a/tickets`).
2.  Refresh the list.
3.  **Wait ~30 seconds**.
4.  Do you see a new ticket?
    *   **Subject** might be the message text or "Chat with [Name]".
    *   **Source** should show as "Chat".

### Step 3: Analyze Results

| Result | Conclusion |
| :--- | :--- |
| **✅ Ticket Appears** | The integration is **WORKING**. It's just set to "Late Creation" (on resolve). <br> *Next Step: We can change settings to create tickets earlier if you want real-time reply sync.* |
| **❌ No Ticket** | The integration is **BROKEN**. <br> *Next Step: We need to re-check the "Marketplace & Integrations" setup in Freshchat.* |
