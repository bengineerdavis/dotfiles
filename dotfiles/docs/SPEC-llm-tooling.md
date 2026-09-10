# LLM tooling

What must stay true while the AI/LLM concerns are factored out of
`apps/ollama` into a provider-agnostic utility with an owned data store.

Named `SPEC-llm-tooling.md` rather than `spec.md` to match the `ROADMAP-*.md`
siblings here — a bare `spec.md` in a directory of ten documents does not say
what it specifies.

## Intent

`apps/ollama` began as "install a runtime, keep a model set in sync" and now also
carries role routing and escalation policy, usage telemetry, speed benchmarking,
a 25-case mechanical eval suite, task-type coverage against a taxonomy, and a
local-only usage profile. Several of those were never ollama-specific: the eval
harness already talks to OpenRouter, and the questions underneath — which model
for which task, when to escalate, what may leave the machine — apply to every
provider.

This document does not schedule that work. It says which properties a refactor
must preserve, because they were each bought by a specific failure and are easy
to lose in a move.

It governs TOOLING. `MODEL-LIFECYCLE.md` governs models — how they are
discovered, judged, adopted and retired. Where they touch, that document wins on
model questions and this one on where the code and data live.

## Triggers

- **SHOULD** apply when moving, splitting or renaming any of `ollama-role`,
  `ollama-usage`, `ollama-bench`, `ollama-evals`, `ollama-profile`, or the eval
  cases and taxonomy.
- **SHOULD** apply when adding a tool that sends content to any model, local or
  remote.
- **SHOULD NOT** apply to the ollama runtime install, the model manifest, or
  role membership. Those stay with the topic and are governed elsewhere.

## Behaviors

### Behavior: Egress asks the policy resolver, at the point of egress

Every tool that sends content to a model SHALL consult `policy check` before
sending, and SHALL treat denied (1) and unknown (2) identically. A missing or
unreadable resolver is itself a denial.

#### Scenario: A tool is moved to the new utility

- **WHEN** a sending tool changes location or name
- **THEN** its policy call moves with it, and the caller test that proves the
  guard RELENTS moves with it too — a guard that only ever refuses is
  indistinguishable from one that no longer runs

#### Scenario: A new tool sends work-tagged content to a remote model

- **THEN** it refuses rather than degrades. There is no partial version of
  sending data to a third party

### Behavior: The tool ships, the numbers do not

Anything derived from real usage — task-type split, prompt-size distribution,
per-model call counts — SHALL stay on the machine. The code that derives it is
publishable; its output is not.

#### Scenario: A doc or case wants to cite a real figure

- **THEN** it names the command that produces the figure instead of the figure.
  `apps/ollama/evals/cases/long-faithfulness.yaml` is the worked example

#### Scenario: The utility gains its own data directory

- **THEN** that directory lives outside every repository, and the tool that
  writes it says so at the top of the file it writes

### Behavior: A mechanism that can decline is proven to relent

Any guard, gate, skip or early-exit SHALL have a test asserting BOTH directions:
that it declines when it must, and that it proceeds when it may.

#### Scenario: A capability gate is added

- **WHEN** a gate can mark work as not-applicable
- **THEN** a test shows a capable subject is NOT skipped. Otherwise a gate that
  skips everything reports a clean run having tested nothing

#### Scenario: A test is written for an existing guard

- **THEN** it is not finished until it has been seen to FAIL against a
  deliberately broken copy. See `tests/policy/test_policy_callers.py` and
  `tests/ollama_evals/`, where injecting the regression is how the suites were
  validated — and how one of them was found to be passing vacuously

### Behavior: Eval cases stay synthesised

Cases SHALL be written from understanding of a problem class, never derived from
real work material — including by replacing names or identifiers. Scrubbing
changes what is recognisable, not where a case came from.

#### Scenario: Live use exposes a class of failure with no case

- **THEN** describe the class and write a new case from it. Do not import the
  transcript that revealed it

### Behavior: Measured numbers carry their conditions

A number moved between documents SHALL carry what produced it — model tag, date,
harness settings — or be re-measured. A figure whose conditions are lost is a
recollection.

#### Scenario: A refactor copies a benchmark table

- **THEN** the conditions move with it, or the table is regenerated. `at cap
  8192` and `on an idle machine` are part of the number, not decoration

### Behavior: Teardown moves with the tool

A tool that installs a symlink, agent, timer or directory SHALL have its removal
updated in the same change.

#### Scenario: A tool moves to the new utility

- **THEN** the old teardown entry is removed and the new one added together.
  Prefer deriving the list from the manifest, as `apps/ollama/tasks/remove.yaml`
  now does for server env vars, so the two cannot drift

## Constraints

### Constraint: No layer grants permission

The refactor MUST NOT introduce a policy field that authorises anything. Every
field forbids or bounds. Permission comes from a human, or from the action not
touching governed data.

### Constraint: Provider assumptions do not move into shared code

Shared code MUST NOT assume ollama. `ollama-evals` already addresses local tags
and `openrouter/…` tags through one interface; that is the standard, not the
exception.

### Constraint: Data ownership is decided before the move, not after

The utility MUST NOT begin holding data until one owner and one retention rule
exist for it. Today it is scattered across `~/.local/share/ollama-{usage,bench,
evals}` and the `llm` CLI's sqlite log, with no retention applied — which is the
open finding this refactor is partly meant to close.

<!-- No skillet-version: this is a repository design document, not an agent
     skill. It borrows the format because it reads well, not because a harness
     consumes it. -->
