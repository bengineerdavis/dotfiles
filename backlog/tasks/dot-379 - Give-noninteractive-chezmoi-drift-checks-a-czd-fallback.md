---
id: DOT-379
title: Give noninteractive chezmoi drift checks a czd fallback
status: To Do
created_date: 2026-11-18 06:38
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AGENTS.md directs agents to use czd, but its absence leaves no documented noninteractive fallback for a machine that has not deployed it.

Ship:

- Document a read-only chezmoi built-in-diff fallback and how to pass absolute target paths.
- Keep the czd exit-status contract distinct from chezmoi diff, which exits zero even with drift.

Constraints:

- Keep czd as the preferred command where deployed.
- Do not change the deployed czd script or run chezmoi apply.
- Verify command forms against the installed CLI help.

Agreed with the maintainer 2026-11-18: fix repository guidance and leave the external retro skill unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The guidance gives a built-in-diff command and absolute target-path example that needs no czd deployment.
- [ ] #2 The guidance states that callers needing an exit status use czd when available.
- [ ] #3 The fallback commands are verified against installed CLI help.
- [ ] #4 skillet validate . exits 0 with no errors.
- [ ] #5 uv run --frozen pytest tests/docs -q passes.
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
