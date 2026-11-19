---
id: DOT-382
title: Declare and prove loreai's Linux system requirements in the topic, not only
  in the VM scenario
status: To Do
created_date: 2026-11-19 08:47
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

A VM scenario must prove the **dependencies** are satisfied. It must not
reproduce the **environment** — full RAM, GPU, credentials — because those are
not what can fail. The distinction is load-bearing and the current scenarios
blur it.

**Dependencies: what can genuinely fail.** The installed binary extracts a
native ONNX Runtime and `sqlite-vec` into a temp dir at runtime. Parsed from
the shipped Linux x64 library (`DT_NEEDED`), the hard link dependencies are:

```
libdl.so.2  librt.so.1  libpthread.so.0  libstdc++.so.6
libm.so.6   libgcc_s.so.1  libc.so.6  ld-linux-x86-64.so.2
```

That is the complete floor: **a C++ runtime, glibc, and the standard loader**.
Nothing else is a hard dependency, and none of it is declared by the role
today. This is what a bare guest must prove, and what would actually break on
a machine missing `libstdc++.so.6`.

**Environment: what must NOT be reproduced.** CPU count, total RAM, and GPU do
not change whether the topic installs or runs. A 4 GiB guest is sufficient to
prove dependency satisfaction, and the author's framing is right on this —
we do not need full system RAM in a VM to know the install works.

The one place environment *does* leak into behaviour is the embedding cap:
`memoryModelEmbedCap()` derives a token cap from **free memory**
(`freeBytes × 0.5 − 680 MiB`, square-rooted, floor 256, ceiling ~4962). The
36 GB host persists a *learned* cap of 1067 after OOM backoff; a 4 GiB guest
computes roughly 2735 and never reaches the backoff path. `~2735` is my
calculation from the constants, **not measured in a guest**. This is a
tuning divergence, not a correctness dependency — worth recording so a passing
run is not misread, not worth matching hardware for.

**The GPU point, corrected by measurement.** I initially accepted a GPU-driver
requirement and the code does not support it:

- `embedding-worker.ts` hardcodes `device: "cpu"`; no `executionProviders`
  anywhere in `packages/core/src/`.
- The shipped `onnxruntime-node` 1.27.0 package contains **two files per Linux
  arch** (`libonnxruntime.so.1`, `onnxruntime_binding.node`). There is no CUDA,
  ROCm, or DirectML provider library in the package at all.
- `vendor-ort-native.ts` filters out `libonnxruntime_providers_cuda.so` and
  `..._tensorrt.so` because, in its own words, "Lore always uses the CPU
  execution provider."
- CUDA/ROCm strings appear in `libonnxruntime.so.1` as registered provider
  *names* for dlopen, not `DT_NEEDED` entries. Nothing is loaded at runtime on
  the `device: "cpu"` path.

So on an AMD Linux machine this embeds on CPU exactly as it does on the Mac —
**no GPU driver is required**, and no GPU driver would be used. What *is*
required is the `DT_NEEDED` floor above. If GPU acceleration is genuinely
wanted (an AMD box embedding on the CPU unnecessarily), that is a separate
feature request against the fork, not a system requirement.

**The real defects found:**

- **`topic_requires: []` and no `apt` tasks.** The role declares no system
  packages. Its only Debian dependencies live in
  `molecule/debian-lima/prepare.yml`, which installs `gzip` and `curl` so the
  *test* can run — hiding the requirement from every consumer except the
  scenario.
- **The C++ runtime floor is undeclared**, satisfied on the guest only because
  the image happens to ship it. `libstdc++.so.6` is exactly the kind of thing
  a minimal or musl-based image lacks.
- **One image is not Linux coverage.** `debian-lima` pins a single Debian 12
  image. Non-glibc distributions cannot satisfy this floor at all and are
  untested and unmentioned.
- **Service-manager branches diverge entirely.** `service.yaml` branches
  `Darwin` (launchctl) vs `Debian` (systemd); the guest proves only systemd,
  and the launchd branch the host runs is exercised by no VM.

Ship:

