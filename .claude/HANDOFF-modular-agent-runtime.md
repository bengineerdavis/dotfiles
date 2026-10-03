# Handoff: interchangeable agent-work components

**Resume the research with a low-configuration container comparison.** Evaluate
Sandcastle's non-root containers alongside workmux's container workflow and a
native wrapper. The initial comparison and native macOS probes are complete.
Container setup effort is the next missing evidence.

This file is enough to locate the session and its evidence. The author requested
this handoff at a stopping point; no research agent remains running.

## Enter this worktree

**Moved 2026-09-28.** This handoff and its report used to be parked in
`.worktrees/wt-restart` on the dead branch `review/topic-restart-stale`. They
now live in this task's own worktree, branched from `main` at `61c50ff`.

| Item | Value |
|---|---|
| Repository | `bengineerdavis/dotfiles`, chezmoi source |
| Worktree | `~/.local/share/chezmoi/.worktrees/agent_components_containers` |
| Branch | `agent_components_containers`, from `main` |
| Report | `.claude/RESEARCH-modular-agent-runtime.md`, beside this file |
| Main checkout | `~/.local/share/chezmoi` |

For a human opening a session:

```sh
cd "$HOME/.local/share/chezmoi/.worktrees/agent_components_containers"
git branch --show-current      # agent_components_containers
git status --short --branch
opencode
```

For agent tools, set `workdir` to the worktree explicitly. Both `.claude/`
files are local and uncommitted. Pull requests from this branch go into
`main` only (`docs/WORKTREES.md` § Bucketing step 6).

## Preserve the local state

This worktree's only local state is the two `.claude/` files: this handoff
and the research report beside it. Both are untracked and uncommitted, and
`.chezmoiignore` excludes `.claude`, so they never deploy. A fresh clone will
not contain them. Keep the report beside this handoff.

Since the 2026-09-24 snapshot, the research results landed on `main` through
PR #9 (`TASKS.md` and `TASKS-RESOLVED.md`), and the pickup pointer through the
same PR. **This handoff and the report still hold the latest author
clarification and findings.** Where older text in the queue differs, reconcile
it against these two files first.

## Read these first

1. Current main `AGENTS.md`, `spec.md`, and `TASKS.md`; read this branch's
   instructions too. Shared governance has advanced beyond the feature branch.
2. Main `TASKS.md` item **Evaluate interchangeable components for agent work**.
   Its sandboxing and coordination sections hold related requirements.
3. Sibling [RESEARCH-modular-agent-runtime.md](RESEARCH-modular-agent-runtime.md).
   Read the recommendation, container clarification, probe limits, and next
   decisions. Appendices give local evidence paths and pinned upstream sources.
4. `/Users/ben.davis/code/work/sentry/support/docs/research/worktree-runtime-isolation.md`
   for the original problem and the earlier Worktrunk/mise trial.

Read applicable repo instructions before exploring any other local repository.
The shared queue lives in **main**, not this feature branch's older `TASKS.md`.

## What the author approved

The author first requested Sandcastle, Claude's sandbox runtime, and tools using
bubblewrap/Seatbelt. They approved assigning one research agent after reviewing
the plan, with this expansion:

> We need this to work with various tasking queue managers like backlog.md or
> workmux or also herdr(?) -- make this list inclusive of other options. What I
> want are components that can be added and removed, so the task management
> system can be interchangeable; so can the sandbox layer, so can gitworktrees
> if we really wanted to.

They also required local repository research alongside web sources. The latest
clarification changes the selection criteria:

> sandcastle's approach with non-root containers is fine as an option, as long
> as its very low configuration to apply it. but containized options are on the
> table so to speak.

Therefore:

- Treat non-root containers as primary candidates. Native execution is a
  workload capability, not a universal requirement.
- Make task storage, dispatch, workspace allocation, sandboxing and environment
  setup independently replaceable. Session/UI tooling is optional too.
- Worktrunk and mise are the baseline, not mandatory permanent dependencies.
- Assess configuration needed for the first project and each additional project.
  Include prerequisites, files, settings, commands, images, credentials and
  maintenance. No numeric threshold for “very low configuration” is settled.
- Research and disposable probes are approved. Selecting a live stack and
  implementing its integration remain separate decisions.

## What is already established

The assigned agent was `general/sandbox-components`; it completed its report.
Its tool session ID was `ses_f2add942bffeSh018ju5KBd9Sx`. The report is the
durable result; resumption does not depend on that session being accessible.

The agent inspected local dotfiles/herdr, ai-prompt-library, llocallabs,
impromptu, support, distill and selected utilities. The report distinguishes
implemented features from task lists and scaffolds. Do not rerun a broad survey
just to reconstruct these findings.

Key results:

- **Task sources:** Backlog.md, Beads, GitHub Issues, Taskwarrior and Markdown
  offer different ownership semantics. Backlog edits/assignees are not worker
  leases; Beads supplies stronger claim/lease mechanisms with a heavier store.
- **Roles:** herdr is session infrastructure. Workmux spans workspace/terminal
  management and has a headless provisioning interface. Neither is itself the
  durable task queue assumed by the initial shorthand.
- **Composition:** task brief and identity, workspace path, command/policy, and
  verified results are useful existing boundaries. A new adapter framework has
  not been justified.
