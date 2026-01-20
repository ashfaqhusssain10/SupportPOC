# App <> Sales Team (Support-Led Ordering System)

## Objective
Transition from a **sales-led ordering model** to a **product-led ordering system** where:
*   The **App is the primary interface**
*   The **Sales team functions as contextual support**
*   Human involvement exists only to **remove friction**, not to sell
## Core Philosophy
*   Sales ≠ Persuasion
*   Sales = **Decision Facilitation + Trust Resolution**
*   Humans exist **only when uncertainty crosses a threshold**
*   Long-term goal: **Reduce human dependency over time**
## Root Questions
### 1\. Why do users need human support?
Users require human help only when one or more of the following uncertainties exist:
*   Trust issues (food quality, reliability)
*   High cognitive load (too many choices)
*   Ambiguity (quantity, portions, taste)
*   Risk perception (large or important events)
*   Low app familiarity or language barriers
If none of the above exist → **no human support required**
### 2\. When do users need human support?
#### Pre-Order Scenarios
*   Unclear guest count
*   Menu suitability confusion
*   Taste/spice anxiety
*   Budget vs expectation mismatch
*   High-importance events (weddings, corporate, religious)
#### Post-Order Scenarios
*   Confirmation anxiety
*   Customisation or modification requests
*   Delivery timing reassurance
*   Issue escalation
**Human support must not exist outside these moments**
### 3\. How do users reach human support?
*   Never “Call Sales”
*   Always positioned as **“Get Help” / “Talk to an Expert”**
Triggered via:
*   User-initiated tap
*   System-detected hesitation -?
*   Abandonment signals -?
*   Repeated navigation loops-?
## App vs Human Role Definition
### App is the Face
*   Menu discovery
*   Package browsing
*   Pricing visibility
*   Standard ordering
*   Payments
*   Order confirmation
### Human is the Backbone
*   Resolves uncertainty
*   Mirrors app logic
*   Helps user finish what they started
*   Never leads the journey
*   Help them in decision making.
## Customer Flow (Golden Path)
1. User opens app
2. Explores menus/packages
3. Either:
    *   Completes order independently
    *   Gets stuck → contextual human help surfaces
4. Order is completed with or without assistance
**User perception:**
“I’m getting help to complete my order”
Not: “I’m talking to sales”
## Sales / Support Team Operating Rules
*   Do not pitch
*   Do not upsell
*   Do not override app logic
Support team must:--?
*   See exact app screen user is on
*   See user inputs and selections
*   Continue from app state, not restart
**Tone guidelines**
*   Calm
*   Non-pushy
*   Decision-validating
*   Informational, not persuasive
## Required System (Pre & Post Order)
### Incidence-Based Model (Replaces Leads)
Every interaction = **Incidence**
#### Incidence Attributes
*   User ID
*   Order ID (if exists)
*   Stage: Pre-Order / Post-Order
*   Channel: Chat / Call / WhatsApp
*   Trigger: User-initiated / System-initiated
*   Outcome: Resolved / Dropped / Converted
### Channel Rules
*   In-app chat → Primary
*   Click-to-call → Secondary
*   WhatsApp → Only if user exits app
All channels must map to the **same incidence**
### Incidence Summary (Mandatory)
Auto-generated for every incidence:
*   Problem category
*   Root cause
*   Resolution type
*   Time to resolve
*   Order impact (Placed / Modified / Lost)
This data feeds:
*   Product improvements
*   Cost analysis
*   Investor reporting
## App Touch Points Connected to Humans
Human support can surface only at defined choke points:
*   Guest count selection
*   Menu comparison
*   Customisation screen
*   Price jump moments
*   Checkout inactivity
*   Payment failure
*   Order confirmation screen
Each touch point must answer:
> “What fear or uncertainty exists here?”
## Assumptions (Validated)
### Known Friction Reasons
*   Trust concerns
*   Quantity confusion
*   Taste uncertainty
*   Option overload
*   Low app literacy
### Additional Hidden Reasons
*   Fear of ordering wrong food
*   Social judgment (event guests)
*   Past bad catering experiences
*   Language barriers
*   Time pressure
## Sales Team Exists for Data (Explicit)
Support interactions must generate insights on:
*   Where users hesitate
*   Which menus convert without help
*   Which events require human support
*   Time spent per incidence
*   Cost per assisted order
Goal: **Design humans out of the system over time**
## Success Metrics
### Primary
*   % orders placed without human help
*   % orders placed with help
*   Conversion uplift due to assistance
### Secondary
*   Time to resolve incidence
*   Cost per assisted order
*   Repeat friction reasons
### Long-Term
*   Reduction in human dependency
*   Increased self-serve conversion
*   System learning velocity
## Anti-Goals (Non-Negotiable)
*   Humans must not become permanent crutches
*   Human help should not replace poor UX
*   Support volume ≠ success metric
## Cost Boundaries (To Be Enforced)
Example thresholds:
*   < ₹5k order → No human support
*   ₹5k–₹25k → Chat only
*   ₹25k → Call allowed
(Exact limits to be finalised)
## Feedback Loop (Mandatory)
*   Top incidence reasons reviewed weekly
*   Top 10 recurring issues → Product fixes
*   No unresolved repetition allowed
No feedback loop = **system failure**
## Final Outcome
*   App drives ordering
*   Humans remove friction
*   Every interaction improves the system
*   Investor confidence through data clarity
*   Scalable, defensible, product-led growth model