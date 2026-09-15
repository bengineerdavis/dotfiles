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

**When `TASKS.md` § Now is empty, the work is not finished** — read `ROADMAP.md`.
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

### Decomposing work into items

Turning a roadmap item into work an agent can be handed is the step with the
least written down, and it is where planning actually happens. `TASKS.md`
already says what a task line must contain; this says how to arrive at the
lines. The rules below are the ones A1–A7 and B1–B8 were cut by — recorded
after the fact, because they were applied on instinct the first time and that
does not survive a new session. One of them was learned by being broken: B4 had
to be re-cut, and the rule about outcomes is what came out of it.

**One item is one thing with one done-condition.** If you cannot write "done
when X" in a sentence, you have a theme rather than an item. The done-condition
is what the agent gets checked against; without one it picks its own, and
nothing can say whether the work finished.

**Lead with the deciding items.** A1 answers the roadmap's open questions and
B1 picks the new home for the factored-out tooling. Neither builds anything,
and both unblock everything after them. Deciding is cheap; building on an
undecided foundation is expensive, and the cost lands as rework rather than as
a failure you can see. The first item in a group is usually a decision.

Keep them small enough to merge on their own, in one commit. A decision item is
only an unlock while it is landing fast; one that grows an implementation
alongside it stops unblocking anything and starts blocking everything.

**Sequence by what blocks what, not by what matters most.** Importance decides
whether a group is scheduled at all. Inside a group, only dependency decides
order. B3 defines the state contract before the backup work, not because it
matters more but because you cannot choose what to back up without knowing who
owns the data.

**Cut along outcomes, not along components.** This is the rule that prevents
most bad splits, and it was learned by breaking it. The factor-out was first cut
as "extract the resolver" and "add the capability interface" — two components,
neither an outcome — and those two could not be landed separately. Re-stated as
the outcome, "topics consume policy through a declared capability, from its new
home", it is obviously one item. Components tempt you to split because they have
names; outcomes do not split unless the value does.

**Test every cut before you make it, not after.** For each proposed split, ask
whether you would ship the first half on its own. If the answer is no, do not
make the cut. The dangerous case is not a half that is obviously incomplete —
it is one that *looks* finished while leaving the problem in place, which is
exactly what extracting the resolver alone would have done.

**Say what each item hands to the next.** A dependency is information, code,
verification, or nothing at all — and which one decides how the work is branched.
Write it into the task while the reasoning is fresh; § What kind of dependency is
it explains what each implies. Left unstated, it gets rediscovered as a merge
conflict.

**Do not decompose past self-containment.** Same rule as commits: atomic means
self-contained, not small. An item that leaves the repo broken so the next one
can fix it is a bad split however tidy the boundary looks.

**Find the collision surfaces before assigning anything.** Before handing items
out, ask which of them touch the same files. Doing that for A1–A7 and the factor-out items
turned up four: dependent items needing stacked branches, items that cannot be
split, shared `conftest.py` fixtures, and the governance documents that
unrelated groups all end up editing. Every one of those would have surfaced as
a merge conflict discovered mid-task instead.

**A rewrite gets a characterization-test item before it starts.** Pin the
existing behaviour, then let the reimplementation run against the same tests.
Parity becomes proven rather than assumed, and review stops meaning "read every
line". This is its own item because it has its own done-condition and because
skipping it is invisible until the rewrite is already finished.

**The plan is a hypothesis.** Items merge and split as the work teaches you
something. When that happens, change `TASKS.md` and say why in the commit —
a plan quietly diverging from the work is how the queue stops describing
reality. Anything that turns out to be bigger than expected and unscheduled
goes to `ROADMAP.md` rather than growing the item.

## What this repo is

A chezmoi-managed dotfiles repo with an Ansible layer for system state.

**Read `dotfiles/docs/TOPICS.md` first** — topic structure, the `topic.yml`
schema, tiers, lifecycle tags, dependency resolution, commit granularity and the
CRUD-ownership invariant. It is the source of truth and the 39 topic files cite it.
`dotfiles/docs/ARCHITECTURE.md` has the big picture,
`CONTRIBUTING.md` at the root carries the workflow around it.

The repo-root `docs/` tree is an older copy of the same material, kept but not
maintained. Edit the `dotfiles/docs/` copies.

The one rule worth repeating here because it is the most common mistake: **one
concern per layer.** chezmoi owns dotfiles and symlinks, Ansible owns package
installs and system state, zsh owns shell runtime config. A symlink task in Ansible
belongs in chezmoi; a `brew install` in a shell script belongs in Ansible.

