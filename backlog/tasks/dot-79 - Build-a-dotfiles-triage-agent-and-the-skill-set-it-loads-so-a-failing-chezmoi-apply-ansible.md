---
id: DOT-79
title: Build a `dotfiles-triage` agent and the skill set it loads, so a failing `chezmoi
  apply` / `ansible-
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Build a `dotfiles-triage` agent and the skill set it loads, so a failing
  `chezmoi apply` / `ansible-playbook` / `update.sh` run goes straight into
  troubleshooting instead of stopping at "non-zero return code".** The
  `apps/opencode` skill-sync failure on 2026-09-12 is the motivating case and the
  first eval fixture: Ansible reported a return code and nothing else, because
  the task read `.stdout` while dotagents writes errors to `.stderr` — finding
  the cause took reading the `@sentry/dotagents` source. The agent's first job is
  the cheap one: name which stream the message went to, which lifecycle tag and
  topic failed, and whether the deployed tree matches the chezmoi source. Then it
  works the known failure classes, one skill each, added as they are met —
  unmigratable state at a destination (`roles/guards/`), a missing dependency, a
  pinned ref that moved (`apps/chrome`), a source edited but never applied. Done
  when a deliberately broken topic run yields a named cause and a next action
  without a human opening task YAML. [me]
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
