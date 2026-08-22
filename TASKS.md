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
- Symlink the two new skills into `~/.claude/skills` on each machine that wants
  them: `ln -s ~/code/personal/ai-prompt-library/skills/<name> ~/.claude/skills/`.
  Per-machine because `~/.claude` is chezmoi-ignored. Skills are `pii-redaction`
  and `commit-hygiene`.
- File the upstream issue on `simonw/llm-pdf-to-images`: it does `import fitz`,
  and PyMuPDF's shim prints a deprecation notice to **stdout**, corrupting any
  captured `llm` output. Draft is written; one-line fix is `import pymupdf`.
  **[blocked: `gh auth login` — the device flow expired]**
- Decide whether `docs/CONVENTIONS.md` needs the commit rules at all. They now
  live in `AGENTS.md` (`git commit -o`, then `git show --stat HEAD`), which is the
  right home for agent process; CONVENTIONS.md § Commit granularity still covers
  only granularity and messages. Leaving it split is defensible — just do not let
  the two drift.
- Build the policy resolver: read `dotfiles/policy/ethics.yaml`,
  `~/.local/state/ai-policy/company.yaml`, `dotfiles/policy/personal.yaml` in that
  precedence order, first layer to speak wins, missing rule denies. The three
  files and the ordering exist and are validated; nothing reads them yet, so no
  rule is currently enforced by anything. See `dotfiles/docs/GOALS.md`.
- Wire `--no-log` for work-tagged prompts, gated on the resolver above. This is
  the concrete reason the resolver matters: until it exists, work content keeps
  landing in the `llm` log with no retention rule applied.
- Scope and apply retention to the 8 rows of work content already in the `llm`
  log. `company.yaml`'s `open_questions.indefinite_local_log` defaults to
  `treat_as_non_compliant`, so the current state is the non-compliant one by our
  own reading. Blocked on the resolver only for automation — the rows can be
  scoped by hand first.
- Add tests for `bin/triage`. It has none, which is why a `platform=None`
  reporting bug reached the deployed script and was caught by a manual smoke test
  rather than the 218-test suite. The env/flag/fallback resolution is the obvious
  first case.

## History was rewritten on 2026-08-21 — reset before you resume

`main` was force-pushed. Every SHA from `bc72f5c` onward is new. Two mixed
commits were unscrambled: `b3ad740` split into a clamav half and a pii-redactor
half, and `5692a86` reworded to describe the 52 zsh deletions it actually
contains. Verified lossless — the tree is byte-identical to before, and the suite
is 218 passed / 7 deselected.

**Anything holding the old history must hard-reset, not pull.** A pull merges old
and new and resurrects the mixed commits.

```bash
git fetch origin
git reset --hard origin/main
git fetch origin 'refs/notes/*:refs/notes/*'   # notes are published now
```

Who needs this:

- **The second machine.** Not currently contributing, so no work is at risk — but
  it must reset before its next commit or it will reintroduce the old SHAs.
- **Any session idle-but-not-finished.** Reset before resuming; a commit against
  the old HEAD undoes the unscramble.

Pre-rewrite history is on `backup/pre-unscramble-272bdf7` if anything needs
recovering. Rollback is `git reset --hard backup/pre-unscramble-272bdf7` plus a
force-push, valid until someone pushes on top.

Each of the three commits carries a `git notes` PROVENANCE entry explaining the
split and pointing at the prevention. Read with `git notes show <sha>`.

## Purge the work email from git history

Privacy, and portability if the author moves on: no work email should survive in
this repo. Personal addresses are fine — `ruubixo@gmail.com` on one 2020 commit is
an old address of the author's and is deliberately left alone.

### What is actually there

Searched author fields, committer fields, commit messages, git notes and file
contents across all history.

| Where | Finding |
|---|---|
| author / committer fields | **Clean.** 323 of 324 commits are `bengineerdavis@gmail.com`; the one exception is the personal alt address. No work email ever authored a commit. |
| commit messages, git notes | **Clean.** |
| current working tree | **Clean.** The header was corrected to the canonical address. |
| **file contents in history** | **`ben.davis@sentry.io`** in `bin/executable_binned`'s `# Author:` header — introduced by `7fc74a5` (2026-04-25), present in the tree of **123 commits** on `main`. |
| also in history | `docs.sentry.io` and `sentry.io/changelog` URLs, generalised out of `triage` by `a5d9e51`. Employer references, not PII. |

So the leak is one string in one file, but it is baked into 123 commit trees and
`git log -p` will surface it in any clone.

### What removing it costs

`git filter-repo --replace-text` rewriting from `7fc74a5` forward — **133
descendant commits**, so every SHA from April onward changes. That is a second
full-history force-push, and it invalidates the SHAs the PROVENANCE notes
reference, which would need re-attaching again.

`.mailmap` does **not** help here: it remaps author identities, not file contents.
This one genuinely requires a rewrite or nothing.

### Options

1. **`git filter-repo --replace-text`** on the email string alone. Precise, keeps
   the URLs, rewrites 133 commits. The right call if this repo will ever be
   public or shared.
2. **Same, plus the URLs**, if employer references should go too rather than just
   PII. Same cost, broader result.
3. **Leave it.** Private repo, single contributor. The current tree is clean, so
   anyone reading the code sees nothing; only `git log -p` reveals it.

**Recommendation: option 1, batched with anything else needing a rewrite.** Two
full-history rewrites in one week is worse than one, so it is worth deciding
whether the URLs go at the same time rather than discovering them later.

### Before running it

- Same prerequisites as any rewrite: all sessions idle, second machine reset
  afterwards, backup branch first, verify the tree is byte-identical except for
  the intended string, re-attach and re-push notes.
- Add a guard afterwards so it cannot return — a pre-commit check for
  work-domain strings would catch the next one at the point it enters, which is
  the enforcement principle in `dotfiles/docs/GOALS.md`. Key it off a pattern in
  `dotfiles/policy/`, not a hardcoded domain, or the guard needs editing at
  exactly the moment it matters most — the employer change it exists to prepare
  for.

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
- `~/.local/state/ai-policy/company.yaml` has **22 TODO fields** awaiting the
  author's language. It is machine-local and unversioned by design, so it cannot
  be tracked here — only pointed at. Until it is filled, `fail_closed` means the
  company layer denies everything it is asked about, which is safe but not useful.
  Work top-down: `device.approved` gates the rest.
- `apps/ollama` writes `_ollama_zsh_completion` from Ansible to a path chezmoi
  also manages — dual ownership, deliberate, documented in `tasks/install.yaml`
  with its consequence (`chezmoi apply` reverts a re-download). Marked UNDECIDED:
  formalise by giving one tool sole ownership, or leave it? Note the inversion —
  for that file the topic-root copy is the live one, the `files/zsh/` copy is dead,
  which is backwards from every `*.zsh`.

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
