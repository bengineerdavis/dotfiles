---
id: DOT-310
title: Guard the chezmoi source tree against molecule/controller scratch — .molecule
  artifacts break the scan
status: To Do
created_date: 2026-11-08 20:14
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-08 during DOT-73's final full-suite acceptance run: leftover molecule controller scratch at home/dotfiles/apps/lima/molecule/debian/.molecule/ (from the Nov 6-7 lima VM testing, run from inside the repo) landed INSIDE the chezmoi source tree — untracked, git-ignored (.gitignore:25: .molecule/), 40 KB, 10 files, containing a DANGLING relative symlink (controller/.local/share/doc/lima/templates -> ../../lima/templates, resolves nowhere from that depth). chezmoi's source scan stats it, fails, exits 1 — reproducing: chezmoi -S home execute-template exits 1 with 'stat .../.molecule/controller/.local/share/doc/lima/templates: no such file or directory'. Cost: the full suite reported 13 failed + 3 errors (every one in chezmoi-template-rendering tests — test_config_identity, test_opencode_config_layers, test_gitconfig_tools), 1426 passed, 301s. Removed the scratch; execute-template exits 0; all 17 affected tests pass in 0.51s. The failure class: a molecule run from inside the repo leaves scan-breaking scratch chezmoi then chokes on silently — the suite reads red with nothing tracked having changed. Guard direction (pick one or both): (1) a test asserting find home -name .molecule is empty (the source tree is repo state; a red suite is the loud failure the trap deserves); (2) a molecule runbook line — run from an ephemeral dir, or clean .molecule after — in the run-molecule.sh contract or the apps/lima README. Related trap class: .vm-* artifacts never committed (the Lima VM-proof pattern); this instance is the source-tree variant. Not a rustup/DOT-282 matter — the scratch came from the apps/lima molecule scenario tooling.
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
