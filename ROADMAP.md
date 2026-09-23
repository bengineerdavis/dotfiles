# ROADMAP.md

What is likely coming and roughly in what order. Not a queue, and not a
commitment.

The four other documents divide as follows. `PRD.md` says what the project is
for. `spec.md` says what must remain true. `TASKS.md` says what is scheduled
now. `AGENTS.md` says how to work here. This file holds what is probably next
and is not scheduled yet — the things that would otherwise sit at the top of the
queue blocking it, or vanish because nothing was tracking them.

Not to be confused with `dotfiles/docs/ROADMAP-topic-cli.md`, which is a design
document for one tool. This file is project-level.

## How to use this

**When `TASKS.md` § Now is empty, the work is not finished.** Take an item from
here and interview the author about it — relentlessly, one branch of the design
tree at a time, resolving dependencies as they surface. That is the same pass
that produced `PRD.md`, and it is what turns a roadmap line into work.

Then update `PRD.md` with whatever requirements the interview settles, and
`TASKS.md` with the work items it produces. Delete the roadmap line only when the
thing exists.

**The test is the done-condition.** If you can write "done when X" in one
sentence, it is a task and belongs in `TASKS.md` § Now. If you cannot, it
belongs here. Size and urgency do not enter into it — a small vague thing is a
roadmap item, and a large precise one is a task.

Items here have no owner, no date and no done-condition. That is exactly what
separates them from `TASKS.md` § Now, whose lines move to `TASKS-RESOLVED.md`
on completion (a stopgap until the process refactor lands).
Anything here that acquires a done-condition should be promoted rather than left.

## Scheduled — pointers only

These are already broken into work items in `TASKS.md`. Listed so this file
reads as a complete picture, not to duplicate them.

- **The `topic` CLI** (A1–A7). Designed in `dotfiles/docs/ROADMAP-topic-cli.md`.
- **Topic bundles** — data-first grouping with bundle-aware playbook runs;
  three items in `TASKS.md` under § Topic bundles. First use case: an
  AI-strategy bundle per machine.
- **Factoring the AI/LLM tooling out** (B1–B8). Required by `PRD.md`.
- **The trust ladder and its ledger.**
- **Two copier templates** — a general repository template, and one for the
  chezmoi-Ansible topic format.

## Not yet scheduled

### Over-arching policy and where it lives

The author's open internal debate, recorded 2026-09-12 rather than resolved.
Some policy is independent of this repository — this repo may be an
*implementation* of a policy whose home is elsewhere (its own repository, a
future impromptu-the-tool, or a machine-local store). The questions nested
inside it:

- If an over-arching policy exists as its own artifact, this repo and other
  sources and tooling would *reference* it rather than contain it.
- This repo can legitimately carry a policy that it feeds to builders (agents)
  or that builders read — the near-term contract for that is a TASKS.md item.
- When a policy tool is built, there must be a known path for saving its
  output and configuration into this machine-management repo where retention
  is wanted — or, if policy lives here, the tool takes over managing it.
- The AI-home decision (2026-09-12) lands skill, eval and tooling work in
  `ai-prompt-library` now and `impromptu` eventually — but the author marked
  that neither home clearly has full scope for *policy management*.
- 2026-09-14 milestone: the author announced `llocallabs.ai` — a collection
  of repositories consolidating the AI tooling and agent projects, starting
  with a new anchor repo, with AI research, testing and benchmarking leaving
  this repo (tasks in TASKS.md § Now). A candidate answer to this section's
  question — a strategy/policy agent is meant to live there — but
  consolidation is deliberately undecided, so the safe default below stands
  until the collection's shape is recorded in `PRD.md`.

**Safe default until the author settles it:** policy stays where it is today —
repo docs and spec for repository-level rules, `~/.local/state/ai-policy/`
layers for machine-local rules, `bin/policy` as the resolver — and no new
policy home is created. This line is deleted only when the over-arching
question is answered and the answer is recorded in `PRD.md`.

### A policy-aware CLI agent, or the topic CLI growing one more job

`AGENTS.md` § What agents do here makes build-versus-configure routing agent
policy, with per-machine granularity. The author named it a candidate for
enforcement by the `topic` CLI (A1–A7, scheduled) or by a separate CLI agent
that abstracts configuration management and updates — a tool that knows what
each machine should have can tell an agent what is configuration work versus
a build. Unscoped; worth settling alongside the topic CLI's `bootstrap`
command (A5), which already owns "run a topic's install" — the same state
knowledge this would read.

