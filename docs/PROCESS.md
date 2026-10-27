# PROCESS.md

How work runs in this repository: the loop, the queue and its workers, and
how a task list is cut. `AGENTS.md` links here and keeps only the rules that
bind — branches, claims, gates, trust. This file explains; `spec.md`
constrains.

## The work loop

Treat work as a loop, not a single prompt. The shape is RECL, by analogy with
a REPL:

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
  provisioning may install and trigger a tool, never contain its logic or
  state — settles most questions about where something belongs.
- **`AGENTS.md`** — the rules that bind: branches, claims, gates, trust, and
  the expertise that is not obvious from reading the code.
- **the backlog queue** (`backlog/`) — what is in flight, who has it, and what is blocked.

`spec.md` sits across all four steps: it is what must stay true whichever step
you are in, and it is what Check checks against.

## The queue and the workers

Agents work a task queue as a pool of workers. The division of intelligence
is deliberate: **the queue is smart, the workers are naive.**

The queue carries the intelligence. Each task file is written so a worker can
pick it up cold — scope, done-condition (the Definition of Done field), owner
(assignee), what it hands to the next (§ Decomposing work into items). Around
the tasks, the queue holds the coordination state: orchestration leases (who
holds what — `backlog-py orchestration queue`), and the worker budget
(`AGENTS.md` § Everything is branched — how many execution sessions may run
on a machine).

The worker's contract is small. Read the task, claim it
(`backlog-py orchestration claim TASK-N --actor <you> --expected-version <v>`),
do the work, prove the done-condition, report
(`orchestration record-run` — the run history lives in the task file),
release the lease. Two duties frame it:

- **Write the task before you start.** Any work done by an agent or subagent
  gets a backlog task first, saying what it is doing and what done means.
  Work split across several agents is several tasks, one per unit of work.
  See `spec.md` § Work — agent work is defined and assigned before it
  starts.
- **Update the task before you finish.** Sessions keep their own in-memory
  task lists, which fragment as soon as two are running; the queue is the
  shared one. Status, notes, and the final summary go in the task file.

A worker that needs to understand the whole architecture to execute its line
is a sign the line was cut wrong — cut smaller until one naive worker can
hold it whole (§ Decomposing work into items, the context-unit rule).

**Where the queue lives.** `backlog/` — per-task Markdown files managed by
backlog-md-py (the migration decision is `docs/BACKLOG-MIGRATION.md`). One
file per task: title, status, description, acceptance criteria, definition of
done, assignees, labels, dependencies, run history. The files are the source
of truth and commit with the code; `backlog-py board` is the index over them.
Task creation lands as its own commit, immediately — a task still sitting
uncommitted when context runs out is a task nobody ever had — and under the
2026-10-23 ruling those commits go straight to main as coordination overhead
(AGENTS.md § Everything is branched carries the carve-out).

### Three roles

Work separates into coordination, planning, and execution. The MVP keeps the
split minimal: coordination calls a planner, then dispatches one or more
execution sessions — no parallelism beyond that is required, and the
invariant underneath is stricter than the parallelism: **one task, one
execution session, one writer agent, one worktree, one branch, one venv.**

- **Coordination** — one live session. Commits task lines, prepares each
  execution slot (worktree, branch, venv, line), dispatches, collects
  (merges back serially, suite after each — `docs/WORKTREES.md` § Lifecycle),
  and relays questions: an execution session that hits a blocker marks its
  line `[blocked: <question>]` (the existing convention) and parks; the
  coordinator relays to the author and writes the answer back on the line.
  One live coordinator means one question channel instead of N. The
  fallback is direct and deliberate: if the coordinator is unreachable, any
  session may ask the author itself — asking is never an incident, and a
  stuck session must not stay stuck for want of a relay.
- **Planning** — read-only. Drafts task lines (scope, done-condition, owner,
  worktree, hands-to-next) from a roadmap item; the coordinator commits
  them. The planner never writes to the tree.
- **Execution** — one session per task. The assigned agent holds the write
  right; every other agent in the session is read-only (`AGENTS.md`
  § Everything is branched, one session one writer). It works inside its
  worktree and its own venv, never mutates shared machine state — no shared
  profile exports, nothing written outside its worktree except its own venv
  cache — and asks through the coordinator. The budget counts execution
  sessions only.

Nested subtask-branching — sub-branches of a task branch running in parallel
— is deliberately deferred: the MVP is one branch per task, buying time to
extend the model for parallel subtask branching later.

Env isolation uses existing mechanisms only: the per-session process
environment, the per-worktree venv (`docs/WORKTREES.md`, `UV_LINK_MODE=copy`),
and the worktree as the task's own scratch space. Nothing homebrewed.

## Observations are deliverables

Work on one item often reveals something about others: a timing dependency, a
collision surface, a cluster that must be classified together, a recorded
claim the tree contradicts. Said in a session, it dies with the session — the
handoff merges in this repo keep proving that prediction.

- An observation a future session would need is written down the moment it is
  made, attached to the task or document it concerns — never left in chat,
  never held in a private queue.
- A finding that contradicts a recorded claim is evidence: update the claim
  or mark it suspect, citing what was found. `spec.md` § Evidence applies to
  these the same as measured numbers.
- An observation with no home yet gets one — a line in the affected item, a
  § Planned task, or a line in the handoff snapshot.
- Produce them deliberately. After finishing an item, ask what it changes
  about other items, what the tree showed that the docs deny, and what
  ordering the work revealed. If the practice earns its keep, promote it to
  a skill (home: `ai-prompt-library`) — do not build it preemptively.

## Decomposing work into items

Turning a roadmap item into work an agent can be handed is the step with the
least written down, and it is where planning actually happens. The task file
already says what a task must contain; this says how to arrive at the
tasks. The rules below are the ones A1–A7 and B1–B8 were cut by — recorded
after the fact, because they were applied on instinct the first time and that
does not survive a new session. One of them was learned by being broken: B4
had to be re-cut, and the rule about outcomes is what came out of it.

**Reduce tasks to the smallest units of context.** Cut until each piece is
something one worker can hold whole — one done-condition, mergeable on its
own — and each piece gets a subtask with its own subsession and worktree
(`AGENTS.md` § Everything is branched). Not smaller for its own sake: the
smallest unit that still has one done-condition. This is what lets the worker
pool stay naive (§ The queue and the workers).

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
something. When that happens, change the task and say why in the commit —
a plan quietly diverging from the work is how the queue stops describing
reality. Anything that turns out to be bigger than expected and unscheduled
goes to `ROADMAP.md` rather than growing the item.

When a task's finished work holds more than one merge — the test is whether
each part can be described in one sentence without "and" — split it into
buckets before publishing: `docs/WORKTREES.md` § Bucketing has the steps,
including how each bucket is checked alone and all of them together.

## What kind of dependency is it

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

## What multi-item branches cost

Share a branch only for atomic pairs. The temptation is to group a whole refactor
onto one long-lived branch, and it should be resisted, because that reproduces
exactly the problem branches were adopted to fix: a big-bang merge whose diff
nobody can review and whose conflicts arrive all at once.

There is a useful self-regulating property here. A branch carrying several items
has a larger blast radius and is likelier to touch a policy path or a deployed
file, so it fails § Merge gates (`AGENTS.md`) and drops to review by a human.
Multi-item branches get more scrutiny automatically — which is right, and which
is also a signal: if a branch keeps failing the gates, it is probably carrying
more than one decision.
