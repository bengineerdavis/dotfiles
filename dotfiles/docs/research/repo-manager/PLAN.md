# Repo-manager research plan — approved 2026-09-24

This is the full, binding plan for the repo-manager research thread. It was
settled with the author in the 2026-09-24 gita-plan orchestrator session and is
written out in full here so later rounds and fresh sessions never re-decide it
from memory. `HANDOFF.md` is the entry point that links here; it carries no
decisions of its own.

## 1. Mission and outcome paths

Find or compose the **repository-fleet manager** for a two-machine personal
fleet (work macOS, home Linux): a tool that keeps each machine's declared
repositories present, synced safely, and reported honestly — with named
groups, per-machine selection, GitHub discovery, and credentials that never
sit in plaintext.

The outcome is one of two paths, both acceptable; the council's job is to
sharpen the choice, the author's job is to make it:

- **Path A** — compose in Ansible now (built-in modules + explicit task-level
  orchestration, author-approved 2026-09-24), and **contribute the missing
  feature upstream** so the tool eventually absorbs the Ansible work.
- **Path B** — create our **own tool** in a **new repository outside this
  repo** (per the AGENTS.md build ladder; this repo stays provisioning-only).
  If chosen, the immediate next task is a new-repo bootstrap; this directory
  migrates wholesale to it.

## 2. Current state (facts, not intentions)

| Fact | Evidence |
|---|---|
| G1's two research passes exist; no tool adopted | `SOURCES.md` ledger; GITA-RESEARCH.md in this directory |
| Author accepted task-level Ansible as fallback | AUTHOR-ANSWERS.md, 2026-09-24 |
| gita 0.16.8.2 discards child exit codes; repoman skips dirty repos before pull; gitup hides fetch failures | GITA-RESEARCH.md pinned-source sections |
| BK1 research exists and is separate scope | `.worktrees/gita-plan_sub_bk1` (branch `agent/gita-plan_sub_bk1`), TASKS.md BK1 |
| Author-answered questions are durable | `AUTHOR-ANSWERS.md` |
| This branch is based on main at `1e5d099` | `git log` on this branch |

## 3. Requirements R1–R11 (binding; detail and sources in REQUIREMENTS.md)

- **R1** Declarative catalogue; each machine picks its set locally (named
  sets, no committed hostnames; work entries stay local to their machine).
- **R2** Named repo groups (gita-style) usable in automation and interactively.
- **R3** GitHub discovery via gh/API: explicit limits, truncation detection,
  auth/rate-limit failure ⇒ UNKNOWN, never "empty".
- **R4** Safe sync: fetch EVERY repo including dirty ones, then ff-only merge
  on clean, attached, non-diverged repos. Never merge/rebase/reset user work.
- **R5** Per-repo verdicts with reliable exit-code or machine-readable
  reporting; one repo's failure must not abort the run.
- **R6** Persistent per-repo last-fetch / blocked-since state.
- **R7** Adopt existing clones by normalized remote identity, not basename;
  report misplaced clones, never relocate.
- **R8** Credentials injectable from 1Password CLI, Bitwarden CLI, or OS
  keychain; nothing persists plaintext tokens. **Tie-breaker:** prefer
  candidates needing no dedicated GitHub service token.
- **R9** Human-friendly: simple workflow, current docs, active maintenance,
  macOS + Linux, permissive license.
- **R10** Rank partly by **contribution viability** (maintainer responsiveness,
  CONTRIBUTING/governance, license, release cadence) — Path A depends on it.
- **R11** Language tie-breaker, rough-not-rigid: Python/Ruby, then Rust, then
  Go, then other. Never disqualifying — the author uses any ecosystem.

## 4. Directory contract

Everything lives in `dotfiles/docs/research/repo-manager/` on this branch:

| File | Role |
|---|---|
| `HANDOFF.md` | Session entry point; links everything; carries no decisions |
| `PLAN.md` | This file — the full binding plan |
| `REQUIREMENTS.md` | R1–R11 with sources and verification notes; draft until Round 0 finalizes |
| `AUTHOR-ANSWERS.md` | Every author question and answer, dated, with downstream effect |
| `SOURCES.md` | Verified sources + candidate ledger + pending-verification list |
| `ROUNDS.md` | Council round records (critic critiques, recruiter reviews, questions) |
| `GITA-RESEARCH.md` | Durable copy of the G1 comparison (canonical here) |
| `SPEC.md` | Written only after requirements settle; skillet-style normative form |

If Path B wins, the whole directory moves to the new repo. Docs cite paths
relatively so they travel.

## 5. Branch and worktree contract

- **Orchestrator**: works exclusively in `.worktrees/repo-manager` on branch
  `agent/repo-manager`. It creates local tasks (queued main-side per TASKS.md
  § Conventions), fans out work, collects results, merges serially, and is
  the **only** session that pushes.
