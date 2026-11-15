# Agentic repositories: the fleet upstream work has to serve

Surveyed 2026-11-16. This inventory exists because decision-5 rests on a
count — lessons surface across many repos, not one — and a count asserted from
memory is a guess. It records which personal repositories carry agent
instructions or an active queue, so the scope of upstream contribution
(DOT-326, decision-5) is measured rather than estimated.

Scope: `~/code/{personal,templates,try,captures,archive}` plus the chezmoi
source at `~/.local/share/chezmoi`. Work repositories are excluded by the
machine-local boundary in `docs/LAYOUT.md` and never named here. Forks are
excluded: they carry upstream's instructions, not ours.

Evidence counted as agentic: an `AGENTS.md` or `CLAUDE.md`, a `backlog/`
queue, a `.opencode/` directory, or an `agents.toml` declaring skills.

## The fleet

| Repository | Evidence | Tasks | `AGENTS.md` | Last commit |
| --- | --- | ---: | ---: | --- |
| `~/.local/share/chezmoi` | AGENTS, backlog | 309 | 1063 | 2026-11-15 |
| `templates/agentic-project-template` | AGENTS, backlog, agents.toml | 49 | 37 | 2026-11-11 |
| `personal/ai-prompt-library` | AGENTS, backlog | 27 | 154 | 2026-11-15 |
| `templates/copier-cat` | AGENTS, backlog | 27 | 48 | 2026-11-15 |
| `templates/copier-template-copier-template` | AGENTS, CLAUDE, backlog, .opencode, agents.toml | 14 | 28 | 2026-11-09 |
| `personal/flagship` | AGENTS, backlog, .opencode, agents.toml | 9 | 84 | 2026-11-13 |
| `templates/copier-testkit` | AGENTS, backlog, .opencode, agents.toml | 2 | 85 | 2026-11-14 |
| `personal/roborev` | AGENTS, CLAUDE | 0 | 347 | 2026-10-27 |
| `templates/copier-mise-sandbox` | AGENTS | 0 | 28 | 2026-09-14 |
| `try/worktrunk-isolation-trial` | AGENTS | 0 | 800 | 2026-09-22 |

Ten repositories, seven with live queues, 437 open tasks. A transient
check-out (`personal/ai-prompt-library-pr2-final-check`) is omitted; it
duplicates `ai-prompt-library`.

## What the survey shows

**The count in decision-5 holds.** Ten repositories carry agent instructions,
and the problem classes this session found — commit scoping under a shared
index, instructions that drift from the tool they describe, no retirement path
for a rule — can appear in any of them. That is the cost argument for a
service over a per-repo capability: a fix written once against ten repos beats
the same fix written ten times.

**`AGENTS.md` size varies by two orders of magnitude**, from 28 lines to
1,063. The large files are not the mature ones: `worktrunk-isolation-trial` is
a trial with 800 lines and no queue, and this repo's 1,063 lines are the
retirement-path problem DOT-357 exists to fix. Size tracks how much evidence
was pasted in, not how settled the practice is.

**The templates are themselves agentic.** Four of the five template repos run
their own queues, so a contribution upstream lands in a repo with its own
conventions and its own agents — which is why CCC-21 requires reading the
target's contributor docs before choosing the artifact, rather than assuming a
house format travels.

**Experience is unevenly distributed, and that is the point.** This repo has
the most agentic history and the most proven conventions, so its findings
carry evidentiary weight. Per decision-5 and CCC-23 that is influence, not
authority: the receiving template's scope decides whether a lesson fits.

## Keeping it current

This is a snapshot and will drift. Re-run the survey when the count matters —
before a DOT-326 sweep, or when deciding whether a mechanism is worth
centralising. The commands are in this file's history; the check is which
directories carry the evidence listed above.

Related: `docs/LAYOUT.md` (where repositories live), `docs/AGENT-ARTIFACTS.md`
(what installs skills into them), `backlog/decisions/decision-5` (who owns
refactoring lessons upstream).
