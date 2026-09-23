# Dotfiles

## Intent

This is the specification for the whole repository: what must remain true here,
independent of who or what is doing the work. It covers topics, tools, tests,
models, data and policy.

Every behavior below exists because something went wrong. The scenarios are the
real cases, kept deliberately, because a rule without its failure is soon argued
away — and because the failure is usually the only part a reader believes.

The documents divide as follows. `PRD.md` says what the project is for and is
where scope questions are settled. `ROADMAP.md` says what is likely next and is
where an empty task queue is refilled from. `AGENTS.md` says how to work here and is
procedural. `dotfiles/docs/` explains and is descriptive. This file constrains.
Where a subject needs instructions of its own the invariant stays here and the
detail is referenced: `dotfiles/docs/TOPICS.md` for topic structure,
`MODEL-LIFECYCLE.md` for how models are judged, `GOALS.md` for why the policy
layers exist. Where this file and a doc disagree, the doc is describing and this
is constraining — fix the doc.

## Triggers

- **SHOULD** apply to any change to this repository, by a human or an agent,
  including changes that only touch documentation.
- **SHOULD** apply when deciding where a change belongs, what proves it, and
  what may be written down about it.
- **SHOULD** apply when a rule here appears to block reasonable work — the
  scenarios say what the rule cost to learn, which is the input to changing it.
- **SHOULD NOT** be treated as a checklist to satisfy after the fact. A behavior
  that was not consulted before the work is not evidence about the work.
- **SHOULD NOT** be extended by analogy to cases it does not name. A new failure
  earns a new behavior, with its scenario, rather than a broad reading of an old
  one.

## Behaviors

### Behavior: Layering — one concern per layer

chezmoi SHALL own dotfiles and symlinks, Ansible SHALL own package installs and
system state, and zsh SHALL own shell runtime config. See
`dotfiles/docs/TOPICS.md`, which is the source of truth and which the topic
files cite.

#### Scenario: A task would work in either layer

- **GIVEN** a change that could be implemented in chezmoi or in Ansible
- **WHEN** the author picks a home for it
- **THEN** it goes where the CONCERN lives, not where it is convenient. A
  symlink task in Ansible belongs in chezmoi; a `brew install` in a shell script
  belongs in Ansible

### Behavior: Layering — teardown changes with the thing it creates

Anything that installs a symlink, agent, timer, directory or environment
variable SHALL have its removal updated in the same commit.

#### Scenario: A tool is added to an install loop

- **WHEN** an install loop gains an entry
- **THEN** the matching removal entry is added in the same change. Prefer
  deriving the list from the manifest — `apps/ollama/tasks/remove.yaml` now
  derives `launchctl unsetenv` from `ollama_server_env`, after a hand-copied
  list silently stopped covering a newly added variable

### Behavior: Layering — source and deployed are checked before editing

`bin/` holds chezmoi SOURCE files and `~/bin/` is what runs; they drift in both
directions, so the author SHALL check both before editing either.

#### Scenario: A `bin/` script needs a change

- **WHEN** a script under `bin/` is about to be edited
- **THEN** run `chezmoi status` first. Committing the source while the deployed
  copy is ahead silently reverts the working version on the next apply

### Behavior: Verification — a mechanism that can decline is proven to relent

Any guard, gate, skip, early-exit or fail-closed path SHALL have a test
asserting BOTH directions: that it declines when it must, and that it PROCEEDS
when it may.

This is the most-violated property here. A guard that fails closed and a guard
that never runs are indistinguishable — both refuse, and both pass a smoke test.

#### Scenario: A policy guard is added to a tool

- **GIVEN** a tool that calls `policy check` before sending content
- **WHEN** the guard refuses because the policy denies
- **THEN** a test also sets the policy to permit and asserts behaviour CHANGES.
  `ask-research` shipped with its helper defined after the call site: bash said
  "command not found", returned 127, the guard refused, and every hand-test
  passed while the resolver was never consulted. See
  `tests/policy/test_policy_callers.py`

#### Scenario: A capability gate marks work not-applicable

- **WHEN** a gate reports that a subject cannot be tested
- **THEN** a test shows a CAPABLE subject is not skipped. Otherwise a gate that
  skips everything reports a clean run having tested nothing. See
  `tests/ollama_evals/test_capability_gate.py`

