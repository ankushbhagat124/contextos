# Deployment and live integration

## Current verification boundary

The application runs locally with SQLite and explicit offline rehearsal. Gemini, Firebase, and Firestore adapters exist but require live project configuration and verification. No cloud deployment or live Google AI result is claimed. GitHub setup is deferred by the user.

## Local configuration

Python 3.14 is used for development and the container. Install `requirements.txt`. Configure environment variables explicitly in your shell (the app does not auto-load `.env`). `.env.example` documents options and contains no secrets.

```sh
export AUTH_MODE=demo
export AI_MODE=offline
export STORE_BACKEND=sqlite
.venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

For live Vertex AI, authenticate with Application Default Credentials through your normal Google Cloud flow and configure:

```sh
export AI_MODE=vertex
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=global
export GEMINI_MODEL=gemini-2.5-flash
```

Model name is configurable; verify availability and access in your selected project before recording. The model default is a starting configuration, not a guarantee of regional availability. Alternatively `AI_MODE=gemini` accepts a server-only `GEMINI_API_KEY` from Google AI Studio. Never paste secrets into source or review files.

## Google Cloud Run

Prerequisites: a user-selected billing-enabled Google Cloud project, Firestore Native mode database, Artifact Registry/Cloud Build, Cloud Run, and Vertex AI APIs. Runtime service account needs Vertex AI User and Firestore data access (`roles/aiplatform.user` and `roles/datastore.user`). Grant only to the dedicated service account. No service-account key file is required on Cloud Run; use its attached identity.

The Dockerfile listens on `$PORT` and runs as a non-root user. Cloud Run startup refuses SQLite because its filesystem is ephemeral. Configure:

```text
AUTH_MODE=demo
AI_MODE=vertex
STORE_BACKEND=firestore
GOOGLE_CLOUD_PROJECT=<selected project>
GOOGLE_CLOUD_LOCATION=global
GEMINI_MODEL=<verified model>
```

Example deployment after the project, service account and exposure policy are chosen:

```sh
gcloud run deploy contextos \
  --source . \
  --project YOUR_PROJECT_ID \
  --region asia-south1 \
  --service-account contextos-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars AUTH_MODE=demo,AI_MODE=vertex,STORE_BACKEND=firestore,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,GOOGLE_CLOUD_LOCATION=global,GEMINI_MODEL=gemini-2.5-flash \
  --memory 512Mi --cpu 1 --max-instances 2 --timeout 120 \
  --no-allow-unauthenticated
```

This example starts private. Decide explicitly how judges will access the deployment. A public synthetic demo exposes live-model usage to visitors; per-workspace call limits are not a global cost-control mechanism and creating new sessions can bypass them. Before public launch add an access gate or service-level quota/budget controls, and confirm the audience. Do not put real confidential data into demo mode.

Firestore stores each bounded workspace as one transactionally updated document, capped at 750 KB, with 30 contexts and 50 model calls. It preserves revisions/audits rather than silently evicting them. This suits the small demo; larger adoption requires collection-level decomposition and archival. Browser-session workspaces persist until explicitly cleaned up by an operator; configure retention before public operation.

## Firebase authentication mode

Set `AUTH_MODE=firebase` and provision accounts with administrator-set custom claims:

```json
{"contextos_workspace":"team-checkout","contextos_role":"developer"}
```

Allowed roles: `pm`, `architect`, `developer`, `qa`, `security`. Members sharing the same workspace claim share the accepted project state. Verify signed ID tokens server-side with revocation checks. All mutation authority uses verified claims, never client-selected personas. Role switching is denied in this mode.

The current UI offers a development token-entry bridge held in memory; a normal Firebase sign-in/refresh flow is not yet implemented. Do not describe this as a polished production authentication experience. Claims are administrator-provisioned, not editable by users.

## Deployment acceptance checks

- [ ] Container builds on Linux and runs as non-root.
- [ ] `/api/health` reports intended AI/auth modes.
- [ ] Live extraction and task calls succeed; real usage recorded.
- [ ] Two app instances see the same Firestore revisions.
- [ ] Concurrent stale proposals fail without overwriting accepted state.
- [ ] Restricted data is absent from sources, tasks, activity, export and metrics for unprivileged roles.
- [ ] A new revision flags dependent runs, while original manifests remain intact.
- [ ] Restart/redeployment retains knowledge and audit history.
- [ ] Public/private judge access, abuse limits and retention are explicitly configured.
- [ ] Prototype remains available during evaluation.

References: [Google Gen AI SDK](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview), [Cloud Run](https://cloud.google.com/run/docs), [Firestore](https://firebase.google.com/docs/firestore). Confirm current deployment prerequisites against official documentation when configuring the project.