**Determinant detection functions are a required capability**, not a nice-to-
have. The boundary is not always visible on the surface: an action can be
valid as configuration (a well-formed task, a plausible config file) and still
be substantively a build — a template writing real code, an install task
compiling a bespoke project, a "config" embedding logic. The functions classify
actions deterministically, and their minimum contract is to **surface the
finding to the author with override** — never a silent pass, never a silent
block. Refusing is the agent ladder's job; the tool's job is to make the
boundary visible so a human decides.

The threshold for when agent-work graduates into a function at all is a
separate, researched policy: `ai-prompt-library`'s TASKS.md owns the research
and the panel-of-judges council decision (queued 2026-09-12), and this item
consumes its verdict.

### Topics as portable, installable modules

`PRD.md` states the requirement: a topic should be installable on its own, so a
third party can borrow one piece of this configuration without adopting the whole
repository. What is undecided is the boundary — what a topic may depend on, how
it declares that, and what happens to shared state like the zsh lifecycle files
and the manifest schema.

Deliberately deferred. The copier topic template can be built against the format
as it stands today; the module boundary only has to be settled before anyone
outside this machine relies on it.

Researched 2026-09-14, so the boundary decision is made with this rather than
from scratch:

- **The ecosystem's unit of distribution is a collection, not a role.**
  `ansible-galaxy collection install` is what makes a role installable by a
  third party with no knowledge of this repo's format. Standalone Galaxy roles
  still exist but are superseded and carry no changelog standard. This matters
  because `PRD.md` asks for borrowable "without adopting the whole repository" —
  a stronger claim than borrowable into another repo that already uses this
  format, which conventions alone can satisfy.
- **`topic.yml` at role root is correct and does not block any of this.**
  Verified empirically: `meta/main.yml` rejects unknown top-level keys
  (`'topic_name' is not a valid attribute for a RoleMetadata`), so the existing
  comment is right. But `topic.yml` and a valid `meta/main.yml` are not mutually
  exclusive — all 27 topics currently have **zero** `meta/` directories, so
  `galaxy_info`, `dependencies` and `argument_specs` are simply absent. Adding
  them is additive and does not disturb discovery.
- **Two collection-native tools wait on the same boundary decision, researched
  2026-09-22.** `ansible-creator` (ansible org, 157★, active, Apache-2.0)
  scaffolds a standard collection tree (`init`/`add`) — but this repo's 27
  topics follow the bespoke `topic.yml`-at-role-root convention above, not
  the generic layout `ansible-creator` generates, so using it now would mean
  retrofitting its output rather than saving work. `ansible-test units` is,
  per Ansible's own docs, "driven through pytest" — it wraps pytest with
  collection-aware namespace injection (fixing the
  `No module named 'ansible_collections'` class of error) and coverage, so
  it does not compete with this repo's own `tests/` suite, it would only
  apply to custom Ansible modules/plugins — and this repo has **zero**
  (`plugins/`, `module_utils/`, `galaxy.yml` all absent, confirmed by
  search). Both tools become relevant the moment topics become a real
  collection, and not before; noted here rather than in TASKS.md because
  neither has a done-condition until that decision lands.
- **Changelogs are collection-scoped upstream.** `antsibull-changelog` generates
  `changelogs/changelog.yaml` per collection; roles appear inside it as objects.
  There is no per-role changelog standard, so the per-topic `CHANGELOG.md` this
  repo now requires is house style — deliberately using antsibull's category
  names so the conversion is mechanical if topics ever become a collection.

Unchanged by the research: the open question is still what a topic may depend on
and how it declares it. `topic_requires` names deps this repo's playbook
resolves; `meta/main.yml` `dependencies` names roles Ansible resolves. Deciding
whether those stay separate, or one generates the other, is the boundary.

### Develop topics with heavy tests; import them without

Raised 2026-09-14: topics might live in their own library where development and
testing happen — molecule scenarios, VMs, the slow things — and be imported for
ordinary use without any of that coming along. Far off, and deliberately an idea
rather than a task.

