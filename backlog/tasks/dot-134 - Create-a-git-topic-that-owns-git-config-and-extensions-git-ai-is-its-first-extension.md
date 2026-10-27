---
id: DOT-134
title: Create a `git` topic that owns git config and extensions; git-ai is its first
  extension
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Create a `git` topic that owns git config and extensions; git-ai is its
  first extension.** Git config is not managed at all today — no
  `dot_gitconfig` in the source, no `apps/git` topic — and the git-ai
  installer's edits are hand-placed: a `~/.gitconfig` written 2026-09-13
  (plain file, unmanaged), the `~/.git-ai/bin` PATH export appended to
  `~/.zshrc` (the one two-way-drifted file), plus any hooks or bin entries it
  installed. **Machine-stamped:** that installer ran on the *second machine*
  — this Mac has no `~/.git-ai` and no git-ai block in `~/.zshrc`
  (verified 2026-09-15), so the audit starts there, not here. Audit everything the installer touched first, then build
  `dotfiles/apps/git/`: it owns the gitconfig as a chezmoi template where
  machine-specific, installs extensions as declared dependencies rather than
  curl-installers, and carries the shell integration the installers keep
  hand-appending — the PATH line moves into the topic's shell-integration
  fragment (or `zsh/path.zsh` if it stays a zsh concern), never the deploy
  target. This supersedes the earlier zsh-fragment framing: git-ai is a git
  extension and belongs beside git config, not scattered into zsh.
  **Open research question — settle before writing install tasks:** is git-ai
  provisioned machine-globally, or per project? Per-project config on this
  machine lives exclusively in the mise `config.toml` files at each project
  root, so a per-project answer must route through that file (mise
  `[tools]`/env/tasks) rather than a global gitconfig hook. Research what
  git-ai actually scopes — global hook, per-repo config, PATH shim — and what
  mise's per-project config can express, then take the decision to the author.
  The answer decides what replaces the installer's hand edits. Until it
  lands, a full `chezmoi apply` would delete the installer's lines from
  `~/.zshrc`, so apply everything else selectively (`chezmoi apply ~/dotfiles
  ~/.config/opencode ~/tools`) and leave `~/.zshrc` out. Done when `apps/git`
  installs cleanly on this machine, git-ai works from a fresh shell with no
  hand-edited line left in `~/.zshrc`, `diff <(chezmoi cat ~/.zshrc) ~/.zshrc`
   no longer shows the git-ai block, and the live `~/.gitconfig` is the one the
   topic owns. [me]
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
