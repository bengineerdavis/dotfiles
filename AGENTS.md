# AGENTS.md

Instructions for coding agents working in this repository. Human-facing detail lives
in `docs/` — this file links there rather than restating it, so the two cannot drift.

`spec.md`, beside this file, is the third layer: the properties that must remain
TRUE regardless of who is working. This file is practice, `docs/` is explanation,
`spec.md` is constraint. Read it before changing a guard, a teardown path, a
policy layer, or anything that reports a measured number.

## Start here

**Read `spec.md` and the backlog queue before starting work.** They pair:
`spec.md` says what must remain true; the queue — per-task files under
`backlog/`, browsed with `backlog-py board` or
`backlog-py task list --plain` — says what is in flight and what each task's
done-condition is. Read `PRD.md` too when the work is about scope — whether
something belongs here at all.

**When nothing is claimable, the work is not finished** — read `ROADMAP.md`.
`backlog-py orchestration eligible` lists tasks whose dependencies are met
and whose leases are free; an empty eligible queue means "nothing scheduled",
never "nothing to do". The roadmap says what to do next: take an item,
interview the author about it, then update `PRD.md` with the requirements
that settles and create backlog tasks for the work items it produces. Any
agent or model working here is expected to have read both — a change that
satisfies the task and violates the spec is not done.

**Prime directive: do not work if something is unclear. Ask.** A guess and a
decision look identical once they are written down, and the guess costs the whole
build while the question costs one exchange. If part of the request is clear and
part is not, do the clear part and ask about the rest at the point it matters.
See `spec.md` § Work — unclear requirements stop the work.

**How work runs is defined in `docs/PROCESS.md`** — the work loop, the task
queue and its workers, observations-as-deliverables, and how tasks are cut.
Read it before your first task. `AGENTS.md` keeps only the rules that bind;
`docs/PROCESS.md` carries the process they serve.

## What this repo is

A chezmoi-managed dotfiles repo with an Ansible layer for system state.

**Read `docs/TOPICS.md` first** — topic structure, the `topic.yml`
schema, tiers, lifecycle tags, dependency resolution, commit granularity and the
CRUD-ownership invariant. It is the source of truth and the 39 topic files cite it.
`docs/ARCHITECTURE.md` has the big picture,
`CONTRIBUTING.md` at the root carries the workflow around it.

`.chezmoiroot` names `home/` as the chezmoi source state. Paths inside
`home/` stay unchanged when they describe deployed files or topic layouts.
Repository-only tooling, tests, and project docs stay outside it. Root
`docs/` is the only maintained project-level documentation tree; topic docs
stay with their topics.

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
(`docs/ROADMAP-topic-cli.md`, `ROADMAP.md`) or a future CLI agent
that abstracts configuration management and updates: a tool that knows what
each machine should have can also tell an agent what is configuration work —
its job — versus a build, which is out of scope. Until that tool exists, the
ladder is enforced by agent judgment and by review.

## Where the source of truth is

Scripts under `home/bin/` are **chezmoi source files**, named `executable_<name>`. The
deployed copy at `~/bin/<name>` is what actually runs. They drift, in both
directions:

```bash
chezmoi status                 # what differs
chezmoi add ~/bin/<name>       # deployed  -> source   (adopt a hand-edit)
chezmoi apply ~/bin/<name>     # source    -> deployed  (push a repo change)
```

Before editing a `home/bin/` script, check `chezmoi status`. Committing the source while
the deployed copy is ahead silently reverts the working version on the next
`chezmoi apply`.

## Working alongside other sessions

More than one agent session runs against this repo, sharing one checkout, one
deployed tree, and one machine. Most work never collides — in practice the only
real conflict so far came from two sessions rewriting the same large file at once.
These are the cases that do need care.

**Check the tool surface before asserting what a tool does.** A named tool in
working memory can be stale three ways: retired (`.pre-commit-config.yaml` →
`prek.toml`), versioned past its docs (Lima's `sudo`/`ssh` subcommands never
existed in v2.2.1; the real spellings are `sudoers`/`show-ssh`), or installed
and absent from it. Before a claim about a tool's behaviour lands in a report,
a PR body, or an instruction: run its `--help`, probe the binary, or grep its
config file — and cite the probe. When a tool turns out missing or
contradictory (help text disagreesing with the binary, a config key with no
consumer, a retired file still referenced), do not silently route around it:
surface it and queue a reconciliation or resolution task in the backlog, the
same way stale docs land as DOT tasks. Measured 2026-11-08, three instances in
one session: hooks described from a deleted config file, `--help` read as
"read-only" for a command that probes sudo, and a permission rule naming a
subcommand that does not exist.

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

