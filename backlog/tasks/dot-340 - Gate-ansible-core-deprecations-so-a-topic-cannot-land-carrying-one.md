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
updated_date: 2026-11-18
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

## Runtime warning check (second layer, amended 2026-11-18)

Author direction: the suite must also check that a given role RUNS without
emitting these warnings — the static scan covers source text, the runtime
check covers executed paths. The two faults are different classes: starship's
`{{ ansible_date_time.iso8601 }}` (tasks.yaml:117) never warns today because
nothing renders it, and a parse-time or source scan and a bare-expression
scan both see it, but only a run proves a code path renders clean. Both
layers stay: the static scan is the primary gate; the runtime check proves
the paths that actually execute.

Probed live 2026-11-18 (ansible-core 2.21.6, throwaway plays under /tmp —
so the task does not re-derive):

- `--check` mode DOES fire the warning — a check-mode run is a valid runner
  for this test, no state mutation needed.
- The warning goes to STDERR only (grep on merged streams = 1 hit; stdout
  only = 0).
- The warning fires once per rendered ORIGIN and is deduplicated per
  (file, var) pair per run: a play rendering `backlog_logs_dir` reports
  `Origin: .../apps/backlog/defaults/main.yaml:20:19`; the same play
  rendering only `backlog_bin` reports line 12; a play with three
  vars_files (backlog, lima, ori) each rendered reports three distinct
  Origins.
- Design unlock: a harness play that loads a topic's defaults as
  `vars_files` and renders EVERY var in the file surfaces every bare-fact
  origin in that file, with file:line, on stderr. Assert zero
  `DEPRECATION WARNING` lines on stderr for a topic = that topic is clean
  on the executed path.

Shape: extend the existing real-ansible harness
(`tests/topic_resolution/conftest.py` — builds throwaway plays, runs real
`ansible-playbook` via subprocess, skips without the binary) with a
per-topic fixture that pulls the topic's defaults through a vars_files play
and renders each var, then asserts the empty stderr match. Parametrize over
topics so the failure names the topic and the file:line origins.

Constraints carried from the probes:

- Cost: one real ansible-playbook invocation per topic per test run; the
  session-scoped `ansible_playbook` fixture and a parametrized single play
  per topic keep this bounded (seconds per topic in check mode, measured).
- The runtime check cannot replace the static scan: it only covers what a
  render touches (facts-less paths, unrendered conditionals and the
  registry-answers dict-key context stay invisible to it) — exactly why
  DOT-339's AC #4 defined-guards matter even after this lands.
- Same red-on-arrival rule as the scan: land after DOT-339, or baseline it.

## Ecosystem research (2026-11-18, review-best-practices pass)

The requirement: catch the class before 2.24 with a mechanism that fails a
gate. Searched three source kinds — tooling (ansible-lint, pytest-ansible,
molecule), standards (porting guides, config docs), practitioner reports
(forum threads, upstream issue trackers). Probed the installed tooling rather
than trusting recall.

**Why the gate is built here instead of adopted: the ecosystem gap is
verified, not assumed.**

- ansible-lint cannot see injected-fact usage. Three upstream reports agree:
  RFE #1611 (open since 2021), discussion #3457 (2023, also asked for
  autofix), bug #4857 (filed Nov 2025 against the 2.20 deprecation, still
  open at 26.11.0 — checked the 26.9–26.11 release notes, no such rule).
- Re-probed the installed linter 2026-11-18 (ansible-lint 26.11.0 +
  ansible-core 2.21.6): a minimal play reading `{{ ansible_env.HOME }}`
  passes `--strict` with exit 0 ("Passed: 0 failure(s) … profile
  'production'"); its only findings in other probes were name[casing] /
  name[play] style rules. The lint-gap claim in the task's own 2026-11-09
  description holds against today's artifact.
- Runtime harnesses exist (pytest-ansible, molecule) but none ship a
  deprecation gate; molecule's own RFE #2619 (2020) closed without shipping
  one.
- What practitioners actually do: read the porting guide before upgrading
  (the official mechanism — Ansible 13's guide documents
  INJECT_FACTS_AS_VARS verbatim), rely on the runtime warning as the
  detector ("with ansible-core 2.20+, it will tell you when you run … which
  places use the old way" — felixfontein, forum #44886), and hand-roll CI
  grep/fail gates on the warning output. No standard tool does this; the
  bespoke gate IS the community practice.

**Revisit trigger:** if ansible-lint ships an injected-facts rule (#4857 /
#1611 — open, no movement as of 26.11.0), the static scan can retire in
favor of the ecosystem tool. Check those issues before re-deriving the scan.

**Dependency rationale (author question 2026-11-18: "isn't it
counterproductive to use ansible while also detecting the notices and
artifacts ansible creates?")**

No — with the following record, so the ruling does not need re-deriving:

- The warning is the dependency communicating, not misbehaving. The
  alternative is a silent breaking change at 2.24; ansible instead gave
  ~1 year of runway and machine-readable file:line origins.
- The debt is bounded and measured: 37 expression hits (DOT-339 census,
  refreshed 2026-11-18), one migration task, one gate. After DOT-339,
  `inject_facts_as_vars = False` makes future fact-injection deprecations
  structurally impossible in this repo — prevented, not merely detected.
- The same tax exists for every actively-developed dependency (this
  session's actual outage was the Python↔ansible version matrix —
  Python 3.15 removing `dataclasses._is_type` broke ansible-core 2.21 —
  not deprecation noise). The question is whether the tool earns its cost,
  not whether it emits notices.
- What would genuinely be counterproductive: hand-rolling per-machine
  package/system state management to avoid deprecation notices — more
  bespoke code, no ecosystem tooling, and no warnings at all when it
  breaks. AGENTS.md's one-concern-per-layer ruling (ansible owns system
  state) already decided this; the gate is what keeps the dependency
  maintainable across releases.
- Cost acknowledged: the tax is recurring across many axes (conditionals,
  module_utils, callbacks — forums document collection-level warning
  spam). The gate converts each upgrade from "surprise every 2–3 years"
  to "did the gate catch anything".

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 A test fails when a file under home/dotfiles/ uses a bare top-level fact in a template expression, and passes on the tree as it stands after DOT-339.
- [ ] #2 A mutation is recorded in the commit trailers proving the test fails: adding {{ ansible_env.HOME }} to a topic file turns it red, and reverting turns it green.
- [ ] #3 The allow-list is a named list in the test, each entry with the reason it survives 2.24, and a positive case exercises it so an over-broad allow-list cannot quietly disable the scan.
- [ ] #4 The test does not report a prose mention of a fact name, and does not report the supported ansible_facts[...] form.
- [ ] #5 A runtime test runs a real ansible-playbook (check mode) over each topic's defaults with every var rendered, and asserts stderr carries zero DEPRECATION WARNING lines; the failure message names the topic and each offending file:line origin.
- [ ] #6 The runtime test is parametrized over topics so one topic's regression names that topic, and skips cleanly when ansible-playbook is absent (session-scoped fixture, same as tests/topic_resolution).
- [ ] #7 A mutation is recorded proving the runtime test fails: re-adding a bare ansible_env read to a topic default turns the runtime test red for that topic, and reverting turns it green.

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
