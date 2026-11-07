---
id: DOT-291
title: Declare worktrunk as the worktree manager topic
status: To Do
created_date: 2026-11-01 19:05
labels:
- dotfiles
- tooling
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install worktrunk (wt) via mise/cargo and wire its shell integration declaratively through the dotfiles. References: https://worktrunk.dev/#install — 'cargo install worktrunk && wt config shell install'. Author-authorized follow-up: reuse the pattern of capturing command output (like wt config shell install prints) so setup becomes declarative — the capture/templating portion needs discussion with the author before implementation. Likely shape: apps/worktrunk topic with install + shell-integration tasks; the captured-output-to-template decision is the open design question.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A worktrunk topic installs the binary through mise (or documents why cargo directly) and is removable via the topic
- [ ] #2 Shell integration is declared, not hand-run: the install-time output is captured and reproduced by the topic, with the capture-vs-template approach agreed with the author first
- [ ] #3 Existing worktree flows (manual git worktree, .worktrees/ pattern) are either migrated to wt or explicitly kept, with the decision recorded
- [ ] #4 The OpenCode plugin is installed by the topic via `wt config plugins opencode install` and removed via `uninstall`; the resulting `~/.config/opencode/plugins/worktrunk.ts` stays unmanaged by chezmoi
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
### The OpenCode plugin (added 2026-11-07)

`wt config plugins opencode install` embeds `dev/opencode-plugin.ts` in the
binary and writes it to `~/.config/opencode/plugins/worktrunk.ts`. Verified
against the source (`src/commands/config/opencode.rs`): the plugin source is
`include_str!`-ed at build time, so the file always matches the installed
binary's version.

**The help text under-describes it.** `wt config plugins opencode install -h`
says "Install the activity tracking plugin", but the embedded file also
registers a **worktree strategy** under OpenCode 2 — 19 `worktree` references,
strategy id `worktrunk`. That strategy routes OpenCode-initiated worktree
creation and removal through `wt switch --create` and `wt remove`, so
agent-created worktrees get the configured `worktree-path` and the project's
lifecycle hooks. It is the session-start half of the worktree-isolation
problem, and it is why the plugin matters beyond activity tracking.

**Ownership decision (author, 2026-11-07): the topic runs the command; chezmoi
ignores the file.** `~/.config/opencode/plugins/` is not chezmoi-managed today
(`chezmoi managed` lists `.config/opencode` but no `plugins/` entry), and the
file changes with every `wt` release. Vendoring it as a template would
duplicate an asset Worktrunk ships and drift on every upgrade; capturing it
into chezmoi would show as drift on every upgrade. Calling the command keeps
one source of truth — the binary.

Rejected: vendoring the TypeScript into the topic (duplicates a shipped asset,
must be re-synced per release); capturing the written file into chezmoi
(permanent drift, since the content tracks the binary version).

**Teardown owed in the same change:** `wt config plugins opencode uninstall`
on topic removal, per the extension-after-adoption rule. A topic that installs
the plugin and does not remove it leaves an ownerless artifact.

**Not verified:** whether the strategy fires on a *new session started in the
main checkout*, or only when a session explicitly asks for a worktree. The
docs describe creation and removal, not automatic per-session creation. This
decides whether the plugin alone eliminates the "session never left main"
failure or only handles worktrees the agent asks for. Test it when the topic
lands — the plugin is not installed on this machine.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
