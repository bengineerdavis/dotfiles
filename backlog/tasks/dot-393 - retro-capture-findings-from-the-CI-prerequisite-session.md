---
id: DOT-393
title: 'retro: capture findings from the CI prerequisite session'
status: To Do
created_date: 2026-11-19 21:28
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Session retro (2026-11-19, `agent/claude_credential_path`, PR #185). This
records the evidence, the corrections, and the unresolved handoff. The CI
repair remains open in DOT-367; it is not Done.

**What worked**

- The original zsh fix used the existing real-shell/fake-Claude seam. CI
  installs zsh; the test harness resolves it from the supplied PATH.
- The chezmoi prerequisite was verified in an actual Ubuntu run
  (44586105725): `info installed /usr/local/bin/chezmoi`. That evidence
  disproves roborev job 150's High finding that the same step must fail
  with `Permission denied`.
- The unconfigured-chezmoi behavior was reproduced with an isolated shim,
  not inferred from a configured Mac: live-policy tests skip when the
  source directory is absent; the gitconfig tests skip when config data
  is missing. An existing source with an empty managed set still fails
  the nonempty assertion.
- The focused suite reached 30 passed, ruff and formatting passed, and
  Pyrefly reported 0 errors after the source-existence and checksum fixes.
  The source-existence guard and checksum guard each had a failing
  mutation run before the final focused pass.

**Corrections**

1. **Focused tests hid a full-suite regression.** Installing chezmoi
   globally flipped six previously skipping tests to failures because the
   runner has no source state or config data. Roborev job 149 caught this.
   The final implementation distinguishes a missing source directory from
   a real source with an empty answer, preserving the nonempty invariant.
   Lesson: changing a shared prerequisite requires a full-suite run, not
   only the tests that motivated it.
1. **The missing-PATH guard still leaked through a present None value.**
   `environment.get("PATH", "")` returns None when the key is present
   with a None value; `shutil.which` then searches the host PATH. The
   regression case failed before `environment.get("PATH") or ""` fixed it.
1. **Review findings were mixed with a false positive.** Job 150's High
   finding contradicted the successful CI log; its source-existence,
   comment, and checksum findings were actionable. A verdict does not
   make each finding true, and a successful run does not erase the others.
1. **`lore data recover --help` was not read-only.** It deleted 613 lines
   from `.lore.md` and six from `AGENTS.md` in the foreign worktree
   `/Users/ben.davis/code/forks/loreai/.worktrees/dot-282-opencode-v2`.
   The user was handed `git -C <that-worktree> checkout -- .lore.md AGENTS.md`
   to restore the uncommitted files. No further repair was attempted by
   this session; do not assume that restore was run. Probing an unfamiliar
   destructive-capable subcommand with `--help` is not a safety check.
1. **The session's PWD drifted to the foreign loreai worktree.** That is
   the same class of wrong-project behavior as DOT-386, not evidence that
   a repo's own path configuration was correct. A later remote PR head was
   a GitHub merge of main, not foreign code; it must be merged into the
   local branch, not overwritten with force-push.

**Negative results and remaining blockers**

- `lore import` found no prior conversation history; `lore data export`
  would reproduce corrupted DB content; neither repairs DOT-305.
- The two failing lore anchors are absent from the DB but survive in git
  history. No DB repair was performed. DOT-305 retains that work and its
  upstream-report requirement. Do not delete or reset the DB.
- The full-suite baseline still lacks the two `.lore.md` failures. It is
  owned by DOT-314 on `agent/retro-ci-guard`; this session must not take
  over that branch. PR #185 cannot merge green until that separate fix
  lands and CI is rerun.
- The earlier merge quiz answer "A or C" was not a clean pass: A named
  the host-PATH fallback that was explicitly removed. The corrected
  behavior is C. A merge requires the repository's quiz gate as well as
  review, green checks, and a current branch.
- The CI install now downloads the official v2.74.1 Linux archive and
  checks SHA256 ae01c66b1a6dbf563667c63fbbd9986b3cfa3c98dd266ddee732f63e8af2e9d1,
  read from the upstream release checksums. The revised archive install
  is Not verified in CI until a new run.
- The duplicate directories under `~/code/templates/` contained only
  agent scaffolding, not Git repositories; the two verified stubs were
  removed. DOT-386 already owns the root cause and notes live processes
  may recreate them. No process was stopped.
- If a worktree moves, check stale absolute paths in `.venv/bin/*`
  shebangs before reporting tests unrun; rebuilding the venv is cheap.

**Follow-ups**

- DOT-367: push the reviewed repair, request a fresh roborev review,
  rerun CI, and merge only when review and required checks pass. Record
  the exact branch/PR and handoff there.
- DOT-314: the known-failure baseline owner; not this session's branch.
- DOT-305: repair lore knowledge from verified historical entries with a
  backup, or re-capture them; upstream corruption report remains required.
- DOT-386: recover wrong-project sessions and their inherited PWD state.
- No duplicate task was created for the duplicate-directory root cause;
  DOT-386 already owns it.


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