### Machine-specific values are resolved, never written out

Anything that differs between machines or environments — home directory, username,
hostname, OS and architecture, the Homebrew prefix, XDG directories, per-machine
toggles — is resolved **on the target at deploy time by the layer that owns the
file**, never pasted in as a literal from whichever machine happened to author it.

Resolve it at the highest layer that already knows the value:

1. **The consuming tool**, where it expands paths itself — `~` in a shell script, or
   in an opencode permission pattern. Nothing to render and nothing to drift.
2. **chezmoi**, for anything it deploys: `{{ .chezmoi.homeDir }}`, `.chezmoi.os`,
   `.chezmoi.arch`, `.chezmoi.username`, `.chezmoi.hostname`. The file becomes
   `*.tmpl`; the target path is unaffected.
3. **Ansible**, for values only a provisioning run can discover or must persist —
   the resolved brew prefix, a fact gathered from the machine, a path written into
   state another run reads back.

Reach for a lower layer only when the one above genuinely cannot supply the value.
Routing a value Ansible discovers through a chezmoi template, or a value chezmoi
knows through an Ansible task, adds a moving part and a second place to be wrong.

**Why this is a rule and not a preference: the failure is silent.** A hardcoded
`/home/bdavis` in an `external_directory` allow-list does not error — the rule
simply never matches, the surrounding deny stays in force, and the config looks
healthy while doing the opposite of what it says. That exact bug sat in
`dot_config/opencode/` until 2026-09-14. A machine-specific literal that has not
broken yet is one whose machine has not differed yet — `dot_zshrc.tmpl` still
carries several, correct only because one box's username happens to match.

So: when a value **must** be baked in, the check that it resolved belongs next to
it. A rule that cannot match is indistinguishable from a rule that is merely
strict, and neither the tool nor the deploy reports the difference.

## What agents do here — and what they refuse

Agents in this repository work the trunk: deciding and managing **which tools,
services, and configurations belong on which machines** — topics, chezmoi
state, Ansible tasks, with per-machine granularity. Writing an install task or
a config file is the job; that is configuration, not a build.

If satisfying a need would require **building** a tool, service, or bespoke
code, agents do not build it here. The ladder, in order:

1. **Outsource.** Route the work to its home and do it there. AI work —
   skills, evals, policy, tooling — goes to `ai-prompt-library` (impromptu
   eventually), per the author's 2026-09-12 scoping decision.
2. **Notify and ask.** If the destination is unclear or the author is present,
   say what would need building and where it could live, and ask before
   anything is created.
3. **Refuse.** If the author declines outsourcing, the build does not happen.
   There is no middle ground where the tool quietly gets built here anyway.

Machine-specific granularity is part of the question, not an afterthought:
**which machines need this** is asked before **how do we get it**, because the
answer can change the decision — something worth building for one machine may
not be worth it for the fleet.

The boundary is not always visible on the surface. An install task that clones
and compiles a bespoke project, a template that writes substantial new code, a
"config" fragment that embeds logic — each passes a surface check as
configuration while being a build. Until the enforcement tool exists, agents
run the ladder as a deliberate check on their own work and **surface probable
builds to the author** rather than deciding silently; the author decides and
can override. Determinant functions that classify actions mechanically — with
surface-and-override as their minimum contract, never a silent pass or a
silent block — are a recorded requirement on the enforcement tool in
`ROADMAP.md`. Building those functions here would itself be a build: they
land with the tool, or the author decides otherwise.

This policy is a candidate for enforcement by the `topic` CLI
(`dotfiles/docs/ROADMAP-topic-cli.md`, `ROADMAP.md`) or a future CLI agent
that abstracts configuration management and updates: a tool that knows what
each machine should have can also tell an agent what is configuration work —
its job — versus a build, which is out of scope. Until that tool exists, the
ladder is enforced by agent judgment and by review.

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

- **Items that must land together share a branch.** Rare, and usually a sign
  the decomposition was wrong — see § Decomposing work into items, which exists
  to stop producing these. B4 was originally cut as two such items and is now
  one.
- **Dependent items stack.** Branch off the parent item's branch, not main, and
  rebase when the parent merges. A3 builds on A2's CLI, so it cannot start from
  main and still compile.

### What kind of dependency is it

"Depends on" is four different relationships, and they do not get the same
answer. The discriminator is **whether the earlier item can merge on its own**.
If it can, the items stay on separate branches. If it cannot, they share one.

