# CONTRIBUTING.md

How work gets into this repository, by an agent or by a person, and what to do
when the agent route fails.

`AGENTS.md` covers the agent path in detail — branches, merge gates, trust
ladder. This file is the shorter, tool-free version, and it is deliberately
readable by someone who has no agent running and no context from a session.

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

Size the message to the change. A subject alone for mechanical edits; a sentence
or two for small ones; one or two short paragraphs for ordinary work. A message
longer than its change warrants means the commit should have been two.

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

## Conventions that were considered and rejected

Recorded so the search is not repeated, per the `review-best-practices` skill.

- **Conventional Commits** — only 12% of this history uses it, and its payoff is
  automated changelog and semantic versioning. This project keeps no
  `CHANGELOG.md` by design and does not release. It would impose a rewrite for
  benefits it does not want.
- **commitlint / gitlint / commitizen** — they enforce *format*. The house style
  is already 71% consistent informally, and the measured problem is length, not
  format. None is installed; adding one buys little.
- **`unslop` style skills** (`no-ai-slop`, cursor's `unslop`) — measured against
  this repo and rejected for wholesale adoption. Every lexical tell they flag
  scores zero here, and their sharpest rule, "avoid em dashes entirely", targets
  a pattern this repository uses at 12 per 1000 words *in documents written
  before any agent touched it*. Adopting it would edit the author's voice, not
  remove slop. The binary-contrast pattern is worth borrowing; the rest is not.