### Behavior: Verification — a test is not finished until it has been seen to fail

Before a new test is trusted, the code it covers SHALL be broken deliberately
and the test watched going red.

The mutation itself SHALL NOT be committed, so the evidence that the test was
seen to fail SHALL be recorded beside the commit as greppable trailers —
`Mutation: <what was broken>` and `Failing-test: <the test that went red>` —
readable with `git interpret-trailers`. Prose in a commit body is not auditable;
trailers are.

#### Scenario: A suite passes on first run

- **WHEN** a newly written test passes immediately
- **THEN** inject the regression it is meant to catch. Three of four injected
  regressions were caught this way; the fourth revealed the TEST was wrong — its
  fixture was too simple to reach the bug — and would otherwise have shipped
  green and useless

#### Scenario: An assertion inspects captured output

- **WHEN** an assertion greps or matches over captured output
- **THEN** assert the output is non-empty first. A grep over an empty string
  proves nothing and reads as a pass

### Behavior: Verification — exit status is read directly

A command's exit status SHALL be read from the command, not through a pipeline.

#### Scenario: A command's exit code decides something

- **WHEN** a script branches on whether a command succeeded
- **THEN** do not read it through a pipe. `cmd | head` reports head's status.
  This is in `AGENTS.md` § Verification and was still hit twice in one session

### Behavior: Verification — invariants are tested as properties

Where a function has a rule that holds for ALL inputs rather than for a
remembered few, it SHALL be tested with generated inputs. Pure functions with
algebraic structure are the candidates: merge, path-set, normalisation,
set-difference and formatting helpers. See `tests/binned/test_binned_property.py`
for the house example.

A property test SHALL state the invariant independently of the implementation. A
property that recomputes the function under test proves only that the code
equals itself.

Example tests do not go away. The division is by what the test knows: a property
knows a rule, an example knows an incident.

#### Scenario: A helper gains a case for one tricky input

- **GIVEN** a pure helper such as `deep_merge` or `unmet_capabilities`
- **WHEN** the author is writing a test for a specific awkward input
- **THEN** ask whether the awkwardness is an instance of a rule. If it is, write
  the property and keep the example as the named regression alongside it

#### Scenario: A property test passes on first run

- **WHEN** a new property passes immediately
- **THEN** check it is not vacuous before trusting it. An over-tight `assume()`
  can filter away every generated input, and hypothesis reports a pass. This is
  the generated-input form of grepping an empty string — assert on the data the
  property actually received

#### Scenario: A property fails and hypothesis shrinks the input

- **WHEN** hypothesis reports a minimal failing example
- **THEN** commit that example as its own explicit test as well as fixing the
  code. The shrunk input is the cheapest regression test that will ever be
  available for that bug, and the generator may not produce it again

### Behavior: Verification — input handling is fuzzed at the boundary

Code that parses input it did not produce SHALL be exercised with malformed and
hostile input, not only well-formed input. The boundaries here are the eval case
loader, the policy field-path parser, and every regex that reads model output.

Model output is an untrusted boundary. It is the input most likely to be
malformed, because the producer is a sampling process and not a program.

#### Scenario: A check expression parses a model response

- **GIVEN** a `check` expression matching a model's answer with a regex
- **WHEN** the response is empty, truncated mid-token, or repeats the prompt
- **THEN** the check fails with a readable message rather than raising. A
  `NoneType has no group` traceback reports a harness defect as a model failure,
  which is the worst possible outcome for a discriminator

#### Scenario: A loader reads a hand-written config

- **WHEN** an eval case or policy layer is loaded
- **THEN** malformed input is rejected with the file and field named. These are
  hand-edited YAML files, so malformed is the expected state during editing, not
  an exotic one

### Behavior: Work — agent work is defined and assigned before it starts

Work carried out by an agent or subagent SHALL have a task in `TASKS.md` before
the work begins. The task SHALL state what done means and who is doing it. Work
fanned out across several agents SHALL be several tasks, one per unit of work,
rather than one task naming the fan-out.

Agents are fast and leave no trace of intent. Without a task written first there
is no record of what was asked, no statement of done to check the result
against, and no way for a parallel session to see the work exists.

#### Scenario: Several threads of work arrive at once

- **GIVEN** more than one request in flight in a single session
- **WHEN** the work is about to start
- **THEN** the tasks are written first. This spec gained five behaviors in a
  session that carried five undefined threads at once, and the threads were
  only reconstructable because they were still in the transcript

