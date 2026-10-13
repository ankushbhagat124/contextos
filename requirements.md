# Requirements

Source of product intent: ContextOS_Complete_Project_Blueprint.md. Event constraints: original event notes and hackathon.md. The broader blueprint is a roadmap, not a claim of implemented scope.

| ID | MVP acceptance requirement | Verification |
|---|---|---|
| R01 | Persistent shared accepted knowledge with immutable revisions | store + API tests |
| R02 | Server-side document and workspace access checks, including derived views | negative access tests |
| R03 | Proposals do not change accepted context; designated reviewer publishes exact content | review tests |
| R04 | Stale-base and repeated publication detected; history preserved | concurrency/idempotency tests |
| R05 | Task retrieval uses only accepted permitted sources and all mandatory rules | retrieval tests |
| R06 | Explicit budget overflow rather than silently dropping mandatory context | budget tests |
| R07 | Every task stores exact source bodies, IDs and revisions actually supplied | manifest tests |
| R08 | Publishing a dependency marks affected tasks stale; rerun explicitly adopts latest sources | impact tests |
| R09 | Ingested notes create review candidates; model output cannot grant authority | ingestion tests |
| R10 | Gemini generates grounded persona output and extraction through server SDK | mocked contract + live cloud gate |
| R11 | Actual model usage is separate from estimated context sizes; no invented savings | telemetry tests |
| R12 | Responsive accessible overview, knowledge, tasks, reviews and insights | browser QA |
| R13 | Google Cloud deployment with durable storage and explicit authentication mode | deployment gate |
| R14 | Rollback proposes a historical body as a new revision | rollback test |
| R15 | Useful errors, input limits, no secrets in browser or Git | API tests + review |

## Boundaries

One workspace per demo browser; synthetic persona identities. Production API identities use verified Firebase tokens with administrator-provisioned workspace/role claims. No arbitrary persona selection outside demo mode. New context items require domain-owner review. The initial search is lexical with explicit dependency expansion, not semantic search. Token budgeting uses a disclosed byte-based upper-bound estimate and live provider usage when available. No claims of measured productivity gains.

## Deferred

Enterprise organizations and SSO, MCP, repository synchronization, embeddings, automatic splitting/merging, arbitrary policy administration, agent delegation, file uploads, distributed background workers, and end-to-end cost/quality benchmarking.
