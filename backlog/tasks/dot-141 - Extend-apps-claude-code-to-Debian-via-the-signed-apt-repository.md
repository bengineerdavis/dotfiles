---
id: DOT-141
title: Extend `apps/claude-code` to Debian via the signed apt repository
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Extend `apps/claude-code` to Debian via the signed apt repository.** The
  topic is `topic_os: [Darwin]` because Homebrew casks are macOS-only, so the
  Debian box has no managed Claude Code at all. Upstream publishes a signed apt
  repo rather than expecting the native installer: keyring at
  `/etc/apt/keyrings/claude-code.asc`, fingerprint
  `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`, and — the part that bites — both
  the URL path *and* the suite name change between channels
  (`.../apt/stable stable main` versus `.../apt/latest latest main`), so
  `claude_code_cask`'s stable/latest choice needs a Debian equivalent rather
  than reuse. Needs `become: true` for the keyring and sources file, which no
  part of this topic currently requires. Note apt installs do not auto-update
  through Claude Code either, so currency still comes from the system upgrade
  pass. Done when the topic flips to `[Darwin, Debian]`, installs on the Debian
  box with the key verified before use rather than trusted blind, and
  `--tags remove` takes the repo file and keyring back out.
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
