# Security policy

## Status and supported scope

ContextOS is a hackathon prototype. Only the current development branch is maintained; there are no supported production releases or service-level guarantees. Local policy tests do not establish production security certification.

## Reporting a vulnerability

Do not open a public issue containing credentials, restricted project data or exploit details. Once the GitHub repository exists, use **Security → Report a vulnerability** if private reporting has been enabled. Otherwise contact the repository owner through an existing private channel and ask for a reporting route before sending sensitive details.

Include the affected commit, minimal synthetic reproduction, expected/actual behavior and potential impact. Do not test against third-party deployments without authorization. No response-time or bounty commitment is implied.

## Deployment boundaries

- Demo mode deliberately allows switching synthetic personas. It must not hold confidential data.
- Firebase mode verifies bearer tokens and administrator-provisioned workspace/role claims. Its current browser token-entry bridge is for development, not a complete sign-in flow.
- Models have no publication or permission-management authority.
- Per-workspace quotas are not global abuse/cost controls. Public access requires separate operational decisions and safeguards.
- Firestore and live model integrations require deployment verification before use with real data.

## Secrets and data hygiene

Keep secrets in runtime configuration or an appropriate secret manager. Never commit `.env`, private keys, ADC files, service-account JSON, databases, logs containing personal data or workspace exports. `.env.example` contains only non-secret configuration guidance. `.gitignore` and the repository check reduce accidental inclusion but do not replace review or secret scanning. If a credential is exposed, revoke/rotate it; removing a file from the latest commit alone is insufficient.
