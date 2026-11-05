---
id: TASK-242
title: Wire provisioning answers into machines.yml (loreai pilot)
status: To Do
created_date: 2026-10-28 00:04
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Topics with first-install prompts record per-machine answers into untracked machine-local files (loreai: ~/.config/loreai/env.zsh) — invisible across machines, drift-prone, unreviewable. Decision decision-1 (backlog/decisions/) settles the design: provisioning answers live in dotfiles/machines.yml as shared answers (provisioning.shared.<topic>, fleet defaults written once) plus machine answers (machines.<host>.provisioning.<topic>, per-host exceptions); placement in the registry is the classification; the topic self-loads and merges the registry; the rendered env file becomes an artifact of the registry (direct edits overwritten; re-answer = edit the registry, re-run). Full semantics and rejected alternatives are in decision-1 — this task does not restate them.

Pilot: loreai. Both machines' answers are settled (telemetry on, inference openrouter, worker model openrouter/z-ai/glm-5.3-flash). pop-os is not yet inventoried in machines.yml — adding it is part of this task.

Implementation lands as one branch (backlog-TASK-<id> per AGENTS.md) + PR: the diff touches docs/LAYOUT.md (standard doc) and the env-file contract, so human review applies; the new/changed test is seen to fail with the mutation recorded in the commit message per the merge gates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The loreai playbook loads dotfiles/machines.yml via a guarded lookup keyed on ansible_hostname: absent file = empty merge; malformed YAML fails loud naming the fix — both directions proven by test.
- [ ] #2 Precedence proven layer-by-layer by test: -e > machine answer > shared answer > prompt > probe default; a registry entry at either tier suppresses prompts.
- [ ] #3 Merge proven by test: machine override beats shared answer; pop-os effective answers equal the current env.zsh values (telemetry 1, inference openrouter, worker model openrouter/z-ai/glm-5.3-flash).
- [ ] #4 machines.yml carries the generic provisioning schema: the shared tier holds the three loreai answers, and `machines.pop-os` (empty = pure inherit) documents the machine registered. The Mac carries NO committed key: its hostname is a hardware serial and fails spec.md § Data's string test, so its machine tier lives in the unversioned local overlay. A guard test rejects serial-shaped keys.
- [ ] #5 Re-run of the loreai topic on pop-os: no prompts, env.zsh re-rendered byte-identical (changed=0 on content). Proven in-suite by two chained runs against a fake registry (the artifact is byte-identical and the render task is not skipped); the live pop-os re-run is author-run, since applying is main-only.
- [ ] #6 Docs updated: apps/loreai/README.md and templates/loreai-env.zsh.j2 header state the artifact contract and registry re-answer flow; docs/LAYOUT.md documents the provisioning schema; docs/GLOSSARY.md gains provisioning answers, shared answers, machine answers.
- [ ] #7 Demote and promote semantics documented (README or LAYOUT.md) per decision-1: demote removes the shared default so future machines re-answer; promote propagates via the visible commit diff, conflicting overrides survive and are reported.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Design changed during implementation, by author ruling after a grilling round
(2026-11-04): decision-1's "keys must match ansible_hostname" clause contradicted
docs/MULTI-MACHINE.md's neutrality ruling and the repo-manager audit's finding 2a
(the existing key is a hardware serial). The employer test now governs: hostname
keys are legal, serial keys are not. A machine whose hostname is a serial (the
Mac) carries no committed key and uses an unversioned local overlay
(~/.config/loreai/answers.yaml) for its machine tier; the loader merges it below
the committed machine tier and reports divergences loudly. The dead per-machine
`repos:` block was removed and its six Mac-only entries migrated into the single
shared catalogue config/repos.yaml, per dot-171's contract.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Both machines' loreai answers live in machines.yml (pop-os inventoried), the loreai topic self-loads and merges the registry per decision-1, a re-run on pop-os re-renders ~/.config/loreai/env.zsh with no prompts and changed=0, docs are updated, and the PR is merged.
<!-- DOD:END -->
