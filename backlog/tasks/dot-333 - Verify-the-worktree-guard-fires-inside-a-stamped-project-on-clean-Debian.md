---
id: DOT-333
title: Verify the worktree guard fires inside a stamped project on clean Debian
status: To Do
created_date: 2026-11-09 00:45
labels:
- testing
- templates
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The worktree guard (`template/scripts/check-worktree.sh` in
`agentic-project-template`) is tested by pytest against a temporary git
repository. That proves the logic. It does not prove the guard **fires in a
stamped project** — that the file lands executable, that `prek` picks it up
from a real checkout, and that the hook runs under the conditions a fresh
machine has rather than the conditions this developer machine has.

The stamp test added in `test_stamp.py` proves the file arrives executable and
wired. That is a different claim from "the hook actually executes and blocks".
The gap between them is a fresh environment.

This is where a VM earns its place, unlike the guard's own unit tests. The
`apps/lima` topic already provides a rootless Debian VM harness
(`molecule/debian` plus `molecule/shared`, delegated driver over QEMU
user-mode networking), run with:

    bash home/dotfiles/executable_run-role.sh lima

Two related gaps worth covering in the same scenario, since they share the
setup cost:

- The `wt-owners` module's liveness probe shells out to `opencode api get`.
  On a machine with no running daemon it must report an *environment* fault,
  not a policy violation. That distinction is unit-tested with a stub and has
  never been exercised against a real absence.
- `git commit-tree` in `claim` supplies its own fallback identity after CI
  caught it failing on a runner with no `user.email`. Worth confirming on a
  box that has never had git configured.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 In a clean Debian VM, stamp a project from `agentic-project-template` and confirm `scripts/check-worktree.sh` exists and is executable.
- [ ] #2 In that stamped project, an agent commit from the main checkout is refused, with the guard's own message rather than a shell error.
- [ ] #3 In the same VM, `wt-owners claim` succeeds with no global git identity configured.
- [ ] #4 The liveness probe against a genuinely absent daemon reports an environment problem, not a policy violation.
- [ ] #5 The scenario is disposable: it leaves no VM, no instance, and no state outside `~/.cache`.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Raised 2026-11-09 from the retro on the worktree-guard session.

Why not just run the pytest suite in the VM: the suite would pass, because it
builds its own fixtures. The claim under test is about the *stamped* artifact
in a *host* environment, so the scenario has to stamp, then attempt a real
commit, then read what happened.

Related: DOT-271 (VM-verified config gate) covers the chezmoi side of the same
idea. This task is the template-repo side, and the two should share the Lima
harness rather than each building one.

### Provenance

Raised by the session that built the guards this task verifies, 2026-11-09.
The two PRs are what there is to verify against:

- agentic-project-template [#5](https://github.com/bengineerdavis/agentic-project-template/pull/5)
  (`53b7382`) — the commit-time guard.
- agentic-project-template [#8](https://github.com/bengineerdavis/agentic-project-template/pull/8)
  (`ac50d67`) — branch ownership, `refs/wt-owners/*`.

Both merged with unit and stamp tests passing; neither has been run in a
stamped project on a host that is not the author's. That gap is this task.

The commit graph is the authorship record: `git log 53b7382` and
`git log ac50d67` in agentic-project-template carry the reasoning, the
mutations tried, and what each change deliberately excluded. Session notes
lived outside the repo by design — `docs/` holds durable reference, not
per-session narrative — so nothing here points at a machine-local path.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A stamped project on clean Debian demonstrably refuses an agent main-checkout commit, and the run is documented in the task.
<!-- DOD:END -->
