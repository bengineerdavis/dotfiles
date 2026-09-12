# Agent artifacts: what installs them, and what they are

Decided 2026-09-12. The author approved the shape in session; the survey behind
it is recorded below so the decision can be revisited when a rejected option
improves.

**The decision, first.** Skills follow the
[Agent Skills specification](https://agentskills.io) — that format is the
stable core. [dotagents](https://github.com/getsentry/dotagents) is the tool
that installs and wires them, chosen because it is the only surveyed candidate
that pins refs and keeps a lockfile. skills.sh is a discovery channel, never
the installer. The manager is deliberately swappable: skills are plain
directories, and nothing outside `agents.toml` and `agents.lock` belongs to
dotagents.

## The requirement

Install versioned agent artifacts — skills in v1; agents, prompts, eval cases
later — from canonical git sources into a shared convention, across every agent
runtime on the machine, with pinned refs, a committed lockfile, and
update-after-install, from a manager we can replace without touching the
artifacts.

A candidate that cannot pin and lock, or that installs per-tool copies instead
of wiring one canonical store, is disqualified.

## The layers

| Layer | What | What we use |
|---|---|---|
| Format | what a skill is | [Agent Skills spec](https://agentskills.io) (open standard, Anthropic-originated) |
| Authoring + verification | how skills are written and proven | [skillet](https://github.com/getsentry/skillet) — spec.md → SKILL.md → evals with `--baseline` lift |
| Distribution | how skills arrive and update | [dotagents](https://github.com/getsentry/dotagents) — `agents.toml` declares, `agents.lock` locks, `~/.agents/skills/` is the canonical store, per-agent dirs get symlinks |
| Provisioning | what installs the installer and triggers sync | Ansible topics (install and trigger, never hold logic or state) |
| Config | per-tool settings | chezmoi, unchanged |

This is the same stack Sentry runs, which the author named as the reference:
author with skillet, distribute with dotagents, format per the open spec. The
stack is coherent by design — `skillet init` itself installs its authoring
skill through dotagents.

## What was searched, and when

All verified 2026-09-12 against the artifacts, not from recall:

- **agentskills.io specification** — SKILL.md format: frontmatter fields,
  progressive disclosure, `skills-ref` validator. Covers format only;
  distribution is the open gap this decision fills.
- **dotagents** — README and the locally installed 3.1.0: `add <source>@<ref>`
  pins in the manifest, `agents.lock` written on install, skills symlink from
  `.agents/skills/` into per-agent dirs ("no copy-pasting between
  directories"), trust policy, `doctor --fix`, project scope with a committed
  `agents.toml` for team use. `@sentry/dotagents-lib` exposes the core
  (SKILL.md loading, source resolution, trust validation) as a library —
  the documented exit path.
- **skills.sh / vercel-labs/skills CLI** (31.5k stars, 75+ agents) — discovery,
  packs, audits, symlink-canonical install; but `skills update` means "to
  latest versions" with no pin and no lock. Telemetry on by default
  (`DISABLE_TELEMETRY=1` — see the note in REFERENCES.md).
- **AGENTS.md** — stewarded by the Agentic AI Foundation under the Linux
  Foundation; the cross-tool instruction standard, already canonical here.
- **MCP** and **ACP** — runtime and editor-interop protocols, adjacent to
  artifact management; tracked, not adopted in v1.

## Rejected, with reasons

| Candidate | Why rejected |
|---|---|
| skills.sh CLI as the installer | Cannot pin or lock; `update` floats to latest across every agent at once — the exact blast radius the chrome tag-force-move incident bought this repo's pinning rule for. Used for discovery only: find a skill there, install its git source through dotagents with a pinned ref. |
| opencode native `skills.paths`/`urls` | Per-tool config; cross-tool coverage means duplicating config into every tool — the drift this repo exists to prevent. |
| ~/.agents/skills as "the universal convention" | Partly false: it is the global path for only some agents (cursor uses `~/.cursor/skills`, codex `~/.codex/skills`). The durable convention is the Agent Skills *format* plus per-agent skills dirs with one canonical store symlinked outward — which is what both surveyed managers build. |
| Hand-rolled manager | The review-best-practices default: a well-tested incumbent exists and was measured against the requirement; building would add maintenance for nothing dotagents lacks. |
| Homebrew/Nix/copier | Wrong layer: system packages and templates, not per-agent skill wiring. |

## The exit path

If dotagents dies or drifts from our needs: skills are plain directories in
`~/.agents/skills/` — any tool, symlink, or short script can serve them. The
only dotagents-specific state is `agents.toml` (declarative, reproducible from
our topic manifest) and `agents.lock` (regenerable by `install`). For a
replacement built on the same sources, `@sentry/dotagents-lib` already
packages source resolution and trust validation as a reusable library.

The swap cost is therefore one manifest rewrite and one resync — bounded, and
recorded here so the bound is a claim we can test rather than a hope.

## Scope and open items

- **v1 is skills only.** MCP, hooks, subagents, and plugins stay out until a
  decision asks for them; dotagents supports all four when that day comes.
- **Open verification (author-run, gated by the deployed permission
  baseline):** `cat ~/.agents/agents.lock` — whether the lock records resolved
  SHAs or refs decides how strong the rollback-determinism claim above is.
- **Eval gate:** a skill version enters the manifest only after its skillet
  evals run green. The library skills' evals have never been executed — see
  the queued eval item in `TASKS.md`; until it runs, the gate is policy, not
  practice.
- **Aider collision carried over:** aider reads a root `TOPICS.md`; this repo
  has `dotfiles/docs/TOPICS.md`. Rename or namespace before any aider adapter
  exists. Aider is not installed on this machine.