#### Scenario: Work is delegated to a subagent

- **WHEN** work is handed to an agent
- **THEN** its task exists, names the agent, and states its done condition
  before the agent is started. An agent given an undefined unit of work returns
  something plausible, and nothing exists to check it against

### Behavior: Work — unclear requirements stop the work

An agent SHALL stop and ask when a requirement is unclear, rather than choosing
the reading that lets the work continue. Guessing SHALL NOT be used to avoid a
question.

This is the same rule as § Ambiguity is marked, not resolved, applied to work
instead of to policy. Both exist because a guess and a decision are
indistinguishable once written down.

#### Scenario: A request admits two readings that lead to different work

- **GIVEN** an instruction that could mean two materially different things
- **WHEN** the agent notices the ambiguity
- **THEN** it asks before building. A wrong guess costs the whole build; the
  question costs one exchange

#### Scenario: Only part of a request is unclear

- **WHEN** some of the work is well defined and some is not
- **THEN** do the defined part, and ask about the rest at the point it is
  needed. Stopping everything on one open question is its own failure

### Behavior: Evidence — measured numbers carry their conditions

A figure moved between documents SHALL carry what produced it — subject, date,
harness settings — or be re-measured.

#### Scenario: A benchmark table is copied

- **WHEN** a measured figure moves from one document to another
- **THEN** the conditions move with it. `at cap 8192` and `on an idle machine`
  are part of the number. A `gemma4` result changed by a whole case when the cap
  moved, and an earlier ranking had to be withdrawn because a 12-day-old
  measurement was compared against a fresh one

### Behavior: Evidence — a claim names what was not checked

A report of success SHALL state its scope, including what was not exercised.

#### Scenario: Reporting that something works

- **WHEN** work is reported as done
- **THEN** say on what, under which conditions, and what was not exercised. "It
  renders and was not yet applied there" is a complete answer; "it works" is not

### Behavior: Data — the tool ships, the numbers do not

Anything derived from real usage — task-type split, prompt-size distribution,
per-model call counts — SHALL stay on this machine. The code that derives it is
publishable; its output is not.

#### Scenario: A doc or eval case wants to cite a real figure

- **WHEN** a document would quote a number derived from real usage
- **THEN** it names the command that produces the figure instead of the figure.
  See `apps/ollama/files/executable_ollama-profile` (deployed as
  `ollama-profile`) and the pointers in
  `apps/ollama/evals/cases/long-faithfulness.yaml`

### Behavior: Data — the repository does not identify the employer

Strings that only make sense from inside the company SHALL be removed. Generic
products anyone can obtain stay — the test is *could I have found or used this
without being part of a company?*

#### Scenario: A vendor name appears in a config

- **WHEN** a vendor or tool name is about to be committed
- **THEN** apply the test. 1Password, Okta, Kandji and a public npm SDK stay; a
  work email, a `~/code/work/<employer>/` path and an internal tool name do not.
  Open items are tracked machine-locally, never in a committed file — see
  `TASKS.md` § Private tasks, and note that an earlier committed doc reproduced
  the very patterns it existed to remove

### Behavior: Data — eval cases are synthesised

Cases SHALL be written from understanding of a problem class, and SHALL NOT be
derived from real work material — including by replacing names or identifiers.
Scrubbing changes what is recognisable, not where a case came from.

#### Scenario: Live use exposes a failure class with no case

- **WHEN** real usage reveals a failure the suite does not cover
- **THEN** describe the class and write a new case from it. Do not import the
  transcript that revealed it

### Behavior: Change records — a human-readable changelog is kept

A changelog written for humans SHALL be maintained. `git log` does not satisfy
this: it records why each change happened, for someone reverting one, and that
is a different question from what changed since a reader last looked.

#### Scenario: A change is worth telling a reader about

- **WHEN** a change alters what someone using this repository would notice
- **THEN** it earns a changelog entry, written at the time of the change rather
  than reconstructed from commits later

#### Scenario: The changelog would repeat the commit log

- **WHEN** an entry would say only what the commit subject already says
- **THEN** it is written for the reader instead, in their terms. A changelog
  that reads like `git log --oneline` has been generated rather than written

### Behavior: Change records — one commit is one reviewable decision

