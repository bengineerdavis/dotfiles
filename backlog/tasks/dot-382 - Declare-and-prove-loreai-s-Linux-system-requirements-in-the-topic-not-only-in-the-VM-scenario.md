---
id: DOT-382
title: Declare and prove loreai's Linux system requirements in the topic, not only
  in the VM scenario
status: To Do
parent_task_id: DOT-385
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

**The warrant: why a pass in the guest says anything about the parent.**

This is the requirement, and it is a claim about *inference*, not about test
steps. A green VM run is only evidence about the parent machine if you can
state the argument for why the tested properties transfer. Today that argument
is missing, and in one direction it is false.

What a Linux guest *can* warrant about the macOS parent:

- **Pure configuration logic** — that a role converges, is idempotent, and
  tears down cleanly. Ansible task order, templating, and conditionals are
  platform-independent unless they branch on platform.
- **The installed artefact's own dependencies**, because the binary is the
  same download on both platforms and its `DT_NEEDED` set is per-ELF, so the
  Linux floor transfers to any Linux host, including `pop-os` — the fleet's
  Linux member in `machines.yml` — but not to macOS. That is the concrete
  machine the Linux half of this task is for, so the requirements table must
  be true of it, not only of the Debian guest.

What it *cannot* warrant, and the failure this task exists to catch:

- **The 8 `Darwin`-gated tasks in `apps/loreai/tasks/`** (launchd agent
  install, `launchctl print`, Darwin unit paths) execute **only** on macOS. A
  Linux run never touches one line of them. There are 6 `Debian`-gated tasks
  in the mirror position. **A Debian guest proves the smaller of the two
  branches, and the parent machine runs the larger one.**
- **There is no macOS scenario anywhere in the repo.** Every `molecule.yml`
  under `home/dotfiles` was checked; none targets darwin. So the launchd path
  — the path the parent actually takes — has no VM proof at all, in any topic.
- **Filesystem and path semantics.** APFS is case-insensitive by default;
  ext4 is case-sensitive. A role that writes two files differing only in case
  passes on Linux and collides on macOS, or vice versa. Not exercised by
  either side today.
- **Home-directory layout.** The Lima guest's home is `/home/molecule.guest`
  because it collides with the host login; the parent's is
  `/Users/ben.davis`. Anything depending on home-path shape is untested on the
  parent.

So "not all parameters of the VM need to match" is correct **and** has a hard
limit: the parameters that may differ are the ones **no code branches on**.
CPU count, RAM and GPU are safe omissions — no task reads them. Platform is
not a safe omission, because 8 tasks branch on it.

The conclusion the task must reach: either prove the Darwin branch (a macOS
scenario, or an explicit decision that `run-role` on the parent is the proof),
or state plainly that the Linux VM warrants only the Linux half and name the
Darwin half as parent-verified-by-hope.

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
- **A written transfer argument** — the warrant — stating for each tested
  property *why a pass here implies a pass on the parent*, and for each
  untested property why the omission is safe. The rule the document must
  express: parameters no code branches on (CPU, RAM, GPU) may differ;
  platform may not, because tasks branch on it.
- **A decision on the Darwin branch.** Either add a macOS scenario, or record
  that `run-role` on the parent is the accepted proof for the 8
  `Darwin`-gated tasks — explicitly, not by omission. A Linux guest proving
  the 6-task Debian branch while the parent runs the 8-task Darwin branch
  must not be reported as coverage of the topic.
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


**Part of DOT-385** — the umbrella for the machine-config lifecycle. Sibling tasks: DOT-383 (macOS coverage) and DOT-384 (rollback). Shared assumptions (what "proven" means, which machines are targets, and that `run-role.sh` is the only runner) are settled there, not here.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 A written transfer argument exists stating, per tested property, why a pass in the guest implies a pass on the parent, and per omitted property why the omission is safe
- [ ] #2 The transfer argument expresses the rule: parameters no code branches on may differ; platform may not, because tasks branch on it
- [ ] #3 The Darwin-versus-Debian asymmetry is recorded with its counts, and a decision is made on how the 8 Darwin-gated tasks are proven — macOS scenario or explicit parent-run acceptance
- [ ] #4 The topic README states the dependencies-versus-environment split explicitly: which properties a VM must prove and which it deliberately does not reproduce
- [ ] #5 The loreai role installs its Debian prerequisites via ansible.builtin.apt with when: os_family == 'Debian', and molecule/debian-lima/prepare.yml no longer pre-installs what the role should own
- [ ] #6 The declared prerequisite set covers the parsed DT_NEEDED floor: libstdc++, libgcc_s, libc/glibc, the dynamic loader, and the unpacking tools
- [ ] #7 topic_requires and topic_os reflect measured reality, replacing topic_requires: []
- [ ] #8 The README requirements table states the glibc/libstdc++ floor, minimum OS per platform, and that non-glibc distributions are out of scope
- [ ] #9 A VM scenario installs the topic and its declared dependencies from a bare image, so the declaration itself is exercised rather than the harness
- [ ] #10 No GPU driver is added or required: the record states the app is CPU-only by design, cites that device: "cpu" is hardcoded, and notes that any acceleration work is a separate feature request
- [ ] #11 Environment differences (RAM, CPU count, embedding-cap divergence, launchd-vs-systemd coverage) are inventoried and classified as deliberate difference or defect, not treated as blockers
- [ ] #12 Every defect carries a recommendation with its reason and consequence, surfaced for author review rather than resolved silently
- [ ] #13 Tested versus untested-but-expected distributions are stated per distribution, with no claim for one that never ran
- [ ] #14 The requirements are stated as true of pop-os, the fleet's Linux member, not only of the Debian guest image
- [ ] #15 Deliberate isolation is preserved and named: no credentials, inference, mounts, or agent forwarding added to the guest
- [ ] #16 Existing debian-lima properties do not regress: idempotence, remove-twice, planted-sentinel preservation, X-Lore-Provider header assertion
- [ ] #17 The board lists DOT-382 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
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
