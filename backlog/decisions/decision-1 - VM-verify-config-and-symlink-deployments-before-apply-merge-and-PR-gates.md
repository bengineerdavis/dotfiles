---
id: decision-1
title: VM-verify config and symlink deployments before apply, merge, and PR gates
date: 2026-10-29 21:46
status: proposed
---

## Context

On 2026-10-29 two config incidents landed on this Mac in one chain:

1. **The payload move broke the global mise config.** Commit `e9fe86b` moved the chezmoi payload under `home/` via `.chezmoiroot`, which left `~/.config/mise/config.toml` dangling until the next apply. The user's global mise config disappeared; backlog-py (installed through mise) failed as a consequence, which is how the chain started. Recovery was the user running `chezmoi update` by hand. No test verified that managed symlinks still resolved after the move.
2. **A generated config captured a dead route.** `lore setup opencode` wrote `opencode.json` with every provider's baseURL pointing at the local gateway (127.0.0.1:3207). When the gateway became unavailable, OpenCode had no working upstream; removing the plugin did not remove the routes. The user regained access only by stopping the gateway. A second config file (`opencode.jsonc`, chezmoi-managed) coexists with the generated one — competing config files are an antipattern even when the tool resolves precedence correctly.

Neither failure was caught by any gate: the payload move passed its tests and broke only on the target machine at apply time.

## Decision

The author ruled (2026-10-29):

1. **VM-verified config gate.** Any change to global config that can destabilize user-level usage is verified by integration/E2E/agent-user-tested checks in a VM matching the target machine environment. The gate runs at three checkpoints: before a PR is made, before a PR merges (with all approved commits), and after `chezmoi apply`/`chezmoi update` completes (and on git pull). Enforcement is mechanical: pre-commit hooks and CI for the first two, a post-apply hook for the third.
2. **Symlinks are tested by default.** All managed symlinks are verified in that gate, especially when a file's location changes — the exact failure class that broke mise.
3. **One config file per tool — the default, reviewed per topic/tool.** One config file per tool is the requirement by default (author amendments, 2026-10-29): if only one config file or config file type is required, there should never be more than one of them. The rule is applied per topic and per tool, and a tool keeps more than one file only where official tool documentation itself establishes the behavior (documented precedence, layered locations, distinct-purpose files) — the review must cite the official doc source, not observed behavior. Same-purpose duplicates — migration leftovers, orphaned generated files — remain unacceptable and get cleaned up explicitly. For OpenCode, the default is `opencode.json` (LoreAI's `lore setup opencode` expects it) unless V2 requires JSONC. Follow the documented approach or what the code does; if a tool misbehaves, open PRs from forked codebases against the respective tools and raise it upstream.
4. **Incidents become post-mortems in backlog.** Capture incidents like these as decisions (this ADR) with linked remediation tasks, so the failure classes stay visible after the session ends. What counts as an incident is deliberately left open here: the author requires a code review or design review to define it before capture can be applied mechanically.
5. **Symlinked config converts to copy deployment** (author ruling, 2026-10-29, during this post-mortem): the global mise config is deployed via chezmoi's `symlink_` attribute, which makes `git pull` the deployment itself — the live config changes the instant the source file updates, with no render/verify/swap step any gate can stand in front of. Convert symlink-deployed files to regular chezmoi-managed files so deployment happens only at `chezmoi apply`, where the post-apply gate can verify. The live-edit convenience (documented in AGENTS.md as a cross-session hazard) is consciously traded away.

## Consequences

- Remediating tasks must exist in the queue and reference this decision: the VM gate (pre-PR + CI), the post-apply/pull hook, the symlink sweep, and the opencode.json/jsonc consolidation.
- A template change that moves managed files is not code-complete until the VM gate runs; "renders clean" is no longer sufficient evidence for deployment-affecting changes.
- The single-config rule constrains the LoreAI topic design (DOT-242 and the plugin work in PR #89): the topic must not leave a second file behind, and must handle the gateway-unavailable case without requiring the user to stop the gateway. A tool may keep more than one config file only where its official documentation establishes the layered behavior — each such allowance is reviewed per topic and cites the official doc source; same-purpose duplicates are still removed.
- Git hooks enforce locally; a post-merge/post-apply hook is local config, so the repo must document (or automate) its install step rather than assume it exists.
