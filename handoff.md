# Handoff

## User intent

Build ContextOS feature by feature into a strong hackathon prototype/MVP, commit stages locally, and continuously maintain context.md, features.md, requirements.md, handoff.md and design/architecture.md. Author: Faizan Choudhary <choudharyfaizan15@gmail.com>. User explicitly deferred GitHub setup. Do not push or invent a remote.

## Read order

README.md → this file → features.md → context.md → design/architecture.md → hackathon.md. Consult the original blueprint for the broader vision.

## Current stage

Documentation, governed domain and API/model adapters implemented. Fourteen local tests pass; UI is next. No cloud project or credentials supplied. Dependencies are installed and locked in requirements.txt. Local commits exist; no remote configured.

## Build order

1. Persistence and access policy.
2. Reviewed immutable publication and history.
3. Bounded retrieval with manifests.
4. Gemini extraction and persona tasks.
5. Change propagation and usage.
6. Five-view UI, regression tests, deployment instructions.
7. Configure Google Cloud, verify live AI and durable deployment.
8. Public repo and submission artifacts, following user direction.

## Decisions

Local synthetic sandbox is explicitly distinct from authenticated production. Never describe deterministic rehearsal as Gemini. No fabricated metrics or promised competition result. Keep changes scoped to this repository. Update this file and log before ending each work session.

## Peer-review protocol

User expects feedback from gemini.md (created by another tool/person) to be evaluated and applicable fixes implemented without straying from the blueprint. Write dispositions and evidence to chatgpt.md. Do not overwrite gemini.md. First check: not present. Core domain test run: 8 passing.
