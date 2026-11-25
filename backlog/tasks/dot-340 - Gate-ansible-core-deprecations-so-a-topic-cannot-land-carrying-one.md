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

- The gate is **ansible-lint plus a custom rule**, not a bespoke scanner. Stock ansible-lint cannot see this class (see the corrections below), but it accepts custom rules through `rulesdir`, which is the ecosystem-sanctioned extension point and was proven working 2026-11-24.
- `home/dotfiles/.ansible-lint` — profile `basic`, `rulesdir: .ansible-lint-rules`, and `enable_list: [injected-fact-vars]`. That last key is mandatory and easy to miss: `profile:` filters the rule set to its ladder and silently drops custom rules, so without it the rule loads, appears in `--list-rules`, and never runs — a gate that reports nothing and exits 0 (measured 2026-11-24).
- `home/dotfiles/.ansible-lint-rules/injected_fact.py` — a `matchyaml` rule, not `matchtask`. Measured coverage on this tree: `matchtask` found 10 of 37 references because it only sees task arguments; `matchyaml` scans file content and found all 37 (36 lines — `apps/loreai/defaults/main.yaml:62` carries two).
- The rule's allow-list of non-fact `ansible_*` names, each with the reason it survives 2.24, and a positive case exercising it so an over-broad list cannot quietly disable the scan.
- Wiring in `prek.toml` (`language: system`, calling mise's ansible-lint) and in `.github/workflows/tests.yml`, both changed-files-only.
- Both new files are repository-only tooling inside the payload tree, so `home/.chezmoiignore` declares them and a guard test asserts chezmoi does not deploy them.

Constraints:

- A gate red on arrival teaches everyone to ignore it. The gate lints **changed files only**, matching the existing ruff CI pattern. A full-tree run reports 49 pre-existing findings after the convention skips; making those a merge gate would be red on arrival for work the change did not cause.
- The custom rule still reports the 36 injected-fact lines until DOT-339 lands, so this task's PR merges after DOT-339. The dependency already says so.
- Do not build the check out of a regex over source text without a mutation that proves it fails. A pattern matching nothing, or matching a prose comment, is not a gate; record the mutation in the commit trailers.
- A comment mentioning `ansible_env` in prose is not a violation; only template expressions are. The rule strips comments before matching.
- The scan must not fire on `ansible_facts[...]`, which is the supported form. The rule's first version did exactly that, which is what the negative test exists to catch.

Drafted 2026-11-09. Rewritten 2026-11-24 to the ansible-lint design.

## Corrections to the 2026-11-18 research (2026-11-24)

The research below says "the bespoke gate IS the community practice" and
that ansible-lint is "deliberately not folded in". Two things changed,
measured 2026-11-24:

1. **Custom rules work, and are the sanctioned extension point.** Fetched
   the configuring and usage docs: `-r/--rules-dir` plus `-R` composes
   custom rules with the defaults. A custom rule was then written and proven
   in both directions on the installed ansible-lint 26.11.0. The ecosystem
   gap the research documents (RFE #1611, discussion #3457, bug #4857 all
   open) is real — no *built-in* rule covers this class — but the gap is
   filled by a custom rule rather than by a pytest scan.
2. **The runtime flip and the lint rule are not redundant.** Probed: with
   `inject_facts_as_vars = False` in `ansible.cfg`, ansible-lint still
   passes `apps/backlog/defaults/main.yaml` clean, because lint never
   templates role defaults. The flip catches the bug at run time; the rule
   catches it at review time. Both layers are needed, which is the same
   conclusion the runtime-check section reaches from the other direction.

What survives from the research unchanged: the upstream reports, the
practitioner guidance to rely on the runtime warning, and the revisit
trigger (retire the custom rule if ansible-lint ships an injected-facts rule).

Measured cost of the whole gate, so the decision can be revisited with
numbers: tree-wide at `profile: basic` with the convention skips is 454
findings before the custom rule, 490 with it. Of the 454, 203 are the
bundled yamllint rule, 222 are `name[casing]`, 72 are `role-name[path]` and
65 are `var-naming` — every one a convention this repo chose on purpose.
After skipping those, 49 findings remain, all real and all fixable.

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

- [ ] #1 A test fails when a file uses a bare top-level fact in a template expression, and passes on the tree as it stands after DOT-339. Delivered as a subprocess run of the real `ansible-lint` over a throwaway play, so the assertion covers the config wiring as well as the rule.
- [ ] #2 A mutation is recorded in the commit trailers proving the test fails: dropping `enable_list` turns it red, a rule that matches nothing turns it red, and adding {{ ansible_env.HOME }} to a topic file turns it red; reverting turns it green.
- [ ] #3 The allow-list is a named list in the rule, each entry with the reason it survives 2.24, and a positive case exercises it so an over-broad allow-list cannot quietly disable the scan.
- [ ] #4 The test does not report a prose mention of a fact name, and does not report the supported ansible_facts[...] form.
- [ ] #8 The lint config is wired into `prek.toml` and CI on changed files only, and the version is pinned in CI while mise's bundle floats — recorded in a comment, because a floating gate means a green commit and a red re-run.
- [ ] #9 `home/dotfiles/.ansible-lint` and its rule directory do not deploy, asserted by asking chezmoi rather than parsing `.chezmoiignore`, with a non-vacuity decoy.
- [ ] #5 A runtime test runs a real ansible-playbook (check mode) over each topic's defaults with every var rendered, and asserts stderr carries zero DEPRECATION WARNING lines; the failure message names the topic and each offending file:line origin.
- [ ] #6 The runtime test is parametrized over topics so one topic's regression names that topic, and skips cleanly when ansible-playbook is absent (session-scoped fixture, same as tests/topic_resolution).
- [ ] #7 A mutation is recorded proving the runtime test fails: re-adding a bare ansible_env read to a topic default turns the runtime test red for that topic, and reverting turns it green.

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

Branch `ansible-lint-gate`, worktree `.worktrees/ansible-lint-gate`.

Mechanics that cost time and should not be re-derived:

- **The config must sit at `home/dotfiles/`.** Its location is what sets
  ansible-lint's project path. A config under `$TMPDIR` made the linter treat
  that directory as the project and report "0 files processed of 1
  encountered", exit 0 — indistinguishable from a pass (measured 2026-11-24).
  The tests therefore pass `-c <payload>/.ansible-lint` and run with
  `cwd=home/dotfiles`, rather than writing a config beside the fixture.
- **`enable_list` is mandatory for a custom rule under `profile:`.** Without
  it the rule loads (`--list-rules` lists it) and is never invoked. This was
  the bug that made the first three probe attempts look like a broken rule.
- **`matchyaml`, not `matchtask`.** `matchtask` receives a `Task` whose
  `str()` is just `Task('name' ...)`; the Jinja lives in `task["action"]`.
  Even reading the action dict only reaches task arguments, so it found 10 of
  37 references. `matchyaml` gets the file content and found all 37.
- **The prek hook must strip the `home/dotfiles/` prefix.** The runner passes
  repo-relative paths while the entry `cd`s to the payload root, so
  `home/dotfiles/x.yaml` resolved to `home/dotfiles/home/dotfiles/x.yaml` and
  failed as `load-failure[not-found]` — a wiring bug wearing a finding's
  clothes.
- **`rulesdir` is relative to the config file**, so `.ansible-lint-rules`
  needs no absolute path.
- **yamllint spacing cannot be configured away.** A custom yamllint config
  is rejected unless it complies with five required settings, so
  `yaml[commas]` and `yaml[colons]` are skipped via `skip_list` instead.

Mutation evidence, all three in the failing direction:

- `enable_list` entry removed → 5 failed (4 bare-fact cases + the wiring
  assertion), 3 passed.
- Rule altered to allow everything → 4 failed (the bare-fact cases), 4 passed.
- Rule altered to over-report (allow-list and comment-stripping removed) →
  3 failed (the supported form, magic vars, prose comment), 5 passed.

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done

<!-- DOD:BEGIN -->

<!-- DOD:END -->
