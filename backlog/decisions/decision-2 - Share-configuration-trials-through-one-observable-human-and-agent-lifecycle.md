---
id: decision-2
title: Share configuration trials through one observable human and agent lifecycle
date: 2026-11-01 17:26
status: accepted
---

## Context

Behavior-changing topic and chezmoi changes need an isolated trial before they touch a live machine. The author also needs a way to inspect an agent's environment, intervene safely, and return control to the agent without losing the candidate state.

The original requirements, interview history, rejected alternatives, and follow-up work are in [DOT-289: Define the configuration trial workflow for topics and machine configurations](../tasks/dot-289%20-%20Define-the-configuration-trial-workflow-for-topics-and-machine-configurations.md). [Decision 3](decision-3%20-%20VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md) is still proposed; ratification of its deployment gate is pending. Trials must not bypass the existing apply and review gates or presume that proposed gate is already accepted.

## Decision

Use one lifecycle and one shared topical CLI for persistent interactive trials and one-shot autonomous verification runs. A trial pins the full candidate checkout and the existing chezmoi machine facts. A topic focus narrows verification scope, not the configuration actually applied.

Use Rancher Desktop's moby engine for the initial fast container path and the existing Lima/Molecule path for full-OS verification. Containers never substitute for full-OS deployment evidence. Reassess rootless Podman later against the same lifecycle, observation, evidence, and machine-profile requirements.

Keep observation read-only by default. Provide pause, takeover, resume, stop, and destroy as distinct controls. Pause preserves state while blocking new agent input; takeover gives the human exclusive terminal control; resume returns that same environment to the agent; stop halts agent processes; destroy is a separate explicit operation. Terminal observation is the default; graphical observation is opt-in.

Run container trials as the invoking user and preserve UID/GID ownership on bind-mounted candidate and evidence files. Root activity inside a disposable environment must never create root-owned artifacts in the live home or mounted checkout. Unexpected ownership fails closed; accepting a --user argument alone is not evidence of safe ownership.

Publish an evidence bundle plus a PR only after review. The bundle includes structured metadata, candidate revision, machine profile, command/event logs, test results, GUI artifacts where enabled, and explicit limitations. PRs contain only reviewed non-secret evidence. No automatic live-home apply or fleet promotion occurs.

## Consequences

- The shared CLI and agent integration live in the topical repository; dotfiles supplies only machine installation and topic wiring.
- The first vertical slice proves create/pin, checks, read-only observation, pause/takeover/resume, evidence retention, and scoped destroy for one container and one VM trial. It also proves no live-home apply occurs and no root-owned artifacts appear in mounted files.
- Trials compose with Decision 1 and the existing apply/playbook and review gates rather than creating a parallel deployment system.
- Autonomous runs can finish while their exact environment and evidence remain available for human inspection and subsequent handoff.
- Reusability and reliability are binding requirements: one public lifecycle and safety contract applies to humans, agents, containers, and VMs. Every trial is reproducible from its pinned candidate and machine profile; failures retain inspectable evidence and a recoverable environment; ownership and observation transitions cannot change silently. Reuse happens through the existing Rancher, Lima, and tmux interfaces with narrow adapters, not a second lifecycle.
- The full machine/provider matrix is deliberately outside the first slice. The Podman reassessment must evaluate this same contract.