**The rewrite window is the session that made the mistake.** A compaction or
reword is only cheap while the bad commits sit at the tip and nothing else has
merged over them: do it immediately, in the same session, before the next merge
lands. Once other work sits on top, do not rewrite — document instead (a
backup ref, a correction commit, the resolved-task entry). Measured 2026-10-03:
compaction offered for PR #36 while it sat two commits deep was sixty-plus
commits, four more PR merges and an in-flight session away an hour later, and
was skipped for exactly the reason this paragraph states.

**Notes do not travel with `git push` by default.** Provenance notes live on
`refs/notes/commits`, which the default refspec does not push or fetch — push
them explicitly alongside the branch:
`git push origin main refs/notes/commits` (fetch side: the reset procedure
above already fetches `refs/notes/*`). Without this, a reword's provenance is
invisible on the other machine even though the commits arrive. Notes are also
unversioned markup as far as forges are concerned — GitHub does not render
them; only `git log`/`git notes show` do.

**Notes are the machine channel** (author ruling, 2026-09-19, from the
research-swarm report): notes are for machines to write and read — humans
read them via `git log`/`git notes show` when needed, but nothing
human-facing is built on them. Reconciled same day: origin's
`refs/notes/commits` was a strict subset of local (5 shared shas, the 2
2026-09-19 reword notes unpushed) — local is ahead, and the one push command
above closes it. Origin also publishes `refs/notes/ai` — an AI-session
provenance trail (61 notes, the git-ai tooling writing its own namespace);
it is fetched locally as its own unowned ref and merged into nothing. One
namespace per producer; never force-overwrite a notes ref.

    git commit -o <paths> -F -    # --only: commit exactly these, ignore the rest
    git show --stat HEAD          # verify before pushing

**For a co-edited file** — a shared governance doc is the likeliest — the sequence is
`git add -p`, then a **bare** `git commit` with nothing else staged, then
`git show --stat HEAD` to verify. `git commit -o` and `git add -p` do not
compose: `--only` commits the working-tree content of the named paths and
discards partial staging, silently taking the other session's hunks. Use
`-o` for paths only you are touching; use add -p plus a bare commit when
another session may share the file.

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
  `~/.local/share/chezmoi` wherever you run it, and governs whichever branch is
  checked out there. Use `-S "$PWD"` to point at a worktree. See
  `docs/WORKTREES.md` § Main-checkout for what a stale branch fakes.

**Claim hot files with an orchestration lease** before touching anything listed
under § Cross-session hazards below: `backlog-py orchestration claim DOT-N
--actor <you> --expected-version <v>` on the covering task (or claim the task
you are doing, which covers its own files). Leases expire on their own;
`orchestration stale-leases` replaces the abandoned-claim check. The lease is
the lock's record — the rule itself is unchanged: one session, one writer,
per file.

**Other global state to check before assuming it is yours:** `~/.binned/config.toml`
(the judge pool and generation model), `~/bin` and `~/dotfiles` (deployed copies),
and long-running background jobs holding the GPU.

## Cross-session hazards

Files with more than one session touching them recently. Check `git log -3 <file>`
and `chezmoi status` before editing. Claim the covering task's lease (above)
first.

- `home/bin/executable_fetchurl` — actively developed; caused the only real merge
  conflict so far.
- `home/bin/executable_pii-redactor` — ported to Python, then extended with layered
  redaction by another session. Suite is 63 tests; run it after any change.
  Its conftest default mock is a *working* model, not `cat`: a pass-through mock
  plus exit-status assertions is green exactly when the tool leaks, which is the
  defect the layers exist to prevent. Ask for `mock_llm("cat")` explicitly.
- `home/bin/executable_model-bench` — multi-case judge suite; the reference scorecards
  in `CASES` must be re-derived if a case script changes.
- `home/dotfiles/apps/mise/files/config.toml` — two sessions edited it within an hour
  on 2026-09-11 (`b038cbe` removed two broken pipx tools, `907f3d0` pinned
  skillet). It rebased cleanly because the edits were in different regions, but
  it is a long flat list of tools that everything installs through, so the next
  pair of edits may not be so lucky. `~/.config/mise/config.toml` is a regular
  chezmoi-managed copy, so editing this source does not change what mise reads
  until the author applies the config. A tool writing the deployed file can
  drift it from this source; capture that deliberately rather than applying
  over it unseen.

  2026-09-22: seen live again — during an unrelated commit, a mise run
  auto-bumped `github:danielmiessler/fabric` 1.4.478 → 1.4.479 in the working
  tree (reverted; the pin is deliberate, see the comment above the fabric
  line) and the `npm:@openai/codex` install failed with Permission denied
  (os error 13) on `/tmp/fslock/...`. Standing machine issue, not a one-off.
- `pyproject.toml` / `uv.lock` — the root project's declaration pair. A
  lockfile conflict is resolved by merging `pyproject.toml` and re-running
  `uv lock`, never by editing the lock. Both are ignored by chezmoi (never
  deploy); `.gitattributes` carries `uv.lock merge=binary`. Register any
  dependency change here.

