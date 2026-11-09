---
id: DOT-320
title: mise phase order runs upgrade before install — breaks fresh hosts
status: To Do
created_date: 2026-11-09 00:00
labels:
- mise
- bug
- vm-preview
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found by the DOT-318 preview, measured 2026-11-08 (VM finding VM-3). In
apps/mise/tasks/main.yaml the router imports lifecycle files in file order —
bootstrap → prerequisites → **upgrade** → install. On a host where mise is
not yet installed (fresh Debian box, new machine, VM), the upgrade phase runs
first: `mise upgrade` fails with "Error executing command." rc=2 and empty
stderr because the binary does not exist. Latent on the author's machine
(mise already present), which is why it has never fired. The empty-stdout
failure also defeats the task's own partial-failure reporting — the error
carries no tool names.

Fix: reorder the imports so install precedes upgrade (install is what puts
the binary on disk), or guard the upgrade phase with a
`mise --version`-succeeded precondition. Prefer the reorder: it makes the
lifecycle files self-consistent on every host shape.

Done when a fresh Debian guest converges apps/mise in ONE pass — no
pre-installed mise — and ends with `mise --version` reporting a version.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] apps/mise/tasks/main.yaml imports install before upgrade (or the upgrade phase is guarded on mise's presence)
- [ ] A fresh-host mise converge (no mise installed) completes in one pass in a VM
- [ ] Seen to fail against the current ordering (upgrade-before-install) before the fix lands
<!-- SECTION:ACCEPTANCE:END -->
