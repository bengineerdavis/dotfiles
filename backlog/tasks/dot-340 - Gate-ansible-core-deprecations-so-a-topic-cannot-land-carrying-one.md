---
id: DOT-340
title: Gate ansible-core deprecations so a topic cannot land carrying one
status: To Do
created_date: 2026-11-10 04:57
dependencies:
- DOT-339
labels:
- ansible
- testing
- tooling
priority: medium
updated_date: 2026-11-10 04:57
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-09: the INJECT_FACTS_AS_VARS deprecation (a bare `ansible_env.HOME`, and every other bare top-level fact) reached a production `update.sh` run. ansible-core 2.24 removes the feature. Nothing in the repo catches this class before it scrolls past in a terminal.

What was probed and does NOT work, so the task does not re-derive it:

- `ansible-lint 26.11.0 --strict` passes a playbook using `{{ ansible_env.HOME }}` clean ("Passed: 0 failure(s) ... profile 'production'"). Its three `deprecations`-tagged rules are `deprecated-bare-vars`, `deprecated-local-action` and `deprecated-module`; none covers injected fact vars.
- `ansible-playbook --help` offers no fail-on-deprecation flag. `DEPRECATION_WARNINGS` / `deprecation_warnings` only toggles display.
- `--syntax-check` does not template, so it cannot see the warning.
- The warning fires at task-argument finalisation, not at parse time, so a parse-time scan misses it as well.

`inject_facts_as_vars = False` was probed and does fail loudly ("'ansible_env' is undefined") while `ansible_facts['env']['HOME']` keeps working. DOT-339 installs that end state; this task builds the layer that stops the next deprecation class from arriving silently.

Ship:

- A repo test that scans the Ansible payload under `home/dotfiles/` for bare top-level fact access, following the `tests/topics/test_task_tag_coverage.py` scan precedent.
- An allow-list of non-fact `ansible_*` vars named in the test, each with a comment saying why it survives 2.24.
- Coverage of every injected fact class, not just `ansible_env`: `ansible_hostname` (8 occurrences today), `ansible_date_time` and `ansible_user_dir` are equally deprecated.

Constraints:

- A gate red on arrival teaches everyone to ignore it. DOT-339 must land first, or the test needs a checked-in baseline with the `scripts/check_suite_baseline.py` shape.
- Do not build the check out of a regex over source text without a mutation that proves it fails. A pattern matching nothing, or matching a prose comment, is not a gate; record the mutation in the commit trailers.
- `ansible-lint` is deliberately not folded in: it is not wired into `prek` or CI, it reports 22 findings on `apps/backlog` alone, and it cannot see this class. Wiring lint is its own decision.
- A comment mentioning `ansible_env` in prose is not a violation; only template expressions are. Where a parse is available, decide on parsed expressions.
- The scan must not fire on `ansible_facts[...]`, which is the supported form.

Drafted 2026-11-09.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A test fails when a file under home/dotfiles/ uses a bare top-level fact in a template expression, and passes on the tree as it stands after DOT-339.
- [ ] #2 A mutation is recorded in the commit trailers proving the test fails: adding {{ ansible_env.HOME }} to a topic file turns it red, and reverting turns it green.
- [ ] #3 The allow-list is a named list in the test, each entry with the reason it survives 2.24, and a positive case exercises it so an over-broad allow-list cannot quietly disable the scan.
- [ ] #4 The test does not report a prose mention of a fact name, and does not report the supported ansible_facts[...] form.
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
