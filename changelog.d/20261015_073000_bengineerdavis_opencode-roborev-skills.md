# Added

- opencode topic: declared the ten roborev-bundled skills as vendored in
  `opencode_skill_vendored`, each directory carrying LICENSE and PROVENANCE.md.
  `roborev skills install` writes them into ~/.agents/skills (and
  ~/.claude/skills), but roborev's skills are not a git source dotagents could
  reference, and MIT licence + the vendored declaration is what the
  approved-sources guard audits against. Refresh is deliberate: a roborev
  upgrade rewrites those directories and may drop PROVENANCE.md — the guard
  fails loudly when it does, by design.
- Also on 2026-10-15: retired the stray mise/npm opencode installs (1.18.30,
  1.18.32 — no config ever declared them; `mise ls` "not active" residue of the
  pre-v2 era), so `opencode` resolves only to the brew opencode-v2 binary, and
  installed `skill-trust` via uv tool (the approved-sources guard names it as
  its own fix and it was absent).