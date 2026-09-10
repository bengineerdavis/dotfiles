# spec.md

Properties this repository must preserve, and the failures that bought them.

`AGENTS.md` says how to work here and links to `dotfiles/docs/` for explanation.
This file is the third thing: what must remain TRUE, independent of who or what
is doing the work. It covers the whole repository — topics, tools, tests, models,
data and policy. Where a subject needs instructions of its own, the invariant
stays here and the detail is referenced: `dotfiles/docs/CONVENTIONS.md` for topic
structure, `MODEL-LIFECYCLE.md` for how models are judged, `GOALS.md` for why the
policy layers exist. Where it and a doc disagree, the doc is describing and this is
constraining — fix the doc.

Every behavior below exists because something went wrong. The scenarios are the
real cases, kept because a rule without its failure is soon argued away.

## Layering and ownership

### Behavior: One concern per layer

chezmoi owns dotfiles and symlinks, Ansible owns package installs and system
state, zsh owns shell runtime config. See `dotfiles/docs/CONVENTIONS.md`, which
is the source of truth and which the topic files cite.

#### Scenario: A task would work in either layer

- **THEN** it goes where the CONCERN lives, not where it is convenient. A symlink
  task in Ansible belongs in chezmoi; a `brew install` in a shell script belongs
  in Ansible

### Behavior: Teardown changes with the thing it creates

Anything that installs a symlink, agent, timer, directory or environment variable
SHALL have its removal updated in the same commit.

#### Scenario: A tool is added to an install loop

- **THEN** the matching removal entry is added in the same change. Prefer
  deriving the list from the manifest — `apps/ollama/tasks/remove.yaml` now
  derives `launchctl unsetenv` from `ollama_server_env`, after a hand-copied list
  silently stopped covering a newly added variable

### Behavior: Source and deployed are checked before editing

`bin/` holds chezmoi SOURCE files; `~/bin/` is what runs. They drift in both
directions.

#### Scenario: A `bin/` script needs a change

- **THEN** run `chezmoi status` first. Committing the source while the deployed
  copy is ahead silently reverts the working version on the next apply

## Verification

### Behavior: A mechanism that can decline is proven to relent

Any guard, gate, skip, early-exit or fail-closed path SHALL have a test asserting
BOTH directions: that it declines when it must, and that it PROCEEDS when it may.

This is the most-violated property here. A guard that fails closed and a guard
that never runs are indistinguishable — both refuse, both pass a smoke test.

#### Scenario: A policy guard is added to a tool

- **WHEN** the guard refuses because the policy denies
- **THEN** a test also sets the policy to permit and asserts behaviour CHANGES.
  `ask-research` shipped with its helper defined after the call site: bash said
  "command not found", returned 127, the guard refused, and every hand-test
  passed while the resolver was never consulted. See
  `tests/policy/test_policy_callers.py`

#### Scenario: A capability gate marks work not-applicable

- **THEN** a test shows a CAPABLE subject is not skipped. Otherwise a gate that
  skips everything reports a clean run having tested nothing. See
  `tests/ollama_evals/test_capability_gate.py`

### Behavior: A test is not finished until it has been seen to fail

Before trusting a new test, break the code deliberately and watch it go red.

#### Scenario: A suite passes on first run

- **THEN** inject the regression it is meant to catch. Three of four injected
  regressions were caught this way; the fourth revealed the TEST was wrong — its
  fixture was too simple to reach the bug — and would otherwise have shipped
  green and useless

#### Scenario: An assertion inspects captured output

- **THEN** assert the output is non-empty first. A grep over an empty string
  proves nothing and reads as a pass

### Behavior: Exit status is read directly

#### Scenario: A command's exit code decides something

- **THEN** do not read it through a pipe. `cmd | head` reports head's status.
  This is in `AGENTS.md` § Verification and was still hit twice in one session

## Evidence

### Behavior: Measured numbers carry their conditions

A figure moved between documents SHALL carry what produced it — subject, date,
harness settings — or be re-measured.

#### Scenario: A benchmark table is copied

- **THEN** the conditions move with it. `at cap 8192` and `on an idle machine`
  are part of the number. A `gemma4` result changed by a whole case when the cap
  moved, and an earlier ranking had to be withdrawn because a 12-day-old
  measurement was compared against a fresh one

### Behavior: A claim names what was not checked

#### Scenario: Reporting that something works

- **THEN** say on what, under which conditions, and what was not exercised. "It
  renders and was not yet applied there" is a complete answer; "it works" is not

## Data and disclosure

### Behavior: The tool ships, the numbers do not