- **Every writer task gets its own worktree and branch**, prepended by task
  id, with the subtask marker explicit:
  - Main task writer: `.worktrees/repo-manager_t<nn>_<slug>`, branch
    `agent/repo-manager_t<nn>_<slug>`.
  - Subtask writers: `.worktrees/repo-manager_t<nn>_sub_<slug>`, branch
    `agent/repo-manager_t<nn>_sub_<slug>`.
- **One writer per worktree** (docs/WORKTREES.md). Read-only analysts fan out
  freely inside one tree; writers never share a tree.
- **Subtasks produce combinable fragments** — patches plus a findings file —
  that the task's writer (or the orchestrator) merges into the task's final
  outcome. A subtask that cannot be described as a fragment toward its parent
  task's done-condition is a decomposition error; re-cut it.
- **Task agents never push.** Councils and researchers return reports to the
  orchestrator; the orchestrator commits and pushes.
- Sub-worktrees of the older gita-plan thread
  (`.worktrees/gita-plan_sub_g1`, `_sub_bk1`, `_sub_prd`, `_sub_queue`) are
  inputs and history; their reports are committed on their own branches and
  the durable G1 copy lives here. Do not continue gita-plan work there.

## 6. Council design

**Round 0 runs before any sonar spend.** Its job is to sharpen requirements,
seeds, and the combination hypotheses while everything is still cheap to
change. A post-research Round 2 is **optional** — convene it only if the
verified evidence contains surprises the author should see critiqued before
deciding.

**Panel (4 critics, fresh context each):**

| Critic | Challenges |
|---|---|
| Adoption skeptic | Is adopting tool X really cheaper than the fallback over a year? |
| Contribution pragmatist | Will Path A actually land upstream? maintainer signals? |
| Build-cost skeptic | Is "own tool" under-scoped? what does maintenance really cost? |
| Security/secrets reviewer | R8 holes: plaintext anywhere? token sprawl? SSH risks? |

**Recruiter (separate agent, Round 0 only, own budget):** reviews the roster,
then **generates/refines expert personas only — it NEVER contacts anyone.**
It uses public web research (named individuals' public work, docs, issue
threads) to justify what each persona contributes or to sharpen an existing
critic's framing. It may recommend zero additions; that is a normal outcome.
Author approves additions before they join; additions spend from the
recruiter cap.

**Budgets:** critics $5 total across both rounds (hosted models). Recruiter:
separate $5 cap. Sonar deep-research: one run, pre-authorized, expect
single-digit dollars; never retried for thin results — a thin result set is a
finding, not a failure.

**Questioning protocol.** Council members and researchers use the installed
`interaction-questioning` skill (~/.agents/skills/interaction-questioning/).
They question the author, each other, and prior answers relentlessly — but
each round funnels through the orchestrator: agents return questions, the
orchestrator surfaces them to the author in batches, answers land verbatim in
AUTHOR-ANSWERS.md, and later critics may challenge earlier answers rather
than re-ask them.

**Explanation standard.** Default pitch: college sophomore/junior with 5–7
years coding (ELI 21–25 + dev-level). Project-specific terms glossed on first
use; analogies when they earn their place. `explain-calibration` and
`feynman-explanation` are **queued, not installed** — apply the rule from
spec.md § Writing until they exist; say which standard you applied rather
than implying a skill ran.

**Every round produces:** a ROUNDS.md entry (critique, panel changes with
reasons, researcher verdicts, and **open-question scenarios** — anything the
findings could not answer, phrased as investigable questions). Open questions
register in OPEN-QUESTIONS within ROUNDS.md or SOURCES.md; nothing stays in
chat.

**Fusion:** if Round 0 wants wider input, a fusion panel of researchers
(several models answering the same brief, findings fused) is allowed — same
caps, same reporting rules.

## 7. Pipeline with gates

| # | Step | Gate / done-condition |
|---|---|---|
| 1 | Sync main; rebase this branch; queue task lines main-side | `tests/tasks_doc` green; no claim left behind |
| 2 | Recruiter reviews panel; author approves additions | ROUNDS.md entry; additions justified by public sources |
| 3 | Council Round 0 critiques REQUIREMENTS draft, seeds, combinations | ROUNDS.md entry; every question answered in AUTHOR-ANSWERS.md |
| 4 | Finalize REQUIREMENTS.md; one-screen diff of changes to the author | Author ack recorded |
| 5 | Sonar deep-research run (`bin/policy check` on the brief first; one call via `llm -m openrouter/perplexity/sonar-deep-research`; raw output to `/tmp/opencode/`, then copied into SOURCES.md as raw-pending) | Raw answer saved; not retried on thin results |
| 6 | Source verification — every candidate's load-bearing claims checked in code at pinned versions (the GITA-RESEARCH standard) | SOURCES.md rows verified or explicitly UNKNOWN |
| 7 | Combination ledger + Path A/B cost sketch | Which repos combine at feature level; where glue lives; maintainer signals |
| 8 | (Optional) Council Round 2 if evidence holds surprises | ROUNDS.md entry |
| 9 | Author decision recorded with dissent notes; TASKS.md/ROADMAP.md updated; Path B queues new-repo bootstrap | Decision commit; dissent beside it |

