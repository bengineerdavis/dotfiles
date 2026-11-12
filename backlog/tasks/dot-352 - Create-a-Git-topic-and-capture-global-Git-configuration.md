---
id: DOT-352
title: Create a Git topic and capture global Git configuration
status: To Do
created_date: 2026-11-12 02:54
assignee:
- OpenCode
labels:
- git
- configuration
priority: medium
orchestration:
  status_key: inprogress
  lease_owner: OpenCode git-topic session
  lease_expires_at: '2026-11-12T04:10:44.271165Z'
  version: 1
updated_date: 2026-11-12 03:11
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Git's global configuration is chezmoi-managed, but no Git topic exists and its referenced commit-message template is missing.

Ship:

- Decide undue Git package handover before adding an app-tier Git topic on Darwin and Debian.
- Keep global Git settings, global excludes, and a commented commit-message template in chezmoi, with identity resolved from the existing name and email prompts.
- Update DOT-134 so its remaining git-ai and shell-integration scope does not claim Git configuration is unmanaged.
- Add tests for topic lifecycle wiring and the global commit-message template.

Constraints:

- chezmoi owns dotfiles; Ansible owns package presence.
- Do not add git-ai, change shell startup, or install telemetry.
- Do not apply the configuration to the live machine.
- Use the canonical topical scaffold and prove each new test fails against a deliberately broken copy.

Agreed with the maintainer 2026-11-10: keep this to Git configuration and package ownership, preserve portable identity, and provide commit-message guidance as comments only.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The Git package's existing owner is identified and either preserved deliberately or transferred in one reviewable decision.
- [ ] #2 The Git topic declares Darwin and Debian support and has a lifecycle wiring test.
- [ ] #3 chezmoi manages the existing global Git config, global excludes, and a commit-message template whose guidance is entirely commented.
- [ ] #4 The rendered Git identity uses the existing name and email prompts rather than a hard-coded machine-specific identity.
- [ ] #5 DOT-134 describes only the remaining git-ai and shell-integration work and no longer says Git configuration is unmanaged.
- [ ] #6 The topic and template tests pass, and each new test has been observed failing against a deliberately broken copy.
- [ ] #7 uv run --frozen pytest tests/chezmoi tests/topics -q passes with only documented pre-existing failures.
- [ ] #8 skillet validate . exits 0 with no errors.
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

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-72f203d3cd364e90b33f1551ed924c04
type: claim_task
actor: OpenCode git-topic session
timestamp: '2026-11-12T03:10:44.271261Z'
result: succeeded
task_id: DOT-352
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Implement the authorized Git topic and global configuration capture.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