**Information dependency — separate branches, strict order.** The earlier item
produces a decision or a document, not code. A1 answers the roadmap's open
questions; B1 picks the new home; B2 writes the move manifest; B3 defines the
state contract. Each merges alone in one small commit, and unblocks the rest by
being on main. Nothing needs stacking because there is no code to build on.

These are the cheapest items in any plan and they should be landed first and
fast, because **a decision item is a parallelism unlock**. B1, B2 and B3 on main
turn B4 through B6 from a serial chain into work several agents can take at
once. Sitting on an unmerged decision serialises everything behind it.

**Code dependency — stack, or wait for main.** The later item builds on the
earlier one's code. A3, A4 and A5 all need `topic new` from A2; B5 and B6 need
the moved resolver from B4. The parent is independently mergeable, so branch the
child off the parent and rebase when the parent lands — or simply wait, if
nothing is gained by starting early.

Stacking buys parallelism and charges rebases for it, and the charge compounds:
every stacked branch rebases when its parent merges, and conflicts multiply with
depth. Stack two deep freely. Three deep with a reason. Deeper than that, either
collapse the stack into one branch or admit the decomposition was wrong.

**Atomic dependency — one branch, always.** Neither half stands alone. This is
not really a dependency; it is a decomposition that split something indivisible.
Sharing a branch is the repair, and re-cutting the items is the fix. The case
that produced this rule was the factor-out, first cut as "extract the resolver"
plus "add the capability interface" — it is now the single item B4, because
either half alone leaves the duplication in place while looking done.

**Verification dependency — the parent must be on main first.** Characterization
tests have to land before the rewrite starts, so the rewrite branch inherits
them. Starting the rewrite from a branch that predates its own safety net
defeats the point of writing it.

**And one thing that looks like a dependency and is not: a collision.** Two items
touching `conftest.py` or the governance documents are not ordered by logic, they
just cannot be merged carelessly. The remedy is different — sequence them, or
land the shared change first as its own item. Treating a collision as a
dependency builds a stack nothing required.

### What multi-item branches cost

Share a branch only for atomic pairs. The temptation is to group a whole refactor
onto one long-lived branch, and it should be resisted, because that reproduces
exactly the problem branches were adopted to fix: a big-bang merge whose diff
nobody can review and whose conflicts arrive all at once.

There is a useful self-regulating property here. A branch carrying several items
has a larger blast radius and is likelier to touch a policy path or a deployed
file, so it fails § Merge gates and drops to review by a human. Multi-item
branches get more scrutiny automatically — which is right, and which is also a
signal: if a branch keeps failing the gates, it is probably carrying more than
one decision.

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

### Pull request descriptions

**A pushed branch is not a pull request.** `git push` prints a
`.../pull/new/<branch>` URL; that is an offer to create one, not one that
exists. Reporting it as a PR link claims something that has not happened — open
the PR with `gh pr create`, then report its number.

**Never open one with an empty body.** Use `--body-file`, because a description
worth reading does not survive being typed on a command line.

A PR description is written for a **different reader than a commit message**,
which is why `commit-hygiene` explicitly excludes them from its scope. A commit
body serves someone reverting one change and asking what it was. A PR
description serves someone deciding whether to merge several changes at once,
who has not been in your session and cannot see what you ruled out.

Carry these, and do not simply list the commits — the reviewer can read those:

- **What changes, and the reasoning they would otherwise reconstruct.** If a
  design decision took an hour to reach, it takes them an hour too unless you
  write it down.
- **What was verified**, including which mutations were tried and caught. "Tests
  pass" is not verification; the suite passing before the change is also tests
  passing.
- **Why it needed review rather than self-merging** — name the § Merge gates
  clause it failed. That is the reviewer's first question.
- **What was deliberately left out**, and why. Scope someone else has to guess
  at is scope they will relitigate.
- **Prerequisites split into their own commits**, and what made them
  prerequisites rather than cleanup.

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
# Tests — pytest is primary. Needs all six, or parts of the suite skip or ERROR.
uv run --with pytest --with hypothesis --with typer --with questionary --with pyyaml --with pillow pytest tests -q
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

The `llm-ctx` half of `tests/policy/test_logging_guards.py` needs `--with llm
--with files-to-prompt` on top, because it imports the script and the script
declares those. Without them those five tests SKIP — quietly, and they are the
ones proving a policy guard relents. They are left out of the command above
because those two pull 34 transitive packages onto every run, which is a real
cost against a suite already too slow to run per change. Run them deliberately
when touching a policy caller:

```bash
uv run --with pytest --with pyyaml --with llm --with files-to-prompt pytest tests/policy -q
```