## Cross-repo changes

Sessions home in one repository, but the family is connected: an
agentic-layer session lands dotfiles changes, a template change ripples into
stamped projects, a tool decision here becomes another repo's dependency.
Working in another local repository is allowed; doing it silently or
carelessly is not. Each rule below carries the incident that bought it, all
from 2026-10-14/17.

**Declare the foreign repo before committing to it.** An agent session
working in repo X that needs to change repo Y says so and gets the
maintainer's acknowledgment first — direction of the work is a human
decision, not the agent's. The 2026-10-14 zshenv work was legitimate only
because the maintainer directed it from the agentic-layer session; an
autonomous session discovering "this needs a dotfiles change" stops and
asks instead.

**Inventory the foreign repo before staging anything.** `git status` first;
pre-existing uncommitted work in a foreign repo is the maintainer's, in
flight, and is never staged, never swept, never "cleaned up". `git add -A`
and bare `git commit` are forbidden twice over here — once by § Working
alongside other sessions, and again because the maintainer's pending
fabric/pipx pins sat in the working tree while an outside session committed
around them on 2026-10-14; a restore script that failed its assertion nearly
lost them, which is why partial-staging scripts assert every replacement
in-tree before committing.

**Submit per the target repository's flow, discovered before the first
commit.** This repo: `agent/*` branch, pull request, merge gates — a
2026-10-14 session stacked seven commits directly on `main`, unpushed, and
was only movable because nothing else had built on them. Solo direct-to-main
repos exist in the family; this one is not one of them.

**Check channel ownership before adding tool installs to another repo's
global state.** A `mise use -g` run from a foreign session created an
ownerless second roborev install channel shadowing the `apps/roborev`
topic's checksum-verified binary — caught by a roborev review of the
commit, not by the session that made it. TOPIC-RECIPES.md's
tool-entry-ownership recipe is the standing rule; foreign sessions read it
before touching `home/dotfiles/apps/mise/files/config.toml`.

**Point back.** A change here that another local repository depends on gets
a provenance pointer in that repository's HANDOFF or spec (the zshenv TMPDIR
work is referenced from agentic-project-template's HANDOFF; the naming-skill
watchlist handoff is the pattern). A dependency without a pointer is a
surprise waiting for the next session.

## Branches and integration

**One branch per work item**, named `<group>-<item>` — `topic-cli-a2`,
`ai-factor-out-b4`. Work items are the queue's tasks; the branch name echoes
the task (`backlog-DOT-42`, `topic-cli-a2`).

Two exceptions, and both must be stated in the task itself:

- **Items that must land together share a branch.** Rare, and usually a sign
  the decomposition was wrong — see `docs/PROCESS.md` § Decomposing work
  into items, which exists
  to stop producing these. B4 was originally cut as two such items and is now
  one.
- **Dependent items stack.** Branch off the parent item's branch, not main, and
  rebase when the parent merges. A3 builds on A2's CLI, so it cannot start from
  main and still compile. The stack lives in branches only: **pull requests go
  into `main` and nowhere else.** A child gets its PR after its parent has
  merged and it has been rebased onto `main`; `docs/WORKTREES.md` § Bucketing
  step 6 has the sequence and the failure that prompted it.

### Everything is branched

**No session commits to main directly. Work lands by merge, never by a direct
write.** One session, one worktree, one branch — including for the governance
docs. Conflicts in shared files are resolved at merge.

**One deliberate carve-out (author ruling 2026-10-23): `backlog/` writes go
straight to main.** Queue mutations — task create/edit, orchestration
claim/release — are coordination overhead, one commit per task, hooks running,
the same class PROCESS.md gives coordination's merge-backs. Per-task files only
collide when two sessions edit the *same* task, and that case is delegated to
the tool's version check, which fails the second claim cleanly. Code, docs,
and policy stay branched. A claim committed on one machine is visible on the
other only after a pull — the old § Claimed gap with a new shape, documented
rather than solved.

**The changelog collector is a separate, narrower exception (author ruling
2026-10-28).** After a PR merges, its default-branch workflow may push one
`changelog: collect PR #N` commit to `main`. It writes only `CHANGELOG.md` and
removes the fragments introduced by that PR. It never changes work code, creates
a version tag, or publishes a GitHub Release. This permission belongs to the
serialized automation, not to an interactive agent.

**One session, one writer.** A session has one assigned agent with read and
write; every other agent in it — subagents, spawned helpers — is read-only.
That single write right is what the isolation guarantee rests on: one task,
one session, one writer, one worktree, one branch.

The rule covers the author as well as every session. The author may override
it for their own commits, for example a quick fix straight to `main`; that is
a deliberate choice they make, not an exception an agent can claim. An agent
never commits to `main` directly, even when the author has recently done so.

