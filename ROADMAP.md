# ROADMAP.md

What is likely coming and roughly in what order. Not a queue, and not a
commitment.

The four other documents divide as follows. `PRD.md` says what the project is
for. `spec.md` says what must remain true. `TASKS.md` says what is scheduled
now. `AGENTS.md` says how to work here. This file holds what is probably next
and is not scheduled yet — the things that would otherwise sit at the top of the
queue blocking it, or vanish because nothing was tracking them.

Not to be confused with `dotfiles/docs/ROADMAP-topic-cli.md`, which is a design
document for one tool. This file is project-level.

## How to use this

**When `TASKS.md` § Open is empty, the work is not finished.** Take an item from
here and interview the author about it — relentlessly, one branch of the design
tree at a time, resolving dependencies as they surface. That is the same pass
that produced `PRD.md`, and it is what turns a roadmap line into work.

Then update `PRD.md` with whatever requirements the interview settles, and
`TASKS.md` with the work items it produces. Delete the roadmap line only when the
thing exists.

**The test is the done-condition.** If you can write "done when X" in one
sentence, it is a task and belongs in `TASKS.md` § Open. If you cannot, it
belongs here. Size and urgency do not enter into it — a small vague thing is a
roadmap item, and a large precise one is a task.

Items here have no owner, no date and no done-condition. That is exactly what
separates them from `TASKS.md` § Open, whose lines are deleted on completion.
Anything here that acquires a done-condition should be promoted rather than left.

## Scheduled — pointers only

These are already broken into work items in `TASKS.md`. Listed so this file
reads as a complete picture, not to duplicate them.

- **The `topic` CLI** (A1–A7). Designed in `dotfiles/docs/ROADMAP-topic-cli.md`.
- **Factoring the AI/LLM tooling out** (B1–B8). Required by `PRD.md`.
- **The trust ladder and its ledger.**
- **Two copier templates** — a general repository template, and one for the
  chezmoi-Ansible topic format.

## Not yet scheduled

### Topics as portable, installable modules

`PRD.md` states the requirement: a topic should be installable on its own, so a
third party can borrow one piece of this configuration without adopting the whole
repository. What is undecided is the boundary — what a topic may depend on, how
it declares that, and what happens to shared state like the zsh lifecycle files
and the manifest schema.

Deliberately deferred. The copier topic template can be built against the format
as it stands today; the module boundary only has to be settled before anyone
outside this machine relies on it.

### A local model that reacts to errors and proposes fixes

Same shape as the agents that turn production errors into pull requests, but
local and personal. The trigger is a failure rather than a prompt, which is what
makes it different from everything else here.

Local by requirement rather than preference: error text and stack traces can
carry work content, so this is governed by the policy layers and cannot use a
remote model under the current rules.

Open before it can be scheduled — what it watches (test failures, shell exit
codes, a log), whether it may open a pull request or only draft a patch, and how
it avoids proposing fixes for failures that are symptoms of work still in flight.

### A queryable knowledge base of the repository

Readable by a human directly, not only feedable to a model. It is the artifact
that survives context compaction, model swaps and long gaps — session memory
does not.

`spec.md` and `PRD.md` are the beginning of this. The gap is everything true
about the system that is neither a requirement nor a constraint.
