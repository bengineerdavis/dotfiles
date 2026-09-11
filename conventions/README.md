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

## Adding one

Add the file, then add a row above and a bullet in `AGENTS.md` § Conventions.
Nothing else changes. A repository that picks up Go adds `GO.md`; one that
wants its security practice written down adds `SECURITY.md`.

Name language files for the language, in caps, matching the root document style.

## Two classes, and why one is only indexed here

A convention either **ships with the artifact** or **governs the repository**.

Topic conventions ship: 40 topic files link to `docs/CONVENTIONS.md` relative to
the deployed tree, and that file is deployed beside them. `conventions/` is
chezmoi-ignored and reaches no machine, so content the deployed output must
carry cannot live here. `TOPICS.md` is therefore an index entry pointing at
`dotfiles/docs/CONVENTIONS.md`, not a copy of it.

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

`.github/CONTRIBUTING.md` is not here either, though it reads like it belongs.
GitHub discovers `CONTRIBUTING.md` only in `.github/`, the root, or `docs/`, so
placing it by tidiness would have cost it the Contributing tab and the sidebar
that appears when someone opens a pull request.


`dotfiles/docs/` explains how parts of this repository work and is descriptive.
`spec.md` constrains. Conventions decide between defensible options — which is
what makes them swappable, and what makes them belong somewhere separate.
