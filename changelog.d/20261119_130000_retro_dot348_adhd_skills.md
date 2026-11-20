# Retro: DOT-348 — install the ADHD skills through dotagents

Merged via PR #188 (merge commit f867d548), 2026-11-19. Both ADHD sources and
the hardened plugin-targets.yaml are live on origin/main.

## What went well

- Two roborev review rounds caught real defects before merge: teardown aborting
  on a missing manifest (blockinfile create=false + missing file exits rc 257 on
  ansible-core 2.22.0), and the empty-list guard making absent-state unreachable
  so a stale managed block could never be cleaned. Both were fixed with
  mutation-proven tests (each new test was seen to fail against the unfixed
  tree). This is the review loop working as intended.
- Predeclaring the per-plugin targets block before `dotagents add` avoided a
  duplicate untargeted declaration — caught by a real isolated-HOME run, not by
  reasoning about the tool. The lesson: `dotagents add` preserves an existing
  targets list but cannot set one, so declaration order matters.
- Measuring the actual dotagents 3.4.0 behavior in an isolated HOME (rather than
  trusting upstream docs) is what surfaced the Copilot hooks rejection and the
  OpenCode skill-link-only boundary. Upstream docs lag the code.

## What went wrong / corrections

- Session context was lost repeatedly (server restarts, location moves). The
  DOT-348 implementation sat uncommitted on the branch across two days
  (Nov 15 → 17) and had to be re-inventoried after each restart. Durable
  artifacts (the branch, the task file) are what made resumption possible.
- The branch was amended by another session after I pushed it (a CI skip-guard),
  then had to be reconciled: I reset to the pushed tip and re-applied the guard
  as a NEW commit rather than force-pushing. Force-push on a published branch is
  restricted for a reason; re-applying as a new commit preserves both histories.
- The mdformat prek hook reformatted the README alongside a two-word doc fix
  (table alignment, ordered-list renumbering). Kept as-is per author ruling —
  the formatter enforces the repo's own style, so the churn belongs. But it is a
  reminder that "docs-only" commits can carry formatter churn that hides the
  intent change; review the actual diff, not the stat line.
- The stale README claim that plugin sources are "opencode-only" survived until
  this task corrected it. dotagents 3.4.0 wires claude and codex to the local
  marketplace too. The convention added to docs/TOPICS.md (keep verified
  corrections and upstream references with the topic) exists to stop this class
  of doc drift.
- roborev job 143 stalled ~28 min with no output before completing with a fail
  verdict. Long reviews of multi-commit branches with new test infrastructure are
  slow; the agent does thorough multi-file verification. Poll less, wait longer.

## Negative results (deliberately not done)

- Did NOT fork either upstream. Both ship canonical skills; a behavioral fork
  would just create another copy to maintain.
- Did NOT install i-have-adhd's OpenCode setup hook or /i-have-adhd command in
  this task — that is DOT-349 (queued). OpenCode gets the skill link only;
  always-on injection stays opt-in.
- Did NOT install the adhd-agent CLI — dropped per the author's 2026-11-17
  ruling. The skill alone drives the diverge/converge loop.
- Did NOT run chezmoi apply or mutate the live agent config. Live install is
  still pending the author's apply from main.

## Follow-ups (filed as tasks)

- DOT-349: native OpenCode adapter (setup hook, slash command, teardown) — the
  deferred B half. Queued, not started.
- Resolved 2026-11-20: the DOT-343 session reconciled and pushed shared main
  (4c4289f5 and 9d0f3aae). Local main is in sync with origin/main, and the
  DOT-348 closure commit 9ec504a remains in history. The live dotagents install
  is still not verified because this session did not run chezmoi apply.
