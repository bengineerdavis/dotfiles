---
id: DOT-382
title: Declare and prove loreai's Linux system requirements in the topic, not only
  in the VM scenario
status: To Do
created_date: 2026-11-19 08:47
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The VM scenarios prove the *configuration logic* runs. They do not establish
that the guest resembles the machine the topic will actually live on, and the
two are measurably different. So a green scenario currently means "the role
converged in a 4 GiB, 2-CPU, Debian-only sandbox" — not "this will work on the
host or on the fleet this is extended to."

**Measured 2026-11-19, host versus `debian-lima` guest:**

| Property | Host | Guest |
|---|---|---|
| OS | macOS (darwin-arm64) | Debian 12 (linux-x64 or arm64) |
| CPUs | 14 | 2 |
| Memory | 36 GB | 4 GiB |
| Service manager | `launchd` | `systemd` |
| Embedding cap | 1067 tokens (learned after OOM backoff) | ~2735 tokens (computed from ~3 GB free) |

That last row is the concrete case where a passing guest proves the wrong
thing. `memoryModelEmbedCap()` derives the token cap from *free memory*
(`freeBytes × 0.5 − 680 MiB`, then a square root). A 4 GiB guest computes a
**higher** cap than the 36 GB host's persisted learned cap, because the host's
1067 is a *learned* value after OOM backoff, not the model output. A guest run
therefore exercises a different code path and different memory pressure than
the host ever does.

**Other divergences found while writing this:**

- **`topic_requires: []` and no `apt` tasks.** The role declares no system
  packages. Its only Debian dependencies live in
  `molecule/debian-lima/prepare.yml`, which installs `gzip` and `curl` so the
  *test* can run — hiding the requirement from every consumer except the
  scenario. A real Debian host gets no such step.
- **Native library floor undeclared.** The binary extracts `onnxruntime-node`
  and `sqlite-vec` into a temp dir at runtime. Both link against glibc,
  libstdc++, libgcc — a requirement stated nowhere and satisfied on the guest
  only because the image happens to have it.
- **One image is not Linux coverage.** `debian-lima` pins a single Debian 12
  cloud image with `cpus: 2, memory: 4GiB` from the shared adapter. Debian 13,
  Ubuntu LTS, and non-glibc distributions are untested with no expectation
  recorded.
- **Service-manager paths diverge entirely.** `service.yaml` branches on
  `Darwin` (launchctl) versus `Debian` (systemd). The guest proves only the
  systemd branch; the launchd branch — what the host actually runs — is never
  exercised by any VM.
- **Environment deliberately differs.** The guest runs with
  `propagateProxyEnv: false`, `mounts: []`, `forwardAgent: false`,
  `loreai_telemetry: 0`, `loreai_inference: none` — no credentials, no
  inference, no mounts. That isolation is *correct for a test* and *wrong as a
  preview*; the task is to know which divergences are deliberate and which are
  defects.

The author's framing: configuration logic and installation are **incomplete
unless all dependencies are accounted for**. A scenario that satisfies
dependencies the role never declares has proven the harness, not the role.

Ship:

- **An inventory of host-versus-guest divergences**, each classified as
  *deliberate isolation* (credentials, inference, mounts) or *defect* (memory
  shape, CPU count, undeclared packages, missing library floor). Written into
  the topic README so the distinction is reviewable.
- **A reviewable recommendation per defect**: fix the role, change the guest
  shape, or declare the requirement — with the reason, and what breaks if
  ignored. Surfaced for the author to decide, not resolved silently.
- **The role declares Debian prerequisites itself** (`ansible.builtin.apt`
  with `when: os_family == 'Debian'`, the `apps/mise` precedent), replacing
  the scenario-only installs in `molecule/debian-lima/prepare.yml`.
- **`topic_requires` and `topic_os` corrected to measured reality.**
- **A requirements table** in the topic README: minimum OS per platform, the
  native C/C++ runtime floor, memory and CPU needed for the embedding path to
  reach a usable cap, and what is explicitly unsupported.
- **A VM scenario that installs the topic and its declared dependencies from
  a bare image**, so the declaration is what gets exercised.
- **At least one tested-versus-untested statement per distribution**, with no
  distribution claimed working unless a scenario ran against it.
- **A guest shape decision**: either bring the guest close enough to be a
  preview (realistic memory, both service managers where feasible), or state
  plainly that it is a proving ground only and name what it cannot prove.

Constraints:

- Do not duplicate DOT-255 (fleet matrix) or DOT-265 (LoreAI on Linux via the
  shared Lima adapter). This owns *dependencies declared, divergences
  surfaced, requirements proven*; those own the broader matrix.
- **The guest is compared to the host, not just asserted.** A scenario that
  never states its divergence from the target machine cannot be a preview, and
  the comparison must be measured, not assumed.
- Requirements must be measured **on a bare guest** — a library present on the
  developer's machine is exactly the defect this exists to catch.
- Deliberate isolation (no credentials, no inference, no mounts) is a feature
  and must be preserved; do not "fix" it into a preview by mounting the host.
- Existing `debian-lima` properties must not regress: idempotence, remove-twice,
  planted-sentinel preservation, the X-Lore-Provider header assertion.
- Findings go to the author for review with recommendations and reasons. This
  task surfaces differences; it does not unilaterally reconcile them.

Scoped deliberately loose per the author's request: "keep that as a task to
flesh out more later." The investigation settles the package list, how many
distributions are worth proving, and which divergences are defects.

Decision 2026-11-19: VM testing must establish that the guest is a faithful
preview of the target — or state clearly what it cannot prove — because
installation is incomplete unless every dependency is accounted for.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 A host-versus-guest divergence inventory exists in the topic README, each entry classified as deliberate isolation or defect, with the measurements behind it
- [ ] #2 Every defect carries a recommendation with its reason and consequence, surfaced for author review rather than resolved silently
- [ ] #3 The loreai role installs its Debian prerequisites via ansible.builtin.apt with when: os_family == 'Debian', and molecule/debian-lima/prepare.yml no longer pre-installs what the role should own
- [ ] #4 topic_requires and topic_os reflect measured reality, replacing topic_requires: []
- [ ] #5 The README requirements table states, per platform: minimum OS, the native C/C++ runtime floor, the memory and CPU needed for a usable embedding cap, and what is unsupported
- [ ] #6 A VM scenario installs the topic and its declared dependencies from a bare image, so the declaration itself is exercised
- [ ] #7 The embedding-cap divergence is resolved or explained: the guest computes a different cap than the host's learned 1067, and the record says which behaviour the proof represents
- [ ] #8 A guest-shape decision is recorded: bring the guest close enough to be a preview, or state plainly what it cannot prove
- [ ] #9 Tested versus untested-but-expected distributions are stated per distribution, with no claim for one that never ran
- [ ] #10 Deliberate isolation is preserved and named: no credentials, inference, mounts, or agent forwarding are added to the guest
- [ ] #11 Existing debian-lima properties do not regress: idempotence, remove-twice, planted-sentinel preservation, X-Lore-Provider header assertion
- [ ] #12 The board lists DOT-382 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
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
