---
id: DOT-318
title: Preview changes in a disposable Lima VM before the author runs update
status: To Do
created_date: 2026-11-09 00:00
labels:
- vm
- preview
- testing
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decided 2026-11-08 (author-approved): a standing preview process so a stream
of config changes is tested in VM isolation before it can break the real
machine. Inspired by the Docker CE migration (PR #143-era) that sat uncaptured
in the deployed tree; a broken real-machine state can cripple the ability to
work at all.

Two modes:
- **Scoped** (default): converge only the topics changed since the last
  preview, in a disposable Lima Debian guest, driven by a throwaway
  hosts:all play (the topic playbooks hardcode localhost, so they cannot be
  retargeted). Fast, per-change.
- **Full** (nightly): fresh guest, chezmoi apply of the whole payload, then
  update.sh-equivalent provisioning of every topic. Slow, scheduled.

Runs on demand (author or agent) and via a systemd user timer that catches
up after sleep/shutdown (author requirement: a sleeping machine must never
have a half-failed update hanging locally).

Healing authority (author-approved): the background agent may converge,
verify, fix tests, and open PRs from worktree branches — never touching
main, never running chezmoi apply against the real home, never merging its
own PRs. Failures are raised as backlog tasks / PRs.

Done when a scoped preview of a known-good change set passes end to end in
one command, the timer exists and survives a sleep, and the run files a
task for every failure it finds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] A scoped-preview command exists: given a topic list, boots a disposable Lima guest, converges those topics via a throwaway play, reports pass/fail per topic
- [ ] The throwaway play lives outside the repo (approved temp dir), never committed
- [ ] The wrapper reuses scripts/run-molecule.sh harness rules: isolated LIMA_HOME, short platform name, digest-pinned image
- [ ] A full-preview mode exists: fresh guest, chezmoi apply of the payload, then topic provisioning
- [ ] A systemd user timer runs the full preview nightly with Persistent=true (catches up after sleep/shutdown)
- [ ] Failures file backlog tasks automatically (one per finding), labeled vm-preview
- [ ] A background agent may fix tests/open PRs from worktrees; it never applies to the real home, never merges, never touches main
- [ ] Verified live once: a scoped preview of docker+apt+mise passes in a disposable guest (the Docker CE migration is the first subject)
<!-- SECTION:ACCEPTANCE:END -->

## Notes

<!-- SECTION:NOTES:BEGIN -->
Harness facts (measured 2026-11-08): guest home must resolve via
ansible_env.HOME (never hardcoded — cloud-init renames it); topic playbooks
are plays, not task files; limactl start/delete allowed for agents (PR #143);
scenario name "debian" is ambiguous (lima + loreai both have one) — address
scenarios as apps/<topic>/molecule/<scenario>.

Companion task: DOT-319 (healing agent loop).
<!-- SECTION:NOTES:END -->
