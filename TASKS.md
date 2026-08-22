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

## Private tasks

Some work cannot be described here without reproducing the thing it is trying to
remove. Those live in `~/.local/state/chezmoi/private-tasks.md` — machine-local,
never in git, same pattern as `~/.local/state/ai-policy/company.yaml`.

Currently one item there: a history-rewrite to remove an employer-domain string
from file contents. Scope, method and prerequisites are recorded in that file.

Note for whoever runs it: `TASKS.md` itself is in scope. An earlier revision of
this section quoted the target string literally before it was redacted, so the
purge must cover this file as well as the original.

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
