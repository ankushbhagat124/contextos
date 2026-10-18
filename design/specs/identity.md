# Identity contract — Firebase session slice

Selected by owner: Firebase Auth + Firestore + Cloud Run (18 October 2026). Implements P3-01/P3-02 first; deployment and provider verification are separate acceptance gates.

- First login method: administrator-provisioned email/password accounts through the documented Firebase Auth REST endpoint. No custom password database or public role selection. Google/OIDC login can be added later without changing the backend session contract.
- Browser sends password directly to identitytoolkit.googleapis.com, exchanges the returned ID token with FastAPI, then discards ID/refresh tokens. No token storage in localStorage/sessionStorage. Firebase public Web API key is allowlisted config, not a server secret.
- GET /api/auth/config: public mode/login readiness/allowlisted public key plus CSRF nonce; sets HttpOnly SameSite=Strict nonce cookie. No UID, membership, model keys or service credentials.
- POST /api/auth/session: {id_token}; requires existing same-origin client/origin checks plus a matching CSRF header and nonce cookie. Verify signature/revocation, auth_time within five minutes and trusted workspace/role claims. Set HttpOnly SameSite=Strict session cookie for eight hours; Secure for HTTPS/Cloud Run. No automatic extension. On expiry return to login; retain no protected screen.
- Firebase API requests accept the session cookie; existing verified Bearer ID tokens stay supported for API consumers. Explicit invalid Bearer never falls back to a valid cookie. Demo cookies never establish a Firebase identity.
- POST /api/auth/logout: same CSRF checks; log current-browser sign-out when possible, clear session and nonce cookies. Idempotent after expiry. Clears this browser's cookie, not other device sessions. Stolen cookies require administrative revocation; check_revoked runs per authenticated request.
- Bad/unprovisioned/revoked identities fail with generic 401/403, with no privilege inferred from form fields. No session cookie issued for recent-sign-in or membership failures.
- In Firebase mode hide persona switching; display sign-out. Clear dialogs, tasks, source buffers and drafts on logout, 401 and browser back/forward restoration. Local demo mode keeps its current experience.
- Session events use existing actor/role audit scope. Passwords, tokens and cookie values are never logged. No sessions are claimed live-verified until project configuration and real test accounts are available.

Verify with mocked provider contracts: sign-in/refresh/logout, missing CSRF, cross-origin, missing/revoked/expired cookie, stale auth_time, invalid membership, client role override, bearer precedence and secure cookie attributes. Browser QA: local demo regression, Firebase login screen/config missing state and protected-content reset. Real Firebase sign-in/revocation test remains an explicit live gate.

Sources: https://firebase.google.com/docs/auth/admin/manage-cookies and https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password
