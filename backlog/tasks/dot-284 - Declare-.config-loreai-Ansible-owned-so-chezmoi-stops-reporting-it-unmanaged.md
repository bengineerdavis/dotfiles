---
id: DOT-284
title: Declare ~/.config/loreai Ansible-owned so chezmoi stops reporting it unmanaged
status: To Do
created_date: 2026-11-03 15:19
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`chezmoi unmanaged ~/.config` reports `.config/loreai`, and `chezmoi source-path ~/.config/loreai/env.zsh` answers "not managed". That reads as an accident. It is not: apps/loreai's first-install prompts write `~/.config/loreai/env.zsh` from `templates/loreai-env.zsh.j2` (tasks/prompts.yaml, `when: not loreai_env_stat.stat.exists`), so Ansible owns that file by design and chezmoi must never write it. Nothing in the repo says so, so the only record of the arrangement is the absence of a source file — and `home/.chezmoiignore` has no entry for it.

Measured 2026-11-03 on pop-os:

- `chezmoi unmanaged ~/.config | grep -c loreai` → 1. Adding `.config/loreai` plus `.config/loreai/**` to `home/.chezmoiignore` takes it to 0 (verified by patching and reverting).
- `home/.chezmoiignore` is 27 lines and carries exactly one `.config` entry (`.config/user-tmpfiles.d/tmp.conf`, darwin-only). There is no pattern for "Ansible-owned destination".
- `chezmoi managed` does not list the path today, so a test asserting "not in managed" would pass vacuously and prove nothing. `chezmoi unmanaged` is the command whose answer actually changes.
- The two states are not equivalent. "Not managed" is also true of a path nobody has thought about; "declared ignored" is a decision someone wrote down. Only the second survives the next session.
- `~/.config/loreai/env.zsh` is mode 0600 in a 0700 dir and holds the live OpenRouter key. An accidental adoption — someone dropping a source file at `home/dot_config/loreai/` — would deploy a rendered template over a file holding a secret.

The fix is a declaration, not a mechanism: extend `home/.chezmoiignore` with an Ansible-owned block naming the path and why, and add a test that fails when the declaration is removed. Per AGENTS.md the ignore file decides what reaches `$HOME`, so this lands as a branch and PR rather than a direct commit.

Out of scope, and deliberately so: `chezmoi diff` hangs on this machine (meld GUI, exit 124 after 15s, no output) because `.chezmoi.toml.tmpl` sets `diff.command = "meld"`. That is a separate defect in the config template and needs its own decision about GUI-vs-terminal diffing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AC1: `home/.chezmoiignore` carries an Ansible-owned block that names `.config/loreai` and `.config/loreai/**`, with a comment stating apps/loreai writes the file and chezmoi must not
AC2: a test asserts `.config/loreai` is absent from `chezmoi unmanaged` output, and its red state has been seen with the ignore block removed
AC3: the test reuses the existing managed/unmanaged invocation style (`chezmoi -S <PAYLOAD_ROOT>`) rather than parsing `.chezmoiignore` directly, so a future ignore-syntax change cannot make the test agree with itself
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 DOD1: `chezmoi unmanaged ~/.config` on this machine lists no loreai path, and `chezmoi status` still reports the same 10 pre-existing entries (nothing else changed)
DOD2: the PR is merged with human review, because `.chezmoiignore` decides what reaches the deployed tree
<!-- DOD:END -->
