---
id: DOT-274
title: Consolidate opencode.json and opencode.jsonc to one config file, defaulting
  to opencode.jsonc
status: To Do
created_date: 2026-10-29 21:46
references:
- backlog/decisions/decision-3 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
orchestration:
  status_key: inprogress
  lease_owner: opencode-d274
  lease_expires_at: '2026-10-30T00:39:06.115431Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-3 item 3: competing config files are an antipattern even when the tool resolves precedence. The author settled the surviving format as **opencode.jsonc** on 2026-11-04; the earlier tentative .json preference is superseded. Keep exactly one chezmoi-managed source of truth, retire the unmanaged shadowed .json with a verbatim backup, and sweep the apps/loreai and apps/opencode topics so migrations never leave a second file behind. The gateway-unavailable route is separate DOT-242 scope.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Exactly one opencode config file remains on the machine, with the loser removed and its source cleaned up
- [ ] #2 The surviving format is justified against OpenCode V2 documentation/code, with the determination recorded
- [ ] #3 Tool-conflict findings (if any) are raised as upstream PRs from forked codebases
- [ ] #4 The apps/loreai and apps/opencode topics are updated so no migration leaves a duplicate config file
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-04: author ruled that JSONC is the surviving format. The chezmoi template remains the only managed global source. A chezmoi run_before_before_ script beside that template preserves the shadowed .json as opencode.json.pre-jsonc-backup before removing it, without requiring equal settings (the shadowed values were never active). It resolves the target from CHEZMOI_DEST_DIR, fails before deletion if .jsonc is missing or the backup already exists, verifies backup bytes, and never overwrites an existing backup. It is executed, not deployed; no helper lives under ~/.local. Ansible does not mutate the global config, so the CRUD teardown invariant stays with chezmoi. The LoreAI plugin task now checks registration before probing or installing the disabled V1 plugin. Direct tests cover absent, equivalent, different, missing-jsonc, existing-backup, readback-failure, and backup-race cases; a real isolated chezmoi apply proves script execution, backup preservation, no deployed script artifact, and idempotence. The backup-readback mutation was seen to fail its test. Measured 2026-11-04 in disposable Debian 12 Lima guest l325: direct helper execution and real chezmoi apply both backed up differing shadowed settings verbatim, removed .json, deployed no script artifact, and reran idempotently (VM_CHEZMOI_CONFIG_MIGRATION_OK, VM_CHEZMOI_APPLY_OK; chezmoi 2.74.0 in the guest). Apply-time removal on the real home remains to be performed; DOT-242 still owns gateway fallback. No upstream conflict is known: LoreAI's setup command is deliberately not run by this topic, and its JSONC fragment remains parity-tested.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-be8e89a9b50b49ad9f74810a6c035f72
type: claim_task
actor: opencode-d274
timestamp: '2026-10-29T23:39:06.115503Z'
result: succeeded
task_id: DOT-274
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Starting config consolidation per author sequencing: rebase #89, then DOT-274/DOT-242
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