Worth recording now because the ecosystem already has the mechanism, which moves
this from "can we" to "what would it cost". `galaxy.yml` takes a **`build_ignore`**
key (Ansible 2.10+): "a list of file glob-like patterns used to filter any files
or directories that should not be included in the build artifact." Listing
`molecule/` and `tests/` there gives exactly the split — the source repository
keeps them, the built collection does not. Only `galaxy.yml`, `*.pyc`, `*.retry`
and `.git` are filtered by default, so test directories must be named explicitly.

This makes the collection direction stronger rather than adding a second one: the
library, the versioning, the changelog and now the dev/ship split are all the same
mechanism. The cost is still the boundary question above — a collection has to
say what a topic may depend on before it can be built at all.

**The split is not binary, and that matters.** Also raised 2026-09-14: a user
importing a topic should be able to *opt in* to its tests if they want them —
to verify a topic on their own machine rather than trusting ours. That pulls
against `build_ignore`, which removes files from the artifact outright: anything
filtered is not available to opt into, only to clone the source for.

So the likely shape is two tiers rather than one line, drawn by what a test
*needs* rather than by what it is:

- `molecule/` — needs a VM or container, a driver, and minutes. Development only;
  a consumer cannot run it without adopting the whole harness. `build_ignore`
  this.
- `tests/` — the pytest suites that check a topic's own logic, already co-located
  per `docs/TOPICS.md`. Cheap, no driver. Ship these and let running them be the
  opt-in.

Unverified, and the thing to check before designing further: whether
`ansible-test` can run a collection's shipped tests from an installed collection
or only from a source checkout. If only from source, then "opt in" means "clone
the repo" and the tiering above buys nothing — which would be worth knowing
before building toward it.

Not essential. Recorded so the dev/ship split is not designed as a single
on/off switch and then found to be one.

### Use the accept-vs-revise signal in git history as training data for the judge gate

Use the accept-vs-revise signal in git history as training data for the judge gate. The gate itself shipped (PR #1) and decides on real test results; this is the unbuilt half of that task, separated rather than quietly dropped. The idea: `binned` records whether a generated script was accepted, revised, or discarded, and that history says which scripts a human actually wanted. Open questions before it is schedulable — where that signal is stored today, whether there is enough of it to be worth anything yet, and what it would change about the gate, since a gate that already defers to real test results may have little left to learn.

### Add refactoring principles to `spec

Add refactoring principles to `spec.md` for the two failure modes we can already see coming: a test suite that grows faster than the behaviour it covers, and features that overlap until no one can say which one owns a concern. The suite is 218+ tests and every new guard adds two (refuse and relent), so growth is structural, not accidental. Wanted: a rule for when a test earns its place, a rule for collapsing near-duplicate cases, and a redundancy check that runs on demand rather than by vibes.

### Sandbox the agent, if containment is actually wanted

Sandbox the agent, if containment is actually wanted. `docs/PERMISSIONS.md` states plainly that the permission layer catches accidents and does not contain a misaligned or prompt-injected agent, and that this is not fixable at that layer: `uv run --with <anything>`, `pytest`, `bats`, `./run-role.sh` and git hooks all execute arbitrary code and are all required. Containment means a restricted filesystem view, a container, or egress control at the OS level. Evaluate before building — this is a solved problem elsewhere (seatbelt/sandbox-exec on macOS, Landlock and bubblewrap on Linux, devcontainers, firewall egress rules) so use `review-best-practices`. Rank on: does it survive an interpreter, does it break the documented test command, and what does it cost per session.

### A local model that reacts to errors and proposes fixes

Same shape as the agents that turn production errors into pull requests, but
local and personal. The trigger is a failure rather than a prompt, which is what
makes it different from everything else here.

Local by requirement rather than preference: error text and stack traces can
carry work content, so this is governed by the policy layers and cannot use a
remote model under the current rules.

Open before it can be scheduled — what it watches (test failures, shell exit
codes, a log), whether it may open a pull request or only draft a patch, and how
it avoids proposing fixes for failures that are symptoms of work still in flight.

### A queryable knowledge base of the repository

Readable by a human directly, not only feedable to a model. It is the artifact
that survives context compaction, model swaps and long gaps — session memory
does not.

`spec.md` and `PRD.md` are the beginning of this. The gap is everything true
about the system that is neither a requirement nor a constraint.
