# TOPICS.md

Conventions for Ansible topics — structure, `topic.yml` schema, tiers, lifecycle
tags, dependency resolution, and the CRUD ownership invariant.

## Where they actually live

**`dotfiles/docs/CONVENTIONS.md`**, not here. This file is the entry in the
conventions index; that file is the content.

That split is deliberate and worth understanding before someone "tidies" it:

- **40 topic files link to `docs/CONVENTIONS.md`** as a path relative to the
  deployed tree, and `~/dotfiles/docs/CONVENTIONS.md` exists there beside them.
- **`docs/` is chezmoi-ignored.** It deploys nowhere. Moving the content
  here would leave those 40 files pointing at a document absent from the tree
  they live in.

So there are two classes of convention in this repository, and they are not
interchangeable:

| Class | Lives in | Deploys | Example |
|---|---|---|---|
| Ships with the artifact | `dotfiles/docs/` | yes, beside what cites it | topic conventions |
| Governs the repository | `docs/` | no | Python, permissions, references |

A convention that the deployed output must carry cannot live in a directory the
deployed output never receives.

## What is covered there

| Section | Covers |
|---|---|
| Topic structure | directory layout, the five lifecycle files |
| `topic.yml` schema | required and optional fields |
| Tiers | ordering and what a tier means |
| Lifecycle tags | `provision`, `remove`, and the `[remove, never]` default |
| Dependency resolution | how topics declare and resolve prerequisites |
| Shared dependencies | what belongs to a topic and what does not |
| Script dependency guards | `~/bin` scripts and their preconditions |
| CRUD ownership invariant | anything created must have a teardown |
| Adding a new topic | the scaffolding path |

## One section that does not belong there

`dotfiles/docs/CONVENTIONS.md` also carries **§ Commit granularity** and
**§ Messages**, which are not topic conventions at all. `AGENTS.md` § Commits
cites them, and `TASKS.md` already asks whether they should move. They are a
candidate for a `conventions/COMMITS.md` — a repository convention that does not
ship with the artifact, and so belongs in the other class.

Not moved yet, because 53 files cite that document and the citations should be
rewritten once rather than twice.
