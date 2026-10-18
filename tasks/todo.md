# Person 3 task backlog

Proposed tasks; select provider-specific files/contracts after module-map review. Acceptance criteria are in PERSON3_DELIVERY.md.

- [x] P3-S00: Review module map and choose persistence/auth stack. Verify: owner decision recorded.
- [x] P3-S01: Specify provider config + identity/session contracts. Verify: trusted membership and logout/expiry cases enumerated; no client role authority.
- [ ] P3-S02: Implement login/logout vertical slice. Verify: mock rejection suite + provider test-account browser flow (P3-01/02).
- [ ] P3-S03: Add selected store contract tests and fail-closed configuration. Verify: transaction rollback and one-winner concurrency (P3-03).
- [ ] P3-S04: Integrate/provision staging store. Verify: redeploy, two-instance visibility, separate-workspace restore; no real data migration without a plan.
- [ ] P3-S05: Finish context/editor and review recovery UX. Verify: draft preservation and owner CTA scope (P3-04/06).
- [ ] P3-S06: Add dedicated relationship screen with accessible list. Verify: restricted-node and keyboard fixtures (P3-05).
- [ ] P3-S07: Agree and implement conversation turn API/storage. Verify: per-turn manifests, idempotent retry and restricted-history filtering (P3-07).
- [ ] P3-S08: Build task chat UI and per-turn inspector. Verify: reopen/follow-up/stale refresh, pending/error/retry browser flow.
- [ ] P3-S09: Separate activity view/filters. Verify: actor/outcome/date filtering and export privacy (P3-08).
- [ ] P3-S10: Add readiness and redacted request telemetry. Verify: injected outages and credential/body redaction (P3-10).
- [ ] P3-S11: Configure staging CI deployment + secret references. Verify: immutable artifact, federation trust and revision rollback (P3-09).
- [ ] P3-S12: Configure probe/alerts/global abuse limits. Verify: test alert received; budget policy and audience recorded.
- [ ] P3-S13: Capture live multi-persona release evidence. Verify: full P3-11 flow and measured browser/device conditions.

Split each implementation task into changes of roughly five source files or fewer, plus required project logs. Test and commit each working slice. A provider-specific task list replaces this proposal only after map review; no tests are skipped to meet a deadline.
