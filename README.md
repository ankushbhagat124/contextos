# ContextOS

**Define once. Share intelligently. Evolve together.**

A governed memory workspace for software teams: accepted decisions, role-specific tasks, reviewable changes, exact source manifests, and visible downstream impact.

## Start locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Each browser receives an isolated synthetic payment-project sandbox. Persona switching is a demo facility, not production authentication. Local data persists in `.data/contextos.db`. Offline responses are explicitly labeled deterministic rehearsal output; no Google AI call is claimed.

```sh
.venv/bin/python -m pytest -q
```

## Project map

- [Features](features.md), [requirements](requirements.md), [change log](context.md), [handoff](handoff.md)
- [Architecture](design/architecture.md), [hackathon alignment](hackathon.md)
- [Demo walkthrough](demo.md), [deployment](DEPLOYMENT.md), [verification](TESTING.md)
- Peer review: `gemini.md`; builder responses: [chatgpt.md](chatgpt.md)
- Original specification: `ContextOS_Complete_Project_Blueprint.md`
- Original event notes: `ai_builder_cup_challenges_and_themes.txt`

Cloud deployment, live model verification, public repository, pitch PDF, and video are separate submission gates. See the handoff for verified status.
