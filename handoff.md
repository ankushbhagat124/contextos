# Handoff — ContextOS local prototype

Last updated: 14 October 2026, Asia/Kolkata.

## User direction

Build ContextOS feature by feature from the two supplied documents, commit stages locally, and maintain context.md, features.md, requirements.md, handoff.md and design/architecture.md. Git author: **Faizan Choudhary <choudharyfaizan15@gmail.com>**.

**User explicitly deferred Google Cloud setup until the local solution looks good. GitHub setup is also deferred. Do not deploy, push, or repeatedly request cloud credentials before that local review.**

## Review protocol

Gemini writes gemini.md; we write chatgpt.md. Check gemini.md after implementation and verification milestones. Evaluate comments against the original ContextOS idea; apply useful fixes, explain deferred/declined comments. Never overwrite gemini.md. Latest read: Round 3 reviewing 30f5de0; all material comments addressed and responses recorded. A later edit may arrive independently.

## Read order

README.md → this file → features.md → context.md → design/architecture.md → hackathon.md → chatgpt.md and latest gemini.md. The blueprint contains the broader roadmap. The referenced SHARED_AGENT_CONTEXT_PLATFORM.md was not present; the two supplied files are preserved.

## Implemented

- FastAPI modular backend with SQLite local persistence and bounded Firestore adapter.
- Isolated synthetic browser sandbox, five personas, protected context and filtered derived views.
- Immutable accepted revisions, proposals, owner/independent review, content hashes, stale-base conflicts, rollback-as-new-revision and audit events.
- Permission-first lexical retrieval, dependency closure, mandatory constraints, explicit byte-based context budget and exact payload manifests.
- Role-specific tasks and note ingestion; Google Gen AI SDK adapters for Vertex and API-key Gemini.
- Explicit offline deterministic rehearsal, failed-call records, known usage preservation and quotas.
- Transitive stale-run detection and explicit rerun with current sources.
- Responsive five-view UI, review comparison, source inspector, search/filter, histories and JSON evidence export.
- Dockerfile, env template, local rehearsal helpers, deployment and demo guides.

## Run and verify

```sh
.venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8000
.venv/bin/python -m pytest -q
node --check web/app.js
.venv/bin/python scripts/rehearsal.py
```

Open http://127.0.0.1:8000. Dependencies are installed in .venv and frozen in requirements.txt. A preview server may still be running; check before starting another. Browser demo data lives in ignored `.data/contextos.db`. Preserve it. A private browser window creates a fresh sandbox without destroying older ones.

## Verified evidence

25 local tests pass (domain, API, concurrent SQLite mutation, mocked Firebase/Gemini). Browser checked at mobile and desktop widths: task → v1 sources → proposal → independent review → v2 → stale prior run → rerun with v2. Also checked note ingestion and PM publication, Insights, and console logs. Screenshot in artifacts/contextos-desktop.jpg. Full details: TESTING.md.

## Important limits

- Currently offline, no live model call verified. Do not describe rehearsal as Gemini reasoning.
- Firebase backend claims checks are tested with mocks; UI currently has only a development token bridge, not a production login flow.
- Firestore adapter is unverified against a live project. One aggregate document per workspace, 750 KB cap; 30 contexts and 50 model calls. Scale-out storage redesign is future work.
- Token estimates are UTF-8 bytes, not model tokenization. Context budget excludes instruction/task/output overhead. Actual provider totals are separate; no savings benchmark has been run.
- No semantic search, automatic dedup/merge, normal task-chat threading, arbitrary policy management, project-creation UI, MCP or repository integrations.
- Docker unavailable locally; container build and Cloud Run deployment unverified.
- Synthetic demo role switching is deliberate impersonation, not production security.

## Next steps after user's local review

1. Address local UX feedback and any new Gemini review notes.
2. Once user requests cloud setup, select their project, verify live Gemini and Firestore, configure access/abuse controls, build/deploy and test durability.
3. Implement normal Firebase sign-in if needed for real multi-user use.
4. Configure GitHub only when user resumes that work; no remote exists now.
5. Prepare pitch using required template, record compliant video and validate submission gates in hackathon.md.

## Git checkpoints

- f15abd4 — plan, source documents and judging alignment.
- eed4fea — governed revisions, persistence and retrieval.
- 30f5de0 — persona API and model adapters.
- 710d28d — interactive UI and deployment kit.
- Latest hardening checkpoint: see `git log -1`; its hash is intentionally not self-embedded.

## Latest review checkpoint — Round 4

Round 4 reviewed and dispositions appended to chatgpt.md. Fixed direct pytest invocation, focus-preserving/IME-aware search, safe backdrop dismissal and favicon. Added manual topic proposals (no model call), still requiring independent owner review. Browser sandbox now also includes a pending Quality proposal “Retry latency acceptance checks” authored by PM. 25 tests pass with `.venv/bin/pytest -q`. Python 3.14 remains the runtime; review's prerelease claim was corrected with an official source. Cloud/GitHub deferral unchanged.
