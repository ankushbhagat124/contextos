# Contributing to ContextOS

## Scope

Keep contributions aligned with shared, permission-aware, governed project memory. Read requirements.md and design/architecture.md first. Distinguish implemented behavior from planned features, and offline rehearsal from live AI.

## Local workflow

1. Use Python 3.14 and the virtual environment described in README.md.
2. Create a focused branch (the default naming convention is `codex/<short-description>`).
3. Make a small, reviewable change. Do not include runtime databases, environment files, credentials, personal data, or unrelated generated artifacts.
4. Run the relevant tests plus `node --check web/app.js` for JavaScript changes. Run `python scripts/check_repo.py` with the virtualenv interpreter before committing.
5. Update context.md with what changed, why, validation and limitations. Update features.md and requirements.md when behavior/scope changes; keep handoff.md current. Record architecture changes in design/architecture.md.
6. Open a PR once the repository exists on GitHub. Explain the problem, resulting behavior, verification and any remaining limits.

Do not make legal, financial, deployment or public-access decisions on behalf of the project owner. Cloud setup and GitHub publication currently await the owner's local review.

## Invariants to preserve

- Authorization is enforced in application code, not by model instructions.
- Model output can propose; it cannot grant permissions or publish protected knowledge.
- Accepted revisions and source manifests retain their original contents.
- Review is independent and bound to the exact proposed content and base revision.
- Restricted knowledge must remain restricted in retrieval, outputs, activity, exports and telemetry.
- Mandatory context cannot be silently omitted to meet a budget.
- Demo results are computed using real rules on synthetic data; never fabricate success or usage metrics.

Add meaningful regression tests for policy, persistence and model-contract changes. Avoid tests that merely restate implementation details.

## Peer review files

Gemini owns gemini.md. Builder responses belong in chatgpt.md. Read incoming feedback, assess it against product intent and record accepted/deferred/declined findings with evidence. Do not overwrite the other reviewer's file.

## Dependencies and style

Python uses four-space indentation; frontend code uses two spaces. Follow surrounding conventions. Keep requirements.txt reproducible; review dependency updates before merging and rerun the offline suite. The UI intentionally has no npm build toolchain. Use safe text rendering for user/model content and preserve keyboard navigation and mobile behavior.
