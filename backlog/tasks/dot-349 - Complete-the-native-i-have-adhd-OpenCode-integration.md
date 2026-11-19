---
id: DOT-349
title: Complete the native i-have-adhd OpenCode integration
status: To Do
created_date: 2026-11-10 20:55
dependencies:
  - DOT-348
updated_date: 2026-11-19 21:03
orchestration:
  status_key: todo
  version: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The global dotagents source installs i-have-adhd's canonical skill but does not establish the complete native OpenCode integration documented upstream. dotagents 3.4.0 links plugin skills into OpenCode; its documentation does not claim to project .opencode/plugins/\*.mjs or OpenCode commands.

Ship:

- Test the installed dotagents projections for i-have-adhd in isolated HOME fixtures for every configured runtime, reporting passed, failed, and unsupported behavior explicitly.
- Add the native i-have-adhd OpenCode plugin, /i-have-adhd command, and matching teardown through apps/opencode, leaving always-on disabled unless the author separately enables it.
- Prepare a narrowly scoped upstream dotagents installation proposal from a fork, or document why the measured integration needs no upstream change.
- Record all verified integration findings and references in the owning topics.

Constraints:

- Do not fork to change the canonical skill rules. Use the existing upstream source.
- Upstream asks that new integrations be discussed in an issue first. Publication to an issue or PR requires separate explicit author approval.
- The OpenCode adapter belongs to apps/opencode; shared skill declarations remain in apps/dotagents.
- Never enable the always-on hook implicitly or run chezmoi apply without author approval.

Decision record: Approved by the author 2026-11-10 as the queued B follow-up to the core dotagents installation.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Isolated projection tests report each configured runtime as passed, failed, or explicitly unsupported; no skip counts as a pass.
- [ ] #2 The native OpenCode plugin and command load in an isolated configuration directory, with tests proving both activation and opt-out behavior.
- [ ] #3 The always-on flag remains absent and no always-on content is injected by default.
- [ ] #4 The OpenCode topic teardown removes exactly the adapter state it creates.
- [ ] #5 The upstream contribution decision and measured evidence are recorded, and no upstream issue or PR is published without explicit approval.
- [ ] #6 The owning topic docs contain the verified findings and authoritative upstream references.

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

