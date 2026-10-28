---
id: decision-1
title: 'Provisioning answers: shared answers + machine answers in machines.yml'
date: 2026-10-28 00:03
status: accepted
---

## Context

Topics with first-install prompts record per-machine answers into untracked
machine-local files (loreai writes `~/.config/loreai/env.zsh`). The answers
are invisible across machines, drift-prone, and unreviewable; committing the
rendered files instead would paste one machine's literals into the fleet and
couple the topic to chezmoi. The `machines.yml` registry exists for
per-machine data (today: repo membership only) but nothing consumes it yet,
and this machine (`pop-os`) is not inventoried in it.

Settled by author interview 2026-10-27 (two grill rounds; every branch
answered). Pilot: the loreai topic.

## Decision

Provisioning answers become a committed, per-machine record in
`dotfiles/machines.yml`, in two tiers:

- `provisioning.shared.<topic>` — fleet-wide defaults, written once.
- `machines.<host>.provisioning.<topic>` — per-host exceptions.

Placement is the classification: where a value sits decides its scope. No
per-topic schema metadata declares variables shared or local.

Semantics:

- Effective answer per variable: machine answer > shared answer. Full
  precedence: `-e` (one-shot) > machine answer > shared answer > prompt >
  probe default. A registry entry at either tier suppresses prompts.
- The rendered env file (`env.zsh` and equivalents) is an artifact of the
  registry, not a source of truth: direct edits are overwritten by the next
  run; re-answering means editing the registry and re-running.
- Demote (shared → machine) removes the shared default, so future machines
  re-answer the variable instead of silently inheriting a choice that is no
  longer universal.
- Promote (machine → shared) makes machines without an explicit override
  inherit it; the propagation is visible as the commit diff. Machines with
  conflicting overrides keep theirs and the run reports the divergence.
  Reverting a machine to fleet behavior is deleting its override.
- The registry holds settled choices only (loreai: telemetry, inference,
  worker model). Probe-derived facts are re-probed every run and never
  recorded. Secrets and key-resolution chains stay template-owned.
- The topic playbook self-loads `machines.yml` (guarded lookup keyed on
  `ansible_hostname`; absent file = empty merge; malformed YAML fails loud
  with the fix named) and computes the merge, so resolution is identical
  under parent-driven fleet runs and `run-role.sh` standalone runs. One
  resolution path.
- Bootstrap: prompts remain for machines absent from the registry; promoting
  their answers into the registry is a deliberate author commit afterwards.

Alternatives rejected: topic-owned per-host vars files (scatter per-machine
data across topics; no single cross-machine view); rendering answers from
chezmoi data (recouples the topic to chezmoi and turns re-answering into a
repo edit on the wrong layer); tooling for promote/demote migrations (YAGNI
until the flow recurs).

## Consequences

- `machines.yml` grows a second concern (provisioning choices) under a
  generic section; `docs/LAYOUT.md` documents the schema.
- The rendered env file loses its "edit directly" status; the template
  header, topic README, and re-answer flow are updated to point at the
  registry.
- Future topics with first-install answers inherit the pattern without new
  schema — the section is generic by topic slug.
- The registry keys must match `ansible_hostname` on each machine; adding a
  machine to the registry is part of adopting its answers.
- The glossary gains "provisioning answers", "shared answers", and "machine
  answers" (docs/GLOSSARY.md, via the wiring PR).
