# TODO: full history scrub

**Status: open. Repo was made PRIVATE 2026-09-10 as the immediate mitigation.**

## Why

This repo was public until 2026-09-10. Tracked files and commit messages name
the employer and several vendor services. At the time of the audit, on
`origin/main` (315 commits):

| term | occurrences in tracked files at tip |
|---|---|
| employer name | 19 |
| password manager | 6 |
| observability vendor | 3 |
| disk encryption | 1 |

Plus 4 commit *messages* naming a vendor. Files involved include
`dotfiles/apps/mise/files/config.toml`, `dotfiles/zsh/aliases.zsh`, and three
`bin/` scripts.

Making the repo private removes the exposure going forward and covers history,
forks and caches in one step. It does **not** remove the strings — if the repo is
ever made public again, or shared with someone who should not see them, they are
still there.

## What a scrub involves

1. Decide the replacement vocabulary first — generic role words ("work laptop
   management", "the observability vendor") rather than a find-and-replace that
   leaves sentences unreadable.
2. Rewrite tracked file content at tip, commit normally. Cheap, no history
   surgery, and it stops the growth.
3. Only then consider rewriting history (`git filter-repo`, not `filter-branch`).
   This is the expensive part: it rewrites every commit SHA, requires a
   force-push, and GitHub retains orphaned commits reachable by SHA for a period
   afterwards — so it does not fully un-publish anything that was already
   fetched, forked or indexed.
4. Rotate anything that turns out to be a credential rather than a name. None
   were found in the audit, but the audit looked for vendor names, not secrets.

## Do not confuse this with the usage-figure decision

Separately, local usage figures (task-type split, prompt-size distribution) are
deliberately NOT committed — see `apps/ollama/files/ollama-profile`. That was
handled at the source: the numbers never entered a commit. This TODO is about
strings that are already in history.

## Priority

Low urgency while the repo is private. It becomes blocking the moment anyone
wants it public again, or wants to share it outside the machine.
