---
id: DOT-374
title: Find why roborev MCP lists no repo for the dotfiles checkout
status: To Do
created_date: 2026-11-17 20:46
labels:
- bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`roborev_list_repos` (MCP) returned no repositories for prefix /Users/ben.davis/.local/share/chezmoi on 2026-11-17, while the CLI `roborev repo list` shows `dotfiles` at that path. The review skills require MCP polling, so agents fall back to the CLI and sleep loops.

Ship:

- the root cause, reproduced with one MCP call and one CLI call
- a fix in local config, or an upstream issue draft for the author to approve

Constraints:

- upstream issues need author approval before filing
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The reproduction and root cause are recorded in the notes
- [ ] #2 roborev_list_repos returns the dotfiles repo, or an approved upstream issue is linked
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
