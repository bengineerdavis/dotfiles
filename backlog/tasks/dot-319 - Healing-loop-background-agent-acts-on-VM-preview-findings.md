---
id: DOT-319
title: Healing loop — background agent acts on VM-preview findings
status: To Do
created_date: 2026-11-09 00:00
labels:
- vm
- healing
- agents
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The second half of the DOT-318 decision: when the preview finds a failure, a
background agent acts on it without waiting for the author to be present.

Approved authority (author, 2026-11-08): the agent may
- converge and verify freely inside the disposable guest,
- fix tests and open PRs **from worktree branches**, so main stays clean at
  the last locally-working state,
- file backlog tasks for anything it cannot fix,
- notify (push branches, open PRs, comment findings).

Hard boundaries (standing rules, unchanged):
- never run `chezmoi apply` against the real home,
- never merge its own PRs,
- never commit to main directly.

Done when a seeded failure (a deliberately broken topic change) is detected
by a preview run, raised as a task, fixed by the agent in a worktree, and
verified green by a re-run — all without author intervention.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] The preview wrapper exposes a machine-readable failure report (JSON: topic, step, error, evidence)
- [ ] The healing agent consumes that report, fixes in a worktree branch, pushes, opens a PR
- [ ] The agent never applies to the real home, never merges, never commits to main (enforced, not just documented)
- [ ] A re-run of the preview proves the fix green
- [ ] Verified once end to end with a deliberately seeded failure
<!-- SECTION:ACCEPTANCE:END -->

## Notes

<!-- SECTION:NOTES:BEGIN -->
Depends on DOT-318 (the preview run it acts on). Budget note: the healing
agent is a writer — .agent-budget.toml workers=1 gates when it may run, per
the fail-closed budget rule.
<!-- SECTION:NOTES:END -->
