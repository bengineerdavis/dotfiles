---
id: DOT-405
title: Record that mise resolves HOME from the passwd entry, so a fake HOME silently
  targets the real install
status: To Do
created_date: 2026-11-25 04:51
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A probe that fakes `HOME` to avoid touching real machine state does not
isolate mise. It resolves the home directory from the passwd entry, not the
environment.

Measured 2026-11-24: `env -i HOME=/tmp/fh mise config ls` still read
`/home/bdavis/.config/mise/config.toml`. `MISE_CONFIG_DIR`, `MISE_DATA_DIR`
and `MISE_GLOBAL_CONFIG_FILE` did not redirect it either. The consequence
was a `mise use -g` probe that installed 179 MB into the real data
directory while the session believed it was sandboxed.

`docs/PERMISSIONS.md` covers why real containment needs a sandbox, but
nothing states the narrower trap: an agent trying to be careful with mise
gets no warning and no failure, only real state changing.

Ship a short reference note — in the mise topic's README or
`docs/CROSS-PLATFORM.md`, whichever the existing doc structure favours —
stating:

- mise resolves the home directory via the passwd entry, so `HOME` and every
  `XDG_*` variable are ignored for config and data location.
- The safe isolations are a scratch project directory with its own
  `mise.toml`, or a container; a fake home is not one.
- An `os = [...]` scope survives `mise use` rewriting the entry (verified),
  which is the fact a probe is usually trying to establish.

Constraints:

- Documentation only; no code change.
- Cite the measured command, so the claim is checkable rather than
  remembered.
- Do not duplicate `docs/PERMISSIONS.md`; link to it for the sandbox
  argument and keep this note to the mise-specific trap.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A reference note states that mise resolves the home directory from the passwd entry, ignoring `HOME` and `XDG_*`
- [ ] #2 The note cites the measured command that demonstrates it
- [ ] #3 The note names the safe isolations — a scratch project with its own `mise.toml`, or a container — and says a fake home is not one
- [ ] #4 The note records that an `os = [...]` scope survives `mise use` rewriting the entry
- [ ] #5 The note links to `docs/PERMISSIONS.md` for the sandbox argument instead of restating it
- [ ] #6 The doc it lands in is reachable from AGENTS.md § Conventions, per `tests/docs/test_conventions_referenced.py`
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
