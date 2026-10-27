---
id: DOT-114
title: Move the bootstrap into chezmoi — a minimal `curl | sh` fetches chezmoi, and
  chezmoi runs the rest
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Move the bootstrap into chezmoi — a minimal `curl | sh` fetches chezmoi,
  and chezmoi runs the rest.** Decision (author, 2026-09-28):
  `dotfiles/bootstrap/bootstrap.sh`'s install chain becomes chezmoi
  run-once / `.pre-apply` hooks so `chezmoi apply` drives Homebrew, uv, and
  the rest. The only step outside chezmoi is fetching the chezmoi binary
  itself. Done when a fresh machine starts from a minimal chezmoi install and
  chezmoi runs the full provision chain.
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
