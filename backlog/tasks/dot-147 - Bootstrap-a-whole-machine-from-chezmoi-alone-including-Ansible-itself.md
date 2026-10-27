---
id: DOT-147
title: Bootstrap a whole machine from chezmoi alone, including Ansible itself
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Bootstrap a whole machine from chezmoi alone, including Ansible itself.**
  Later, deliberately. chezmoi ships as a self-contained static binary with no
  runtime, which makes it the one thing that can be present before anything else
  is — so `chezmoi init --apply <repo>` could pull the configuration *and* stand
  up the system dependencies it needs, rather than the current order where
  Ansible must already exist for the playbook to run. That removes the
  chicken-and-egg step in `bootstrap/` and shortens a new machine to one
  command. Worth checking before designing: chezmoi's `run_once_before_` scripts
  are the hook for this and already appear in the repo
  (`crontab/run_onchange_after_install-crontab.sh.tmpl`), so the mechanism is
  known rather than novel. The interesting question is what minimum must be
  bootstrapped — mise brings Ansible today, and mise itself has to arrive
  somehow.
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
