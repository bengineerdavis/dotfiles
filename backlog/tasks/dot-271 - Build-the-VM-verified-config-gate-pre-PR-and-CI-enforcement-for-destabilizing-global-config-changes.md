---
id: DOT-271
title: 'Build the VM-verified config gate: pre-PR and CI enforcement for destabilizing
  global-config changes'
status: To Do
created_date: 2026-10-29 21:46
references:
- backlog/decisions/decision-1 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-1: any change to global config that can destabilize user-level usage is verified by integration/E2E/agent-user-tested checks in a VM matching the target machine environment. Gate 1 of 3: a pre-commit/pre-push hook and CI job that run the VM verification for diffs touching managed global-config sources (opencode, mise, shell). The gate must be mechanically derived from the diff, not from a remembered task-class table. Work includes: choosing the VM harness (the Lima adapter from PR #99 is the candidate), defining which file paths trigger the gate, and wiring prek hooks plus CI. Done when: a diff that touches a managed global-config source cannot reach a PR without the VM check having run and passed, proven by a mutation (a deliberately broken config that the gate rejects).

The VM scenario must cover the eventual two-stage deployment path: run `chezmoi apply` into the VM's target home, then run the parent `dotfiles` Ansible playbook through the same entry point and tags used by `update.sh`. Prove the deployed configuration and Ansible-converged machine state work together; do not substitute a render-only check or an Ansible-only upgrade for this path. Current `update.sh` is Ansible-upgrade-only and does not run `chezmoi apply`, so the test must distinguish that current behavior from the eventual combined pipeline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A diff touching managed global-config sources triggers the VM gate automatically, derived from the diff itself
- [ ] #2 The gate runs pre-PR (hook) and in CI on the PR
- [ ] #3 A deliberately broken config change is rejected by the gate, with the mutation recorded
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
