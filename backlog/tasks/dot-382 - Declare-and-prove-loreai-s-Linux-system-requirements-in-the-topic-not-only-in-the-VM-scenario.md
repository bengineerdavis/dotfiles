---
id: DOT-382
title: Declare and prove loreai's Linux system requirements in the topic, not only
  in the VM scenario
status: To Do
created_date: 2026-11-19 08:47
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The loreai topic declares `topic_requires: []` and declares no system
packages. Its Debian behaviour is real but **unowned**: the only place Linux
dependencies appear is `molecule/debian-lima/prepare.yml`, which installs
`gzip` and `curl` so the *test* can run.

That is backwards. A scenario installing what the role needs hides the
requirement from every consumer except the scenario. A real Debian host
running the topic — not the molecule harness — has no such step.

Measured 2026-11-19 in `apps/loreai`:

- `topic.yml` states `topic_requires: []` and `topic_os: [Darwin, Debian]`.
- No `ansible.builtin.apt` task anywhere in `tasks/`; only `prepare.yml`
  installs `gzip` and `curl`, with a comment saying Lima's guest "already has
  Python and CA certificates".
- The install path fetches a gzip-compressed release asset and unpacks it to
  `~/.local/bin/lore`. Standalone executable — no node, no python runtime, no
  bundled ORT is needed on the *host*, because the binary is self-contained.
- The gateway uses `sqlite-vec` and native `onnxruntime-node`, both extracted
  from the binary into a temp dir at runtime — so the shared-library
  prerequisites of those (glibc floor, libstdc++, libgcc) are load-bearing on
  Linux and are nowhere declared.
- The molecule README states plainly what is *not* covered: "this is not
  LLM-inference, Linux-host, or macOS-guest-on-Linux coverage."

So there are two gaps, and they are different in kind:

1. **Declared requirements are absent.** What the topic genuinely needs on
   Debian — unpacking tools, and the C/C++ runtime the bundled ONNX and vec0
   libraries link against — is not stated in the role.
1. **Coverage is a single image.** `debian-lima` pins one Debian 12 cloud
   image. Debian 13, Ubuntu LTS, and any non-glibc distribution are untested,
   and there is no expectation recorded either way.

The author's request is to state the system requirements in the module and
prove them by installing the topic and its dependencies in a VM. This task
scopes that; the fleet-matrix design is DOT-255 and the existing Linux proof
is DOT-265, so this must not duplicate either.

Ship:

- The loreai role declares what it needs on Debian through the ordinary
  topic mechanism (`ansible.builtin.apt` with `when: os_family == 'Debian'`,
  as `apps/mise` does), replacing the scenario-only installs in
  `molecule/debian-lima/prepare.yml` with the role's own prerequisite tasks
- `topic_requires` and `topic_os` are corrected to whatever the investigation
  proves, rather than the current aspirational `[]`
- A written requirements table in the topic README stating, per platform, the
  minimum OS version, the C/C++ runtime floor the bundled native libraries
  demand, and what is explicitly unsupported
- A VM scenario that installs **the topic and its declared dependencies from
  a bare image** — not a scenario that pre-installs them — so the proof
  exercises the declaration
- An explicit statement of which distributions are tested and which are
  untested-but-expected, since one Debian image is not Linux coverage

Constraints:

- Do not duplicate DOT-255 (fleet matrix) or DOT-265 (LoreAI on Linux via the
  shared Lima adapter). This task owns *declaring and proving the
  requirements*; those own the broader matrix.
- Configs must work off macOS — a standing house rule. A requirement stated
  only in a molecule file does not meet it.
- The topic must stay a standalone executable with no runtime dependency. If
  the investigation finds a host library genuinely required, that is a
  finding to record, not a licence to add node or python.
- Idempotence and teardown properties already proven by `debian-lima` must not
  regress; the remove-twice and sentinel-preservation checks stay.
- Requirements must be **measured on a bare guest**, not inferred from the
  host. A missing library that happens to be present on the developer's
  machine is exactly the defect this task exists to catch.
- No claim that a distribution works unless a scenario ran against it. State
  untested platforms as untested.

Scoped deliberately loose. The author asked to keep this as a task to flesh
out later: the investigation decides the actual package list and how many
distributions are worth proving. The Ship bullets above are the shape; the
detail belongs in implementation.

Decision 2026-11-19: system requirements belong in the module and are proven
in a VM that installs the topic's dependencies, rather than being satisfied by
the test harness.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 The loreai role installs its Debian prerequisites through ansible.builtin.apt with when: os_family == 'Debian', following the apps/mise precedent, and molecule/debian-lima/prepare.yml no longer pre-installs what the role should own
- [ ] #2 topic_requires and topic_os reflect what the investigation measured, replacing the current topic_requires: []
- [ ] #3 The topic README states a requirements table: per platform the minimum OS, the C/C++ runtime floor the bundled native libraries need, and what is explicitly unsupported
- [ ] #4 A VM scenario installs the topic and its declared dependencies from a bare image, so the declaration itself is what gets exercised
- [ ] #5 Tested versus untested-but-expected distributions are stated explicitly; no distribution is claimed to work without a scenario having run against it
- [ ] #6 The native-library floor is measured on a bare guest, not inferred from a developer machine where the library happens to exist
- [ ] #7 Existing debian-lima properties do not regress: idempotence, remove-twice, and planted-sentinel preservation still pass
- [ ] #8 The board lists DOT-382 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
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
