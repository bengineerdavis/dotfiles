---
id: DOT-256
title: Make throwaway agent-session tests fail closed and leave no persistent state
status: To Do
created_date: 2026-10-28 17:10
labels:
- testing
- agents
- design
priority: high
updated_date: 2026-10-28 17:43
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generalize the lessons from the Lore/OpenCode E2E work for agent-related topics. A throwaway test must isolate process identity, project discovery, config, credentials, and persistent state, and prove cleanup through public interfaces.

Required design rules from measured failures on 2026-10-28:

- Set both subprocess cwd and PWD to the throwaway project. On this machine OpenCode used the inherited PWD despite subprocess cwd, loading the parent repo config and attributing the model call to it.
- Isolate XDG config/data/cache/state locations for the child agent. Do not let a test inherit a parent agent's OPENCODE session variables.
- Treat test credentials and network access as explicit capabilities; keep real-model tests marked llm_judge.
- Never invoke a destructive cleanup command with an inferred or empty project scope. Resolve a unique project ID from the public CLI, verify the target is the test-created resource, and delete that exact ID. Fail closed if any required lookup fails.
- Do not confuse `lore data clear` with project deletion. `clear` empties records but retains the project; `data delete project <id> --yes` removes it. A missing --project argument invoked current-project behavior and caused an accidental main-project data loss in this session.
- Cleanup must run on test failure too. A failed cleanup is a failed test, never a warning-only pass.
- Verify the public postconditions: the temporary project and its records are gone, and pre-existing project IDs are unchanged. Do not delete an existing real project to make the assertion pass.
- Capture enough diagnostics on failure to distinguish an agent-process, gateway, recording, attribution, and cleanup failure.

Decide where process-level isolation is enough and when a Molecule/VM is warranted for service, reboot, privilege, filesystem, or cross-OS behavior. Prefer a shared test interface only after a second agent topic needs it; avoid a one-caller abstraction. This task is for review and implementation in the appropriate test/template home, not a license to add a bespoke tool to dotfiles.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A reusable throwaway-session pattern defines isolated cwd/PWD, XDG paths, parent-session variables, and real-model opt-in behavior.
- [ ] #2 Destructive cleanup fails closed before execution unless it has a unique test-created resource ID and explicit scope; no empty or inferred project scope is allowed.
- [ ] #3 Cleanup is proven on success and injected-failure runs, and leaves no test project, records, or agent artifacts behind.
- [ ] #4 Pre-existing persistent state is compared before and after; tests do not delete real data to manufacture a passing assertion.
- [ ] #5 The design distinguishes process isolation from VM-required scenarios and links the Molecule matrix work (DOT-255).
- [ ] #6 The Lore/OpenCode E2E test exercises the real agent/gateway path through public interfaces and remains excluded from the default suite.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-28 measured refinement: prefer an isolated Lore gateway and LORE_DB_PATH under the throwaway directory over destructive cleanup in the live database. tests/loreai/test_opencode_e2e.py now starts a test-owned gateway on a free port, strips inherited OPENCODE*/LORE_* state, matches PWD to cwd, isolates XDG paths, disables curation and project-file exports, and stops its own process group. It asserts the exact OK model response, polls the isolated CLI for a completed session, and verifies the temp project never appears in the live project list. It does not call data clear or data delete. Real-run evidence: green after PWD and upstream fixes; removing the PWD assignment failed as intended. This covers the first Lore adapter and part of the process-isolation design; it does not complete cross-agent reuse, injected-cleanup-failure coverage, or the VM matrix. During review, a missing --project argument accidentally cleared the main Lore project. A pre-import database and public-data backup was written under the opencode temp directory; a supported `lore import --project /Users/ben.davis/.local/share/chezmoi` recovery is running. Do not claim exact restoration until it completes and the recovered data is compared. This task should make isolated state the default and reserve destructive commands for explicitly identified test-owned resources.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