**A fork inherits and must leave.** A forked or spawned session — opencode
`/fork`, a claude code spawn, a second cursor window aimed at the same
worktree — starts inside its parent's worktree, on its parent's branch.
Before its first commit it creates its own worktree and branch — `git
worktree add .worktrees/<sid> -b <group>-<item>`, off main, or off the parent
branch only when the stacking rules above say so. One exception, deliberate:
the author told the fork, in its instructions, to continue the parent's task
on the parent's branch. The rule binds through each tool's instruction
loading — opencode and cursor read `AGENTS.md`, claude code reads the
`CLAUDE.md` symlink to it — so it needs no tool-specific enforcement to
apply.

**A new task asks before it claims.** Finishing one task and reaching for the
next is a branch decision, and the session asks the author — interactively —
before claiming: carry on here (allowed only under the two shared-branch
exceptions above), or open a fresh worktree and branch. If the author is
unavailable, default to a fresh worktree and branch, and say so in the claim
line. The ideal is one task, one session, one worktree. Sessions already in
flight when these rules land finish under the structure they started with.

**A subtask is the same rule, one level down.** One subtask, one subsession,
one worktree — the worker is an execution session, and a subagent run inside
it is a read-only helper (one session, one writer, above). The
subtask's task file — scope, done-condition, owner, worktree name —
is its single source of truth; a handoff document is the escalation when the
context exceeds the file, and the task points at it rather than restating it.
Sub-worktrees follow `docs/WORKTREES.md`: `<sid>_sub_<slug>`, branching off
the parent branch, one writer each, merged back by the parent's owner.
Mid-task adjustment — a bugfix, a re-cut — forks the same way, off the task
branch, and merges back into it: the task branch is the integration point
for everything beneath it.

**Execution sessions are budgeted per contributor, per machine.** Concurrent
execution sessions — the tasks' writers — are capped, because they consume
that contributor's hardware and money. Coordination's own commits (task
lines, merge-backs) are overhead, not writers: the budget counts execution
sessions only. The cap is a slider: 0
is serial work, N is full parallel, and the number in between is how linear
or parallel the task list runs on that machine. The value lives in
`.agent-budget.toml` — project-scoped, gitignored, generated from
`.agent-budget.sample.toml`, never committed — and each contributor sets it
for each machine they work from, so nobody inherits a bill they did not
choose. Sessions read it at start and **fail closed**: no budget file means
ask the contributor to set one, then write it from their answer, before
claiming or spawning a writer. Cross-machine coordination still runs
through the claims board; the budget caps only what one machine runs at
once. Read-only research and review fan out freely — the budget is for
writers.

The queue went straight to main for a while, then everything was branched to
stop the collisions one shared file bought. The 2026-10-23 ruling settles the
current shape: **`backlog/` writes go to main** (the carve-out above), and the
constraint that survives either way is:

- **Merge often.** A branch that sits for a week hides its tasks and its
  claims from every other session for a week. Short-lived branches keep the
  bill small.
- **Governance docs** (`spec.md`, `PRD.md`, `AGENTS.md`) — still their own
  commit, still the surface where unrelated branches collide. Branch them like
  everything else and merge them promptly.

The live gap this opens: § Claimed is read in real time to avoid collisions, and
a claim on an unmerged branch cannot be read by anyone. Until that is resolved,
treat an empty § Claimed as "no claims I can see", not "no claims exist".

### Applying is main-only

**An agent runs `chezmoi apply` only from `main`, after showing `chezmoi
status` and `chezmoi diff`, and only when the author approves the prompt.** The
permission is `ask`; the prompt is the approval step, not a formality. Read-only
`chezmoi status` and `chezmoi diff` are expected and encouraged — an agent that
never checks drift is how twenty days of uncaptured work accumulated in
`aliases.zsh`.

**Use `czd`, not `chezmoi diff`, to read drift.** `chezmoi diff` honours
`[diff] command` from `~/.config/chezmoi/chezmoi.toml`, which on this fleet is
meld: a GUI that writes nothing to stdout and exits 0. A piped or agent-driven
`chezmoi diff` therefore reads as "no differences" on a machine that differs —
measured 2026-11-02, where a drifted `opencode.jsonc` produced empty output and
exit 0. `czd` calls `chezmoi diff --use-builtin-diff`, which bypasses the
graphical command and writes a unified diff to stdout. The meld config stays as
the author's interactive preference; `--use-builtin-diff` is the per-call
override, so nothing is changed for the human running it by hand.

`czd` also exits **1 when drift exists and 2 on error**, because `chezmoi diff`
exits 0 either way. A drift check that cannot fail is indistinguishable from one
that passed, so a caller can branch on `$?` rather than parse output.

