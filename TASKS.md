# TASKS.md

Shared work queue for this repo. Agent sessions keep their own in-memory task
lists, which fragment the moment more than one is running — this file is the
durable version. Read it at the start of a session; update it before you finish.

Keep it short. This tracks *open* work and cross-session hazards, not history —
`git log` already has history, and duplicating it here just creates drift.

## Conventions

- One line per item, imperative, with enough context to pick it up cold.
- Mark **[blocked: reason]** rather than deleting — a blocked item that vanishes
  gets rediscovered from scratch.
- Mark **[inferred]** for anything reconstructed from repo evidence rather than
  stated by the author. Those may be wrong; correct them rather than trusting them.
- When you claim an item, say so in the line. When you finish it, delete the line
  — the commit is the record.

## Claimed

Sessions run in parallel and cannot see each other. Add a line when you start on
anything that touches a file in **Cross-session hazards** below, or that will hold
a global resource (ollama, `chezmoi apply`) for more than a minute. Delete your
line when you stop — including when you stop without finishing.

Append; never reflow or reorder this section. Two sessions editing the same lines
is exactly the collision it exists to prevent.

Format: `- <UTC start> — <what> — <files or resource>`

- 2026-08-22T02:14Z — generalizing hardcoded employer defaults — bin/executable_triage, bin/executable_binned, bin/executable_findline

A stale claim is not a lock. If a line looks abandoned, check `git log -3` on the
file and whether a process is still running before assuming it is safe — then
delete the line and say so in your commit.

## Open

- Add a cheap gate in front of the LLM judge panel: generate and run the script's
  tests, use real pass/fail as the signal, escalate to judges only when the result
  is inconclusive. Treat formatting/lint as fix-as-you-go, not gate criteria. The
  accept-vs-revise signal in git history is training data for it.
- Evaluate frontier cloud alternatives to OpenAI/Grok as judge and generation
  candidates — Qwen, DeepSeek, Moonshot Kimi, Z.ai GLM, MiniMax, Mistral,
  ByteDance Seed, Cohere are all on the existing OpenRouter account. Rank them
  with `model-bench`, not by assertion: several post-date any model's training
  cutoff, so relative quality is genuinely unknown until measured.
- Port the two commit rules that `docs/CONVENTIONS.md` § Commit granularity lacks:
  commit by pathspec (`git commit -- <paths>`, since a bare commit takes whatever
  another session has staged) and verify contents afterwards (`git show --stat
  HEAD`). Both are in the `commit-hygiene` skill; each independently prevents the
  scramble annotated on 5692a86 and b3ad740.
- Push the git notes on 5692a86 and b3ad740 if they should outlive this clone:
  `git push origin refs/notes/*`. No notes refspec is configured, so they are
  local-only. Deliberately did not set `remote.origin.push` — doing so overrides
  the default branch-push behaviour.
- Symlink the two new skills into `~/.claude/skills` on each machine that wants
  them: `ln -s ~/code/personal/ai-prompt-library/skills/<name> ~/.claude/skills/`.
  Per-machine because `~/.claude` is chezmoi-ignored. Skills are `pii-redaction`
  and `commit-hygiene`.
- File the upstream issue on `simonw/llm-pdf-to-images`: it does `import fitz`,
  and PyMuPDF's shim prints a deprecation notice to **stdout**, corrupting any
  captured `llm` output. Draft is written; one-line fix is `import pymupdf`.
  **[blocked: `gh auth login` — the device flow expired]**

## Decisions waiting on the author

- `gpt-oss:20b` and `ministral-3:8b` sit at 2 stars in `bin/binned`'s
  `_RECOMMENDED_MODELS`, marked provisional. `model-bench` measures *judging*, not
  *generation*, which is what the stars document — so promoting them on bench
  evidence would import a number measured on a different task. Leave provisional,
  or build a generation-side test?
- `bin/binned`'s SaaS tier is down to five entries after the gpt-* rows were
  dropped. Repopulate from the frontier evaluation above, or leave it thin?
- Commit-granularity guidance now exists twice: `docs/CONVENTIONS.md` § Commit
  granularity (repo-specific — scope vocabulary, worked examples from this
  history, the don't-over-split floor) and the portable `commit-hygiene` skill
  with executable evals (message-size table, pathspec commits, verify-after).
  They cross-reference and roughly half overlaps. Keep both split by audience —
  humans in this repo vs agents in any repo — or consolidate? One commit message
  called CONVENTIONS.md "the single home", so this needs a decision, not a merge.

## Cross-session hazards

Files with more than one session touching them recently. Check `git log -3 <file>`
and `chezmoi status` before editing.

- `bin/executable_fetchurl` — actively developed; caused the only real merge
  conflict so far.
- `bin/executable_pii-redactor` — ported to Python, then extended with layered
  redaction by another session. Suite is 63 tests; run it after any change.
  Its conftest default mock is a *working* model, not `cat`: a pass-through mock
  plus exit-status assertions is green exactly when the tool leaks, which is the
  defect the layers exist to prevent. Ask for `mock_llm("cat")` explicitly.
- `bin/executable_model-bench` — multi-case judge suite; the reference scorecards
  in `CASES` must be re-derived if a case script changes.

## Standing reminders

- `bin/` scripts are chezmoi source (`executable_<name>`); `~/bin/<name>` is what
  runs. Check `chezmoi status` before editing or you will silently revert the
  working copy.
- A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while
  testing almost nothing. Run it with `typer`, `questionary` and `hypothesis`
  present — see AGENTS.md.
