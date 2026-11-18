---
id: DOT-134
title: Create a `git` topic that owns git config and extensions; git-ai is its first
  extension
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-11-12 22:27
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Extend the Git topic with git-ai and its shell integration.** DOT-352 now owns Git package presence and global configuration in chezmoi; this task retains only the extension work.

The git-ai installer's edits were hand-placed: a `~/.gitconfig` written 2026-09-13, a `~/.git-ai/bin` PATH export appended to `~/.zshrc`, plus any hooks or bin entries it installed. **Machine-stamped:** that installer ran on the second machine — this Mac has no `~/.git-ai` and no git-ai block in `~/.zshrc` (verified 2026-09-15), so the audit starts there, not here. Audit everything the installer touched first, then extend `dotfiles/apps/git/`: install the extension as a declared dependency rather than a curl-installer, reconcile only its own Git configuration additions with the chezmoi source, and carry its shell integration in the topic's shell fragment (or `zsh/path.zsh` if it stays a zsh concern), never the deploy target. Git-ai is a Git extension and belongs beside Git, not scattered into zsh.

**Open research question — settle before writing install tasks:** is git-ai provisioned machine-globally, or per project? Per-project config on this machine lives exclusively in the mise `config.toml` files at each project root, so a per-project answer must route through that file (mise `[tools]`/env/tasks) rather than a global Git hook. Research what git-ai actually scopes — global hook, per-repo config, PATH shim — and what mise's per-project config can express, then take the decision to the author. The answer decides what replaces the installer's hand edits. Until it lands, a full `chezmoi apply` would delete the installer's lines from `~/.zshrc`, so apply everything else selectively and leave `~/.zshrc` out. Done when the Git topic installs git-ai cleanly on the intended machine, git-ai works from a fresh shell with no hand-edited line left in `~/.zshrc`, `diff <(chezmoi cat ~/.zshrc) ~/.zshrc` no longer shows the git-ai block, and the live Git configuration contains only reviewed, chezmoi-managed settings. [me]
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-11: DOT-352 creates apps/git and captures Git's existing global configuration. This task no longer owns that base topic or config capture.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
