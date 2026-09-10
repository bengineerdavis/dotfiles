# AGENTS.md

Instructions for coding agents working in this repository. Human-facing detail lives
in `docs/` — this file links there rather than restating it, so the two cannot drift.

`spec.md`, beside this file, is the third layer: the properties that must remain
TRUE regardless of who is working. This file is practice, `docs/` is explanation,
`spec.md` is constraint. Read it before changing a guard, a teardown path, a
policy layer, or anything that reports a measured number.

## Start here

**Read `spec.md` and `TASKS.md` before starting work.** They pair: `spec.md` says
what must remain true, `TASKS.md` says what is in flight and who is touching
which files. Read `PRD.md` too when the work is about scope — whether something
belongs here at all.

**When `TASKS.md` § Open is empty, the work is not finished** — read `ROADMAP.md`.
Open is a queue whose lines are deleted on completion, so it cannot hold anything
long-horizon; an empty queue means "nothing scheduled", never "nothing to do".
The roadmap says what to do next: take an item, interview the author about it,
then update `PRD.md` with the requirements that settles and `TASKS.md` with the
work items it produces. Any agent or model working here is expected to have read both — a
change that satisfies the task and violates the spec is not done.

**Prime directive: do not work if something is unclear. Ask.** A guess and a
decision look identical once they are written down, and the guess costs the whole
build while the question costs one exchange. If part of the request is clear and
part is not, do the clear part and ask about the rest at the point it matters.
See `spec.md` § Work — unclear requirements stop the work.

**Write the task before you start.** Any work done by an agent or subagent gets a
line in `TASKS.md` first, saying what it is doing and what done means. Work split
across several agents is several tasks, one per unit of work. See `spec.md`
§ Work — agent work is defined and assigned before it starts.

Update `TASKS.md` before you finish. Sessions
keep their own in-memory task lists, which fragment as soon as two are running;
that file is the shared one. It also lists which files another session is
actively touching.

## How work runs here

Treat this as a loop, not a single prompt. The shape is RECL, by analogy with a
REPL:

- **Requirements** — write down what the work is before doing it.
- **Execute** — do it.
- **Check** — prove it. Not "it looks right": a test seen to fail, a validator
  exiting 0, a mutation caught.
- **Loop** — feed what the check found back into the requirements.

The step that gets skipped is the first one, and skipping it is what produces
work nobody asked for. Three files carry the requirements between them:

- **`PRD.md`** — what the project is for, who it serves, and what it must never
  become. Read it when a decision is about scope rather than mechanism. Its
  north star is "a machine that is ready to use", and its architecture rule —
  provisioning may install and trigger a tool, never contain its logic or state
  — settles most questions about where something belongs.
- **`AGENTS.md`** — this file. How to work here, and the expertise that is not
  obvious from reading the code.
- **`TASKS.md`** — what is in flight, who has it, and what is blocked.

`spec.md` sits across all four steps: it is what must stay true whichever step
you are in, and it is what Check checks against.

## What this repo is

A chezmoi-managed dotfiles repo with an Ansible layer for system state.

**Read `dotfiles/docs/CONVENTIONS.md` first** — topic structure, the `topic.yml`
schema, tiers, lifecycle tags, dependency resolution, commit granularity and the
CRUD-ownership invariant. It is the source of truth and the 39 topic files cite it.
`dotfiles/docs/ARCHITECTURE.md` has the big picture,
`dotfiles/docs/CONTRIBUTING.md` the workflow around it.

The repo-root `docs/` tree is an older copy of the same material, kept but not
maintained. Edit the `dotfiles/docs/` copies.

The one rule worth repeating here because it is the most common mistake: **one
concern per layer.** chezmoi owns dotfiles and symlinks, Ansible owns package
installs and system state, zsh owns shell runtime config. A symlink task in Ansible
belongs in chezmoi; a `brew install` in a shell script belongs in Ansible.

## Where the source of truth is

Scripts under `bin/` are **chezmoi source files**, named `executable_<name>`. The
deployed copy at `~/bin/<name>` is what actually runs. They drift, in both
directions:

