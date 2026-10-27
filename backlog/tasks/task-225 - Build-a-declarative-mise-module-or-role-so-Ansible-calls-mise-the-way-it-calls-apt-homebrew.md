---
id: TASK-225
title: Build a declarative mise module or role so Ansible calls mise the way it calls
  apt/homebrew
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Build a declarative mise module or role so Ansible calls mise the way it
  calls apt/homebrew.** Every mise-managed tool — gita, codex, roborev,
  skillet, and every future pipx: entry — currently shells out to
  `mise use -g` / `mise unuse --global` / `mise upgrade` in its topic, with
  probe-first greps to stay idempotent. A module or role turns those into
  declarative tasks (present/absent, reported change, check-mode aware) like
  `community.general.homebrew`. The gita topic's install/remove are the first
  consumer and the migration pattern. Done when that topic runs through the
  module and its mise shell-outs are gone. Gated on the backlog-md-py
  queue migration (§ Now).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
