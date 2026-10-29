# GLOSSARY.md

Project terminology — the words that mean something specific *here*. This is
not a CS dictionary: a general term (idempotent, hermetic, TOCTOU) gets
glossed inline where it is first used and stays out of this file. The binding
rule is in `spec.md` § Writing: a doc using a term defined here links to the
definition on first use.

One heading per term so the anchor is stable. Definitions are one or two
sentences and point at the doc of record rather than restating it.

## agentic dependency

A skill referenced for its method by a spec, doc, or `AGENTS.md`. The
reference makes the skill a project dependency: declared, installed and kept
current by the machine's skill manager, and skill-trust-checked. Doc of
record: `spec.md` § Dependencies.

## capability manifest

The declaration every subtask carries in the multi-agent coordination layer:
paths, refs, commands, egress, secrets, limits, runtime. Enforced in three
layers — declare, sandbox, gate. Doc of record: `TASKS.md` § Now #1 sub-item
(k).

## claim

A line in `TASKS.md` § Claimed saying a session holds a hot file or a global
resource. Not a lock — a stale claim is checked against `git log` and running
processes before it is removed.

## consumer / provisioner

The two task classes for parallel agent work. Consumers run offline
(`UV_OFFLINE=1`, `--frozen`) and may run in parallel; provisioners touch the
network and are serialised. The path-intersection guard enforces the split.

## deployed tree / source tree

The deployed tree is what chezmoi manages on the machine — `~/bin`,
`~/dotfiles`, `~/.config`. The payload is the repository's `home/` directory,
which becomes the chezmoi source state. The wider checkout also contains
repository-only tooling, tests and docs that must never deploy.

They drift in both directions; `chezmoi status` is the check. A change
reaching the deployed tree cannot be undone by `git revert`. Doc of record:
`ROADMAP.md` § Move the deployed tree under `.chezmoiroot`.

## fan-out / wave

Fan-out is the orchestrator splitting a work item into parallel subtasks, each
in its own worktree. A wave is one round of that: the independent frontier
runs, merges serially, and the plan is re-derived before the next wave.

## frozen lease

A subtask's write envelope, expanded from `topic.yml` declarations and then
frozen to a literal path list plus metadata (commit hash, resolver version,
TTL). Enforcement reads the frozen artifact and never re-calls the resolver,
which closes the TOCTOU hole where a lease silently widens as others merge.

## handoff

The snapshot in `TASKS.md` § Where things stand: verified facts, settled
decisions, and the task list, written so a fresh session can resume without
the previous one's context. Deleted and rewritten, never appended.

## hot file

A file listed in `TASKS.md` § Cross-session hazards — recently touched by
more than one session. Editing one without a claim line is a Class C
incident.

## incident class

The severity taxonomy behind the trust ladder: Class A (disclosure or policy
bypass), Class B (corrupted evidence), Class C (process violation), Class D
(judgment). Defined in `AGENTS.md` § Incident classes.

## ledger

The durable record of agent trust: rungs per task class, promotion streaks,
incidents. Queued, not yet built — until it exists, a first-time agent starts
at rung 0 everywhere.

## merged-state suite

The test suite run on the tree *after* a merge, not on any branch. The only
check that catches semantic coupling between parallel work, and the reason
merges are serial with the suite after each.

## RECL

The working loop this repo runs on: Requirements, Execute, Check, Loop — a
REPL by analogy. The step that gets skipped is Requirements. Doc of record:
`AGENTS.md` § How work runs here.

## resolver

The Ansible role (`roles/topic-resolution`) that derives the topic dependency
maps — `provides_map_all`, `provides_map_run`, `requires_map` — from the
`topic_requires` / `topic_provides` declarations across the topic files.

## rung

A level on the trust ladder (0–4), held per task class, never globally. What
an agent may do unsupervised: propose, branch-and-PR, self-merge docs/tests,
self-merge code in a blast radius, work unattended. Doc of record: `AGENTS.md`
§ Trust ladder.

## skill-trust

The vetting a skill passes before this project depends on it — licence,
provenance, behaviour. Lives in `tools/skill-trust/`.

## topic

The unit of machine configuration: a directory under `dotfiles/` carrying a
`topic.yml`, Ansible tasks, and chezmoi-managed files, with one concern per
layer. Doc of record: `docs/TOPICS.md`.

## worktree

A git worktree under `.worktrees/`, one per agent session, giving that
session its own index — the structural fix for mixed commits on the shared
index. Naming and lifecycle: `docs/WORKTREES.md`.
