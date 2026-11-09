---
id: DOT-324
title: A stale Molecule artifact in the main checkout fails four chezmoi tests and is not in the CI baseline
status: To Do
created_date: 2026-11-08 17:15
labels:
- bug
- testing
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Four `tests/chezmoi` cases fail on this host for a reason that has nothing to
do with the code under test, and the failure is not in the CI baseline. On a
host in this state the merge gate cannot come out green.

**Correction to an earlier report.** I first attributed this to
`tests/merge_gates/test_cli.py` with "9 errors on main". That was wrong —
`tests/merge_gates` passes 43/43 on both main and the feature branch. The
actual failing set is one `tests/chezmoi` failure plus three errors, and it
reproduces identically with the branch's changes stashed:

```
FAILED tests/chezmoi/test_config_identity.py::test_config_template_keeps_its_data_section
ERROR tests/chezmoi/test_gitconfig_tools.py::test_mergetool_labels_all_three_panes
ERROR tests/chezmoi/test_gitconfig_tools.py::test_difftool_labels_both_panes
ERROR tests/chezmoi/test_gitconfig_tools.py::test_no_empty_named_tool_sections
```

**The error, verbatim:**

```
chezmoi: stat
  /home/bdavis/.local/share/chezmoi/home/dotfiles/apps/lima/molecule/debian/.molecule/controller/.local/share/doc/lima/templates:
  no such file or directory
```

**Root cause, established 2026-11-07.** A Molecule run was killed part-way
through `unarchive` of the Lima release tarball. Extraction is alphabetical,
so `share/doc/lima/` landed but `share/lima/` did not, leaving a dangling
symlink `share/doc/lima/templates -> ../../lima/templates` inside a partially
installed tree. That tree sat in the scenario's `.molecule/`, which was inside
chezmoi's source walk at the time.

The failure is specific and was measured in an isolated scratch source:

| Command | Broken symlink in a dot-dir |
|---|---|
| `chezmoi managed` | rc=0 — stays green |
| `chezmoi status` | rc=0 — stays green |
| `chezmoi apply` | rc=1 |
| `chezmoi execute-template` | rc=1 |

So a check built on `status` or `managed` detects nothing. Chezmoi resolves
the whole symlink chain while loading source state, and only `apply` and
`execute-template` walk far enough to trip.

**Why this is still open after DOT-303.** DOT-303 moved future run state out
of the source (PR #148), so this class cannot recur for new runs. It does not
clean up the state already there, and it does not make the failure visible:
the four tests fail with a message about `templates` that names neither
Molecule nor the artifact. DOT-309's report catches in-source legacy state
only when the wrapper runs for that scenario.

**Two subsets to separate.** This task is the *existing artifact*, not the
class. The class — no reaper on a Mac, and no guard that would notice a
broken symlink in the source — belongs to DOT-323. Do not let a fix here
stand in for a fix there.

**Why it is not in the baseline.** `scripts/check_suite_baseline.py` compares
exact node IDs, and `AGENTS.md` § Known failures lists only `tests/clipped`
and `tests/restart_stale`. Adding these four would make CI green on a
condition that only one machine has, which is the wrong repair — the right
question is whether the artifact should exist at all.

**What has to be decided.** The artifact is VM state, not the author's
working files, but deleting it is destructive and it may belong to a run
some-body else has in flight. DOT-256's rule applies: destructive cleanup
must resolve a unique, test-created identifier and fail closed when it
cannot, never infer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The cause is confirmed or refuted by evidence — the dangling symlink named, its target shown missing — rather than inferred from the error text
- [ ] #2 Whether the artifact is safe to delete is decided with the author, and the decision recorded, since it is VM state and may belong to a live run
- [ ] #3 After the fix, `tests/chezmoi` is green on this host without stashing changes, proven by a run recorded on the task
- [ ] #4 The failure is either impossible to recur or impossible to miss: a broken symlink under the chezmoi source is detected by something that actually fails on it — not by `status` or `managed`, which stay green (measured)
- [ ] #5 `AGENTS.md` § Known failures either gains these node IDs with the reason, or the task records why the baseline stays as it is
- [ ] #6 The four failing tests are named on the task with their full node IDs, so the next reader recognises them without re-running the suite
<!-- AC:END -->

## Implementation Notes
<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Start with `git stash -u` and re-run to prove the failure is not the current
branch's — that is the check that separated this from DOT-302's work.

The artifact is at:

```
home/dotfiles/apps/lima/molecule/debian/.molecule/
```

It is gitignored (`.gitignore:25`), so `git status` never shows it. It was
created 2026-11-06 12:14 by a run from the main checkout; the broken link
inside it dates from 2026-10-03.

Finding the symlink: `find home/dotfiles/apps/lima/molecule -xtype l` lists
dangling links. `.molecule` is a dot-dir, so `chezmoi managed` will not list
it — the source walk that matters here is `execute-template`'s, not
`managed`'s.

Do **not** fix this by adding the node IDs to `EXPECTED_FAILURES` alone. That
hides a machine-specific condition behind a green check.

Related: DOT-303 and DOT-309 (PR #148) moved run state out of the source and
added a legacy-state report; DOT-323 (macOS, and the broken-symlink guard);
DOT-256 (fail-closed destructive cleanup).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `uv run --frozen pytest tests/chezmoi` is green on this host, and a broken symlink in the source can no longer fail four unrelated-looking tests
<!-- DOD:END -->