```bash
chezmoi status                 # what differs
chezmoi add ~/bin/<name>       # deployed  -> source   (adopt a hand-edit)
chezmoi apply ~/bin/<name>     # source    -> deployed  (push a repo change)
```

Before editing a `bin/` script, check `chezmoi status`. Committing the source while
the deployed copy is ahead silently reverts the working version on the next
`chezmoi apply`.

## Working alongside other sessions

More than one agent session runs against this repo, sharing one checkout, one
deployed tree, and one machine. Most work never collides — in practice the only
real conflict so far came from two sessions rewriting the same large file at once.
These are the cases that do need care.

**Commit with `git commit -o <paths>`, never a bare `git commit`.** All sessions
share one `.git/index`. `git add <paths> && git commit` stages your paths and then
commits *the entire index* — including whatever another session staged and had not
yet committed. This is not hypothetical: it has already happened in both
directions. The now-rewritten `b3ad740` was titled as a clamav systemd change and
also contained another session's pii-redactor rewrite; `5692a86` was titled as a
pii-redactor change and also contained 52 zsh deletions belonging to a third
session. Neither could be reverted without taking unrelated work with it, which
is the whole property commits are supposed to have.

Both were unscrambled on 2026-08-21 into `bc72f5c` (clamav), `0bf73dc`
(pii-redactor) and `118c22e` (the zsh deletions), each carrying a `git notes`
PROVENANCE entry. That was judged worth a force-push *once*, while the branch had
one real consumer; it is not the standing answer. Prevention below is cheaper
than a rewrite every time, and a rewrite stops being available as soon as anyone
else has built on the history.

    git commit -o <paths> -F -    # --only: commit exactly these, ignore the rest
    git show --stat HEAD          # verify before pushing

`git add -p` is the other half when two sessions are editing the same file.
`TASKS.md` is the likeliest place for that, since everyone writes to it.

**A worktree gives you your own index.** That is a stronger reason to use one than
the file-churn argument below — the index is shared on *every* commit, not just
during large rewrites. Weigh it against the chezmoi `-S` requirement, which is easy
to forget and lands work on the wrong branch when you do.

**Before `chezmoi apply`, run `chezmoi status`.** Source and deployed drift in both
directions. Applying picks up whatever another session has committed but not yet
deployed, which may not be ready — Debian topic changes have sat committed and
unapplied for exactly this reason. Apply specific paths rather than everything.

**Before benchmarking, run `ollama ps`.** Model memory is global and unforgiving:
loading an 18 GB model while another is resident kills the server, and the failure
looks like a model or timeout bug rather than contention. A cold load can also
exceed a short `--timeout`, and a warmup that times out cascades into every
subsequent run failing.

**For a large rewrite of a single file, use a worktree and a branch.** Small
focused commits straight to `main` are fine and collide far less than the ceremony
would cost. Two caveats if you do branch:

```bash
git worktree add ../chezmoi-<topic> -b <topic>
chezmoi -S "$PWD" add ~/bin/<script>     # -S is required, see below
```

- chezmoi's source directory is **fixed**, not cwd-relative — it resolves to
  `~/.local/share/chezmoi` wherever you run it. Without `-S "$PWD"` a `chezmoi add`
  from a worktree writes into the main checkout and silently lands work on another
  branch.
- The deployed tree cannot be branched. `~/bin/<script>` is one file no matter how
  many branches hold versions of it, so `chezmoi apply` from either branch
  overwrites the other.

**Claim hot files in `TASKS.md` § Claimed** before touching anything listed under
Cross-session hazards, and delete the line when you stop.

**Other global state to check before assuming it is yours:** `~/.binned/config.toml`
(the judge pool and generation model), `~/bin` and `~/dotfiles` (deployed copies),
and long-running background jobs holding the GPU.

## Branches and integration

**One branch per work item**, named `<group>-<item>` — `topic-cli-a2`,
`ai-factor-out-b4`. Work items are the lettered entries in `TASKS.md`.

Two exceptions, and both must be stated in the task itself:

- **Items that must land together share a branch.** B4 and B5 are the standing
  example: moving the policy resolver without the capability interface just
  relocates the duplication instead of removing it.