The reason for the ordering is structural: there is one deployed tree and it
cannot be branched. `~/dotfiles` is a single set of files no matter how many
branches hold versions of them, so two agents applying from two branches
overwrite each other. Applying happens from main only, by the author or by a
session holding the apply claim in an orchestration lease. When a session holds
the claim, other sessions stay off it. (The shared checkout is the same state
at rest: `docs/WORKTREES.md` § Main-checkout is where the "verify branch before
reconcile/apply/status" rule lives, stated once.)

A target that changed since chezmoi last wrote it is a judgement call, not a
prompt to answer hastily: inspect `chezmoi diff <target>` and either fold the
local edit into the source or discard it deliberately.

**`R` in `chezmoi status` means Run, not Remove.** The reference table reads
"Run" / "Script will be run" for `R`; it is the second column's "what apply
will do" marker. A `run_before_` script shows `R` on every status by design —
normal, not a defect. Probe the letter's meaning against the reference before
calling a status line a bug (measured 2026-11-08: an `R` was misread as a
rename "ghost" and the correction needed a follow-up PR).

### Merge gates

Gate selection is computed from the diff (`git diff --name-only`), never
memorized by task class — a class table looked up by hand is a rule an agent
can misremember; a diff check can only be fed the wrong paths, and that
failure is itself catchable.

- **Diff touches only docs** (markdown, comments, non-executable metadata):
  `skillet validate .` exits 0 and the doc-link/doc-integrity tests are
  green. Nothing else required — seconds, not the full suite.
- **Any other self-mergeable diff**: all of the following hold —
  - the full suite is green
  - `skillet validate .` exits 0 with no errors
  - the new or changed test has been seen to fail, with the mutation
    recorded in the commit message
  - nothing under § Cross-session hazards was touched without a claim
- **Diff touches any policy path, egress path, or deployed-tree file**:
  always PR, always human review — no self-merge gate applies, regardless
  of streak or rung.

This keeps two things separate that a single gate list conflated: the trust
ladder (above) answers *who may self-merge this class of change at all*; the
gate list here answers *what must pass*, and that answer is a function of
what changed, not who changed it or which class it was filed under.

A full-suite pass only proves this change didn't break anything — it says
nothing about whether the trunk was already broken. That is a separate,
periodic job (nightly or on a cadence), not a per-merge one; the follow-on
lives in the backlog queue.

Anything else: push the branch, open a PR, and report. Stakes and size decide,
not preference. A new feature goes to PR; so does any change that takes more
than a paragraph to explain.

**A permission-blocked push resolves by handoff, not workaround.** Force-pushes
(`--force-with-lease`, `--force`, `-f`) are denied at the shell layer for agents
by policy — root-adjacent history rewrites are author-tier, the same class as
`chezmoi apply`. Do not retype variants at the deny until one slips through:
a bare `git push` after a rebase fails non-fast-forward and teaches nothing.
Hand the author the exact command instead, and bind the drift check into the
command itself:

- `git ls-remote origin <branch>` first — the handoff was written against a
  remote tip that can move before it runs.
- hand off the **explicit-expectation form**, never bare `--force-with-lease`:
  `git push --force-with-lease=<branch>:<sha-from-ls-remote> origin <branch>`.
  Bare `--force-with-lease` validates against the local remote-tracking ref,
  which a background fetch can move between the check and the push — the lease
  then accepts the moved tip and the expected `<old>...<new>` output confirms
  the overwrite instead of catching it (review job 588). The explicit form
  makes the observed SHA the lease, so any push after the check rejects.
- if the push rejects, the remote moved: re-verify with `ls-remote`, never
  re-run with the old SHA or drop the expectation.
- after it lands, verify from the assistant side with `git ls-remote`, never by
  re-pushing.

The same shape covers `git push origin --delete <branch>` and any other
author-tier remote write: verify what the remote holds, hand the one command
binding what you verified, read back what it printed. Measured 2026-11-08:
three push attempts (compound denied, lease denied, bare non-fast-forward)
preceded the handoff that worked on the first try.

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

A session arriving from PR feedback — a review comment, a review request —
does not start from main. Its entry path is `docs/WORKTREES.md`
§ Arriving from a PR: fetch, worktree the PR branch, claim, push.

### Review starts with the tests

Read the tests first. They should read cleanly enough to serve as the spec, and
they are where an agent's work is most likely to be wrong in a way the code
hides — an agent will happily write code and then write tests that ratify
whatever it just wrote. That is what § Prove the test fails exists to catch.

**Verify-then-claim for tool facts.** A reviewer (human or agent) who states
what a tool does — "read-only", "fails closed", "not supported on this host" —
cites the probe that produced the claim: the `--help` read, the versioned
source, the measured run. Bare adjectives are not findings; they are guesses
with confidence. A reviewer citing a probe that a fix then contradicts
(`sudoers --check` read as "read-only" from `--help`, while the binary probes
sudo) has verified the wrong thing, and the fix that cites *its* probe wins.
Settle contradicting reviews by reading the cited source, not by counting
reviews.

### Quiz before merge

When a PR is opened, or when a change is too large to explain in a paragraph,
the agent quizzes the author on what the change contributes before it merges.
The point is not to test the agent's work; it is to check that the author
actually understands what was built. A change that passes review while nobody
internalised the design is a change nobody can maintain.

A quiz carries **no recommended answer**. Marking one option "(Recommended)"
hands over the agent's own reading and turns the check into a rubber stamp —
the one thing it exists to prevent. Options stay neutral; the agent's reasoning
belongs in the report it already wrote.

## Trust ladder

Autonomy is earned per task class and blast radius, never globally. The rungs,
promotion counts, incident classes and ageing rules are in
`docs/TRUST-LADDER.md` — read it when an item is being promoted, demoted, or
graded, not while writing code.

Two rules bind regardless, and live here:

- **This file's § Merge gates decide what must pass.** The ladder decides who
  may self-merge that class of change at all. Keep the two questions separate.
- **Asking is never an incident.** A question whose answer already existed costs
  nothing; making questions expensive teaches silence.

## Commands

The hook runner is **prek** (`prek.toml` at the repo root; `.pre-commit-config.yaml`
was retired with it). When you need a hook's config, flags, or file selection, read
`prek.toml` — not a remembered `.pre-commit-config.yaml`, which no longer exists
and will silently misreport the suite. A stale assertion about hooks is how
"the ruff hook checks X" gets reported as fact from a file that is gone.

### Three commands that fail in a way that looks like a broken repo

Each was measured on 2026-11-09 and each cost a session real time. The failure
is never the thing you assume; check these before diagnosing further.

**`gh pr create` with a slashed branch name.** `--head agent/template-research`
fails with *"No commits between main and agent/template-research"* even when the
branch is fine and `gh api .../compare` reports `ahead_by: 2`. Name the owner:
`--head <owner>:<branch>`. The error describes a repository problem that does
not exist.

**`gh` without `--repo` resolves by remote, not by cwd.** In a tree holding more
than one clone of a similarly-named repo, `gh pr view 1` can read a *different*
repository and report a PR you never created. Pass `--repo <owner>/<name>` on
every `gh` command here; treat any surprising owner name in the output as this
bug rather than as your own mistake.

**`git diff <branch>` is not a claim about what your branch does.** Two-dot
`git diff main` renders main's later additions as deletions, so a branch that
deletes nothing appears to delete everything added since the merge-base. Use
`git diff main...HEAD` for "what my change is" and `git merge-base HEAD main`
before asserting that a merge would remove something. Measured the same day: a
false "this merge deletes six files" alarm, from the two-dot form, on a branch
that deleted nothing.

```bash
# Fast loop — the default for iteration. Tests spread across CPUs. Measured on
# this machine 2026-09-23 (32 cores, 641 passed / 2 pre-existing failures):
# 170s -> 47s. Run one suite at a time. Two at once contend on the uv cache lock
# and Hypothesis starts reporting deadline failures that are CPU starvation, not
# bugs — which is corrupted evidence, worse than a slow run.
uv run --frozen --with pytest-xdist pytest tests tools -q -n auto --dist worksteal

# Merge gate — the full suite, unsplit, because a merge gate compares the whole
# failure list. Dependencies are locked in uv.lock; --frozen rebuilds the
# environment offline from the cache. Model-calling tests are excluded by
# default (`[tool.pytest]` `addopts` in pyproject.toml); -m llm_judge overrides
# that filter.
uv run --frozen pytest tests tools -q

uv run --frozen --group test-llm pytest tests tools -m llm_judge -q   # only real-model tests

bats tests/<name>.bats         # bash scripts only — see Languages below
bash home/dotfiles/executable_run-role.sh <topic>          # apply one ansible topic
bash home/dotfiles/executable_run-role.sh <topic> remove   # tear it down
```

A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while testing
almost nothing — the `binned_module` fixture skips without `typer`/`questionary`.

### Known failures

**This table is stale post-DOT-73 (PR #114): both suites below now pass.**
The table and `scripts/check_suite_baseline.py` `EXPECTED_FAILURES` move
together — DOT-314 owns that update as part of `agent/retro-ci-guard`'s rebase.
Until then, read the table as the pre-#114 baseline, not current behaviour.

Two suites failed on a clean checkout before DOT-73, for reasons outside the
code. Expect this shape in older baselines, and do not spend a session proving
they are not yours:

| Suite | Count | Why |
|---|---|---|
| `tests/clipped` | ~10 | Drives the real clipboard through subprocesses; needs a live `wl-copy`/`wl-paste` and a TTY. |
| `tests/restart_stale` | 2 | Exercises launchd/systemd role behaviour that the test host does not have. |

A full run on the reference host read **12 failed, 1093 passed, 20 skipped**
pre-#114; measured 2026-11-08 post-#114, the same host reads **zero failed**
from these suites (1426 passed, 20 skipped) once the `.molecule` scratch trap
(DOT-310) is cleared. Tracked in DOT-73 (Done) and DOT-314 (baseline refresh).

Two ways to keep this cheap, in order of preference:

```bash
# Preferred: run the suites that can actually pass, in parallel.
uv run --frozen --with pytest-xdist pytest tests tools -q -n auto --dist worksteal \
  --ignore=tests/clipped --ignore=tests/restart_stale
```

`--ignore` is a deliberate choice for a fast loop and a bad habit for a merge
gate: it would hide a real regression in those two directories. For a merge
gate, run the full suite and judge the failure list — **until DOT-314 refreshes
the baseline, an empty failure list is green** (both tabled suites now pass),
any FAILED or ERROR node outside the table is a regression, and
expected-but-absent table entries are nonfatal (the baseline script's own
ruling — a baseline that is too generous is a lesser fault than a gate nobody
can run). A change is green when the failure LIST matches, not when the count
does.

**CI applies that rule mechanically.** `.github/workflows/tests.yml` runs the
full suite on every pull request and every push to `main`, then feeds the
captured log to `scripts/check_suite_baseline.py`. That script compares the
failure node IDs against the table above and fails on anything outside it, so a
count that stays at 12 while one suite is fixed and another regresses is caught.
It also refuses to pass when the log holds no pytest summary — a run that died
before reporting has an unknown result, not a green one.

The baseline is a list of exact node IDs, never of directories. An earlier
version matched `tests/clipped/` as a prefix, so a brand-new regression beside a
known clipboard failure passed silently — the same silent-pass shape the script
exists to prevent. `ERROR` outcomes are parsed too: a collection or fixture error
does not appear in the summary's failed count, so a run reporting "1 passed, 1
error" was green under a failures-only check.

The workflow lints only the files a change touches. A whole-tree `ruff check`
reports pre-existing debt the hooks never see, and a gate that is red on arrival
teaches everyone to ignore it.

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
uv run --frozen --group test-llm pytest tests/policy -q
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

**Creating a task is itself a commit.** Every task you create lands as its own
commit of its task file, immediately, separate from whatever work is in flight —
two tasks are two commits, and revising a task is a further commit rather than a
rewrite of the one that added it. The point is that a task survives the session
that thought of it: a task still sitting uncommitted when context runs out is a
task nobody ever had. Under the carve-out, queue commits go straight to main;
anything bigger than a task goes on a branch as before.

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
other programs does not qualify however long it is — `home/bin/findline` is 256 code
lines that pipe `rg` into `fzf` with a `bat` preview, so all the behaviour and all
the speed live in three Rust binaries. Porting it would add interpreter startup to
an interactive tool and make it worse. Its header records this so the question is
not reopened. Contrast `home/bin/clipped`: similar size, but genuinely branchy platform
dispatch, and worth porting.

Stdlib-only Python needs no dependency block — use `#!/usr/bin/env python3` like
`home/bin/mailbox`. Reach for `#!/usr/bin/env -S uv run --script` with inline PEP 723
deps only when third-party packages are genuinely needed, as `home/bin/llm-ctx` does.

`home/bin/binned` applies this rule to the scripts it generates: it counts effective
lines, recommends Python above 100, and asks a model in the 80–100 band.

### Conventions

Conventions live in **`docs/`**, one file per subject, so the repository root
holds only the documents that govern the project. `docs/README.md` is the index
and carries what each file covers; this list exists because
`tests/docs/test_conventions_referenced.py` requires every convention reachable
from here, and an agent that never reads a convention has a file, not a rule.

Read by name when the work touches them:

- **`docs/PROCESS.md`** — how work runs. Read before your first task.
- **`docs/PYTHON.md`** — uv, PEP 723, pytest, ruff, ty, logging.
- **`docs/PERMISSIONS.md`** — what you may run. Read before widening a rule.
- **`docs/REFERENCES.md`** — standards followed and their versions. Add a row
  before adopting one.
- **`docs/LAYOUT.md`** — the `~/code` taxonomy. Cite it, do not paste absolute
  paths into queue prose.
- **`docs/LANGUAGES.md`** — language inventory and per-language tool profile.
- **`docs/GLOSSARY.md`** — project terminology, linked on first use.
- **`docs/LINK-CHECKING.md`** — the Lychee cadence and its security boundary.
- **`docs/WORKTREES.md`** — the worktree naming contract and lifecycle.
- **`docs/BRANCH-SYNC.md`** — how a branch stays mergeable: the pre-push
  check, and why a declared hook stage without a shim never runs.
- **`docs/TOPICS.md`** — topic structure, lifecycle, dependency and ownership.
- **`docs/TRUST-LADDER.md`** — rungs, incident classes, promotion and ageing.
- **`docs/TESTING.md`** — mutation proving, properties and fuzzing.
- **`docs/CROSS-PLATFORM.md`** — traps that have bitten on macOS and Debian.
- **`docs/BACKLOG-MIGRATION.md`** — the queue's migration record.
- **`docs/BACKLOG-UPSTREAM-CONFIG.md`** — upstream backlog configuration.

## Tests

See `spec.md` § Verification for the properties a suite must have — chiefly that
a mechanism which can decline is proven to RELENT, and that a test is not
finished until it has been seen to fail against a deliberately broken copy. Both
were bought by suites here that passed while testing nothing.

**pytest is primary.** Any Python script gets pytest tests. bats remains correct
only for scripts that are still bash (`home/bin/cleanup`).

When porting a script, keep its bats suite until the pytest suite is proven
equivalent — it tests the CLI as a black box, so it survives a language change
unaltered and is the safety net that proves the port. Then retire it.

Layout: `tests/<script>/conftest.py` plus `test_*.py` split by concern. Mark tests
that call real models with `llm_judge` so they stay out of the default run.

A port is a chance to test what bash could not. `default_output()` in
`home/bin/pii-redactor` was previously only reachable by running the whole CLI and seeing
which file appeared; called directly, the path edge cases became explicit. Platform
dispatch in `home/bin/clipped` could only be exercised by mocking `uname` on `PATH`, so
in practice only the host platform was ever tested.

### Prove the test fails

A test is not finished until it has been seen to fail against a deliberately
broken copy — `spec.md` § Verification makes this a SHALL. Record the evidence
as commit trailers, `Mutation:` and `Failing-test:`; only trailers are
greppable.

`docs/TESTING.md` has the working detail: which mutations have actually bitten
here, how to read WHICH tests failed, the harness traps, and when a property or
fuzz test earns its place. Read it when writing or repairing a test.

## Writing

Technical docs in this repo use plain language: short sentences, active voice,
common words, the conclusion first, one idea per paragraph. Write for someone
deciding what to do. This covers this file, `docs/`, READMEs, changelog
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
legitimate as **benchmark subjects** — that is what `home/bin/model-bench` is for. The
line is hosted-vendor dependency, not the name: `gpt-oss:20b` is open-weights and
runs locally under Ollama, so it is welcome; `gpt-4o` is not.

Model ids must be the exact `ollama list` tag. What is pulled here are MLX and QAT
builds, so `qwen3.5:35b` does not exist but `qwen3.5:35b-mlx` does. Never match ids
by substring: `home/bin/binned` used to, so a bare `qwen3.5:35b` matched the installed
`-mlx` tag, passed the availability check, then failed at `llm -m` from inside a
judge panel.

**Do not invent ratings or benchmark numbers.** Quality claims must come from a
measured run. `home/bin/model-bench` scores judges on *calibration* against a reference
scorecard rather than on the scores they emit, because measuring raw magnitude
rewarded generosity — two local models awarded a flat 10/10 to a script with no
comments and an unguarded `--delete`, and outranked the model that caught it.

## Dependencies

Check every dependency a script shells out to, system tools and hand-rolled
`~/bin` scripts alike. Being topic-managed is not a reason to skip the check: it
only means something *should* have installed it, which is exactly the assumption
that breaks on a fresh or half-applied box. See `require()` in `home/bin/llm-ctx`.

Name the fix in the error, not just the failure: `~/bin` scripts come from
`chezmoi apply ~/bin`, system tools from the Ansible topics via `update.sh`.

Adding a tool to `apps/mise/files/config.toml`: use the `github:` backend for
GitHub release binaries, never `ubi:` — mise deprecates it (removal in
2027.1.0). The convention comment at the top of `[tools]` is the enforcement
point; existing `ubi:` entries migrate to `github:` when touched.

## Cross-platform

macOS and Debian/Ubuntu are both targets. Guard the package manager in-task
rather than abstracting it — `CONTRIBUTING.md` rule 2 has the pattern. A topic
supporting both should not declare `homebrew` in `topic_requires`, or it becomes
unschedulable on Linux; see `apps/ollama/topic.yml`.

Assume tools installed by uv or mise are identical across platforms. Only system
binaries need per-OS handling.

`docs/CROSS-PLATFORM.md` lists the traps that have actually bitten here — launchd
versus systemd user timers, `nc -U` providers, BSD and GNU flag differences.
Read it before writing a task that differs by OS.

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

## Agent skills

### Issue tracker

`backlog/` via `backlog-py` / `backlog-py-mcp`. The 2026-10-27 cutover is a
breaking change for any branch carrying `TASKS.md` — the conversion procedure
and per-branch disposition live in `docs/BACKLOG-CUTOVER.md`; the decision
record is `docs/BACKLOG-MIGRATION.md`. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, label strings unchanged. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context: `docs/GLOSSARY.md`; ADRs in `backlog/decisions/` via
`backlog-py decision create`. See `docs/agents/domain.md`.
