---
id: TASK-38
title: Drop the `npm:@sentry/skillet` pin in `apps/mise/files/config.toml` to
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
- blocked
ordinal: 36
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`latest`.** The pin sat at 1.7.0 since 2026-09-11 because mise's npm resolver
  (aube) could not fetch vite's 39 MB packument through
  `sfw.security.sentry.io` — `curl` and `npm` both can, so it is a mise-side
  limit, not registry or auth. **Resolved 2026-09-14: 1.8.0 verified working
  here** (`skillet validate .` exits 0; 1.8.0 was already installed, and `mise
  install` pruned 1.7.0 — reinstall it via
  `mise install npm:@sentry/skillet@1.7.0` if ever needed), committed as
  ee09e38. What remains before the pin drops to `latest`: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, decide
  whether the four `npx @sentry/skillet@latest` task aliases stay floating
  (they align once the pin is `latest`), and `spec.md`'s 1.7.0 pin plus the
  `docs/REFERENCES.md` row need aligning — that alignment is queued there
  already. Done when the config says `latest`, the pin-print tells the truth,
  and the spec/REFERENCES rows agree with it. **Changelog-read blocker,
  recorded 2026-09-15:** the REFERENCES standard (read the 1.7.0→1.8.0
  changes before moving the pin) cannot currently be satisfied from this
  machine — the source repo is not accessible (the getsentry org is
  SAML-blocked; npm metadata carries no repository URL) — so the pin stands
  on local evidence only and the read must happen from a machine with
  access. **Read DONE 2026-09-15, on this Mac after all** — the block was
  the second machine's. The 1.7.0→1.8.0 compare (5 commits) shows grammar
  and exit codes untouched; the change is diagnostics (the no-eval-case
  warning was deleted) and the authoring workflow (evals opt-in). Pin
  aligned at 1.8.0 across `config.toml` and the spec footer (94389a5);
  REFERENCES records the read. What remains of this task: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, and the
  four `npx @sentry/skillet@latest` aliases need a float-vs-pin decision.
- Install `ty` and typecheck the Python. Named in the house toolchain and
  currently absent — not installed, zero references in the repo. 42 test files
  and 22 Python scripts are unchecked (counted 2026-09-23: 13 `uv run
  --script`, one the stray `bin/executable_archive.bk`; 9 `python3` — the
  earlier "32" and "36" were stale). `bin/executable_scanfiles` has a
  `# /// script` block under a `python3` shebang: inert, as it declares no
  dependencies, but against the `docs/PYTHON.md` rule. Note `ty` is
  pre-1.0; decide whether it
  gates commits or just reports before wiring it into `prek`.
- Wire `ruff` into `.pre-commit-config.yaml`. It is installed and the toolchain
  names it, but the hook config runs shellcheck and bats only, so no Python file
  in this repo is linted on commit. Settle the ruleset first — 22 scripts written
  before any linter will not pass a default config cleanly.
  mise also declares ruff twice — `ruff` (`apps/mise/files/config.toml:147`)
  and `pipx:ruff` (line 186) — so pick one first; § Now #1 (p) may pin it in
  a lock group instead.
- Integrate `xdoctest` and make illustrative examples a tested part of the
  docs. Docstring examples in the 22 Python scripts and any Python modules
  run under pytest via the xdoctest plugin; docs (`dotfiles/docs/`, READMEs)
  carry code examples where they clarify, verified rather than trusted —
  written for humans first, machines as the proof they still work. Survey the
  ecosystem before building anything: xdoctest for docstrings, and for fenced
  blocks in markdown weigh sybil / pytest-examples / a pytest-markdown runner
  before hand-rolling one. Done when: xdoctest is in the documented pytest
  command (AGENTS.md § Commands), docstring examples in `bin/` are collected
  and green, `docs/PYTHON.md` records the convention (what must carry
  examples, how to write and run them), and a markdown-example mechanism is
  either adopted or consciously rejected with the reason recorded. Pairs
  with the plain-language standard item — examples are prose too.
- Make test conftests skip rather than error on a missing optional dependency.
  `tests/ollama_evals/conftest.py` loads the eval harness as a module, and the
  harness imports Pillow at module level, so without `--with pillow` the whole
  directory produces 53 collection errors instead of 52 passes — the suite
  aborts instead of running what it can. Same class as the hypothesis guard
  fixed today, one layer deeper: the import happens before pytest can skip
  anything. `pytest.importorskip` in the conftest is the likely fix, but check
  what else the harness pulls in at import time first.
- Check AGENTS.md and CONTRIBUTING.md for places the agent→function
  graduation policy should apply, and reference the policy artifact from
  `ai-prompt-library` once it exists. The bias: prefer a trusted function
  over agent judgment where the task is mechanical; agents stay for
  adaptability and interpretation (high-context tasks — deciding what to do,
  how to succeed). **[blocked: the threshold research and council decision
  are owned in ai-prompt-library's TASKS.md — no text lands here until the
  artifact exists.]** Same artifact the shift-left study's two-track trust
  model (§ Now, "Build the LEDGER") routes its global-vs-per-repo,
  skill-portability question to — one open question, two entry points here.
- Sweep committed machine-adjacent strings, per the audit in
  `dotfiles/docs/MULTI-MACHINE.md` (2026-09-12). The audit found: employer-
  adjacent paths (`~/code/work/sentry/`, `sfw.security.sentry.io`), the §
  Private tasks section describing the work it points to (obfuscation that
  signals itself), environment mentions ("work machine", "the second
  machine", "a Seer clone", "the work workspace"), and session-claim
  provenance narration. Rewrites generalize to environment-neutral classes;
  the purge of employer strings itself stays under § Private tasks. Done
  when a grep over the committed tree for the audit's patterns comes back
  clean and the MULTI-MACHINE design's generalization test is applied to
  every rewritten line. **Wait for the council verdict first** — the council
  may change what "bounded pointer" means before the sweep rewrites
  pointers.
- Decide when `scriv collect` runs. The changelog exists and fragments
  accumulate, but nothing says what a "release" is for a dotfiles repo that does
  not release. Candidates: on a cadence, at each machine rebuild, or never —
  leaving everything under Unreleased, which is legitimate and costs nothing.
  Until this is settled the changelog grows one section and is still readable.

Legacy: TASKS.md § Now item 36 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