- **Dependent items stack.** Branch off the parent item's branch, not main, and
  rebase when the parent merges. A3 builds on A2's CLI, so it cannot start from
  main and still compile.

### Never branched

- **`TASKS.md`** — the shared queue. Commit it straight to main with nothing else
  staged: `git add -p`, then a bare `git commit`, then `git show --stat HEAD`.
  It has to stay current for sessions that cannot see your branch. Deleting your
  own task line is a main-side commit even when the work was done on a branch.
- **Governance docs** (`spec.md`, `PRD.md`, `AGENTS.md`) — land these as their own
  commit, and prefer main whenever the change does not depend on branch code.
  They are the surface where unrelated branches collide.

### Applying is main-only

**Agents never run `chezmoi apply`.** Read-only `chezmoi status` and `chezmoi
diff` are expected and encouraged — an agent that never checks drift is how
twenty days of uncaptured work accumulated in `aliases.zsh`.

The reason is structural: there is one deployed tree and it cannot be branched.
`~/dotfiles` is a single set of files no matter how many branches hold versions
of them, so two agents applying from two branches overwrite each other. Applying
happens from main, by the author or by a session holding the apply claim in
`TASKS.md` § Claimed.

### Merge gates

An agent may merge its own branch to main when **all** of these hold:

- the full suite is green
- `skillet validate .` exits 0 with no errors
- the new or changed test has been seen to fail, with the mutation recorded in
  the commit message
- nothing under § Cross-session hazards was touched without a claim
- the change touches no policy path, no egress path, and no deployed-tree file

Anything else: push the branch, open a PR, and report. Stakes and size decide,
not preference. A new feature goes to PR; so does any change that takes more
than a paragraph to explain.

### Review starts with the tests

Read the tests first. They should read cleanly enough to serve as the spec, and
they are where an agent's work is most likely to be wrong in a way the code
hides — an agent will happily write code and then write tests that ratify
whatever it just wrote. That is what § Prove the test fails exists to catch.

### Quiz before merge

When a PR is opened, or when a change is too large to explain in a paragraph,
the agent quizzes the author on what the change contributes before it merges.
The point is not to test the agent's work; it is to check that the author
actually understands what was built. A change that passes review while nobody
internalised the design is a change nobody can maintain.

## Trust ladder

An agent earns wider autonomy by track record, **per task class and blast
radius**, never globally. Task classes: docs, tests, code, policy, deployed.
An agent may sit at rung 3 for docs and rung 1 for policy at the same time.

### Rungs

| Rung | What the agent may do |
|---|---|
| 0 | Propose only. Every diff is reviewed before it is committed. |
| 1 | Commit to a branch and open a PR. Nothing reaches main unreviewed. |
| 2 | Self-merge docs and tests when § Merge gates pass. |
| 3 | Self-merge code inside a named blast radius when § Merge gates pass. |
| 4 | Work unattended on a task class and report async. |

**Promotion** is a streak of clean items at the current rung: 5 to reach rung 2,
10 to reach rung 3, 20 to reach rung 4. Clean means merged with no author
correction of any class below. The counts rise because the cost of a mistake
rises with what the rung permits.

**Demotion** is by incident class. Rung 0 has no floor below it.

### Incident classes

Defined here, in advance, because a class invented to explain a particular
failure is not a class — it is an excuse with a name.

**Class A — disclosure or policy bypass. Drops to rung 0, every task class.**

- Work or customer data, employer-identifying strings, or machine-local usage
  figures committed, sent off-device, or written to a shared store.
- Egress without consulting the resolver, or treating unknown (2) as permitted.

One occurrence ends autonomy everywhere, not just in the class where it
happened. The reason is that the harm does not reverse: `spec.md` § Change
records already records that a history rewrite does not un-publish, so anything
fetched, forked or indexed is beyond recall. A ladder that let an agent climb
back after this would be pricing an irreversible harm as a recoverable one.
Reinstatement is an explicit author decision, not a streak.

**Class B — corrupted evidence. Drops two rungs.**

- A test that passes without exercising what it claims to: a grep over empty
  output, an `assume()` that filters away every generated input, a fixture too
  simple to reach the bug.
