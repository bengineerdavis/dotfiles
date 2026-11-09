---
id: DOT-335
title: write_atomic should preserve the destination mode by default
status: To Do
created_date: 2026-11-09 15:18
labels:
- now
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
apps/apt/files/apt_keyring.py write_atomic() hardcodes chmod 0o644. It is now called for two kinds of file: the keyring (0644 is correct) and, since the roborev-665 atomic-write fix, the apt source file via rewrite_signed_by() (mode should be preserved, not assumed). The mode parameter already exists; the fix is to stat the destination and default mode to the existing mode, keeping the explicit override for the keyring write. Latent trap: correct for the current two callers, but a future caller writing a non-0644 file would silently clobber its mode.
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