A commit SHALL contain one reviewable decision. The test is not file count; it
is whether a reader can hold the *why* in their head, and whether the change can
be reverted alone without taking unrelated work with it.

A changelog for humans is required, and `git log` is not one. They serve
different readers: a commit body serves someone reverting one change and asking
what it was; a changelog serves someone asking what changed since they last
looked, who does not want to read commits at all.

Message quality still matters, for the same reason it always did — a commit is
the only record of *why* a change happened. It is simply not a substitute for
the other document. `dotfiles/docs/TOPICS.md` § Commit granularity is the
source of truth; `AGENTS.md` § Commits carries the short version.

#### Scenario: Several unrelated changes are ready together

- **WHEN** a working tree holds more than one logical change
- **THEN** split by concern, not by file. Splitting is a review pass in its own
  right — re-reading the clamav Debian port as six commits surfaced a variable
  collision the single commit had hidden

#### Scenario: Splitting would leave the tree broken

- **WHEN** splitting a change would produce a commit that does not stand alone
- **THEN** do not split. Atomic means self-contained, not small; a commit that
  breaks the tree so the next can fix it breaks `git bisect`

### Behavior: Change records — what is committed is verified, not assumed

Staging SHALL be checked before the commit and the result checked after.

#### Scenario: Several paths are staged at once

- **WHEN** more than one path is passed to `git add`
- **THEN** confirm each landed. `git add` given five paths, one of which no
  longer existed, aborted without staging the other four — and the commit went
  out carrying only a file DELETION, leaving main briefly with neither the old
  document nor its replacement

#### Scenario: A file is co-edited by another session

- **GIVEN** a file another session may also be writing
- **WHEN** part of it is ready to commit
- **THEN** `git add -p`, then a bare `git commit` with nothing else staged, and
  verify immediately with `git show --stat HEAD`. `git commit -o <path>` commits
  the WORKING-TREE content of that path and discards partial staging, so it
  quietly takes the other session's hunks too

### Behavior: Change records — durable why lives in the code, not the message

Reasoning that must survive SHALL be written beside the decision it explains. A
commit body carries what a reverter needs; a comment carries what a maintainer
needs.

#### Scenario: A decision needs an explanation to survive

- **WHEN** the reason for a change would be lost if the commit were rebased away
- **THEN** put it in a comment next to the code. Rebases cannot lose it, and
  readers who never open `git log` will find it

### Behavior: Change records — a recorded reason is one that survives scrutiny

#### Scenario: A stated reason is later disproved

- **WHEN** a reason already written down turns out to be wrong
- **THEN** correct the record where it lives, not only in conversation. The
  `deepseek-r1:32b` demotion was written as a correctness failure; the case
  proved ambiguous and the model scored full marks on the rewrite. The manifest
  comment now states the latency reason and retracts the original claim

### Behavior: Change records — attribution says whose work it is

#### Scenario: An agent commits changes authored by the human

- **WHEN** an agent commits work it did not author
- **THEN** the message says so. Recording someone else's work is not the same as
  co-authoring it

### Behavior: Change records — history surgery is recorded and bounded

Rewrites SHALL be preceded by a backup branch and explained in `git notes` on
the resulting commits.

#### Scenario: History needs rewriting to remove something

- **WHEN** a rewrite is proposed to remove content already pushed
- **THEN** do it, and record that it does not un-publish. Anything already
  fetched, forked or indexed is beyond its reach, so the rewrite bounds future
  exposure and nothing else

### Behavior: Models — a model earns its place by measurement on this machine

A model SHALL NOT enter a role on a vendor benchmark, a leaderboard, a model
card, or recall. Those may motivate a candidate; they may not justify one.
Detail lives in `dotfiles/docs/MODEL-LIFECYCLE.md`.

#### Scenario: A release lands and sounds impressive

- **WHEN** a new model is proposed for a role
- **THEN** it is a candidate, not an adoption. It is measured on this hardware,
  at the quantisation and context actually used, on the task the role performs

### Behavior: Models — a tier ordering states what it encodes

Where tiers exist, the manifest SHALL say what separates them, and SHALL NOT
imply a quality gradient that was never measured.

#### Scenario: Every tier measures identically

- **WHEN** two tiers score the same on every case
- **THEN** say so, and say what the ordering actually encodes. `think` was
  documented as speed-and-capability, not accuracy, once `fast` and `best`
  scored the same on every case — and `best` was relabelled as "most capable",
  meaning vision and context, rather than "most accurate"

