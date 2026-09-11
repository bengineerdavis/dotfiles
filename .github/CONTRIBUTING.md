# CONTRIBUTING.md

How work gets into this repository, by an agent or by a person, and what to do
when the agent route fails.

**This file routes; it does not restate.** Three documents already cover pieces
of this and duplicating them is how they drift apart:

- **`dotfiles/docs/CONTRIBUTING.md`** — adding or changing a topic, the CRUD
  teardown invariant, the `<scope>: <imperative>` commit convention, and the
  Ansible checks to run before committing. The detail lives there.
- **`AGENTS.md`** — the agent path: branches, merge gates, decomposition, the
  trust ladder.
- **`conventions/`** — per-subject standards (Python, permissions).

What is only here: the **manual path**, what to do when an **agent fails
mid-task**, and pull request mechanics. It is deliberately readable by someone
with no agent running and no context from a session.

It lives in `.github/` because GitHub discovers `CONTRIBUTING.md` only there, at
the repository root, or in `docs/`. There is a stale copy at `docs/CONTRIBUTING.md`
that GitHub would otherwise surface; `.github/` takes precedence over it.

## The manual path always works

**Everything here can be done with git, an editor, and a browser.** That is a
requirement rather than a happy accident: an agent that fails mid-task, a
machine without the tooling installed, or a person who simply prefers to do it
by hand must all be able to finish the work.

Where a mechanism helps, it is a *prompt*, never a gate you cannot pass without
it. The commit template suggests; it does not block. The hook checks one thing
and tells you how to proceed.

### Committing, by hand

```bash
git add -p                  # stage deliberately; never `git add -A` on a shared tree
git diff --cached           # is this one reviewable decision?
git commit                  # the template opens with the house rules in comments
git show --stat HEAD        # confirm it contains what you meant
```

The commit template is wired via `git config --local commit.template .gitmessage`
and is **already set** in this clone. On a fresh clone, run that line — it is the
one piece of setup that is not automatic.

`dotfiles/docs/CONTRIBUTING.md` § Commits has the subject convention. The only
addition is size: a subject alone for mechanical edits, a sentence or two for
small ones, one or two short paragraphs for ordinary work. A message longer than
its change warrants means the commit should have been two.

### Opening a pull request, by hand

A pushed branch is **not** a pull request. `git push` prints a
`.../pull/new/<branch>` URL — that is an offer, not an artifact.

```bash
git push -u origin <branch>
gh pr create --base main --head <branch> --body-file <file>   # or open the URL
```

`.github/pull_request_template.md` fills the body automatically in the browser
and via `gh`. **PR descriptions are not length-limited.** They serve a reviewer
deciding on several commits at once, who was not in your session.

### When the agent fails mid-task

1. `git status` and `git stash list` — find what it left behind.
2. `git log --oneline -5` — check whether it committed to the branch you expect.
   An agent committing to the wrong branch and pushing a different one has
   happened here.
3. `TASKS.md` § Claimed — delete its claim line so nothing else waits on it.
4. Finish by hand, or revert: `git reset --hard origin/<branch>` discards local
   work, `git revert <sha>` undoes a published commit safely.

Nothing an agent does here is unrecoverable by design. `chezmoi apply` is denied
to agents for exactly this reason — it is the one action that reaches outside
git.

## What is enforced, and by what

| Rule | Enforced by | Fails how |
|---|---|---|
| Shell scripts lint clean | `prek` pre-commit hook | blocks the commit |
| Message proportional to change | `commit-msg` hook | blocks, and says to split |
| Conventions reachable from AGENTS.md | `tests/docs` | fails the suite |
| Governance docs not deployed | `tests/chezmoi` | fails the suite |
| Everything else | review | nothing |

Hooks are **not installed automatically**. Run `prek install` on a fresh clone,
then prove it works rather than assuming: commit a shell script with an unquoted
`$var` in a test and watch it be rejected. This repository's hook config sat
inert for its entire history because nobody checked.

## Skills an agent should have loaded

These are standards in their own right, not shortcuts. Each is a separate
concern, and an agent working here should have all four available.

| Skill | When it fires |
|---|---|
| `commit-hygiene` | committing, or deciding how to split finished work |
| `review-best-practices` | before committing to an approach, or adopting a convention |
| `no-ai-slop` | editing any prose — docs, PR descriptions, commit bodies |
| `pii-redaction` | anything that strips or sends personal data |

They live in `~/.claude/skills/`, which is machine-local and chezmoi-ignored, so
installing them recurs on each host. `TASKS.md` carries the command.

**`no-ai-slop` is vendored from a third party** (MIT, see its `PROVENANCE.md`)
and carries one recorded deviation. Its em-dash rule allows one or two per
longer draft and says to cut clusters and decorative dashes. Density in this
repository is around 12 per 1000 words — and identical in documents written
before any agent touched it, so that baseline is the author's voice rather than
an AI tell. Apply the rule as written; do not read the raw count as slop.

**The manual equivalent** is the skill files themselves: they are prose, and a
person can read `~/.claude/skills/<name>/SKILL.md` and apply it by hand. Nothing
in them executes.

## Conventions that were considered and rejected

Recorded so the search is not repeated, per the `review-best-practices` skill.

- **Conventional Commits** — only 12% of this history uses it, and its payoff is
  automated changelog and semantic versioning. This project keeps no
  `CHANGELOG.md` by design and does not release. It would impose a rewrite for
  benefits it does not want.
- **commitlint / gitlint / commitizen** — they enforce *format*. The house style
  is already 71% consistent informally, and the measured problem is length, not
  format. None is installed; adding one buys little.
- **cursor's `unslop`** — rejected in favour of `no-ai-slop`, which is adopted
  above. Its rule is "Em dash overuse. Avoid em dashes entirely", an absolute
  that conflicts with measured house style: 12 per 1000 words in documents
  predating any agent. `no-ai-slop` reaches the same goal with a calibrated
  rule — cut clusters and decoration, keep the ones that beat a comma — and is
  MIT with a clear license file, where the cursor skill sits in a monorepo whose
  licensing is less clear to vendor from.
  Worth noting what neither catches: **length**. The measured defect in this
  repository's agent-written commits was a 232-word median against a 114-word
  baseline, and no lexical rule in either skill would have flagged one of them.
  That is what the commit-msg hook is for.
