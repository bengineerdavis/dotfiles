---
id: TASK-175
title: G6 — give gh one installation owner and adopt the existing Debian install
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G6 — give gh one installation owner and adopt the existing Debian install.**
  Add a small `dotfiles/apps/gh` topic: Homebrew on macOS and GitHub's signed
  apt repository at `cli.github.com` on Debian. The handoff's 2026-09-23
  evidence is `apt-cache policy`: gh is a dpkg package from
  `https://cli.github.com/packages stable/main`, installed by hand rather
  than by a topic or deb-get; `deb-get list --installed` had no match.
  Adopt with `state: present`, not a reinstall. `apps/deb-get` currently
  repairs that repository's keyring and protects gh during removal. Move
  the keyring-repair entry from `dotfiles/apps/deb-get/vars/main.yaml` to
  the gh topic so the key has one owner, and account for the existing
  removal protection. A stale third-party apt source also offers older gh
  builds on the Linux target; the recorded apt selection preferred
  GitHub's newer package. Keep that source collision visible during adoption.
  Check recent history and claim `dotfiles/apps/deb-get/` before editing.
  Done when `--check` on the Linux target adopts without reinstalling and
  removal leaves apt's sources clean; exercise Homebrew in a Mac session.
  G6 may run any time, including alongside G2–G5, because it touches
  different files. Missing gh remains G7's UNKNOWN discovery case.
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
