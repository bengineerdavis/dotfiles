---
id: TASK-146
title: Give privileged topics a dedicated ansible user per environment, and a service
  that runs configurati
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Give privileged topics a dedicated ansible user per environment, and a
  service that runs configuration updates.** Today the five apt-using topics
  (`docker`, `clamav`, `lynis`, `mise`, `ollama` — the only `become: true`
  topics, per `dotfiles/managers.yaml`) escalate through whoever happens to be
  running the playbook, which means an unattended update is impossible and an
  attended one carries the human's full sudo rights. A dedicated account fixes
  both: the service has an identity, and its powers can be smaller than a
  person's.
  **Scope the privileges before building anything.** A service that can apply
  machine configuration unattended is a standing grant, not a convenience — the
  sudoers entry should enumerate the specific commands the playbook actually
  needs rather than `NOPASSWD: ALL`, and `dotfiles/managers.yaml` already names
  which managers need escalation and which do not, so the list is derivable
  rather than guessed. `docs/PERMISSIONS.md` is the relevant prior art and is
  blunt that this layer stops accidents, not a misaligned or prompt-injected
  agent; a scheduled runner with root is exactly the thing that document warns
  is not contained by permissions. Decide deliberately whether the service ever
  runs agent-authored changes, or only reviewed ones.
  Per environment, because the two boxes differ: launchd on Darwin, systemd on
  Debian. Both have precedent here — `apps/ollama` installs a launchd agent and
  `apps/clamav` a systemd timer — so this is a new user and a new unit, not a
  new mechanism. Done when each machine has an ansible user whose sudo rights
  are enumerated and reviewable, a scheduled unit that applies configuration and
  reports what it changed, and a documented way to run it by hand.
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
