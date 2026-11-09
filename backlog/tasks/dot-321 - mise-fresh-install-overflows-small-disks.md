---
id: DOT-321
title: mise fresh-install path overflows small disks — cargo tools need build deps
status: To Do
created_date: 2026-11-09 00:00
labels:
- mise
- disk
- vm-preview
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Found by the DOT-318 preview, measured 2026-11-08 (VM finding VM-4). On a
fresh Debian 12 guest with a 10 GiB disk, `mise install --yes` materializing
the full config.toml (75 tools) filled the disk at 33/75 and failed with "No
space left on device" — cargo-compiled tools (goldboot, broot, fd-find,
ripgrep, shellharden, mdcat) download full crate sources plus build
artifacts (~2 GB+ of /tmp cargo-install* and ~/.cargo registry alone), and
the builds also need pkg-config/libssl-dev that a bare guest lacks (goldboot
failed on missing openssl before the disk did).

Two coupled problems, one task because they share the fix surface:
1. **Disk budget**: the topic assumes tools are already installed (the real
   machine's state) and never bounds the install. A fresh-box run needs
   several GB of headroom it never checks.
2. **Build deps**: cargo-backend tools compile from source; their build
   dependencies (pkg-config, libssl-dev) are not in any topic's
   prerequisites — apps/mise installs ffmpeg only.

Done when the mise topic declares its fresh-install requirements: a
documented disk floor checked before materialization (fail loudly, not
mid-install), and build deps added to prerequisites for hosts that need
source builds. Preview environments (10 GiB guests) are an explicit
non-goal — they document the floor and skip, as the preview accommodation
does now.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] apps/mise checks free disk before `mise install --yes` and fails with a named requirement (not mid-install ENOSPC)
- [ ] cargo-tool build deps (pkg-config, libssl-dev) installed by prerequisites on Debian
- [ ] The disk floor is documented in the topic README
<!-- SECTION:ACCEPTANCE:END -->
