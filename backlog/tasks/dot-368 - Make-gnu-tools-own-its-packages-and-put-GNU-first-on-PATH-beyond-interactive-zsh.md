---
id: DOT-368
title: Make gnu-tools own its packages and put GNU first on PATH beyond interactive
  zsh
status: To Do
created_date: 2026-11-17 16:50
dependencies:
- DOT-327
labels:
- feature
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
decision-6 makes the Homebrew GNU userland primary on macOS, matching Linux. The gnu-tools topic's install.yaml and remove.yaml are skeletons, and its path.zsh reaches only interactive zsh: measured 2026-11-17, login zsh, /bin/sh, launchd and Ansible still resolve /usr/bin/sed (BSD).

Ship:

- gnu-tools installs and removes coreutils, gnu-sed, gnu-tar, grep, findutils (and gawk, diffutils if confirmed in use) through community.general.homebrew
- GNU gnubin reaches the login and non-interactive PATH (zshenv or zprofile, chosen per DOT-327's PATH reasoning), and the playbook's environment PATH where tasks call these tools
- the topic README states decision-6 and the PATH reach
- tests: the topic's packages are declared, and a login zsh resolves GNU sed

Constraints:

- CRUD ownership (docs/TOPICS.md): the topic both installs and removes
- the Darwin-only topic must not make anything unschedulable on Linux
- launchd jobs keep explicit absolute paths and are not changed silently
- deployed-tree change: PR, human review
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 install.yaml and remove.yaml manage the named Homebrew packages
- [ ] #2 zsh -lc 'sed --version' reports GNU sed on the managed Mac after apply
- [ ] #3 The README cites decision-6 and states which contexts get GNU first
- [ ] #4 The new tests were seen to fail against a broken copy
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
