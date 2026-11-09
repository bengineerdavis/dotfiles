---
id: TASK-242
title: Wire provisioning answers into machines.yml (loreai pilot)
status: Done
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
- [x] #1 The loreai playbook loads dotfiles/machines.yml via a guarded lookup keyed on ansible_hostname: absent file = empty merge; malformed YAML fails loud naming the fix — both directions proven by test.
- [x] #2 Precedence proven layer-by-layer by test: -e > machine answer > shared answer > prompt > probe default; a registry entry at either tier suppresses prompts.
- [x] #3 Merge proven by test: machine override beats shared answer; pop-os effective answers equal the current env.zsh values (telemetry 1, inference openrouter, worker model openrouter/z-ai/glm-5.3-flash).
- [x] #4 machines.yml carries the generic provisioning schema: shared tier holds the three loreai answers; pop-os's key matches ansible_hostname; the Mac carries no committed key, since its hostname is a hardware serial.
- [x] #5 Re-run of the loreai topic on pop-os: no prompts, env.zsh re-rendered byte-identical (changed=0 on content).
- [x] #6 Docs updated: apps/loreai/README.md and templates/loreai-env.zsh.j2 header state the artifact contract and registry re-answer flow; docs/LAYOUT.md documents the provisioning schema; docs/GLOSSARY.md gains provisioning answers, shared answers, machine answers.
- [x] #7 Demote and promote semantics documented (README or LAYOUT.md) per decision-1: demote removes the shared default so future machines re-answer; promote propagates via the visible commit diff, conflicting overrides survive and are reported.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Done via PR #130 (`659d84c`), merged 2026-11-05. This task's front matter was
never flipped when that PR landed, so it sat at `To Do` while the work was on
main — the same status-field drift DOT-233 had.

Every acceptance criterion re-verified against current main on 2026-11-09, not
assumed from the PR's existence:

- **#1** `registry-answers.yaml:43-49` — stat guard for absence, `block/rescue`
  around `lookup`+`from_yaml` so a malformed file names the fix.
- **#2** `test_explicit_extra_vars_beat_the_registry`,
  `test_machine_answer_beats_shared`,
  `test_registry_answers_suppress_prompts_and_render`.
- **#3** `test_committed_registry_gives_pop_os_the_installed_answers`.
- **#4** `machines.yml:23-45` — `provisioning.shared` carries the three loreai
  answers, `machines.pop-os` is registered, no Mac key is committed.
- **#5** `test_registry_rerender_is_byte_identical`.
- **#6** `apps/loreai/README.md`, `docs/LAYOUT.md`, `docs/GLOSSARY.md`.
- **#7** the README's re-answer flow covers demote/promote.

Suite on main: **18 passed in 40.97s**
(`uv run --frozen pytest tests/topics/test_loreai_registry_answers.py -q`).

PR #119 was a stale duplicate of this work — 194 commits behind, conflicting in
five paths — and was closed rather than rebased, so it could not reintroduce an
older `machines.yml` over the current one.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Both machines' loreai answers live in machines.yml (pop-os inventoried), the loreai topic self-loads and merges the registry per decision-1, a re-run on pop-os re-renders ~/.config/loreai/env.zsh with no prompts and changed=0, docs are updated, and the PR is merged.
<!-- DOD:END -->
