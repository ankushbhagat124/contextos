# ContextOS change log

Append an entry in every implementation commit: change, reason, verification, limitations. Git is the exact file-level history; this is the human-readable decision log. Dates use Asia/Kolkata.

## 2026-10-14 — F01: project foundation

- Read both supplied source documents and existing ignore configuration. No application code or commits existed. The blueprint references SHARED_AGENT_CONTEXT_PLATFORM.md, which is not present.
- Selected the payment-retry cross-role workflow and Challenge 5.
- Added README, requirements, feature ledger, architecture, hackathon checklist and handoff.
- Chose FastAPI plus a buildless web UI to reduce build/deployment complexity. SQLite is the local store; Firestore adapter is the cloud path. Gemini via Google Gen AI SDK.
- Local Git author explicitly requested: Faizan Choudhary <choudharyfaizan15@gmail.com>. Remote GitHub setup deferred at user's request.
- Verified official themes page for broad mandates and scoring; portal-specific constraints remain sourced from supplied notes.
- No implementation or cloud readiness claimed at this stage.

## 2026-10-14 — F02–F04: governed memory core

- Added synthetic checkout contexts and personas; restricted findings are filtered before retrieval and from proposal/activity views.
- Added immutable reviewed publication with independent owner checks, content hashes, stale-base conflicts, new-revision rollback semantics and attributable audit events.
- Added atomic SQLite and bounded Firestore workspace stores; Cloud Run refuses ephemeral SQLite.
- Added deterministic mandatory-context retrieval, lexical ranking, dependency closure, exact serialized manifests and explicit budget overflow.
- Added core regression tests for permissions, review, concurrency, persistence, isolation, rollback and change impact.
- Deliberate limits: 30 contexts and 750 KB per transactional workspace; a byte-based estimate, not actual tokenization; Firestore needs live verification.
- Validation: 8 domain tests passed. Dependency versions captured in requirements.txt.
- User added a peer-review workflow: read forthcoming gemini.md and write reasoned responses to chatgpt.md while preserving the original product scope. File not present at first check.

## 2026-10-14 — F05–F06: API and model workflows

- Added validated FastAPI routes, opaque demo sessions, server-stored personas and Firebase-verified API identity mode.
- Added Gemini/Vertex SDK adapter for structured extraction and grounded persona tasks. Offline mode is an explicit deterministic rehearsal; live failures do not fall back silently.
- Added persistent usage reservations, failed-call accounting, workspace rate limits, exact task manifests, stale-during-inference detection, and filtered export.
- Added same-origin write checks, response security headers and request bounds.
- Fixed an integration-test finding: new demo sessions now persist even when their first API operation returns an error.
- Validation: 14 domain/API tests passing. Two upstream dependency deprecation warnings; live Google services untested without configuration.
