---
id: DOT-209
title: Factor a general git repository template out of this work, using copier
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Factor a general git repository template out of this work, using copier
  (9.17.2, installed). **Its own repository at `~/code/personal/`**, alongside
  ai-prompt-library and impromptu — not a directory here, and not under
  `~/code/work/`. Name is not settled; it is the reusable half of this repo's
  practice, so something like `spec-driven-repo-template` describes it. What has
  earned its place and is not dotfiles-specific: the document set and its
  separation of concerns (PRD what-for, spec what-must-stay-true, ROADMAP
  what-is-next, TASKS what-is-now, AGENTS how), the RECL loop, the verification
  practices (both-directions, prove-the-test-fails, property and fuzz guidance),
  the branching and merge-gate conventions, and the Python toolchain section.
  Excluded: anything chezmoi, Ansible or model-specific, and anything
  language-specific — language conventions are a pluggable `<LANGUAGE>.md`
  chosen by copier prompt, so the template ships `docs/PYTHON.md` as one
  option rather than baking Python into AGENTS.md. `docs/` is the unit
  the template plugs into — adding a language means dropping one file there. That is what lets the template grow to
  cover other languages without a rewrite. This template IS the
  reusable AGENTS.md baseline, so the baseline-versus-overlay split happens here
  rather than separately. Done when a fresh repo scaffolded from it has the full
  document set, passes `skillet validate`, and asks its project-specific parts as
  copier prompts rather than leaving placeholders to hand-edit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

**Three-template sweep (author, 2026-11-08).** This task predates the
three-template split the author now intends: chezmoi migrates to being stamped
by all three of `agentic-project-template` (agentic layer),
`python-project-template` (Python CLI base), and
`copier-template-copier-template` (meta — scaffolds new templates). Sweep of the
merged PRs and `CHANGELOG.md` for shareable items that are not dotfiles / chezmoi
/ Ansible / model-specific, classified by which template they belong to. Each
item is a candidate feature request; file them on the owning repo's queue with
the maintainer's acknowledgment (AGENTS.md § Cross-repo changes) — do not
silently commit to a foreign repo.

**agentic-project-template** (agent/coordination/trust/policy):

- Trust ladder + LEDGER — `docs/TRUST-LADDER.md` and DOT-208 (rungs 0-4,
  promotion streaks 5/10/20, incident classes A-D, deterministic vs judgment
  track). [noted on DOT-208]
- Open-PR / review-merge policy — DOT-322 (push + open PR allowed; merge stays
  human-approved; the guard is on the merge, not the PR). [noted on DOT-322]
- Multi-agent coordination layer — DOT-57 (worktree-per-agent, frozen leases,
  risk-tiered merge gates, read-only `.git`, rerere). [noted on DOT-57]
- v2 permissions-array semantics — `opencode.jsonc.tmpl`: ordered rules, LAST
  match wins, catch-alls first, destructive carve-outs after broad allows
  (changelog PR #117, "Backlog through 2026-10-28" § permissions rework).
- Commit-proportionality check — `scripts/check_commit_proportionality.py`
  (PR #147): sizes the message to the change, leads failure with the escape
  hatch (`Proportionality:` trailer). Agent-discipline hook, not dotfiles.
- Issue-tracker + triage-labels wiring — `backlog-py`/`backlog-py-mcp`,
  `docs/agents/issue-tracker.md`, five canonical triage labels (changelog
  "Backlog through 2026-10-28" § docs/agents).

**python-project-template** (Python CLI base):

- Ruff repo standard — line-length 88, Google docstrings, W505/D205
  grandfathered per-directory, E501 never grandfathered, verbatim-fixture
  remedy is per-file-ignores (never `# noqa:` inside a string literal); prose
  docstrings rewrapped by hand. (lore knowledge ruff standard; PR #33 lineage)
- `uv run --frozen` + pyproject `[tool.pytest]` addopts — locked groups,
  `package = false`, model-calling tests behind `llm_judge` so they stay out of
  the default run (changelog "Backlog through 2026-10-28" § root pyproject;
  `uv --frozen` safety rule in AGENTS.md § Commands).
- Mutation-proving doctrine — "a test is not finished until seen to fail
  against a deliberately broken copy", `Mutation:`/`Failing-test:` commit
  trailers (`spec.md` § Verification, `docs/TESTING.md`).
- Two known-failure suites documented in AGENTS.md with the exact node-ID
  baseline + `check_suite_baseline.py` that refuses a green when the log holds
  no pytest summary (PR #114/#126/#132 — partly meta, see below).

**copier-template-copier-template** (meta — scaffolds new templates):

- changelog.d → CHANGELOG.md collection with scriv, Keep a Changelog; collector
  NEVER deletes fragments (DOT-317) and retries a rejected push (PR #136/#138).
- check_suite_baseline CI — judge a run by the known-failure list rather than
  the count, parse ERROR outcomes, refuse when no summary (PR #126, PR #132) —
  the general shape is meta; the specific baseline table is per-repo.
- Queue-integrity guard — `test_no_shadowed_task_ids` fails when a read command
  reports a duplicate task id (PR #111) and the decision-id guard (PR #125/#137).

Open question carried forward (not decided here): DOT-209's own title says "a
general git repository template", which is now subsumed by the three-template
architecture. Before extracting, re-scope DOT-209 to "record and route the
shareable items to the three templates" rather than "build one general
template", or split it — author call.

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
