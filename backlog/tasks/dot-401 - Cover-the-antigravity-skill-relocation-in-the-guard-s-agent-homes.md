---
id: DOT-401
title: Cover the antigravity skill relocation in the guard's agent homes
status: To Do
created_date: 2026-11-24 06:43
labels:
- bug
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
dotagents ships one target definition per agent runtime, each declaring where the runtime puts user-level skills. The guard keeps a hardcoded transcription of those relocation targets in `roles/guards/defaults/main.yaml` (`guard_agent_homes`), and `tests/guards/test_guard_wiring.py` compares the two so an upgrade cannot silently under-cover.

Measured 2026-11-23 on this machine: a dotagents target definition for Google Antigravity declares `userSkillsParentDirs: [join(homedir(), ".gemini", "config")]`. `guard_agent_homes` lists only `~/.claude` and `~/.copilot`, and `grep -c gemini` over the guard defaults returns 0. A skill directory colliding between dotagents and Antigravity is therefore waved through instead of failing closed.

Ship:

- `guard_agent_homes` in `roles/guards/defaults/main.yaml` covers `~/.gemini/config`.
- `KNOWN_RELOCATION_TARGETS` in `tests/guards/test_guard_wiring.py` maps the antigravity expression to a marker the guard defaults must contain.

Constraints:

- The two lists move together in one change; the test asserts the marker appears in the guard defaults, so editing only one side leaves the gate red.
- The test skips when no cached dotagents exists (an absent package is not evidence the list is right); the fix must not weaken that skip into a pass.
- Add only the observed target. Unsourced additions to a security-shaped allow-list are not an improvement.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 tests/guards/test_guard_wiring.py::test_guard_covers_every_agent_dotagents_relocates passes where it previously failed
- [ ] #2 guard_agent_homes contains a ~/.gemini/config entry
- [ ] #3 A mutation removing the Gemini entry from guard defaults makes the test fail
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
