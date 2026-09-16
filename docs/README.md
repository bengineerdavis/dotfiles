# conventions/

Pluggable conventions for this repository. One file per subject.

`AGENTS.md` stays general: it says how work runs here, and it is meant to be
reusable across projects more or less unchanged. Anything that is true of *a
language* or *a subject* rather than of *this way of working* lives here
instead, so the root holds only the five documents that govern the project.

## What is here

| File | Covers |
|---|---|
| `PYTHON.md` | uv, inline script metadata, pytest, ruff, ty, prek, logging, error handling |
| `PERMISSIONS.md` | what an agent may run, and the threat model it does not address |
| `REFERENCES.md` | external standards followed, their versions, when last checked |
| `TOPICS.md` | index entry for topic conventions, which live in the deployed tree |
| `LAYOUT.md` | the cross-machine directory standard: taxonomy, ownership, migration plan |
| `LANGUAGES.md` | which languages the repo's scripts use, and the reusable per-language tool profile |

## Adding one

Add the file, then add a row above and a bullet in `AGENTS.md` § Conventions.
Nothing else changes. A repository that picks up Go adds `GO.md`; one that
wants its security practice written down adds `SECURITY.md`.

Name language files for the language, in caps, matching the root document style.

## When something earns its own file

Conventions start cheap and get promoted only when they stop fitting. The ladder,
in order — do not skip a rung because the next one looks tidier:

| Rung | Where | Promote when |
|---|---|---|
| 1 | a paragraph in `AGENTS.md` | it is a sentence or two and applies everywhere |
| 2 | ~~nested `AGENTS.md`~~ | **not used here.** The standard supports it — closest-wins precedence — but one project-level `AGENTS.md` is the current choice. Revisit when a subtree genuinely needs its own rules |
| 3 | `conventions/<SUBJECT>.md` | it is long enough to drown the file above it, or it should be swappable per project |
| 4 | a directory | it needs companions — references, evals, fixtures, a license |

Rung 4 is what the ecosystem does. Skills in `anthropics/skills`,
`cursor/plugins` and `obra/superpowers` are all directories: a `SKILL.md` plus
whatever it needs beside it.

**The test for rung 3 is not length, it is variance.** A long convention that
would be identical in every project belongs in `AGENTS.md`, where it composes.
A short one that changes per project belongs here, where it can be swapped
without rewriting the file above it.

## Vendor-neutral: content here, manifests elsewhere

Three repositories that ship agent skills lay out the same way, and it is worth
copying because it was arrived at independently:

- **Content is vendor-neutral**, in plain directories — `skills/`, `agents/`,
  `docs/`.
- **Vendor directories are dot-prefixed and hold only manifests.**
  `obra/superpowers` carries `.claude-plugin`, `.codex-plugin`,
  `.cursor-plugin` and `.devin-plugin`; each contains a `plugin.json` and
  nothing else.

So the rule here: **use the neutral location whenever it also satisfies the
vendor; use the vendor's path only when nothing neutral works.** `CONTRIBUTING.md`
at the repository root is neutral *and* one of GitHub's three discovery
locations, so it goes there. A pull request template has no neutral equivalent,
so it stays in `.github/`.

## Two classes, and why one is only indexed here

A convention either **ships with the artifact** or **governs the repository**.

Topic conventions ship: 53 files reference `docs/TOPICS.md` relative to the
deployed tree, and that file is deployed beside them. The conventions in *this*
directory are chezmoi-ignored and reach no machine, so content the deployed
output must carry cannot live here.

That is why **`dotfiles/docs/TOPICS.md`** holds the topic conventions and there
is no copy here. An index entry pointing at it used to exist and was removed —
two files named `TOPICS.md` was the ambiguity the rename set out to end.

Everything else here governs the repository and is never deployed.

## Why a directory

Three reasons, in order of how much they cost when ignored.

The root is the first thing a person or an agent reads. Five documents that
govern the project — `PRD.md`, `spec.md`, `ROADMAP.md`, `TASKS.md`, `AGENTS.md`
— are legible at a glance. That list stops being legible once it also carries
one file per language.

Conventions and governance are different in kind. A convention is a choice about
tools that could reasonably be made differently in another project. The five root
documents are about the project itself. Mixing them invites treating a tool
preference as though it had the standing of a requirement.

And this directory is the unit the planned copier template ships. A template that
offers a language is a template that drops one file in here; that only stays true
while the directory has exactly one job.

## Not conventions

`CONTRIBUTING.md` is not here either, though it reads like it belongs.
GitHub discovers `CONTRIBUTING.md` only in `.github/`, the root, or `docs/`, so
placing it by tidiness would have cost it the Contributing tab and the sidebar
that appears when someone opens a pull request.


`dotfiles/docs/` explains how parts of this repository work and is descriptive.
`spec.md` constrains. Conventions decide between defensible options — which is
what makes them swappable, and what makes them belong somewhere separate.
