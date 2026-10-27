---
id: draft-1
title: Unify zshrc on the topic loading pattern (retire the isMac dual template)
status: Draft
created_date: 2026-10-27 20:13
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
dot_zshrc.tmpl maintains two configurations switched by .isMac: the macOS branch is the target pattern (source ~/.localrc, then load apps/*/files/zsh/*.zsh plus the zsh/*.zsh core exactly once, ordered path, rest, compinit, completion, with typeset -U path PATH dedup), while the Linux branch is the legacy monolith marked TODO PLEASE REFACTOR: oh-my-zsh plus zinit (starship, syntax-highlighting, autosuggestions, OMZ snippets) and hand-duplicated tool inits (mise activate, zoxide init, fzf --zsh, pyenv, cargo env, ROCm and GPU exports, homebrew shellenv detection, api_keys source) that topics already own as files/zsh fragments. The Linux branch never loads topic fragments at all, so every tool-init change is written twice or drifts between machines. Goal: one zshrc loader for both OSes on the topic loading pattern; each live Linux-monolith concern moves into its owning topic fragment (or a new topic where none exists); dead blocks are dropped; only genuinely OS-specific lines stay under conditionals. Open questions for the author: retire oh-my-zsh and zinit in favor of topic fragments plus apps/starship, or keep zinit as its own topic? Where do the ROCm/GPU env vars live (apps/ollama vs a new apps/rocm topic)? Do ~/.bash_aliases, ~/.functions and ~/.LESS_TERMCAP fold into topics or stay personal-local? Does the api_keys source stay in the loader as secrets handling rather than becoming a topic? Sequence with TASK-77 (hardcoded home-bdavis paths in this same file) and TASK-63 (zsh tooling standard spec). Done when: one loader serves both machines, the .isMac split is gone or trivial, every former monolith block is migrated to a topic fragment or recorded as deliberately dropped, and a shell on each machine starts with each tool init running exactly once (no double-init warnings like the zoxide _ZO_DOCTOR one the macOS branch comments on).
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
