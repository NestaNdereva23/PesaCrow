
# Dispute Resolution System: Implementation Plan

This document outlines the features and implementation steps required to build a comprehensive, three-phase dispute resolution system for PesaCrow.

---

## Phase 1: Direct Negotiation (User-to-User)

This phase focuses on providing a structured environment for the client and developer to resolve issues on their own.

### Existing Features:

*   **[✓] Dispute Initiation:** Users can already raise a dispute against a deliverable (`raise_dispute` view).
*   **[✓] Dispute Listing:** Users can view their own disputes (`disputes_list` view).
*   **[✓] Time-boxing:** The `Dispute` model has an `escalation_deadline` field, which sets a 48-hour window for resolution.
*   **[✓] Manual Escalation:** Users can manually escalate a dispute before the deadline (`escalate_dispute_manually` view).
*   **[✓] Mutual Resolution:** Users can mark a dispute as resolved by agreement (`resolve_dispute` view).

### Needed Features & Enhancements:

*   **[✓] Structured Communication Channel:**
    *   **Feature:** Create a dedicated view for an individual dispute where both parties can communicate.
    *   **Implementation:**
        *   Create a new `DisputeMessage` model with a `ForeignKey` to `Dispute`, `User`, and a `TextField` for the message content.
        *   Create a `dispute_detail` view that displays the dispute information and a chronological list of messages.
        *   Add a form to this view to allow users to post new messages.
    *   **File Locations:**
        *   **Model:** `disputes/models.py`
        *   **View:** `disputes/views.py`
        *   **Template:** `disputes/templates/disputes/dispute_detail.html`
        *   **URL:** `disputes/urls.py`

---

## Phase 2: Admin-Led Mediation

This phase begins when a dispute is escalated to an administrator. The focus is on evidence gathering and facilitated negotiation.

### Needed Features:

*   **[ ] Admin Dispute Dashboard:**
    *   **Feature:** A centralized place for administrators to view and manage all escalated disputes.
    *   **Implementation:**
        *   Create an `admin_disputes` view that lists all disputes with a status of `escalated`.
        *   The view should display key information: project title, parties involved, date of escalation, and a link to the dispute details.
    *   **File Locations:**
        *   **View:** `home/views.py` (as it's part of the admin dashboard)
        *   **Template:** `home/templates/home/admin_disputes.html`
        *   **URL:** `home/urls.py`

*   **[ ] Evidence Locker:**
    *   **Feature:** A system for both parties and the admin to upload and review evidence related to the dispute.
    *   **Implementation:**
        *   Create an `Evidence` model with a `ForeignKey` to `Dispute`, `User` (the uploader), a `FileField` for the evidence file, and a `TextField` for a description.
        *   Modify the `dispute_detail` view (from Phase 1) to include a section for uploading and listing evidence. This section should be visible to both parties and the admin.
    *   **File Locations:**
        *   **Model:** `disputes/models.py`
        *   **View:** `disputes/views.py` (modify `dispute_detail`)
        *   **Template:** `disputes/templates/disputes/dispute_detail.html` (add evidence section)

*   **[ ] Admin Mediation Tools:**
    *   **Feature:** Allow the admin to communicate with both parties within the dispute thread.
    *   **Implementation:**
        *   The admin should be able to post messages in the `dispute_detail` view, just like the other users.
        *   Admin messages should be visually distinct (e.g., different background color) to stand out.

---

## Phase 3: Binding Arbitration

This is the final phase where the administrator makes a binding decision.

### Needed Features:

*   **[ ] Admin Ruling Interface:**
    *   **Feature:** A form for the administrator to issue a final ruling on the dispute.
    *   **Implementation:**
        *   In the `dispute_detail` view, create a section that is only visible to administrators.
        *   This section will contain a form where the admin can:
            1.  Select a final decision (`client_favored`, `developer_favored`, `mutual_agreement`).
            2.  Write a detailed justification for the decision.
        *   Submitting this form will update the dispute's `status` to `resolved_by_admin` and `decision` field, and trigger the appropriate fund release.
    *   **File Locations:**
        *   **View:** `disputes/views.py` (modify `dispute_detail` or create a new `resolve_by_admin` view)
        *   **Template:** `disputes/templates/disputes/dispute_detail.html` (add admin-only ruling section)

*   **[ ] Automated Fund Release:**
    *   **Feature:** The system should automatically release the escrowed funds based on the admin's decision.
    *   **Implementation:**
        *   This will likely involve calling a service function from the `payment` app.
        *   The logic will be:
            *   If `client_favored`, refund the milestone amount to the client.
            *   If `developer_favored`, release the milestone amount to the developer.
            *   If `mutual_agreement` (or a future "partial" option), the implementation will depend on the specific agreement.
    *   **File Location:** This logic will be triggered in the view that handles the admin's ruling (`disputes/views.py`).

---
