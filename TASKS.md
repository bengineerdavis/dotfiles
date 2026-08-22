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

## Unscramble the cross-session commits — deferred, not abandoned

Two published commits each carry another session's work under a subject that does
not mention it, because all sessions share one `.git/index` and a bare
`git commit` takes the whole index:

| Commit | Subject says | Also contains |
|---|---|---|
| `b3ad740` | clamav systemd timer | a pii-redactor rewrite (8 files total) |
| `5692a86` | pii-redactor layering | 52 zsh deletions (52 files total) |

Neither can be reverted without taking unrelated work with it. Both are published
ancestors of `origin/main`, with 18 and 16 commits stacked on top respectively,
and both carry git notes keyed to their SHAs.

**Not urgent.** The tree is correct; only the attribution and the revert story are
wrong. `git commit -o` stops it recurring — that is the fix that mattered and it
is already in AGENTS.md.

### What is still needed before touching this

Answer these first; several may make the whole thing not worth doing.

1. **Has anyone else cloned or pulled `origin/main`?** A rewrite forces every
   consumer to reset. If this repo is only ever this machine, the cost is near
   zero; if it is on a second machine, that machine has to be reconciled by hand.
2. **Are all sessions stopped?** A rewrite while another session holds a stale
   HEAD produces exactly the scramble it is meant to fix. This needs a quiet
   window with every session confirmed idle, not merely unresponsive.
3. **What should the git notes follow?** `git filter-branch`/`rebase` rewrite
   SHAs, and notes are keyed to the old ones. They must be re-attached
   deliberately or they silently detach. Note they are also **local-only** — no
   notes refspec is configured, so they are not on the remote either way.
4. **Is splitting worth it, or is documenting enough?** Splitting means an
   interactive rebase 18 commits deep, re-resolving each, and force-pushing. A
   `git notes` annotation on both SHAs saying what else is inside costs minutes
   and breaks nothing. Default to the annotation unless there is a concrete need
   to revert one half.
5. **Whose call is the attribution?** Both commits are authored `Ben Davis`, so
   there is no authorship to correct — only the subject line and the ability to
   revert cleanly. If neither half is likely to be reverted, this is cosmetic.

### If it does go ahead

- Take a backup branch first, as the earlier reconcile did
  (`backup/pre-reconcile-d39ff82` is the precedent and is still present).
- Rewrite from the older commit (`5692a86`) so a single pass covers both.
- Verify at tree level afterwards: the final tree must be byte-identical to the
  pre-rewrite tree. That check is what proved the last reconcile lossless.
- Re-run the full suite; it was 220 passed / 5 skipped at the time of writing.

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