#### Scenario: A model is demoted

- **WHEN** a model is moved out of a role
- **THEN** the recorded reason is the one that survives scrutiny.
  `deepseek-r1:32b`'s demotion was first written as a correctness failure; the
  case turned out to be ambiguous and the model scored full marks on the
  rewrite. The demotion stands on latency, and the note says that, including
  that it does not license calling the model worse

### Behavior: Models — a role pick is declared where it can be installed

A tag named in a role SHALL also be declared in the model manifest.

#### Scenario: A model is promoted to a role

- **WHEN** a tag is added to a role
- **THEN** add it to its family too. A role pick no family declares is
  unpullable by `sync` on a fresh host and looks like an orphan to `prune` —
  which once left 18GB of in-use weights one command from deletion. `status` and
  `check` report this as role drift

### Behavior: Policy — egress consults the resolver, at the point of egress

Every tool that sends content to a model SHALL consult `policy check` before
sending, and SHALL treat denied (1) and unknown (2) identically. A missing or
unreadable resolver is itself a denial.

#### Scenario: Work-tagged content would go to a remote model

- **WHEN** content tagged as work would be sent to a third-party model
- **THEN** refuse rather than degrade. There is no partial version of sending
  data to a third party

#### Scenario: A sending tool is moved or renamed

- **WHEN** a tool that performs egress is relocated
- **THEN** its policy call and its relenting test move with it

### Behavior: Writing — technical docs are plain, specs are normative

Technical documentation SHALL be written to a plain-language standard: short
sentences, active voice, common words, the conclusion first, and one idea per
paragraph. This covers `AGENTS.md`, `dotfiles/docs/`, READMEs, changelog and
release prose, anything a tool prints to a user, and — the three most often
written and least often counted — **commit messages, pull request descriptions
and code comments**.

Length is part of the standard, not separate from it. Prose SHALL be
proportional to what it describes, and a passage longer than its subject
warrants is evidence the subject should have been split.

This file and any skillet spec are exempt and SHALL keep normative language —
SHALL, MUST, MUST NOT — with BDD scenarios. Plain language optimises for a
reader deciding what to do; spec language optimises for a reader deciding
whether a rule was met. Softening SHALL to "should try to" changes the meaning,
which is why the exemption exists rather than a style preference.

#### Scenario: A doc explains a rule this file states

- **GIVEN** a rule that appears both here and in a doc
- **WHEN** the doc is written or revised
- **THEN** the doc explains it plainly and links here for the normative form.
  Two normative statements of one rule drift; a plain explanation plus a link
  does not

## Constraints

### Constraint: No layer grants permission

A policy layer MUST NOT contain a field that authorises anything. Every field
forbids or bounds. Permission comes from a human, or from the action not
touching governed data. A field that cannot be written as a restriction is
mis-shaped — `local_model_allowed` became
`local_model_on_unapproved_device_allowed` for exactly this reason.

### Constraint: Ambiguity is marked, not resolved

An unclear rule MUST NOT be guessed. It goes in `open_questions` with a safe
default. Guessing produces a compliance artifact that reads as authoritative and
is not.

### Constraint: Shared code does not assume a provider

Tooling MUST NOT assume ollama. `ollama-evals` addresses local tags and
`openrouter/…` tags through one interface; that is the standard.

### Constraint: Data ownership precedes data

A tool MUST NOT begin holding data until one owner and one retention rule exist
for it. Today usage data is scattered across `~/.local/share/ollama-{usage,bench,
evals}` and the `llm` CLI's sqlite log with no retention applied — the open
finding that `TASKS.md` tracks.

<!-- Grammar is skillet's, so `skillet validate` can check it. This is a
     repository spec rather than an agent skill: there is no SKILL.md derived
     from it and no eval cases reference its behavior ids, so it exceeds the
     ~8-behavior guidance deliberately. Splitting it would trade one warning for
     the drift of many files. -->
<!-- skillet-version: 1.8.0 -- moved from 1.7.0 on 2026-09-15 after reading
     the upstream compare (5 commits): grammar and exit-code logic untouched,
     acceptance identical; the change is diagnostics and the authoring
     workflow. Evidence: docs/REFERENCES.md skillet row. -->
