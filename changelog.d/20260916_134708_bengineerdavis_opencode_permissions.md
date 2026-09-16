**Changed**

- opencode project permissions were reworked (`opencode.json` →
  `opencode.jsonc`): rules deduplicated and reordered so last-match-wins falls
  the right way, interpreters and the test/lint toolchain are now `allow`,
  `chezmoi apply` is denied, and an opt-in `autonomous` agent widens the
  frequent-but-reversible operations (commit/push, `gh`, fetches, installs,
  model pulls, webfetch) without touching the deny tier.
- The global opencode template's bash catch-all moved first — it had sat last,
  which would have turned every command into a prompt at the next restart.
- History rewriting (`git filter-repo`/`filter-branch`) changed from `deny` to
  `ask` in both opencode and Claude Code, so the human sees the command and
  applies the backup-branch + `git notes` ceremony per invocation. Force-push
  stays denied.

**Security**

- The Claude Code config's secret-path deny rules named a different machine's
  macOS home (`/Users/ben.davis/...`), so on this machine they never matched
  and the secrets they guarded were reachable in principle. They now use `~`
  and apply on any machine.

**Added**

- `docs/LANGUAGES.md` — which languages the repo's scripts use, and the
  reusable per-language tool profile.