## 8. The research brief (run verbatim after step 4)

```
Find open-source tools (CLI first; GUI and Ansible collections second) that manage a
personal fleet of git repositories across multiple machines, combining:

R1 A declarative list of desired repositories, where each machine picks its own set
   locally (named sets selected on the machine; no committed hostnames).
R2 Named groups of repositories (one group per directory type) that work in both
   automation and interactive use — the way gita's groups and group-commands work.
R3 GitHub discovery: enumerate a user/org's repos via gh or API, with explicit limits,
   truncation detection, and treating auth/rate-limit failure as "unknown", never "empty".
R4 Safe sync: fetch EVERY repository including dirty ones, then fast-forward only clean,
   attached, non-diverged repos (git merge --ff-only). Never merge/rebase/reset local work.
R5 Per-repository verdicts (fast-forwarded / skipped-reason / failed) with reliable
   failure reporting: exit codes or machine-readable output; one repo's failure must not
   abort the run.
R6 Persistent per-repo last-fetch / blocked-since state for staleness warnings.
R7 Adopt existing local clones by normalized remote identity (host/owner/repo), not
   basename; report misplaced clones, never auto-relocate.
R8 Credentials injectable from a secrets manager or OS keychain (1Password CLI,
   Bitwarden CLI, secret-tool, gh keyring). The tool or its config must not persist
   plaintext tokens in its own files or require them in dotfiles. Config references
   secret sources; values resolve at run time. Prefer candidates needing NO dedicated
   GitHub service token — the author's normal gh auth or SSH should suffice.
R9 Human-friendly: simple workflow, current documentation, active maintenance,
   cross-platform (macOS + Linux), permissive license.
R10 Rank partly by how practical upstream contribution is — maintainer responsiveness,
   CONTRIBUTING/governance, license, release cadence.
R11 Language tie-breaker (rough, not rigid): prefer Python/Ruby implementations, then
   Rust, then Go, then other. Never disqualifying.

Per candidate ALSO report:
- Test coverage: NONE / LIGHT / SOLID, with links — what the tests actually exercise
  (do they cover dirty-fetch, failure paths, the documented contracts?). Never exclude
  for missing tests; note them.
- Documented vs implicit contracts: what docs promise vs what only code shows (exit
  codes, config semantics, auth storage). Flag undocumented load-bearing behavior.
- Secrets handling: where the tool persists any token it needs.

Combination analysis (required deliverable, not optional): identify which repositories,
combined at the feature level, would create the needed tool with the least glue — e.g.,
gita's groups + repoman's machine manifests + X's dirty-fetch. For each combination
state where the glue would live (Ansible tasks, upstream patch, thin new tool) and the
maintainer signals for contributing.

Outcome framing (assess both):
(A) Compose in Ansible now + contribute the missing feature upstream, so the tool
    eventually absorbs the Ansible work.
(B) Create our own tool (would live in a new repository, not the dotfiles repo).

Method: GitHub topics (multi-repo, repo-manager, meta-repo, workspace), awesome-git
lists, HN/Reddit "managing many git repositories" threads, Ansible Galaxy. Seeds
(verify, don't assume): Zephyr west, grm (git-repo-manager), mu-repo, gitws, polyrepo,
Google repo, myrepos, ghq, ghorg, gita, repoman (klokie), gitup (earwig), vcstool,
mani, batchfetch, GitKraken Workspaces.
EXCLUDE unless materially changed: gita (discards exit codes), repoman (skips dirty
repos before pull), gitup (no failure reporting), ghorg (clean/reset update path).

For every candidate: name, URL, last release/commit, per-R verdict
(MET/PARTIAL/MISSING/UNKNOWN + source link), workflow summary, test-coverage note,
secrets note, disqualifiers. Rank. If nothing meets all nine, name the closest three
and exactly which requirement each misses.
```

## 9. Guardrails

- `bin/policy check` on the brief before the sonar call (house egress rule).
- NEVER contact real people. Recruiter researches public artifacts only.
- No real machine-file data anywhere until the BK2–BK4 restore gate passes
  (gita-plan binding order still in force).
- No secrets, no work identifiers, no employer strings in any committed file.
- Agents never run `chezmoi apply`; only the orchestrator pushes, and only
  its own branches plus main fast-forwards.
- Mutation evidence as `Mutation:` / `Failing-test:` trailers when tests are
  added to support the eventual Path A/B implementation.

## 10. Definition of done (whole thread)

The author's recorded decision (Path A, Path B, or a narrowed hybrid), with
dissent notes; SOURCES.md complete with verification status; ROUNDS.md
complete; TASKS.md/ROADMAP.md updated; and — only if Path B — the new-repo
bootstrap queued outside this repository.
