# Domain docs

How the engineering skills consume this repo's domain documentation.

## Before exploring, read these

- `docs/GLOSSARY.md` — project terminology. Use its vocabulary; do not drift to
  synonyms it avoids.
- `backlog/decisions/` — decisions that touch the area you are about to change.

`dotfiles/docs/` is an older copy of the convention docs. The glossary of
record is the root `docs/GLOSSARY.md`.

## Layout

Single-context: one glossary, one decision store. There is no `GLOSSARY-MAP.md`
and no per-package context.

## ADRs use the queue's decision store

Create an architecture decision with:

```bash
backlog-py decision create "<title>" --status accepted
```

That writes `backlog/decisions/decision-N - Title.md` with Context / Decision /
Consequences sections. Fill those sections; do not hand-write a different
format.

This follows the tool's convention, so tasks and decisions live in one store
and `backlog/` stays the single source of truth. It also means decisions are
CLI-only for now: `backlog-py-mcp` exposes no decision tools.

Upstream does not support pointing the decision store at `docs/adr`. The
evidence and the drafted upstream work are in
`docs/BACKLOG-UPSTREAM-CONFIG.md`. Do not create `docs/adr/` while that is true.

## If a concept is missing

Note it for `/domain-modeling` rather than inventing a term in a ticket or test
name. If output contradicts an ADR, surface it explicitly instead of overriding
silently.
