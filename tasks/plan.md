# Person 3 delivery sequence — proposed

Source: [capability map and acceptance backlog](../PERSON3_DELIVERY.md).
Status: owner selected Firebase Auth + Firestore + Cloud Run. Session backend/UI implemented locally; live auth, persistence and infrastructure verification pending target project.

1. Confirm module map and persistence choice. Draft provider-specific identity and store contracts.
2. Ship real login/session/logout as one verified slice, retaining offline demo access as a separate mode.
3. Provision/integrate the selected managed store in staging; prove durability, role isolation and publication concurrency.
4. Complete context/review recovery flows and a permission-filtered relationship view.
5. Add persisted task conversation contracts/UI and per-turn inspection.
6. Add dedicated activity filters and operational health/logging.
7. Configure CI staging promotion, secret references, monitoring and rollback for selected project.
8. Run signed-in multi-persona evidence flow, accessibility/responsive checks and fresh-browser judge access.

P0 launch path may ship before P1 relationship visualization and full task chat if deadline requires, but omitted capabilities stay visibly open. Do not claim all Person 3 responsibilities are complete merely because existing demo pages exist.
