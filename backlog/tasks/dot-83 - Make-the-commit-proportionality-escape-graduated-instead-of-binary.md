---
id: DOT-83
title: Make the commit-proportionality escape graduated instead of binary
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Make the commit-proportionality escape graduated instead of binary.**
  `Proportionality:` currently short-circuits `verdict()` before the budget is
  computed, so it does not tolerate variance — it switches the check off for that
  commit, permanently and invisibly. The evidence that this is the wrong shape is
  the usage record: **one use in 449 commits, and that one was unnecessary** —
  193 words against a 220 budget on 10ccccd, added pre-emptively after the
  previous commit was rejected. An escape easier than thinking gets used without
  thinking. Three changes, in this order:
  (1) **Bound it.** A trailer grants a multiplier on the budget, not exemption —
  and a hard ceiling no trailer can exceed, so an essay still fails.
  (2) **Type it.** A small vocabulary — `security`, `deletion`, `migration` —
  each with its own multiplier, free text after the category. That makes the
  *why* greppable, which is what turns the escape into something auditable rather
  than a hole. An unrecognised category earns no bonus, so the choice is a known
  reason or a split.
  (3) **Close the loop.** Report at commit time when an escape was not needed
  ("this would have passed with 27 words to spare"). Nothing today can notice a
  false positive, which is exactly why the only one went unnoticed.
  Deliberately **not** doing diff-derived modifiers (test ratio, additions vs
  deletions) yet: they sound the most contextual and are the most likely to be
  wrong. A test-ratio bonus would have penalised this session's best commits,
  which were mostly tests, and it is trivially gamed. Add derived signals only if
  the audit from (2) shows a category is systematically mis-sized. Use the
  existing `--calibrate` mode to check any multiplier against history before
  adopting it — and heed the script's own warning that fitting to the corpus
  encodes the habit as the standard. Done when a message over budget with a typed
  reason passes within its multiplier, the same message without one fails, an
  essay fails either way, and an unnecessary escape is reported as such. [me]
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