- A gate reported as passing that was not actually run — a mutation check
  claimed in a commit message but never performed.
- Work reported as done that is not, or a claim that something works without
  naming what was not checked.

This is worse than a plain bug and is deliberately punished harder. The ladder
runs on the evidence in the ledger; an agent that can misreport a gate makes the
whole instrument fiction. Every one of these has already happened here at least
once, which is why `spec.md` § Verification carries them.

**Class C — process violation. Drops one rung.**

- Editing a file under § Cross-session hazards without a claim, or running
  `chezmoi apply` at all.
- A commit whose contents do not match its message, staging not verified, or an
  intermediate state that leaves the tree broken.
- Shipping against a stated behavior in `spec.md` — a teardown not updated with
  the thing it creates, a measured number moved without its conditions.

**Class D — judgment. Drops one rung above rung 2; a recorded warning at or
below it.**

- Resolving a material ambiguity silently instead of asking.
- Doing work the task did not define, or quietly narrowing work it did.

Judgment errors are treated more gently at low rungs on purpose. An agent
learning the repository will misjudge scope, and demoting for it teaches
caution about *asking*, which is the opposite of what § Start here requires.

### What is not an incident

Stated explicitly, because a ladder that punishes these produces an agent that
hides things.

- A bug that review caught and the tests could not have caught. That is a
  coverage gap, and it becomes a test.
- A refusal that turned out to be unnecessary. Failing closed is the designed
  behaviour; being wrong about it costs nothing.
- Asking a question whose answer already existed. **Asking is never an
  incident.** If questions cost trust, the agent stops asking, and the prime
  directive dies quietly.
- An approach tried, reported honestly, and abandoned.

### Ageing

A Class C or D incident stops counting against promotion after five clean items,
but stays in the ledger permanently. Class B ages out after twenty. Class A does
not age out. The ledger is a record, not a scoreboard to be reset — its value is
that a pattern across months stays visible.

## Commands

```bash
# Tests — pytest is primary. Needs these four or parts of the suite silently skip.
uv run --with pytest --with hypothesis --with typer --with questionary --with pyyaml pytest tests -q
uv run --with pytest pytest tests -m "not llm_judge" -q   # skip real-model tests
uv run --with pytest pytest tests -m llm_judge -q         # only real-model tests

bats tests/<name>.bats         # bash scripts only — see Languages below
./run-role.sh <topic>          # apply one ansible topic
./run-role.sh <topic> remove   # tear it down
```

A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while testing
almost nothing — the `binned_module` fixture skips without `typer`/`questionary`.

Without `pyyaml`, `tests/policy` drops from 22 tests to 15 passed / 1 skipped, and
the skipped module is the one asserting the policy layers grant no permissions —
so the check that matters most is the one that disappears quietest.

## Commits

**`dotfiles/docs/CONVENTIONS.md` § Commit granularity is the source of truth.** Read
it before committing. `spec.md` § Change records states the invariants — including
that staging is verified rather than assumed, and that the history is the
changelog, there being no `CHANGELOG.md` by design. The short version, so this file is usable on its own:

One commit is one reviewable decision. The test is not file count — it is whether a
reader can hold the *why* in their head, and whether the change can be reverted on
its own without taking unrelated work with it.

Sequence commits so every intermediate state works. Land the inert parts first and
the switch that activates them last — for an Ansible topic that is usually
`topic_os`, which gates whether any of the preceding commits run at all.

Do **not** over-split. A commit that leaves the tree broken so the next one can fix
it is worse than a slightly coarse one: it breaks `git bisect`. Atomic means
self-contained, not small.

Durable *why* belongs in a code comment next to the decision, where it survives
rebases and is read by people who never open git log. The commit body carries only
what a reverter needs.

Splitting is also a review pass in its own right. Re-reading the clamav Debian port
as six commits surfaced a bug the single commit had hidden: a new
`clamav_clamd_conf` var collided with an existing `register:` of the same name, and
registered vars outrank role vars — so the rendered script would have received a
task-result dict instead of a path.

## Languages

**Bash while a script is small; Python once it is not.** Short bash needs nothing
but a shell, which is why it wins for small jobs. Past roughly 80–100 lines that
trade stops paying: argument parsing, temp files and error paths are where bash gets
verbose and subtly wrong.

