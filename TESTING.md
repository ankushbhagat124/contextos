# Verification record

Verified locally on 14 October 2026 (IST), Python 3.14.6.

## Automated

```sh
.venv/bin/python -m pytest -q
node --check web/app.js
.venv/bin/python scripts/rehearsal.py
```

25 tests pass covering:

- Document visibility and filtering of restricted proposals, events, outputs and retrieval.
- Owner authorization, independent review, content hashes and duplicate decisions.
- Immutable history and rollback through a new reviewed revision.
- Stale-base rejection and actual concurrent SQLite publication (one winner).
- SQLite persistence, workspace isolation and rollback on storage-limit failure.
- Mandatory context retention, explicit budget overflow, exact serialized manifests.
- Transitive change impact and a revision changing during model inference.
- Firebase identity claims, denied demo-role switching, cross-workspace denial (verification SDK mocked).
- Gemini prompt/schema contract, reported usage and malformed output (provider mocked).
- Known token usage preserved when downstream validation fails; visible provider errors.
- HTTP validation, same-origin write checks, rate limits, assets and security headers.

Two upstream deprecation warnings remain: Starlette's httpx compatibility and google-genai's Python union alias. They do not fail the suite. No warning suppression is configured.

## Browser checks

Tested the running application using the Codex in-app browser at mobile width (~358 px) and desktop width (1440 px):

1. Overview loads real workspace counts and navigation.
2. Developer runs a payment task; inspector shows source bodies and v1 architecture.
3. Developer proposes a retry-limit change without publishing.
4. Architect reviews before/after text and publishes v2.
5. Previous run shows “Needs review”; rerun inspector shows architecture v2.
6. Stakeholder note becomes a pending candidate; Product Manager independently publishes it.
7. Insights shows dependency links, audit events, actual zero offline model usage, and disclosed estimates.
8. No browser console errors observed during this workflow.

Screenshot: `artifacts/contextos-desktop.jpg` (synthetic demo state, not a live-AI claim).

## Unverified / intentionally deferred

- Live Gemini, real Firebase credentials, Firestore transactions and multi-instance behavior.
- Linux container build (Docker unavailable locally).
- Cloud deployment, public access and load/abuse testing.
- Broad assistive-technology audit and multi-browser compatibility.
- Retrieval-quality and end-to-end productivity/cost benchmarks.

User explicitly deferred cloud setup until local review, and GitHub setup until later. These remain open gates, not completed work.
