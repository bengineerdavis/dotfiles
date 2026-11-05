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
The aqua lychee 0.24.2 binary needs GLIBC 2.38+ and dies on this Debian 12 machine (GLIBC 2.35), so every pre-commit docs-links-local run fails at the hook — caught 2026-11-01 while committing the docker/limactl permission change, and again 2026-11-02/04 blocking a ROADMAP.md prose fix. The failure is machine-level and pre-existing: the identical error reproduces on the unmodified ROADMAP.md in a pristine checkout, and both installed aqua builds (`0.24/` and `0.24.2/`) fail the same way.

The cargo build of the same version works. Re-verified 2026-11-04:

- `mise exec cargo:lycheeverse/lychee -- lychee --version` → `lychee 0.24.2`, rc=0
- `mise exec cargo:lycheeverse/lychee -- which lychee` → `.../installs/cargo-lycheeverse-lychee/latest/bin/lychee` (a real cargo-backend install, not a fall-through to aqua)
- the cargo backend runs the blocked file clean: `lychee --offline --files-from -` on `ROADMAP.md` → `0 Errors`, rc=0

The switch:

- `scripts/check-docs-links.py` probes backends in order — `cargo:lycheeverse/lychee` first, then `aqua:lycheeverse/lychee` — and runs the first that executes. The probe is a cheap `--version`; it must fall through ONLY on failure-to-execute, never on link findings, or a broken link would silently pass.
- If no backend executes, exit non-zero with the reason. The hook must fail loudly rather than skip (this is the load-bearing property: a check that declines looks identical to a check that passed).
- mise config prefers the cargo entry; the aqua entry stays as the fallback the Mac uses, so `docs/LINK-CHECKING.md` stops naming aqua as *the* backend and records the glibc trap.
- Why the VM tests never saw it: the Debian 12 Lima/genericcloud image ships GLIBC 2.36, newer than this machine's 2.35, so the aqua binary executes there. The failure only surfaces on the real host that runs the hooks.

Dependency: needs a guaranteed `cargo`, which is DOT-282's job (rustup owns the toolchain; mise syncs to it). Verified on this machine already — `mise exec rust -- cargo --version` → `cargo 1.99.0` — so the work is testable here today, but the fresh-box story is DOT-282's.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The pre-commit docs-links-local hook passes on this Debian 12 machine
- [ ] #2 A host with a newer glibc (the Mac) still resolves a working lychee through the aqua fallback
- [ ] #3 The backend preference and the glibc trap are recorded in docs/LINK-CHECKING.md
- [ ] #4 A host where no lychee backend executes exits non-zero with the reason, rather than skipping
- [ ] #5 A backend that executes and finds a broken link still fails — fall-through happens only on failure-to-execute
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Re-scoped 2026-11-04 (author ruling): rustup owns the Rust toolchain and mise
syncs to it, so DOT-282 is a real prerequisite rather than a duplicate channel.

Corrected an earlier misreading in this session: mise and rustup are NOT two
competing cargo channels. `mise registry` shows `rust core:rust`, and that
backend already drives rustup — `readlink ~/.local/share/mise/installs/rust/1.99.0`
resolves to `~/.cargo/bin`, and `mise exec rust -- printenv RUSTUP_HOME` reports
`~/.rustup`. One channel, one toolchain store.

Cargo lychee re-verified working on the blocked file 2026-11-04:
`mise exec cargo:lycheeverse/lychee -- lychee --offline --files-from -` on
`ROADMAP.md` → `0 Errors`, rc=0.

The hook failure is pre-existing and machine-level: the same GLIBC error
reproduces on the unmodified ROADMAP.md in a pristine main checkout, and both
aqua builds (`0.24/`, `0.24.2/`) fail identically.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