Anything derived from real usage — task-type split, prompt-size distribution,
per-model call counts — SHALL stay on this machine. The code that derives it is
publishable; its output is not.

#### Scenario: A doc or eval case wants to cite a real figure

- **THEN** it names the command that produces the figure instead of the figure.
  See `apps/ollama/files/executable_ollama-profile` (deployed as
  `ollama-profile`) and the pointers in
  `apps/ollama/evals/cases/long-faithfulness.yaml`

### Behavior: The repository does not identify the employer

Strings that only make sense from inside the company are removed. Generic
products anyone can obtain stay — the test is *could I have found or used this
without being part of a company?*

#### Scenario: A vendor name appears in a config

- **THEN** apply the test. 1Password, Okta, Kandji and a public npm SDK stay; a
  work email, a `~/code/work/<employer>/` path and an internal tool name do not.
  Open items are tracked machine-locally, never in a committed file — see
  `TASKS.md` § Private tasks, and note that an earlier committed doc reproduced
  the very patterns it existed to remove

### Behavior: Eval cases are synthesised

Cases SHALL be written from understanding of a problem class, never derived from
real work material — including by replacing names or identifiers. Scrubbing
changes what is recognisable, not where a case came from.

#### Scenario: Live use exposes a failure class with no case

- **THEN** describe the class and write a new case from it. Do not import the
  transcript that revealed it

## Models

Detail lives in `dotfiles/docs/MODEL-LIFECYCLE.md` — discovery, triage,
measurement, adoption and retirement. Only the invariants are here.

### Behavior: A model earns its place by measurement on this machine

A model SHALL NOT enter a role on a vendor benchmark, a leaderboard, a model
card, or recall. Those may motivate a candidate; they may not justify one.

#### Scenario: A release lands and sounds impressive

- **THEN** it is a candidate, not an adoption. It is measured on this hardware,
  at the quantisation and context actually used, on the task the role performs

### Behavior: A tier ordering states what it encodes

Where tiers exist, the manifest SHALL say what separates them — and SHALL NOT
imply a quality gradient that was never measured.

#### Scenario: Every tier measures identically

- **THEN** say so, and say what the ordering actually encodes. `think` was
  documented as speed-and-capability, not accuracy, once `fast` and `best` scored
  the same on every case — and `best` was relabelled as "most capable", meaning
  vision and context, rather than "most accurate"

#### Scenario: A model is demoted

- **THEN** the recorded reason is the one that survives scrutiny.
  `deepseek-r1:32b`'s demotion was first written as a correctness failure; the
  case turned out to be ambiguous and the model scored full marks on the rewrite.
  The demotion stands on latency, and the note says that, including that it does
  not license calling the model worse

### Behavior: A role pick is declared where it can be installed

A tag named in a role SHALL also be declared in the model manifest.

#### Scenario: A model is promoted to a role

- **THEN** add it to its family too. A role pick no family declares is
  unpullable by `sync` on a fresh host and looks like an orphan to `prune` —
  which once left 18GB of in-use weights one command from deletion. `status` and
  `check` report this as role drift

## Policy

### Behavior: Egress consults the resolver, at the point of egress

Every tool that sends content to a model SHALL consult `policy check` before
sending, and SHALL treat denied (1) and unknown (2) identically. A missing or
unreadable resolver is itself a denial.

#### Scenario: Work-tagged content would go to a remote model

- **THEN** refuse rather than degrade. There is no partial version of sending
  data to a third party

#### Scenario: A sending tool is moved or renamed

- **THEN** its policy call and its relenting test move with it

## Constraints

### Constraint: No layer grants permission

A policy layer MUST NOT contain a field that authorises anything. Every field
forbids or bounds. Permission comes from a human, or from the action not touching
governed data. A field that cannot be written as a restriction is mis-shaped —
`local_model_allowed` became `local_model_on_unapproved_device_allowed` for
exactly this reason.

### Constraint: Ambiguity is marked, not resolved

An unclear rule goes in `open_questions` with a safe default. Guessing produces a
compliance artifact that reads as authoritative and is not.

### Constraint: Shared code does not assume a provider

Tooling MUST NOT assume ollama. `ollama-evals` addresses local tags and
`openrouter/…` tags through one interface; that is the standard.

### Constraint: Data ownership precedes data

A tool MUST NOT begin holding data until one owner and one retention rule exist
for it. Today usage data is scattered across `~/.local/share/ollama-{usage,bench,
evals}` and the `llm` CLI's sqlite log with no retention applied — the open
finding that `TASKS.md` tracks.

<!-- Format borrowed from the skill specs in ai-prompt-library because it reads
     well. Deliberately carries no skillet-version: no harness consumes this. -->