2026-11-17 progress (branch agent/dot-349, commit 2848cf71): measured that dotagents 3.4.0 installs the plugin's FULL upstream tree including .opencode/plugins/i-have-adhd.mjs but projects only skill links into OpenCode — so no vendored clone is needed and option (a) reduced to a 38-line loader rather than a third-party tree. OpenCode 2.3.1 on this box; the plugin exports setup(ctx), the V2 API, so the Lore V1-API failure does not repeat here. Verified OpenCode auto-discovers ~/.config/opencode/plugins/\*.js via `opencode plugin list`, which lists herdr-agent-state.js as a loaded local plugin — so the loader needs no plugins-array entry in opencode.jsonc. Shipped: templates/i-have-adhd-loader.js.j2 (re-exports upstream, resolves its dependency from os.homedir() at load time — no machine-specific literal), install.yaml probe-then-write with the fix named (run the dotagents topic), remove.yaml teardown of loader + flag only, and the always-on flag file by author request 2026-11-17 (upstream's alwaysOnInjection() returns null without it, so the loader alone is a no-op). 16 tests in tests/topics/test_opencode_adhd_loader.py, 10 mutations each seen failing. Gate: full suite 3 failed / 1720 passed / 6 skipped, all 3 pre-existing on main (2 lore rules + test_guard_wiring dotagents-stderr, the latter confirmed failing at HEAD~1 too). Ruff clean, skillet Valid. REMAINING before the task is done: push, PR, author merge, then chezmoi apply + run-role opencode from main and confirm the hook injects. Deliberately NOT done: upstream dotagents proposal (task's third Ship bullet) — publication needs separate author approval per its Constraints.
2026-11-19 HANDOFF — PR #187 open, unmerged. Branch agent/dot-349, commit 31ceada8 (rebased onto origin/main fb141d52; the branch was rebuilt clean because the worktree had inherited a stale merge commit and a leftover DOT-348 backlog commit from the previous session — both never pushed, so no history was rewritten).

WHAT IS DONE: all three code pieces ship and are green. templates/i-have-adhd-loader.js.j2 (38 lines) re-exports upstream's plugin, resolving the dependency from os.homedir() at load time; install.yaml probes for the dotagents tree then writes the loader, failing with the fix named; remove.yaml tears down the loader AND the always-on flag; defaults/main.yaml carries opencode_adhd_plugin, opencode_adhd_plugin_source, opencode_adhd_plugins_dir, opencode_plugin_dir, opencode_adhd_loader_name, opencode_adhd_always_on, opencode_adhd_always_on_flag. Always-on defaults TRUE by author request 2026-11-17. 16 tests in tests/topics/test_opencode_adhd_loader.py, 10 mutations each observed failing.

WHAT A NEW SESSION PICKS UP:

1. PR #187 needs author merge. Do not self-merge (AGENTS.md — deferred-tree file).
1. AFTER MERGE, from the MAIN checkout only (never a worktree): `chezmoi apply ~/dotfiles/apps/opencode` then `bash dotfiles/executable_run-role.sh opencode`. Both need author approval per the apply rule.
1. CONFIRM the hook actually fires — this is the acceptance check nobody has run yet. The loader and flag are verified to exist and to load under node, but NOT verified to inject into a live session. A running OpenCode must be restarted first. Evidence to gather: ~/.config/opencode/.i-have-adhd-always exists, `opencode plugin list` shows i-have-adhd as a local plugin, and a reply in a fresh session carries the ADHD ruleset.
1. Fallback if the loader does not load: check ~/.local/share/opencode/log/opencode.log for the plugin id; the loreai topic's tasks/agents/opencode.yaml has the classifier pattern for loader rejections.

STILL OPEN IN THIS TASK: the third Ship bullet (upstream dotagents proposal). The measured finding is that NO upstream change is needed — dotagents already delivers the full tree and simply does not project plugin files into OpenCode. Publishing that as an issue needs separate author approval; nothing is written to upstream.

ALSO FOUND, NOT FIXED (separate tasks): (a) tests/guards/test_guard_wiring.py::test_every_dotagents_caller_reports_stderr fails on main AND at HEAD~1 — it matches the word 'dotagents' in comments, so apps/opencode/tasks/install.yaml trips it; pre-existing, not this branch. (b) DOT-305's two missing .lore.md rules still fail. (c) lore doctor reports OpenCode 'file missing' because it looks for opencode.json while this fleet deploys opencode.jsonc — a false negative in a diagnostic.
2026-11-19 CORRECTION to the earlier gate report — I was wrong that all 3 failures were pre-existing, and the CI evidence proved it. `tests/guards/test_guard_wiring.py::test_every_dotagents_caller_reports_stderr` PASSES at the commit before mine and FAILED at my commit: my install.yaml names 'dotagents' in a task name and in the failure message, and that guard matched the bare word anywhere in a file containing any command task, so my `brew --version` probe made the file look like a dotagents caller. My earlier 'verified failing at HEAD~1' check ran against a DIFFERENT base before the rebase and did not test the actual parent. The lesson: verify against the real parent commit of the commit under test, and re-run after every rebase.

Fixed in commit 237d7be8 ('guards: match dotagents as a command, not as a word'): the guard now parses the task YAML and inspects only command/shell values, which is what 'shells out to dotagents' always meant. The original 2026-09-12 bug is still caught — proved by mutation: swapping .stderr for .stdout with failed_when flipped FAILS the test, and dropping both guards FAILS it. tests/guards is 33 passed; guard + loader suites are 27 passed on the rebased tree.

REMAINING CI EVIDENCE (not yet green at time of handoff): the other 8 failures on the same run were pre-existing and appear on main's own CI with the identical node IDs (6x tests/claude_credentials/\*, 2x tests/docs/test_lore_md_rules_survive.py) — verified by reading main's failing run 44611684900, which lists the same claude_credentials set. Those belong to other sessions and are NOT this PR's to fix.
=== HANDOFF 2026-11-19 (session wrap) — PR #187 OPEN, UNMERGED ===

STATUS: code complete and pushed; waiting on author merge. Task stays in progress, not Done (Done tracks merge state).

REPO/BRANCH/WORKTREE: bengineerdavis/dotfiles; branch agent/dot-349; worktree /Users/ben.davis/.local/share/chezmoi/.worktrees/dot-349. PR #187 — https://github.com/bengineerdavis/dotfiles/pull/187

COMMITS (in PR): 31ceada8 (opencode loader + always-on flag), 237d7be8 (guard fix — see CORRECTION in the prior entry), 36bb17e0 (docs: the two verification mistakes). Branch tracks origin/agent/dot-349; a bot merges main into it periodically, so ALWAYS `git fetch` and rebase before pushing — a push rejected as non-fast-forward means the bot moved the tip, not that you lost work.

OWNED FILES (this PR): home/dotfiles/apps/opencode/{defaults/main.yaml,tasks/install.yaml,tasks/remove.yaml,templates/i-have-adhd-loader.js.j2}, tests/topics/test_opencode_adhd_loader.py, tests/guards/test_guard_wiring.py, docs/WORKTREES.md, changelog.d/20261119_223000_opencode_adhd_loader.md, backlog/tasks/dot-349\*, backlog/tasks/dot-388\*.

FOREIGN DIRTY FILES — DO NOT TOUCH: tests/ollama_models/test\_{adopt_command,comment_preservation,rewrite_units}.py (another session); backlog/tasks/dot-{140,343,378,379}\*.md (DOT-378/379 leased by 'OpenCode retro-git-topic'); CHANGELOG.md, AGENTS.md and dot-381 on the MAIN checkout, which was mid-merge of PR #190 when this session ended. The main checkout is NOT clean and that is not this task's to fix.

CHECKS ACTUALLY RUN: tests/guards 33 passed; tests/guards+topics 27 passed on the rebased tree; tests/docs+guards 59 passed / 2 failed; full suite earlier 3 failed / 1720 passed. The 2-3 failures are pre-existing and NOT regressions: 2x tests/docs/test_lore_md_rules_survive.py (content genuinely absent from .lore.md — DOT-305 owns it; verified 0 matches in the file while the guarded code rule still exists in mise/remove.yaml), 1x the guard failure this branch introduced and then fixed. Mutation coverage: 10 mutations on the loader/flag, 2 on the guard, each observed failing.

NOT VERIFIED: the hook injecting into a live OpenCode session. The loader loads under node (id=i-have-adhd, setup=function) and the flag path is upstream's, but nothing has watched a real reply. This is the acceptance check that remains.

ACCEPTANCE CRITERIA REMAINING:

1. Author merges PR #187.
1. From the MAIN checkout only: `chezmoi apply ~/dotfiles/apps/opencode` then `bash dotfiles/executable_run-role.sh opencode`. Applying from a worktree is forbidden; recovery procedure is in docs/WORKTREES.md § If you already applied from a worktree.
1. Restart OpenCode, then confirm: ~/.config/opencode/.i-have-adhd-always exists, `opencode plugin list` shows i-have-adhd, and a fresh session's reply carries the ADHD ruleset.
1. Third Ship bullet (upstream dotagents proposal): the measured finding is NO upstream change is needed — dotagents already ships the full plugin tree and merely does not project it into OpenCode. Publishing an issue needs separate author approval; nothing was written upstream.

BLOCKERS: none technical. Merge is the author's by house rule.

RESUME: cd .worktrees/dot-349 && git fetch origin && git rebase origin/agent/dot-349 && gh pr view 187 --repo bengineerdavis/dotfiles

DURABLE HANDOFF: this task record (nothing lives only in chat). Related queued work: DOT-390 (guard hardening), DOT-305 (.lore.md loss).

<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

Measured 2026-11-15 in isolated dotagents 3.4.0 fixtures: targeting only OpenCode installs ~/.agents/plugins/i-have-adhd and links ~/.config/opencode/skills/i-have-adhd to the canonical skill. It creates no .opencode plugin or command output. The upstream .opencode/plugins/i-have-adhd.mjs setup hook registers a context hook on load; always-on injection remains flag-gated. B must prove the native setup hook and command explicitly; an installed skill link is not evidence that B is complete.

Author ruling 2026-11-15: A stays skill-only for OpenCode. B retains the setup hook and command work, with always-on opt-in.

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
event_id: run-3008b671dc4e47398837e15fb9dc35dd
type: claim_task
actor: opencode-dot349
timestamp: '2026-11-18T04:11:55.206286Z'
result: succeeded
task_id: DOT-349
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```

<!-- RUN_HISTORY_ENTRY:END -->

<!-- RUN_HISTORY_ENTRY:BEGIN -->

```yaml
event_id: run-327acafbe4914f1aa01dc7d6d9471348
type: release_task
actor: opencode-dot349
timestamp: '2026-11-19T20:45:50.088948Z'
result: succeeded
task_id: DOT-349
from_status: inprogress
to_status: todo
```

<!-- RUN_HISTORY_ENTRY:END -->

<!-- SECTION:RUN_HISTORY:END -->
