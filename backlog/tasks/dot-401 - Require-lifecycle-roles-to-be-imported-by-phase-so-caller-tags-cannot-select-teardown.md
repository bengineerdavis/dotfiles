---
id: DOT-401
title: Require lifecycle roles to be imported by phase, so caller tags cannot select teardown
status: To Do
created_date: 2026-11-20 18:27
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

**Why.** A role imported as a whole carries the importing task's tags down into
every phase underneath it. `--tags install` then selects the teardown too, and
`never` cannot stop it: `never` skips a task only when nothing else selects it,
and the inherited `install` tag does select it.

Measured 2026-11-20: a tagged install of the backlog topic stopped the live
daemon, deleted its plist, and left a replacement whose `ProgramArguments` was
the mise shim alone. `roles/services` is fixed (PR #197) by having callers pass
`tasks_from`, and by making `tasks/main.yaml` fail loudly on a whole-role
import. Every other role is unaudited.

**Ship**

- Audit each role that has more than one lifecycle phase, and record per role
  whether a whole-role import is possible: `roles/services` (fixed),
  `roles/guards`, `roles/restart-stale`, `roles/topic-resolution`,
  `roles/secrets-session`.
- Give each lifecycle role the same loud guard `roles/services` now has, so a
  caller that forgets `tasks_from` fails instead of running both phases.
- State the rule where role authoring is taught, so the next role does not
  re-derive it.
- Cover `roles/guards` and `roles/secrets-session`, which have no
  `tasks/main.yaml` at all — Ansible treats such a role as having no tasks, so
  a whole-role import silently no-ops rather than failing.

**Constraints**

- A role with no `tasks/main.yaml` must not be "fixed" by deleting the router:
  that is the silent no-op shape, not a fix. Do not remove `main.yaml` from any
  role.
- Do not change a role's task behaviour; this is about import routing.
- `roles/services` is the reference implementation — follow its shape.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Every lifecycle role is audited and its whole-role-import behaviour recorded
- [ ] #2 Each lifecycle role fails loudly on a whole-role import, matching `roles/services`
- [ ] #3 The phase-import rule is stated in the docs that teach role authoring
- [ ] #4 `roles/guards` and `roles/secrets-session` no longer silently no-op when imported whole
- [ ] #5 No role loses its `tasks/main.yaml`

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
