---
id: DOT-305
title: Lore re-distillation corrupts .lore.md entries — verify rules survive every
  rewrite
status: To Do
created_date: 2026-11-07 22:16
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two consecutive roborev reviews of agent/retro-docs (jobs 463 and 479) failed on .lore.md defects that the Lore daemon's own re-distillation produced or aggravated. Measured 2026-11-07: (1) title/body swap — entry 01a18498 ('uv run without --frozen...') carried unrelated chezmoi -S content, deleting the uv safety rule; the 21:40 heal restored it but SWAPPED a second entry (389: 'Merge PR queue: stacked-PR stranding' now carries the inline-Python-batching body, and the stacked-PR procedure is nowhere in the file). (2) Deleted-correct-entry + false trap — the requires_map entry ('skip the removal when requires_map undefined') matches remove.yaml exactly (uninstall gated on index_available; debug explains the skip; docs/TOPICS.md:146-149 mandates it: 'Undefined means unproven, not unshared — skip the removal'), yet the heal deleted it and wrote a trap entry claiming it contradicted remove.yaml. The first review's 'aborts with an explicit error' reading was ALSO wrong — verified against remove.yaml:18-22,30-48. (3) Wrong pointer — codex entry (line 58) cites decision-2 while naming decision-4 (both files exist). Root cause: the daemon rewrites the file on its own schedule; a hand-fix or capture commit races the next rewrite, and each heal can mint new defects. Fix direction: this is upstream behavior — report to BYK/loreai (DOT-298 pattern). Until it settles, treat .lore.md commits as captures-only (never hand-edit content), re-verify load-bearing rules survive each rewrite, and keep reviews green on the non-.lore.md payload. Interim guard: the drift test pattern (tests/docs) applied to .lore.md known-rule text, e.g. grep the uv --frozen rule after each re-distillation.
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