Count lines of **logic**, not lines of file. A script that is mostly an interface to
other programs does not qualify however long it is — `bin/findline` is 256 code
lines that pipe `rg` into `fzf` with a `bat` preview, so all the behaviour and all
the speed live in three Rust binaries. Porting it would add interpreter startup to
an interactive tool and make it worse. Its header records this so the question is
not reopened. Contrast `bin/clipped`: similar size, but genuinely branchy platform
dispatch, and worth porting.

Stdlib-only Python needs no dependency block — use `#!/usr/bin/env python3` like
`bin/mailbox`. Reach for `#!/usr/bin/env -S uv run --script` with inline PEP 723
deps only when third-party packages are genuinely needed, as `bin/llm-ctx` does.

`bin/binned` applies this rule to the scripts it generates: it counts effective
lines, recommends Python above 100, and asks a model in the 80–100 band.

### Python toolchain

Python here is 36 standalone PEP 723 scripts plus the test suite. **There is no
`pyproject.toml` and no package**, which changes what several of the usual rules
mean.

- **uv runs everything.** Scripts start `#!/usr/bin/env -S uv run --script`. Run
  tools through `uv run` rather than installing them globally, so the version is
  the script's and not the machine's.
- **Dependencies live in each script's `# /// script` block.** Add them with
  `uv add --script <file> <lib>` instead of hand-editing the block. If a
  `pyproject.toml` is ever added, the same rule applies to it: `uv add LIB` or
  `uv add --dev LIB`, never a hand edit.
- **pytest, test first.** See § Tests and § Prove the test fails. A test that has
  not been seen to fail is not yet a test.
- **Share fixtures through `conftest.py`.** `tests/ollama_evals/conftest.py`
  loads the harness as a module so every suite in that directory gets it once.
- **ruff lints.** Installed, but not yet in `.pre-commit-config.yaml` — the hooks
  currently run shellcheck and bats only, so no Python file is linted on commit.
  Queued in `TASKS.md`.
- **ty typechecks.** Not installed yet, and not referenced anywhere in the repo.
  Also queued. Treat any claim that the Python here is typechecked as false until
  that lands.
- **prek runs the hooks.** Both `prek` and `pre-commit` are installed and both
  read `.pre-commit-config.yaml`; which one is authoritative is unsettled and
  queued.
- **Log, do not print,** for anything an agent may need to read back while
  debugging.
- **Do not hide or wrap errors.** Swallowing an exception turns a fixable failure
  into a mystery. Where an error genuinely must not escape, convert it
  deliberately at a boundary and keep the message: `run_check` turns any raise
  into a named failure rather than discarding it, which is why a broken check
  reports itself instead of aborting the run.

## Tests

See `spec.md` § Verification for the properties a suite must have — chiefly that
a mechanism which can decline is proven to RELENT, and that a test is not
finished until it has been seen to fail against a deliberately broken copy. Both
were bought by suites here that passed while testing nothing.

**pytest is primary.** Any Python script gets pytest tests. bats remains correct
only for scripts that are still bash (`bin/cleanup`).

When porting a script, keep its bats suite until the pytest suite is proven
equivalent — it tests the CLI as a black box, so it survives a language change
unaltered and is the safety net that proves the port. Then retire it.

Layout: `tests/<script>/conftest.py` plus `test_*.py` split by concern. Mark tests
that call real models with `llm_judge` so they stay out of the default run.

A port is a chance to test what bash could not. `default_output()` in
`bin/pii-redactor` was previously only reachable by running the whole CLI and seeing
which file appeared; called directly, the path edge cases became explicit. Platform
dispatch in `bin/clipped` could only be exercised by mocking `uname` on `PATH`, so
in practice only the host platform was ever tested.

### Prove the test fails

`spec.md` § Verification says a test is not finished until it has been seen to
fail. This is how: break the code on purpose and watch the suite go red. It is
mutation testing done by hand, and it is cheap.

