---
id: TASK-76
title: Adopt molecule for topic testing, with the vagrant driver where macOS is required
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
- blocked
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Adopt molecule for topic testing, with the vagrant driver where macOS is
  required.** Approved 2026-09-14. Molecule is the standard Ansible role test
  harness and its `idempotence` action is precisely the converge-twice check the
  task above wants, so this supersedes hand-rolling one. It also fits two
  decisions already made: scenarios live at `apps/<topic>/molecule/default/`,
  inside the topic, matching the co-location rule; and molecule is the
  conventional harness for collections, which is the direction the portability
  research points. Split the drivers by what they can actually reach — measured
  from `topic_os`: **19 topics are `[Darwin]`-only, 6 are both, 2 are
  `[Debian]`-only.** The docker/podman drivers are Linux containers and cover
  the 8 Debian-capable topics cheaply; the 19 Darwin-only ones — casks, launchd
  agents, `monitorcontrol`, `rancher-desktop` — cannot be containerised at all
  and need vagrant against a macOS VM. Unknowns to settle first, because they
  decide whether the Darwin half is affordable: which vagrant provider works on
  Apple Silicon (tart, UTM, Parallels — VirtualBox does not), image size, and
  Apple's licensing limit of two macOS VMs per host. Do not convert all 27 at
  once. Done when one Debian topic and one Darwin topic each have a scenario
  that converges and passes `molecule test`'s idempotence step. **herdr is
  the named first consumer** (judge round 1's accepted high gap: no
  automated converge; its pytest suite already covers everything molecule
  does not), the per-driver
  choice is written into `docs/TOPICS.md`, and the pytest suite still owns
  everything molecule does not — molecule tests convergence on a machine, not
  the repo's own logic. [blocked: needs the `--check` fix above, since a run
  that cannot dry-run cannot be trusted to converge twice either]
  **Plugin choices — corrected 2026-09-22, superseding the same-day note
  below it.** The first pass recommended `pytest-molecule` on PyPI metadata
  alone (Production/Stable classifier); checking its actual GitHub repo
  caught what the classifier hid: **archived 2023**, own notice says
  "functionality merged into pytest-ansible, switch there." Followed that
  chain and it dead-ends: pytest-ansible has *also* deprecated the same
  molecule-via-pytest integration and is itself EOL December 2026 (its
  README's own migration table, fetched directly). The stated reason is
  architectural, not fashion — wrapping each scenario as one
  `molecule test -s <scenario>` subprocess cannot support Molecule's own
  `shared_state` (create once in the default scenario, run component
  scenarios, destroy once) or `--workers` concurrency; those need
  Molecule's native multi-scenario orchestration. **Corrected choice: run
  `molecule test --all --workers 4` directly, no pytest wrapper** — this is
  also pytest-ansible's own recommended replacement for exactly this use.
  `pytest-testinfra` is unaffected by any of this (it's the verifier
  molecule scenarios call, not a molecule-orchestration plugin) and stays
  the choice for translating the herdr-style Python assertions
  (`host.file(...)`, `host.service(...)`) against post-converge state.
  `pytest-ansible` stays rejected, now with the sharper reason: not just
  the earlier self-deprecation quote, but a concrete EOL date and a
  published migration table (ADE for collection unit tests, tox-ansible for
  CI matrices, `ansible-inventory --list` + `pytest.mark.parametrize` for
  host iteration — none of which this repo currently uses pytest-ansible
  for, confirmed by grep, so there is nothing here to migrate, only
  something to not adopt).
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
