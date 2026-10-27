---
id: DOT-87
title: Drop the `npm:@sentry/skillet` pin in `apps/mise/files/config.toml` to `latest`
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Drop the `npm:@sentry/skillet` pin in `apps/mise/files/config.toml` to
  `latest`.** The pin sat at 1.7.0 since 2026-09-11 because mise's npm resolver
  (aube) could not fetch vite's 39 MB packument through
  `sfw.security.sentry.io` — `curl` and `npm` both can, so it is a mise-side
  limit, not registry or auth. **Resolved 2026-09-14: 1.8.0 verified working
  here** (`skillet validate .` exits 0; 1.8.0 was already installed, and `mise
  install` pruned 1.7.0 — reinstall it via
  `mise install npm:@sentry/skillet@1.7.0` if ever needed), committed as
  ee09e38. What remains before the pin drops to `latest`: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, decide
  whether the four `npx @sentry/skillet@latest` task aliases stay floating
  (they align once the pin is `latest`), and `spec.md`'s 1.7.0 pin plus the
  `docs/REFERENCES.md` row need aligning — that alignment is queued there
  already. Done when the config says `latest`, the pin-print tells the truth,
  and the spec/REFERENCES rows agree with it. **Changelog-read blocker,
  recorded 2026-09-15:** the REFERENCES standard (read the 1.7.0→1.8.0
  changes before moving the pin) cannot currently be satisfied from this
  machine — the source repo is not accessible (the getsentry org is
  SAML-blocked; npm metadata carries no repository URL) — so the pin stands
  on local evidence only and the read must happen from a machine with
  access. **Read DONE 2026-09-15, on this Mac after all** — the block was
  the second machine's. The 1.7.0→1.8.0 compare (5 commits) shows grammar
  and exit codes untouched; the change is diagnostics (the no-eval-case
  warning was deleted) and the authoring workflow (evals opt-in). Pin
  aligned at 1.8.0 across `config.toml` and the spec footer (94389a5);
  REFERENCES records the read. What remains of this task: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, and the
  four `npx @sentry/skillet@latest` aliases need a float-vs-pin decision.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
