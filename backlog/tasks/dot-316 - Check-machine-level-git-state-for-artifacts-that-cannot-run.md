---
id: DOT-316
title: Check machine-level git state for artifacts that cannot run
status: To Do
created_date: 2026-11-09 00:00
labels:
- git
- machine-state
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-08. `~/.git-template/hooks/pre-commit` dated 2023 exec'd
`/home/bdavis/.local/pipx/venvs/pre-commit/bin/python`, a path DOT-59 removed
when the repo switched to prek. `init.templateDir` points at that directory,
so `git init` in any new directory produced a repo whose commits failed with
`mise ERROR No version is set for shim: pre-commit`. Found because a pytest
fixture inherited it and the whole suite errored before reaching the code
under test.

Removed the shim on 2026-11-08 (backup at
`~/.cache/tmp/opencode/git-template-backup/pre-commit.2023-shim`); a fresh
repo now commits cleanly.

The gap: nothing checks machine-level git state. chezmoi owns
`~/.config/*`, but `~/.git-template/`, `~/.gitconfig` outside the managed
block, and `core.hooksPath` are all outside it. The dotfiles suite also
depended on that state, which is why it broke rather than warned.

Done when a check enumerates the machine-level git surface and fails loudly
on an artifact that cannot run — an executable shim whose interpreter is
gone, a `core.hooksPath`/`init.templateDir` pointing at a directory that
does not exist or that contains shims from a retired tool. It must fail
rather than skip when it finds nothing to inspect: the 2023 shim sat
unreferenced for three years precisely because nothing looked.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] A check enumerates the machine-level git surface: `init.templateDir`, `core.hooksPath`, and the shims in whichever directory those resolve to.
- [ ] It fails when a shim is executable but its interpreter is gone, naming the shim and the missing path.
- [ ] It fails when `init.templateDir` or `core.hooksPath` names a directory that does not exist.
- [ ] It fails when the surface contains shims written by a tool the repo no longer uses.
- [ ] It fails, not skips, when there is nothing to inspect. Silence is the failure mode this task exists for.
- [ ] The check runs from the suite, and a deliberately broken shim proves it goes red (mutation recorded in the commit message).
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-08: task filed by another session; released unclaimed to main
(`2c03c70`). Not owned — claim it on the next available execution-session
budget (.agent-budget.toml currently `workers = 1`). The claim itself is the
signal: record it via `backlog-py orchestration claim DOT-316 --actor <you>
--expected-version <v>`, and fold any hold-onto-main machine-git check into
the existing suite rather than a new tool.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
