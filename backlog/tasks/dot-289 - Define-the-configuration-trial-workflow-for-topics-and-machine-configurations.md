---
id: DOT-289
title: Define the configuration trial workflow for topics and machine configurations
status: To Do
created_date: 2026-11-01 16:41
labels:
- design
- vm-tests
- topics
priority: high
references:
- backlog/decisions/decision-3 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
- backlog/decisions/decision-2 - Share-configuration-trials-through-one-observable-human-and-agent-lifecycle.md
updated_date: 2026-11-01 16:43
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Settled design: [decision-2: Share configuration trials through one observable human and agent lifecycle](../decisions/decision-2%20-%20Share-configuration-trials-through-one-observable-human-and-agent-lifecycle.md).

Author request 2026-11-01: developing a topic or changing the chezmoi repo should be triable in isolation before it touches a live machine. Desired shape: a fast disposable container (rootless Podman or Docker) for early feedback, then a disposable full-OS VM (existing rootless Lima/Molecule path) for real deployment verification, with an agent able to launch and try the candidate immediately. The author wants this to become the normal beta workflow for changing a topic or one instance of a topic for a given user's system configuration, with promotion only after review. This is a requirements/design task first (grill-with-docs), not a build. It must compose with decision-1 and DOT-271 (VM-verified gate, chezmoi apply + parent playbook) and DOT-272/DOT-273 rather than creating a parallel deployment system. Open decisions: which changes require a trial versus opt-in; the public interface for launching, snapshotting, rolling back and reporting a trial; whether a literal venv-like shell experience is required or an agent-driven disposable environment is sufficient; per-machine configuration declaration; container engine choice and its known limits (no systemd parity claims); where any runner tooling lives under the build-versus-configuration ladder. The Lore fork beta (DOT-282) is the first consumer/proof case, not part of this build.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A written requirements record settles trial scope, the container-then-VM lifecycle, rollback and promotion authority, and per-machine configuration declaration.
- [x] #2 The design names one public trial interface and its verification seams, reusing the existing Lima/Molecule machinery and decision-1 gates.
- [x] #3 The build home is decided through the AGENTS.md ladder before any runner code is written; machine-side wiring remains ordinary topic configuration.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Related author clarification: Lore should eventually be required memory infrastructure. The configuration-trial workflow must not turn required integrations into permanent optional bypasses. It supplies isolated evidence and controlled promotion; host resilience to plugin failure is investigated separately.

Author decisions, grill-with-docs round 1, 2026-11-01: every behavior-changing topic or chezmoi change gets at least one isolated trial; use a container for fast iteration and require a full VM for OS behavior or Decision 1 risk cases. Documentation-only changes skip trials. A configuration trial is an agent-driven disposable candidate environment, not a claim that the live shell and services can hot-swap like a Python venv. Successful trials produce evidence and a PR; they never apply to the real home or promote to the fleet without explicit author approval. After the Lore V2 port, investigate OpenCode plugin-failure modes before building general trial infrastructure or scheduled automation.

Author requirement, 2026-11-01: provide one common CLI for humans and agents to create, enter, observe, and try both container and VM trials interactively. HITL intervention must always offer a way to see what the agent can see. Settle terminal and graphical observation, read-only versus takeover behavior, and transcript/evidence access in the next interview round. Do not satisfy this with separate human-only and agent-only interfaces.

Author decisions, grill-with-docs round 2, 2026-11-01: support persistent interactive trials and one-shot autonomous verification runs through one lifecycle and one interface, not two deployment systems. Every run has a stable identity and produces a resumable, inspectable environment plus evidence; an autonomous run may finish while its environment remains available for review. Observation is read-only by default. The HITL controls are pause (block new agent input while preserving state), takeover (give the human exclusive terminal control), resume (return the same environment/session to the agent after inspection or correction), stop (halt agent processes), and destroy (a separate explicit operation). A trial pins the full candidate checkout and selected machine configuration; a topic focus limits testing scope, not the configuration actually applied.

The shared CLI and its agent integration belong in the existing topical repository, with dotfiles limited to machine installation and topic wiring. This follows docs/ROADMAP-topic-cli.md's settled one-repository CLI/plugin design; ai-prompt-library holds skills, not this machine-configuration runner. Existing research also supports reusing the installed Rancher moby engine, Lima lifecycle/snapshot/SSH primitives, and tmux read-only/control modes instead of inventing separate observation machinery. Rejected: persistent-only trials (autonomous setup cost and no exact finished environment to review), disposable-only runs (no interactive review of the exact result), immediate-stop-only control (loses state and unsafe checkpoints), cooperative-only stop (an unresponsive agent may continue), ai-prompt-library as build home (wrong ownership domain), and adopting a new environment runner without evidence it covers the whole requirement.

Author decisions, grill-with-docs round 3, 2026-11-01: use the installed Rancher Desktop moby/Docker engine for the initial fast container path and Lima for full-OS verification. A container trial never claims systemd or full-deployment proof; only the VM path can satisfy Decision 1's deployment gate. Reassess rootless Podman as a follow-up because the author considers its feature set ahead of Docker's, rather than installing a second engine before the workflow exists. Identify the target through the existing chezmoi facts (machine, arch, isMac, distro) and common/os/hosts declarations; do not create a competing trial-specific machine configuration format. Terminal observation and takeover work by default; graphical observation is opt-in for trials that need GUI behavior, with screenshots or a shared desktop as appropriate, while the existing headless VM remains the default.

Author decisions, grill-with-docs round 4, 2026-11-01: a successful trial publishes an evidence bundle plus a PR. The bundle contains structured trial metadata, candidate revision, machine profile, command/event logs, test results, GUI artifacts where enabled, and explicit limitations; PRs contain only reviewed non-secret evidence. There is no automatic apply or fleet promotion. The first vertical slice proves one container and one VM trial through the public behaviors: create and pin the candidate, run checks, read-only observe, pause/takeover/resume, retain evidence, and scoped destroy, with a negative test proving no live-home apply occurs. Do not expand the first slice into the full machine/provider matrix. Podman reassessment belongs to this requirements record: compare it later against the same shared lifecycle, rootless operation, observation, snapshot/evidence, and machine-profile requirements rather than treating Docker as permanently settled.

Author constraint, 2026-11-01: the container backend must run trials as the invoking user and preserve UID/GID ownership on bind-mounted candidate and evidence files. Root activity inside a disposable container or VM must never create root-owned artifacts in the live home or mounted checkout. The backend fails closed on unexpected ownership; a probe proving only that --user accepts a UID/GID is not sufficient evidence. No live-home write is part of this probe.

Reusability and reliability are binding requirements: the same public lifecycle and safety contract applies to humans, agents, containers, and VMs. A trial is reproducible from its pinned candidate and machine profile; a failed check leaves inspectable evidence and a recoverable environment; ownership and observation transitions cannot change silently. Reuse the existing Rancher, Lima, and tmux interfaces through narrow adapters rather than inventing a second lifecycle. The first slice proves this contract before generalization, and the Podman reassessment evaluates that same contract.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
