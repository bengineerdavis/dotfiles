# Domain docs

How the engineering skills consume this repo's domain documentation.

## Before exploring, read these

- `docs/GLOSSARY.md` — project terminology. Use its vocabulary; do not drift to
  synonyms it avoids.
- `docs/adr/` — decisions that touch the area you are about to change. The
  directory does not exist yet; `/domain-modeling` creates it lazily.

`dotfiles/docs/` is an older copy of the convention docs. The glossary and ADRs
of record are the root `docs/` paths above.

## Layout

Single-context: one glossary, one ADR directory. There is no `GLOSSARY-MAP.md`
and no per-package context.

## ADRs stay here, not in the queue

`backlog-py` has its own decision store (`backlog/decisions/` via
`backlog-py decision create`). Do not use it. Architecture decisions belong in
`docs/adr/`, next to the existing decision records, so there is one place to
read. The queue tracks work; it does not store architecture decisions.

## If a concept is missing

Note it for `/domain-modeling` rather than inventing a term in a ticket or test
name. If output contradicts an ADR, surface it explicitly instead of overriding
silently.
