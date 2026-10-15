# GitHub readiness

The owner authorized pushing the local project to `silent-doom/contextos` on 15 October 2026. The configured origin is https://github.com/silent-doom/contextos.git. Git author is Faizan Choudhary <choudharyfaizan15@gmail.com>. Cloud setup remains deferred.

## Included

- README with local setup, screenshots, architecture, demo instructions and honest limitations.
- .gitignore, .dockerignore, .editorconfig and .gitattributes.
- Dependency lock, pytest discovery config, offline tests and repository hygiene check.
- Read-only GitHub Actions CI: Python tests, rehearsal, JavaScript syntax, repository checks and Docker build.
- Dependabot configuration for Python and GitHub Actions updates.
- Bug/feature issue forms, pull-request template, contribution and security guides.
- Feature/requirements ledger, change log, handoff, architecture, demo and deployment documentation.

## Owner decisions before publication

- [ ] Select a repository name, owner and visibility.
- [ ] Choose a license and add LICENSE; none has been assigned automatically.
- [ ] Review source, screenshots, review logs and complete Git history for intended public disclosure.
- [ ] Confirm the author email is the desired public Git identity (it was explicitly supplied for commits).
- [x] GitHub target selected and push authorized by the owner.

## Repository settings after publication

- [ ] Confirm CI passes on GitHub, including Linux dependency installation and image build.
- [ ] Enable private vulnerability reporting, Dependabot alerts and available secret-scanning/push-protection features.
- [ ] Configure branch protection/rulesets with pull-request review and the actual CI check names after the first run.
- [ ] Review repository Actions permissions; CI requests only contents:read and does not deploy or use cloud credentials.
- [ ] Choose maintainers and optionally add CODEOWNERS using real GitHub usernames; none are guessed here.
- [ ] Set the repository description and topics; add the deployed URL only after it exists and is verified.

Suggested description: “Governed shared context for software teams and AI agents, with reviewed revisions, exact source manifests and change-impact alerts.”

No green CI badge is shown before a real hosted run. Files in .github configure checks and templates; they do not enable repository security settings by themselves.