Without `pillow` it is louder but worse: `tests/ollama_evals` produces 53 collection
ERRORS instead of 52 passes, because its `conftest.py` imports the eval harness,
which imports Pillow at module level. An error is not a skip — the suite aborts
rather than running what it can. That the documented command omitted `pillow` for
as long as it did is the argument for running the command as written now and then,
rather than the one in your shell history.

## Commits

**`CONTRIBUTING.md` § Commit granularity is the source of truth.** Read it
before committing. `spec.md` § Change records states the invariants — including
that staging is verified rather than assumed, and that a human-readable
changelog is kept alongside the commit history rather than instead of it. The
short version, so this file is usable on its own:

One commit is one reviewable decision. The test is not file count — it is whether a
reader can hold the *why* in their head, and whether the change can be reverted on
its own without taking unrelated work with it.

**Size the message to the change.** A subject line alone for mechanical edits, a
sentence or two for small single-purpose changes, one or two short paragraphs for
ordinary features and fixes. The `commit-hygiene` skill is the source of truth and
says why: a message longer than the change warrants is not thoroughness, it is
evidence the commit should have been two. Reach for splitting before you reach for
more prose.

This was measured, not asserted. Across one session the median body ran 232 words
against a repository median of 114, topping out at 521 — roughly double the house
norm, while a skill stating the rule sat installed and unread.

Sequence commits so every intermediate state works. Land the inert parts first and
the switch that activates them last — for an Ansible topic that is usually
`topic_os`, which gates whether any of the preceding commits run at all.

Do **not** over-split. A commit that leaves the tree broken so the next one can fix
it is worse than a slightly coarse one: it breaks `git bisect`. Atomic means
self-contained, not small.

**Writing a task is itself a commit.** Every task you queue in `TASKS.md` lands as
its own commit, immediately, separate from whatever work is in flight — two tasks
are two commits, and revising a queued task is a further commit rather than a
rewrite of the one that added it. Where creating a single task honestly takes more
than one commit, branch instead of interleaving it with in-flight work on main. The
point is that a task survives the session that thought of it: a queued line still
sitting in the working tree when context runs out is a task nobody ever had.
`TASKS.md` § Conventions carries the same rule for readers who never open this file.

Durable *why* belongs in a code comment next to the decision, where it survives
rebases and is read by people who never open git log. The commit body carries only
what a reverter needs.

Splitting is also a review pass in its own right. Re-reading the clamav Debian port
as six commits surfaced a bug the single commit had hidden: a new
`clamav_clamd_conf` var collided with an existing `register:` of the same name, and
registered vars outrank role vars — so the rendered script would have received a
task-result dict instead of a path.

**Rewriting hooks leave residue.** Formatter-type hooks (trailing-whitespace,
end-of-file-fixer, ruff-format) modify the working tree and fail the commit, so
re-committing without looking can land a mix nobody reviewed as a unit. After any
commit in a repo whose hooks rewrite files, `git status` must be clean or the
residue is staged and committed deliberately. This repo's hooks only check, so
`git show --stat HEAD` covers it here — the rule bites in other repos, like
ai-prompt-library, where formatters run.

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

### Conventions

Conventions live in **`docs/`**, one file per subject, so the repository
root holds only the five documents that govern the project:

- **`docs/PYTHON.md`** — uv, PEP 723 dependency blocks, pytest, ruff, ty,
  prek, logging and error handling.
- **`docs/PERMISSIONS.md`** — what the agent may run, the three tiers in
  `.claude/settings.json`, and the threat model they do and do not address.
  Read it before widening a rule.
- **`docs/REFERENCES.md`** — every external standard this repo follows,
  the version it follows, and when that was last checked. Add a row before
  adopting a standard; a convention with no version means whatever its latest
  revision says.

`CONTRIBUTING.md` is the human entry point and lives there rather than
here on purpose: GitHub only discovers `CONTRIBUTING.md` in `.github/`, the
repository root, or `docs/`. In any other directory it never reaches the
Contributing tab or the sidebar shown when someone opens a pull request — which
is the one moment it exists to be read.

This file stays general on purpose. How work runs here is reusable across
projects; conventions are the part that swaps out. A repository that adds another
language adds `docs/<LANGUAGE>.md` and one bullet above, and changes
nothing else here. See `docs/README.md` for what belongs there and what
does not.

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
and release prose, anything a tool prints to a user, and **commit messages, pull
request descriptions and code comments** — the three written most often and
counted least.

Length is part of it. Prose should be proportional to what it describes.

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
than abstracting it — `CONTRIBUTING.md` rule 2 has the pattern. A topic
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
