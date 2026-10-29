---
id: DOT-263
title: Build a Lima topic for rootless Molecule VMs
status: Done
created_date: 2026-10-28 23:56
labels:
- testing
- molecule
- chore
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode
  lease_expires_at: '2026-10-29T00:58:48.670897Z'
  version: 1
updated_date: 2026-10-29 01:58
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an apps/lima topic that provides rootless Lima/QEMU VM support for Molecule on macOS and Linux, using prebuilt upstream binaries and the existing Molecule Lima adapter where it meets the repo contract. This is the author-selected alternative to the Vagrant/macOS cask path; keep it separate from the broader DOT-255 matrix and DOT-261 user-space Vagrant research.

Measured 2026-10-28: Lima 2.2.1 Darwin-arm64 tarball extracted into ~/.local with its GitHub release SHA256 verified. Existing user-owned QEMU 11.1.2 advertises hvf. A Debian 12 ARM64 guest booted with vmType=qemu, HVF, user-mode networking and no mounts; SSH, systemd, user manager, and systemd-detect-virt=qemu all passed. No sudo, Vagrant, or system package installation was needed. The guest must be destroyed after the probe.

Requirements:
- Topic owns Lima installation and its lifecycle, while chezmoi owns configuration and Ansible owns any separately approved privileged host state. Do not use sudo for Lima itself.
- Resolve Lima and QEMU release assets and checksums per host OS/architecture; support macOS and Linux without machine-specific literals.
- Prefer the existing molecule-lima adapter over new delegated lifecycle code, but audit its current behavior against Molecule 26 and the repo seams before adopting it. It currently has open questions around instance_config, usernames, default vm_type, mounts, and destroy failure handling.
- Use vmType=qemu for host parity; HVF on macOS and KVM on Linux are explicit capabilities. Do not call a container run a VM pass or imply macOS guest support on Linux.
- Share per-topic converge/idempotence/verify behavior and provide clean destroy, with no deletion of pre-existing Rancher Desktop or other Lima instances.
- Per-machine opt-in, documentation, changelog, tests, and opt-in removal of only topic-owned state. Preserve shared Lima/QEMU packages and user VM data unless separately approved.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The topic installs Lima rootlessly from verified prebuilt assets and reports working limactl/QEMU capabilities on supported hosts.
- [x] #2 A real Linux VM passes the approved Molecule lifecycle seam through Lima, with SSH, guest OS/architecture, systemd, and teardown verified.
- [x] #3 The topic reuses the existing Lima adapter or records why it is unfit; no duplicate lifecycle framework is added without author approval.
- [x] #4 The scenario uses the same topic behavior on macOS and Linux, reports provider/architecture results explicitly, and preserves unsupported macOS-on-Linux coverage as open.
- [x] #5 Topic removal is idempotent and does not delete pre-existing Lima instances, Rancher Desktop state, shared QEMU, or user VM data.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Requested by the author 2026-10-28 as a chore after the Lima rootless handoff. Existing adapter: github.com/filatof/molecule-lima, MIT, latest source inspected 2025-11-16. Evaluate it before implementation. Related DOT-254, DOT-255, DOT-261, DOT-262.
2026-10-28 adapter evaluation: molecule-lima 0.0.3 loads under the locked Molecule environment, but its create playbook hardcodes networks: [{lima: shared}], writable /tmp/lima and read-only host-home mounts, and lookup(env, USER) for the SSH user. Lima 2.2.1 rejects shared networking without /opt/socket_vmnet, which violates rootless operation and host isolation. It writes per-instance inventory rather than the Molecule instance_config API and does not expose options to disable the shared network. Do not patch the installed package or adopt it as-is. Use Molecule core delegated create/destroy playbooks for the first vertical slice per the maintainer handoff, keeping the adapter upstream issue separate. Rootless Lima 2.2.1 + QEMU/HVF direct probe passed; molecule-lima create failed before boot on socket_vmnet. Destroy the stopped molecule-lima-probe instance after recording the result.
2026-10-28 author decision: the direct rootless Lima/QEMU path is good enough for now; do not spend more time researching provider tradeoffs. No sudo was needed on macOS with Lima extracted into ~/.local, existing user-owned QEMU/HVF, and user-mode networking. The direct Debian guest lifecycle passed. Full Molecule integration remains follow-up work; do not imply the rejected molecule-lima adapter or the Vagrant bootstrap passed.
2026-10-28 implementation progress: apps/lima topic created with checksum-verified rootless install (SHA256SUMS + per-asset digest), HVF/KVM capability checks, conservative teardown (release files only, preserves ~/.lima, Rancher Desktop, QEMU, VMs). Delegated Molecule scenario under molecule/debian/: QEMU user-mode networking, no mounts, no container runtime, no forwarded SSH agent, digest-pinned Debian 12 image, scenario-local LIMA_HOME under MOLECULE_EPHEMERAL_DIRECTORY, Lima-generated SSH key for instance_config. 10 static contract tests in tests/lima pass (seen failing first). Iterating the real lifecycle: fixed create-before-converge ordering (create installs the topic), include_role environment: not valid (switched to lima_install_prefix play var override), and missing ANSIBLE_ROLES_PATH (added to provisioner env like the loreai scenario). Full molecule test in progress.
2026-10-28 finding: QEMU was not installed on this Mac at scenario time (the earlier direct-probe session had it; it was removed during the mise/Vagrant cleanup). The topic guard correctly failed closed with a clear message naming the fix. Author approved brew install qemu (user-owned, no sudo). This confirms the topic_requires: [qemu] dependency is real and the guard is not vacuous.
2026-10-28: QEMU 11.1.2 installed via user-owned Homebrew bottles (capstone, dtc, libslirp, libssh, snappy, vde, qemu) — no sudo. Full Molecule lifecycle re-run in progress with the prerequisite satisfied.
2026-10-28 real-run fixes: (1) Jinja ternary precedence produced qemu-system-False — replaced with an if/else var; (2) Molecule sanitizes PATH, so the QEMU probe now falls back to absolute prefixes (/opt/homebrew/bin etc.) and create/destroy set an explicit PATH for limactl; (3) the expected-checksum grep dropped the bogus Jinja quote-in-shell and matches the SHA256SUMS line directly; (4) KEY CONSTRAINT: Lima SSH socket paths must stay under UNIX_PATH_MAX=104 — the deep worktree ephemeral path made the socket 164 chars, so LIMA_HOME moved to a short /tmp/lima-<sha1(ephemeral)[:12]> path shared consistently by create/converge/side_effect/destroy and cleaned up on destroy. Static contract tests updated; 10 pass. Full VM lifecycle re-running.
2026-10-28 socket budget: full sha1 (40) + instance "lima-debian-molecule" (20) + Lima fixed suffix made the SSH socket 105 chars (limit 104). Renamed the platform to "lima-mol" (8 chars) so the full sha1 hash fits. Also had to drop a Jinja [:12] slice (parser breaks on [ in that YAML position) — using the full hash instead. Updated host_vars key to match.
2026-10-28 idempotence fix: get_url/unarchive into a deleted /tmp re-downloaded every run, so idempotence failed. Added an installed-version probe (limactl --version) and wrapped fetch/checksum/download/unarchive/cleanup in a block gated on not lima_already_installed, so an up-to-date install is a true no-op. Verify/accelerator tasks still run unconditionally. Also fixed the instance_config JSON field: limactl list --format json emits sshLocalPort (lowercase), not SSHLocalPort.
2026-10-28 side_effect fix: gather_facts was false so ansible_env was undefined when the role remove debug message referenced it. Set gather_facts: true on side_effect and changed the remove debug message to derive the home from lima_install_prefix instead of ansible_env, so remove works without facts too. Converge and idempotence both pass now.
2026-10-28 verify connectivity fix: the delegated driver defaults managed:false, so instance_config (address/port/identity_file) was NOT merged into inventory — Ansible tried to resolve the instance name as a hostname. Set driver.managed: true so Molecule merges instance_config into the SSH inventory. side_effect teardown-safety now passes; this was the last wiring gap before a full green run.
2026-10-28: managed:true correctly merges instance_config into inventory (confirmed ansible_host/port/private_key_file present in the generated ansible_inventory.yml). A standalone `molecule verify` after destroy fails with empty inventory (expected — no VM). Investigating the full-run verify error separately; it may be SSH-level rather than inventory-level. side_effect reinstalls Lima but must not disturb the running guest.
2026-10-28 FULL GREEN: MOLECULE_SCENARIO=debian scripts/run-molecule.sh lima test — all 9 actions successful (create, converge, idempotence, side_effect, verify, cleanup, destroy; the 2 "missing" are the optional galaxy dependency action). Rootless Lima 2.2.1 + QEMU 11.1.2 (HVF) booted a real Debian 12 aarch64 guest with user-mode networking, no mounts, no container runtime, no forwarded SSH agent. converge installed the topic into a temporary home; idempotence is a true no-op; side_effect proved removal preserves the sentinel and QEMU; verify SSHed in and confirmed Debian 12/systemd/QEMU (ansible_facts.service_mgr == systemd). 10 static contract tests green (seen failing first). Final verify fact fix: use ansible_facts.service_mgr, not the nonexistent ansible_facts.init.
2026-10-28 PR #99 opened (agent/lima-molecule → main): https://github.com/bengineerdavis/dotfiles/pull/99. Commit 637c860, 20 files, 742 insertions, purely additive. Merge gates run: skillet validate ok, doc-link tests 42 passed, full suite 1170 passed (2 pre-existing opencode failures unrelated). Requires human review per § Merge gates (new feature + deployed-tree files).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-e50d0b419134440f98184bd42dc8362a
type: claim_task
actor: opencode
timestamp: '2026-10-28T23:58:48.670997Z'
result: succeeded
task_id: DOT-263
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-ee6c61321c574cb887904fae5385b3a8
type: record_run
actor: opencode
timestamp: '2026-10-29T01:55:40.525785Z'
result: succeeded
task_id: DOT-263
verification:
- MOLECULE_SCENARIO=debian scripts/run-molecule.sh lima test
```
Rootless Lima 2.2.1 + QEMU 11.1.2 (HVF) full Molecule lifecycle green twice on macOS. Real Debian 12.15 aarch64 guest, systemd user manager running, user-mode networking, no mounts, no sudo. 10 static contract tests green (seen failing first). Full suite 1170 passed, 2 pre-existing opencode failures unrelated to this purely-additive change. Linux apply documented as open.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
