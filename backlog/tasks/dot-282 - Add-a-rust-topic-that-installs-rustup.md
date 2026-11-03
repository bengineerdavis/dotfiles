---
id: DOT-282
title: Add a rust topic that installs rustup
status: To Do
created_date: 2026-11-03 03:17
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Settled with the author 2026-11-01 (grilling Q1): Rust needs a topic that installs rustup, and rustup includes cargo — so the cargo: mise backends (lychee, broot, eza, fd-find, ripgrep and the rest of the cargo: lines in home/dotfiles/apps/mise/files/config.toml) gain a fleet-managed prerequisite. Today the Rust toolchain on this machine comes from mise's rust tool (1.94-1.99 symlinked versions present, measured 2026-11-01) with no topic owning it; a fresh or half-applied box has no documented install story for the compiler the mise config depends on. The topic installs rustup per the standard topic structure (topic.yml + tasks/install.yaml), Debian and macOS both targets, and its README states that cargo-installed mise tools resolve through it. DOT-281 (lychee cargo fallback) depends on this.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A fresh box can install rustup through the topic and cargo resolves
- [ ] #2 macOS and Debian are both handled or explicitly gated
- [ ] #3 The topic README states that cargo: mise tools resolve through rustup
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
