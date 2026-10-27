---
id: DOT-98
title: uv work-machine capture — flag this Mac and capture the private index
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
- blocked
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**uv work-machine capture — flag this Mac and capture the private index.**
  [blocked on author inputs, 2026-10-03] The uv topic provisioned cleanly on
  L37V3P6GQ3 (ok=10 changed=0 failed=0; version assert 0.12.21 >= 0.12.17;
  self-update no-op; capture skipped with the designed personal-machine
  message; ~/.localrc untouched). The work-machine half has two blockers,
  both author-side: (1) op CLI has no signed-in account here — 1Password.app
  2.39.0 IS installed, so the fix is Settings > Developer > "Integrate with
  1Password CLI", then `op signin` (biometric); (2) the vault item's
  username/password have no source on this machine — /etc/uv/uv.toml carries
  only the index URL (not reproduced here: employer-identifying, spec.md
  § Data), with no netrc and no UV_* env vars. If the index is
  network/SSO-gated, the vault item and the role's three-value assert need
  relaxing to URL-only — a spec change to PR. Remaining sequence once
  unblocked: create vault item `uv-private-index` (Private vault,
  url/username/password per apps/uv/defaults/main.yaml) -> flip this host to
  work: true in .chezmoidata/uv.yaml (one PR; landing it earlier breaks
  apply loudly and fails the role's vault reads) -> `bash
  dotfiles/executable_run-role.sh uv install` from dotfiles/ -> author
  `chezmoi apply` -> verify the rendered config has private default + public
  fallback. Done when: the rendered uv.toml shows the private index as
  default on this host and tests/uv stays green.
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
