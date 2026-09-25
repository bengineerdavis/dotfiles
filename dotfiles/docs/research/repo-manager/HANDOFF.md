# HANDOFF — repo-manager research orchestrator

**You are the repo-manager orchestrator.** If the author gave you this file,
you take over this thread using this branch and worktree **exclusively**:
you create local tasks, and — other than council rounds, which report back —
you push each task to a **fresh agent session** (own worktree, own branch per
§ Contract below), collect results, merge serially, and report to the author.
You are the only session that pushes. This file carries no decisions; it
links them. Read in the order given in [README.md](README.md).

## Session context

- Authored 2026-09-24 by the gita-plan orchestrator session (OpenCode,
  z-ai/glm-5.3-flash) at the author's request to compact and hand off.
- This branch is based on **main at `1e5d099`** (post fast-forward of 87
  commits from other sessions — restart-stale role, skill-trust buckets,
  opencode tiers). **Rebase/merge onto current main before starting**; main
  is active.
- The author was told: "beware a lot of changes are coming from main."

## Read first (in order)

1. [PLAN.md](PLAN.md) — the full binding plan; nothing here re-decides it
2. [REQUIREMENTS.md](REQUIREMENTS.md) — R1–R11 draft (Round 0 sharpens)
3. [AUTHOR-ANSWERS.md](AUTHOR-ANSWERS.md) — every answer to date; challenge,
   don't re-ask
4. [SOURCES.md](SOURCES.md) — verified candidate ledger; verification rules
5. [GITA-RESEARCH.md](GITA-RESEARCH.md) — the G1 comparison (input baseline)
6. [ROUNDS.md](ROUNDS.md) — where council rounds are recorded (empty)

External inputs (committed on their own branches):

- Gita+backup approved plan: `.worktrees/gita-plan/HANDOFF.md`
  (branch `agent/gita-plan`, `46042e9`) — 41 settled decisions, binding order
- G1 research original: branch `agent/gita-plan_sub_g1` (`ebb82e9`)
- BK1 research: branch `agent/gita-plan_sub_bk1` (`5b2880d`) — **PENDING**
  spot verification before the BK1 decision (separate thread, gita-plan)

## Task queue state (main)

- Queued: "Repo-manager research: find or compose the repository-fleet
  manager…" in TASKS.md § Now (commit `ee1ac75` on main). **Your first
  action**: sync main, rebase this branch, re-read TASKS.md (it moves fast),
  claim the line, and delete your claim when you stop.
- Superseded: the tool-choice half of G1 (TASKS.md § Now) is consumed by this
  thread; resolve G1 when the decision lands.
- BK1 (backup host/install/keys) is **separate scope** — gita-plan thread,
  awaiting author decisions. Do not fold it into this thread; cite it.

## Contract (from PLAN.md § 5 — binding)

- Orchestrator: `.worktrees/repo-manager`, branch `agent/repo-manager`.
  TASKS.md updates land main-side per TASKS.md § Conventions; work happens
  here.
- Every writer task: own worktree + branch, task-id prepended, subtask
  marker explicit:
  - `.worktrees/repo-manager_t<nn>_<slug>` / `agent/repo-manager_t<nn>_<slug>`
  - `.worktrees/repo-manager_t<nn>_sub_<slug>` / `agent/repo-manager_t<nn>_sub_<slug>`
- One writer per worktree (docs/WORKTREES.md). Readers fan out freely.
- Subtask outputs are combinable fragments (patches + findings file) toward
  the parent task's done-condition; a non-fragment subtask is re-cut.
- Task agents never push; they return patches + findings to you. You merge
  serially (inert → behaviour → activating, suite after each), verify with
  `merge-base --is-ancestor` before any worktree/branch reaping.
- Fresh agent per task; no shared context between task agents. Sub-agents
  must NOT push (AGENTS.md gotchas).

## Council (from PLAN.md § 6 — binding)

- **Round 0 before any sonar spend.** 4 critics (adoption skeptic,
  contribution pragmatist, build-cost skeptic, security/secrets), fresh
  context, cross-questioning. $5 cap total (hosted models).
- **Recruiter, Round 0 only, separate $5 cap**: reviews the roster, then
  generates/refines expert personas ONLY. It NEVER contacts anyone — public
  web research (named individuals' public work, docs, issue threads)
  justifies each persona or sharpens an existing critic's framing. Zero
  additions is a normal outcome. Author approves additions before they join.
- Round 2 is optional — convene only if verified evidence holds surprises.
- Fusion panel of researchers allowed for wider input (same caps).
- Every round: ROUNDS.md entry with open-question scenarios for anything the
  findings could not answer. Later rounds may recommend additional research
  questions.
- Questioning uses the installed `interaction-questioning` skill; question
  the author, each other, and prior answers relentlessly — funneled through
  you to the author, answers recorded verbatim in AUTHOR-ANSWERS.md.

## Communication standards (binding)

- **Explanation default: ELI 21–25 + dev-level** — college sophomore/junior
  with 5–7 years coding. Project terms glossed on first use; analogies when
  they earn their place.
- `explain-calibration` and `feynman-explanation` are **queued, not
  installed** — apply spec.md § Writing's rule and say so; don't imply a
  skill ran.
- Installed skills: `interaction-questioning`, `review-best-practices`,
  `commit-hygiene`, `pii-redaction`, `skillet-authoring`.

## Pipeline gates (from PLAN.md § 7)

Recruiter → Round 0 → finalize REQUIREMENTS (one-screen diff to author) →
policy check → sonar run (one, verbatim brief in PLAN.md § 8) → source
verification (pinned versions) → combination ledger + Path A/B sketch →
(optional Round 2) → author decision with dissent notes → TASKS.md/ROADMAP
updates; Path B queues a new-repo bootstrap **outside this repo**.

## Commit map for this handoff

| SHA | Where | What |
|---|---|---|
| `ee1ac75` | main | queue repo-manager thread + claim |
| `28dc016` | this branch | PLAN.md (full plan) |
| `f39e3b3` | this branch | AUTHOR-ANSWERS.md |
| `f85c349` | this branch | SOURCES.md |
| `9ef9ce6` | this branch | REQUIREMENTS.md draft |
| `163527d` | this branch | README + ROUNDS scaffold |
| `e9ba530` | this branch | GITA-RESEARCH.md canonical copy |
| `ebb82e9` | agent/gita-plan_sub_g1 | G1 research (provenance) |
| `5b2880d` | agent/gita-plan_sub_bk1 | BK1 research (provenance) |

## Compaction note

The originating session was compacted around this handoff: the user runs
`/compact` when starting the new session. This file plus the committed docs
are the durable memory — if the compacted transcript and this file disagree,
**this directory wins** and the discrepancy is reported to the author.

## First actions checklist

1. Sync main; rebase this branch; read TASKS.md fresh (87+ commits landed
   recently; more are coming — claim your line, work path-scoped).
2. Read PLAN.md → REQUIREMENTS.md → AUTHOR-ANSWERS.md → SOURCES.md.
3. Run the recruiter (public research, personas only, never contact anyone).
4. Convene Council Round 0 on the requirements draft + seeds + combination
   hypotheses. Funnel questions to the author; record answers.
5. One-screen requirements diff to the author; on ack, run the sonar brief
   verbatim (policy check first).
6. Verify everything at source level; build the ledger, combinations, and
   Path A/B sketch; decide Round 2; take the decision to the author.

Guardrails: `bin/policy check` before egress; never contact people; no real
machine-file data (BK2–BK4 gate still binding); no secrets or employer
strings in commits; agents never run `chezmoi apply`.