```bash
cp bin/executable_thing /tmp/thing.good          # keep the original
# edit the target: invert a guard, neuter a mechanism, make an error
# path return a positive value instead of "unknown"
uv run --with pytest pytest tests/thing -q       # MUST fail, and on the right test
cp /tmp/thing.good bin/executable_thing          # restore
uv run --with pytest pytest tests/thing -q       # green again
```

Mutations worth trying, in rough order of what has actually bitten here:

- **make the guard unconditional** — `if ordered and not cleared:` -> `if True:`
- **make it never fire** — the same line -> `if False:`
- **turn "unknown" into a claim** — `return None` -> `return set()` on an error
  path. This one skipped every case that declared a requirement and reported a
  clean run
- **move a definition below its first use** — bash resolves at call time, so the
  helper becomes "command not found", returns 127, and a fail-closed guard passes
  for the wrong reason

Read WHICH tests fail, not just how many. Of four regressions injected across the
eval harness, three were caught and the fourth was not — and that fourth revealed
the TEST was wrong: its fixture had no blank line inside the prompt, so
`rfind("\n\n")` landed on the seam by accident and the assertion passed either
way. A mutation that survives is either a coverage gap or a broken test, and both
are worth the two minutes.

Where a mechanism can decline, the mutation that matters is the one that makes it
decline ALWAYS — because refusing looks identical to not running. Same reason
`tests/policy/test_policy_callers.py` flips the policy to permit and asserts the
behaviour changes.

Two harness traps found here, worth checking for in any suite you touch:

- A test path pointing at a file that does not exist. `tests/clipped.bats` used
  `$BATS_TEST_DIRNAME/../clipped` — the repo root — so every case ran against a
  missing binary, and the one case that "passed" did so because a nonexistent
  command also exits nonzero.
- GNU-only syntax in a portability test. `script -qec` is GNU; BSD `script` has no
  `-c`, so two TTY tests could never pass on macOS whatever the code did. Use
  `pty.openpty()`.

### Properties and fuzzing

Most tests here are examples: a specific input, a specific expected result. Two
other kinds earn their place in specific situations.

**Write a property test when a rule holds for every input, not just the one you
thought of.** Pure functions with algebraic structure are the candidates — merge,
path-set, set-difference, normalisation, formatting. `spec.md` § Verification —
invariants are tested as properties says when this is required.

The rule is the test. State it without reference to how the code works: if your
property recomputes the function under test, it only proves the code equals
itself. Good properties look like "content survives", "the result is a subset of
what was asked for", "running it twice gives the same answer", "it never
mutates its input".

House examples: `tests/ollama_evals/test_harness_property.py` and
`tests/binned/test_binned_property.py`. Add `--with hypothesis` to the run
command; it is already in the one under § Commands.

Two things to watch:

- **A property that passes immediately may be testing nothing.** An `assume()`
  that is too tight filters away every generated input and hypothesis still
  reports a pass. This is the generated-input version of grepping an empty
  string. Check that the property is seeing real data before you trust it.
- **When a property fails, keep the counterexample.** Hypothesis shrinks the
  failure to its smallest form. Commit that as its own example test alongside
  the fix. It is the cheapest regression test you will ever get for that bug,
  and the generator is under no obligation to produce it again.
  `test_set_path_names_the_path_when_a_segment_is_not_a_mapping` is one: the
  property found that a mis-typed sweep path died with a bare `'int' object does
  not support item assignment`, naming neither the case nor the field.

**Fuzz where input arrives that you did not produce.** In this repo that means
model output, hand-edited YAML cases, and policy layer files. Model output is the
sharpest of the three, because the producer is a sampling process rather than a
program — empty responses, truncation mid-token, echoed prompts and control
characters are all normal. A harness that raises on those reports its own defect
as a model failure, which is the worst thing a discriminator can do.

Fuzz the data, not the code path that executes it. `run_check` runs `exec()` on
the check source, so the tests generate hostile *responses* and draw broken
*sources* from a fixed list. Generating source text to `exec()` would be running
arbitrary generated code.

Properties and fuzzing do not replace the mutation check above. Break the code
and watch the property go red, the same as any other test.

## Writing