- **Sandcastle:** `mattpocock/sandcastle`, package `@ai-hero/sandcastle`.
  The pinned source has container/cloud providers, not a shipped native
  Seatbelt/bubblewrap provider. With containers acceptable, a custom native
  provider is unnecessary for evaluating it. Check explicit `cwd`, branch
  strategy and lifecycle ownership; some modes merge or remove managed work.
- **Worktrunk/mise:** the existing `mise run worktree-new` fixes missing guard
  setup. Worktrunk can call those tasks. Creation-only `pre-start` skips an
  existing worktree, even one left by failed setup. Readiness needs rechecking.
- **Independent clones:** they can replace linked worktrees, but the current
  guard's `git-common-dir` lookup cannot discover another clone's inputs. That
  requires an explicit setup contract, not copying all ignored material.

### Measured evidence

The sandbox probes ran on **macOS 26.6.2 arm64**, with **SRT package 0.0.77**
and **mise 2026.9.12**. Exact pins and commands are in the report.

- SRT permitted workspace I/O and denied the tested sibling writes, synthetic
  secret reads and child writes. Its local network allow/deny cases worked.
- SRT returned **exit 0 after the child killed itself with SIGTERM**. A normal
  exit 7 was preserved. The coordinator reproduced this lifecycle defect.
- Mise already has optional native sandbox flags. Its filesystem and offline
  restrictions worked; `--allow-net 127.0.0.1` and `--allow-net localhost` both
  failed Seatbelt profile compilation. The coordinator reproduced those cases.
- SRT permitted a write in one allowed subtree while denying a write at the
  same workspace's root. This contradicts the old blanket absence claim in the
  queue; the correction was written there but was absent after main changed.
  It does not establish safe concurrent writers sharing an index/tree.

The tested SRT CLI misleadingly prints version `1.0.0`; the package manifest
and lockfile identify `0.0.77`. Keep upstream HEAD separate from that package.

Debian, container startup, queue contention, herdr restore, descendant-daemon
cleanup and complete queue/workspace swaps remain unrun. The sandbox swap was
only exercised for a narrow filesystem workload. These were benign functional
probes, not an escape audit. `tests/tasks_doc` last passed all 12 checks;
that verifies queue structure, not runtime behavior.

## Evidence on disk

Disposable clone:
`/Users/ben.davis/code/try/worktrunk-isolation-trial`

Sandbox probes:
`/Users/ben.davis/code/try/worktrunk-isolation-trial/sandbox-probes`

That directory retains `probe.py`, `edge-probe.py`, `mise-probe.py`, policy JSON,
the pinned npm runtime/lockfile, scratch home/cache, and synthetic fixture files.
Its `secrets/` directory contains synthetic probe data. It is not a credentials
directory. The clone's `accounts.toml` is also an invented fixture.

Run only a probe needed for an unresolved question, from its own directory:

```sh
python3 probe.py
python3 edge-probe.py
python3 mise-probe.py
```

These run commands and local endpoints, not agents or model calls. The existing
probe code sets scratch environment paths. Read it before extending it.

The harness denied the nominal temporary directory under `/var/folders/...`.
The author explicitly approved the clone under `~/code/try/` instead. Use that
approved scratch location; do not bypass a permission refusal. An earlier unused
clone also remains in the denied temporary location and is not needed to resume.

## Next research unit

**Compare the configuration burden of Sandcastle's non-root container path,
workmux's container workflow, and the native-wrapper baseline.**

Record this bounded unit and its owner in main `TASKS.md` before assigning an
agent. The previous one-agent research workflow was approved. Review materially
new scope or machine changes with the author rather than silently adding them.

1. Inspect available local container engines and pin candidate versions. Read
   upstream setup/source and relevant local provisioning before installation.
2. Walk through the documented fresh-project setup. Separate machine-level
   prerequisites from per-project configuration and per-run inputs. Record
   what the scaffold supplies and what still needs manual editing.
3. On an available backend, use synthetic data and a benign workload. Verify
   the process UID/GID, bind-mount ownership, workspace writes, exit/signal
   behavior, interruption, retained artifacts and cleanup ownership. Distinguish
   a non-root process in a container from a rootless container engine.
4. Check the replacement boundaries: an external queue supplies the brief, an
   external allocator supplies the directory, and sandbox shutdown does not
   independently close the task or integrate/delete the work. Mark each seam
   exercised, source-supported or unsupported.
5. Report first-project effort, repeat-project effort and ongoing maintenance.
   Recommend the smallest useful pilot, citing unresolved capabilities rather
   than inventing a setup-effort score.

If the backend is unavailable, report that and ask before changing shared host
services or installing system components. Do not launch real agent/model work
or read real customer data to prove the setup. Keep any new runtime logic out
of dotfiles; this repo provisions tools rather than owning bespoke frameworks.

### Decisions still open

- Human-serialized dispatch versus concurrent autonomous claims.
- Whether workers may commit, and which component owns integration.
- Required network and interprocess-communication restrictions.
- Resume/retention ownership and herdr wrapper/restore behavior.
- What measured setup burden the author considers “very low configuration.”

The author has approved the research direction, not a final task manager,
sandbox or workspace provider. Start with the focused setup comparison; retain
these choices where they affect the result.
