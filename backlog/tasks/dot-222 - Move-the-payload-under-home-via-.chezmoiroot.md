---
id: DOT-222
title: Move the payload under `home/` via `.chezmoiroot`
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Move the payload under `home/` via `.chezmoiroot`.** [decisions
  2026-10-03: mechanism `.chezmoiroot`, subdir `home`; structure B — one
  branch, piecewise commits, squash-merged; ROADMAP "Move the deployed tree
  under `.chezmoiroot`"] Runs under the ground-shift protocol
  (`dotfiles/docs/research/coordinating-parallel-work-across-refactors.md`):
  runbook landed first (this item plus the research doc are it), census
  recorded there § Applied with author-confirmed dispositions, sentinel
  test proven red-on-old/green-on-new before the flip, session-start sync,
  observe-don't-patch with the 4h expiry, post-merge reconciliation pass
  re-running the census. Branch `agent/payload-home` off post-landing main
  (after the four census landings plus the author's run-role-cwd-fix).
  Internal commit sequence, each green: (1) pin the layout seam —
  `PAYLOAD_ROOT` in the root test conftest, ~25 fixture files rewired,
  still resolving to today's layout; (2) binned resolves its source path
  dynamically (`chezmoi source-path` / git-root walk) instead of hardcoding
  `:3100`, with `:3123`'s test-context walk re-anchored; (3) hooks match
  the payload root in either layout — `.pre-commit-config.yaml:44` and
  `scripts/run-bats.sh:31` regexes → `^((home/)?bin|scripts)/`, mutation-
  proven both directions; (4) pin the gate checker to real managed output —
  the committed real-data test; (5) the flip — `.chezmoiroot` containing
  `home`, `git mv` of `bin/`, `dotfiles/` (post docs-relocation),
  `dot_config/`, `dot_functions`, `dot_gitconfig.tmpl`, `dot_zprofile`,
  `dot_zshrc.tmpl`, `.chezmoiignore`, `.chezmoi.toml.tmpl`, `.chezmoidata/`
  into `home/` (`RESOURCES.md` stays root — repo-only by construction;
  special files move INTO `home/`, probe-verified unread at root; prune
  .chezmoiignore's now-noop tooling entries; payload-relative patterns
  survive), P1's constant → `home`, checker git-path normalization (git
  paths gain `home/`, managed source-relative forms don't change),
  governance-test advice line (`:83`). Squash-merge the five into ONE
  commit on main — chezmoi's failure mode is `.chezmoiroot` with an
  empty/misnamed subdir: silent empty source state, apply plans mass
  deletion — so main never holds the move half-landed. Mutation/
  `Failing-test` trailers consolidate into the squash commit message.
  Preps P1–P4 run as parallel sub-branches off the move branch, merged
  back by its owner (sequential by the mover is the fallback if the bench
  is empty). Verification: `chezmoi status` clean immediately post-flip;
  managed census compared at TARGET level before/after (delta = the
  cleanup plus docs items only); scratch clone `chezmoi init --apply`
  verified; suite green from a neutral cwd; checker normalization mutation
  seen to fail; bats hook proven to fire on a staged `home/bin/*.sh`.
  Lands after the docs relocation and ideally after PR #41 merges — both
  touch `dotfiles/apps/ollama`. The author runs `chezmoi apply` from main
  after review. [unclaimed]
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