Technical docs in this repo use plain language: short sentences, active voice,
common words, the conclusion first, one idea per paragraph. Write for someone
deciding what to do. This covers this file, `dotfiles/docs/`, READMEs, changelog
and release prose, and anything a tool prints to a user.

`spec.md` and any skillet spec are the exception. They keep normative language —
SHALL, MUST, MUST NOT — with BDD scenarios, because they are read to decide
whether a rule was met, not what to do next. Softening a SHALL to "should try
to" changes the meaning, so the exemption is about accuracy rather than taste.

Where a doc explains a rule that `spec.md` states, explain it plainly and link to
the spec for the binding wording. Two normative statements of one rule drift
apart; an explanation plus a link does not.

See `spec.md` § Writing — technical docs are plain, specs are normative.

## Models

Local Ollama first, then Anthropic or Google **via `llm-openrouter`**. The `llm`
environment deliberately carries only `llm-openrouter` and `llm-ollama` for hosted
access, so vendor-native ids like `claude-opus-4.7` resolve to nothing — use
`openrouter/anthropic/claude-opus-4.7`.

No hosted GPT or Grok as a default, a recommendation, or a fallback. They are
legitimate as **benchmark subjects** — that is what `bin/model-bench` is for. The
line is hosted-vendor dependency, not the name: `gpt-oss:20b` is open-weights and
runs locally under Ollama, so it is welcome; `gpt-4o` is not.

Model ids must be the exact `ollama list` tag. What is pulled here are MLX and QAT
builds, so `qwen3.5:35b` does not exist but `qwen3.5:35b-mlx` does. Never match ids
by substring: `bin/binned` used to, so a bare `qwen3.5:35b` matched the installed
`-mlx` tag, passed the availability check, then failed at `llm -m` from inside a
judge panel.

**Do not invent ratings or benchmark numbers.** Quality claims must come from a
measured run. `bin/model-bench` scores judges on *calibration* against a reference
scorecard rather than on the scores they emit, because measuring raw magnitude
rewarded generosity — two local models awarded a flat 10/10 to a script with no
comments and an unguarded `--delete`, and outranked the model that caught it.

## Dependencies

Check every dependency a script shells out to, system tools and hand-rolled
`~/bin` scripts alike. Being topic-managed is not a reason to skip the check: it
only means something *should* have installed it, which is exactly the assumption
that breaks on a fresh or half-applied box. See `require()` in `bin/llm-ctx`.

Name the fix in the error, not just the failure: `~/bin` scripts come from
`chezmoi apply ~/bin`, system tools from the Ansible topics via `update.sh`.

## Cross-platform

macOS and Debian/Ubuntu are both targets. Guard the package manager in-task rather
than abstracting it — `docs/CONTRIBUTING.md` rule 2 has the pattern. A topic
supporting both should not declare `homebrew` in `topic_requires`, or it becomes
unschedulable on Linux; see `apps/ollama/topic.yml`.

Assume tools installed by uv or mise are identical across platforms. Only system
binaries need per-OS handling.

Traps that have actually bitten here:

- **A per-user launchd agent maps to a systemd *user* timer, not a system one.**
  Same ownership, no root. It only fires while the user has a session, so report the
  `loginctl enable-linger` fix rather than silently changing login behaviour.
- **`nc -U` needs `netcat-openbsd`.** Debian ships two providers and
  `netcat-traditional` has no `-U`; probe the `nc` on `PATH`, because alternatives
  can point at the wrong build.
- **BSD and GNU flags differ** for `script`, `stat`, `sed -i` and `mktemp`. Prefer
  Python over a portability shim, or try both forms.

## Verification

Prefer evidence over assertion, and say plainly what was and was not checked.

- Render Ansible templates under **both** `os_family` values and run `bash -n` over
  the result. Use Jinja's `StrictUndefined` — it catches missing variables that a
  permissive render silently leaves blank.
- Do not report a template or playbook as working on a platform it has not run on.
  Say it renders and was not yet applied there.
- When a background command's exit code matters, do not read it through a pipe:
  `| head` masks it.
- A model call that times out may just be a cold model load. Loading an 18 GB model
  can exceed a 120 s timeout, and the warmup timing out cascades into every
  subsequent run failing, which looks like a model problem and is not.
