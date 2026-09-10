# TODO: scrub employer-identifying strings

**Status: open. Repo made PRIVATE 2026-09-10 as the immediate mitigation.**

## Scope — what counts

IN SCOPE: strings that identify the employer or the author personally. A reader
of this repo should not be able to tell who Ben works for.

OUT OF SCOPE: generic vendors and tools that many companies use. Naming them
implies nothing about a particular employer, and stripping them would make the
configs unreadable for no privacy gain. Explicitly fine to keep:

    1Password · Bitwarden · Okta · Kandji · Datadog · Intercom · FileVault

## Scope — what is actually there

Audited at `main` tip, 2026-09-10, matching `ben.davis@`, `@sentry.io`,
`sentry.io`, `Sentry IT`, `code/work/sentry`, and internal tool names.

**9 occurrences across 5 files:**

| file | count |
|---|---|
| `dotfiles/apps/chrome/defaults/main.yaml` | 4 |
| `dotfiles/apps/chrome/README.md` | 1 |
| `dotfiles/apps/chrome/files/executable_browser-ext` | 1 |
| `dotfiles/docs/ROADMAP-topic-cli.md` | 1 |
| `dotfiles/zsh/executable_aliases.zsh` | 1 |

Worst of it is the `chrome` topic: a work email as a profile identifier, a
`~/code/work/<employer>/…` path, an internal tool name, and references to the
employer's IT admin console.

**1 commit message:** `fe937f0` — "TASKS.md: scope the work-email purge from a
full search". Note this implies the work-email problem was already known and
being tracked before this audit.

### One judgement call, not yet decided

`@sentry/browser` appears twice as an npm dependency. It is a public SDK used by
thousands of unrelated projects, so on its own it implies nothing. It only
becomes identifying next to the work path and email — which the scrub removes
anyway. Recommend keeping it; revisit only if the surrounding context stays.

## How to do it

1. Agree replacement vocabulary first. Generic role words — "the work
   organisation", "work browser profile", `~/code/work/<org>/` — rather than a
   blind find-and-replace that leaves sentences ungrammatical.
2. Fix tracked content at tip and commit normally. Cheap, no history surgery,
   stops the growth. **This alone is most of the value** now the repo is private.
3. Only then consider rewriting history (`git filter-repo`, not
   `filter-branch`). Expensive: every SHA changes, requires a force-push, and
   GitHub retains orphaned commits reachable by SHA afterwards — so it does not
   fully un-publish anything already fetched, forked or indexed during the ~13
   days this repo was public.
4. The audit looked for NAMES, not secrets. Before any of this, grep for tokens
   and keys separately; none were found incidentally, but that was not the test.

## Correction to an earlier version of this file

The first draft claimed "19 occurrences of the employer name" across the mise
config, zsh aliases and three `bin/` scripts. That was wrong twice over: it was
measured against a 13-day-stale `origin/main` that predated the `chrome` topic,
and it counted generic vendor names alongside employer-identifying ones. The
real employer-identifying figure is **9**, and the `chrome` topic — not mise — is
where the exposure concentrates.

## Not to be confused with the usage-figure decision

Local usage figures (task-type split, prompt-size distribution) are deliberately
not committed — see `apps/ollama/files/ollama-profile`. That was handled at the
source: the numbers never entered a commit. This TODO is about strings that are
already in history.

Two pre-existing exceptions remain at tip, both predating that decision and both
low-sensitivity (aggregate token percentiles, no task content):
`apps/ollama/defaults/main.yaml` and `apps/ollama/docs/RESEARCH_BRIEF.md`.

## Priority

Low while private. Blocking if the repo is ever made public again, or shared
outside this machine.
