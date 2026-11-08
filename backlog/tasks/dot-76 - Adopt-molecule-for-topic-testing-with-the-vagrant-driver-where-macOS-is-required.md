---
id: DOT-76
title: Adopt molecule for topic testing, with the vagrant driver where macOS is required
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
- blocked
priority: high
updated_date: 2026-10-27 22:21
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
- [ ] #1 A Linux VM scenario for one Debian topic converges, passes idempotence, and asserts post-converge state — the stronger definition being a clean guest that runs chezmoi apply plus the dotfiles playbook and ends with the topic's own command succeeding
- [ ] #2 One Darwin topic has a scenario that converges and passes idempotence, using a provider chosen from the research file's evidence rather than assumption
- [ ] #3 The macOS provider choice records its rejected alternatives and why each failed (Apple Silicon support, image size, Apple's two-VMs-per-host limit)
- [ ] #4 A `macos-15` CI job runs the playbook twice and asserts idempotence (`changed=0.*failed=0`), replacing the earlier budget-based deferral — standard runners are free for public repositories
- [ ] #5 The per-driver choice is written into docs/TOPICS.md
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
## The research landed (2026-11-08), and it changes a decision

`docs/research/cross-os-vm-testing.md` (921 lines, primary sources) settles the
hypervisor question and overturns the CI decision recorded above.

**There is no legal, supported way to run a macOS guest on Linux.** Apple's
Virtualization.framework is macOS-host-only; Tart, UTM and Anka all sit on top
of it. Apple's SLA § 2B(iii) grants two VM instances for development and testing,
but only on Apple-branded hardware. OSX-KVM works technically on this box
(x86_64, SVM, /dev/kvm present) and is a Hackintosh outside the SLA — rejected.

**The Actions-minutes reason for deferring CI macOS runners does not hold.**
GitHub's billing docs: standard runners are free for public repositories, and
this repo is public. So CI macOS is $0, not a budget question. Verified.

**The strongest precedent needs no VM at all.** `geerlingguy/mac-dev-playbook`
runs the real playbook on `macos-15` and `macos-14`, twice, grepping for
`changed=0.*failed=0` (its `.github/workflows/ci.yml`). It uninstalls the
runner's preinstalled Homebrew first — otherwise the install tasks never run.

**Molecule has no macOS driver.** grep for macos/darwin across its source and
docs returns nothing. Its `delegated` driver can drive a Mac over SSH, and this
repo's `create.yml` already emits that instance shape — so a `darwin-lima`
scenario is a backend change, not a new harness.

**DOT-306's bug class needs no Mac.** chezmoi's deliverable tree renders for
Darwin on Linux (`-D --override-data '{"chezmoi":{"os":"darwin"}}'`), and
injected `os_family` facts select the Darwin Ansible branch — verified on this
host. That boundary is exactly right for path bugs and useless for module bugs
(`homebrew_cask`/`launchd` fail even in check mode).

### Revised order (supersedes "Linux VM first, macOS deferred")

1. **Linux VM end-to-end** for one Debian topic — unchanged, still the first
   half, and the definition of working from the merge above stands.
2. **A `macos-15` CI job** modelled on mac-dev-playbook. $0. This replaces
   "deferred on budget".
3. **Molecule-over-SSH to the real Mac** on demand, if 2 proves insufficient.
4. **Lima `vmType: vz` on the Mac** only if 1-3 all fall short.

The layout-fixture option (seed the other machine's tree, assert the committed
config resolves both ways) is scoped to DOT-306 and is the cheapest check for
the bug class that actually bit here.

Merged from DOT-311 (2026-11-08), which was created separately and is retired here
rather than duplicated. It adds the fleet framing this task lacked and records the
decisions taken since the original 2026-09-14 approval.

## Fleet framing and what "both machines" means

The fleet is exactly two machines: one Linux desktop (Pop!_OS, amd64, KVM
available) and one Apple Silicon Mac (arm64). Every topic declaring
`topic_os: [Darwin, Debian]` needs its converge path proven on both. Today only
the Linux half is real — `limactl` 2.2.1 boots Debian 12 guests through the
shared adapter at `home/dotfiles/apps/lima/molecule/shared/`, driven by
`scripts/run-molecule.sh`.

Definition of "working" for the Linux half, deliberately stronger than
"ansible converged": a clean guest that has run `chezmoi apply` plus the
dotfiles playbook, and ends with `gita ls` listing registered repos and
`gita fetch` succeeding. That is the only definition that tests something the
host cannot, because the host is already configured.

## macOS guest: open question, with the unknowns named

Lima runs Linux guests on macOS, not macOS guests, so this task's original
"vagrant against a macOS VM" plan needs the hypervisor question settled. For
Apple Silicon that narrows to Virtualization.framework-based tools (UTM, Tart,
Anka); VirtualBox does not work. The unknowns this task already listed remain
the blockers: which provider works on Apple Silicon, image size, and Apple's
licensing limit of two macOS VMs per host.

## Decisions taken 2026-11-08

- **Linux VM first.** Get the Debian scenario end-to-end before spending on the
  macOS half.
- **CI-based macOS runners deferred.** `macos-14`/`macos-15` are not the
  fallback yet: the GitHub Actions minutes budget for private repos is not
  settled.
- **A layout-seeded Linux VM is not a substitute for OS testing.** One VM per
  target OS environment across the fleet is the requirement. A fixture seeded
  with the other machine's directory layout tests data, not platform — it may
  still be the right check for a specific bug class (a committed config
  carrying one machine's paths), which is DOT-306's problem, not this task's.

Research in flight at `docs/research/cross-os-vm-testing.md`: what actually runs
a macOS guest, how Ansible/Molecule practitioners test macOS roles, what
GitHub's macOS runners provide, and what comparable dotfiles repos do. Read it
before choosing a provider.


<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
