---
id: DOT-281
title: Switch lychee to cargo as primary with aqua fallback
status: To Do
created_date: 2026-11-03 03:17
labels:
- now
priority: high
dependencies:
- DOT-282
updated_date: 2026-11-03 03:17
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The aqua lychee 0.24.2 binary needs GLIBC 2.38+ and dies on this Debian 12 machine (GLIBC 2.35), so every pre-commit docs-links-local run fails at the hook — caught 2026-11-01 while committing the docker/limactl permission change. The cargo build of the same version works (mise exec cargo:lychee -- lychee --version verified rc=0, measured 2026-11-01). Switch: scripts/check-docs-links.py tries cargo:lycheeverse/lychee first and falls back to aqua:lycheeverse/lychee (the Mac keeps working either way), mise config prefers the cargo entry, docs/LINK-CHECKING.md stops naming aqua as the install backend and records the glibc trap. Why the VM tests never saw it: the Debian 12 Lima/genericcloud image ships GLIBC 2.36, newer than this machine's 2.35, so the aqua binary executes there — the failure only surfaces on the real host that runs the hooks. The hook must fail loudly when NO backend executes, never silently skip. Rust prerequisite: cargo backends need a working Rust toolchain (rust 1.94-1.99 present via mise on this machine); no rust/rustup topic exists as of 2026-11-01 — the author confirmed rust needs a topic that installs rustup (which includes cargo); lychee then requires rustup for the cargo installer. That rustup topic is this task's prerequisite — scope it as its own task and make this one depend on it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The pre-commit docs-links-local hook passes on this Debian 12 machine
- [ ] #2 A host with a newer glibc (the Mac) still resolves a working lychee
- [ ] #3 The backend preference and the glibc trap are recorded in docs/LINK-CHECKING.md
- [ ] #4 A host where no lychee backend executes fails loudly rather than skipping
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
