# TASKS-RESOLVED.md

A stopgap archive for resolved tasks, ahead of the process refactor queued in
`TASKS.md` § Planned. The convention says a finished task is deleted — "the
commit is the record" — but the queue now spans two machines, and a task
deleted into flattened git history is hard to audit later. Until the
replacement process exists, resolved work moves here instead: one entry per
task, with the outcome, the evidence, and where the durable record lives.
Newest last. Do not grow this file past the refactor — it exists to be
deleted.

## 2026-09-14

- **Approved-source allowlist replaced `apps/opencode`'s per-skill manifest,
  with a guard.** Resolved by the other machine's session (landed via merge
  a586c5b — the opencode defaults change in e60982c, the skill-trust/guard
  work in 10ccccd and 33f6ad7; machine attribution is not verifiable from
  git, identical author identity on both sides; verified against the tree
  2026-09-14). `dotfiles/apps/opencode/defaults/main.yaml`
  now holds approved *sources* — owner/repo shorthand, a `why`, per-source
  `exclude` vetoes — wired to `dotagents trust add` and
  `dotagents add <source> --all`; the guard
  `dotfiles/roles/guards/tasks/dotagents-approved-sources.yaml` also compares
  on-disk skill directories against the declared set, so a hand-placed skill
  is reported rather than ignored. All three done-conditions met: the topic
  names only sources, an unapproved source fails the run, an undeclared
  on-disk skill directory is reported.
- **Source denylist and licence-as-implicit-trust shipped as
  `tools/skill-trust`.** Same session; verified 2026-09-14.
  `tools/skill-trust/skill_trust/decide.py` implements the full precedence
  (denied source > excluded skill > approved source > approved licence >
  deny), the three licence tiers (permissive auto-trusts, copyleft opt-in,
  source-available denied — BSL-1.1, FSL, SSPL, Elastic-2.0), and
  absent-is-not-permissive (no LICENSE or `NOASSERTION` → deny). Follow-on
  still open in § Now: a topic should install skill-trust rather than the
  current hand install.

## 2026-09-15

- **A8 — what each dependency manager requires of a topic, as data the CLI
  can read.** Delivered 2026-09-14 by the other machine's session as
  `dotfiles/managers.yaml`; the handoff snapshot and A9 both record it
  delivered, yet the task line stayed queued — found by the advisor pass.
  The design detail (four axes: variables, privilege, currency, channel
  selection; per-manager exceptions) is in git history under the A8 task
  line and in the file itself. Moved here per the finish-a-task convention.
- **Document that `git add -p` and `git commit -o` do not compose.** Landed
  2026-09-15: AGENTS.md § Working alongside other sessions now teaches the
  correct sequence for a co-edited file (add -p, then a bare commit with
  nothing else staged, then verify with `git show --stat HEAD`) instead of
  pairing `-o` with partial staging. Fixed before it bit — the advisor pass
  caught AGENTS.md still teaching the unsafe combination while the fix sat
  queued here.