- **The dependencies-versus-environment split written into the topic README**,
  naming which properties a VM must prove (packages, shared libraries, loader)
  and which it deliberately does not reproduce (RAM, CPU count, GPU,
  credentials, inference). This is the artifact that stops the next reader
  re-arguing it.
- **The role declares its own Debian prerequisites** (`ansible.builtin.apt`
  with `when: os_family == 'Debian'`, the `apps/mise` precedent), replacing
  the scenario-only installs — including the libraries the parsed `DT_NEEDED`
  list proves are needed.
- **`topic_requires` and `topic_os` corrected to measured reality.**
- **A requirements table** stating the glibc/libstdc++/libgcc floor, the
  unpacking tools, minimum OS per platform, and what is unsupported —
  notably that non-glibc distributions are out of scope.
- **A VM scenario that installs the topic and its declared dependencies from
  a bare image**, so the declaration is what gets exercised rather than the
  harness.
- **A divergence inventory** of host versus guest, each entry classified as
  *deliberate environment difference* or *defect*, with a recommendation and
  reason for each defect, surfaced for author review rather than silently
  resolved. The embedding-cap difference belongs here as a tuning note.
- **A tested-versus-untested statement per distribution**, with no claim for
  any that never ran.

Constraints:

- **Prove dependencies, do not reproduce the environment.** A scenario that
  needs the host's RAM or GPU to pass is testing hardware, not the topic.
- **Do not duplicate DOT-255 (fleet matrix) or DOT-265 (Linux proof).** This
  owns declared dependencies, the environment/dependency split, and the
  requirements table; those own the matrix.
- Do not add GPU support as part of this task. Record the finding — the app
  is CPU-only by design and needs no driver — and if acceleration is wanted,
  file it separately.
- Deliberate isolation is a feature and must be preserved: no credentials, no
  inference, no mounts, no agent forwarding.
- Requirements must be measured **on a bare guest**; a library present on the
  developer's machine is the defect this exists to catch.
- Existing `debian-lima` properties must not regress: idempotence,
  remove-twice, planted-sentinel preservation, X-Lore-Provider header.
- Findings go to the author for review with recommendations. This surfaces
  differences; it does not unilaterally reconcile them.

Scoped deliberately loose per the author's request: "keep that as a task to
flesh out more later." The investigation settles the package list and how many
distributions are worth proving.

Decision 2026-11-19: a VM proves dependency satisfaction, not environment
parity. Hardware capacity and GPU are out of scope; the shared-library floor and
the role's undeclared packages are in scope.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 The topic README states the dependencies-versus-environment split explicitly: which properties a VM must prove and which it deliberately does not reproduce
- [ ] #2 The loreai role installs its Debian prerequisites via ansible.builtin.apt with when: os_family == 'Debian', and molecule/debian-lima/prepare.yml no longer pre-installs what the role should own
- [ ] #3 The declared prerequisite set covers the parsed DT_NEEDED floor: libstdc++, libgcc_s, libc/glibc, the dynamic loader, and the unpacking tools
- [ ] #4 topic_requires and topic_os reflect measured reality, replacing topic_requires: []
- [ ] #5 The README requirements table states the glibc/libstdc++ floor, minimum OS per platform, and that non-glibc distributions are out of scope
- [ ] #6 A VM scenario installs the topic and its declared dependencies from a bare image, so the declaration itself is exercised rather than the harness
- [ ] #7 No GPU driver is added or required: the record states the app is CPU-only by design, cites that device: "cpu" is hardcoded, and notes that any acceleration work is a separate feature request
- [ ] #8 Environment differences (RAM, CPU count, embedding-cap divergence, launchd-vs-systemd coverage) are inventoried and classified as deliberate difference or defect, not treated as blockers
- [ ] #9 Every defect carries a recommendation with its reason and consequence, surfaced for author review rather than resolved silently
- [ ] #10 Tested versus untested-but-expected distributions are stated per distribution, with no claim for one that never ran
- [ ] #11 Deliberate isolation is preserved and named: no credentials, inference, mounts, or agent forwarding added to the guest
- [ ] #12 Existing debian-lima properties do not regress: idempotence, remove-twice, planted-sentinel preservation, X-Lore-Provider header assertion
- [ ] #13 The board lists DOT-382 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
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
