# Author answers — repo-manager thread

Every decision-shaping question asked of the author in this thread, with the
answer and its downstream effect. Answers are verbatim intent, lightly
normalized for grammar. New entries append at the end; later critics may
challenge earlier answers but never silently re-ask them.

## 2026-09-23 (gita-plan orchestrator session)

| # | Question | Answer | Effect |
|---|---|---|---|
| 1 | For G0's transcription of the approved plan, review-and-commit or show each diff? | "You review, then commit" | Orchestrator commits faithful transcription on main, one task per commit; new implementation decisions still return to the author |
| 2 | What monthly ceiling when comparing personal remote-backup hosting? | "Recommend on merits" | BK1 compares verified costs without a budget cap; no purchase authorized |
| 3 | Where should custom repo-reconciliation logic live? | "Is there a better alternative tool that already has this problem solved? It needs to be human-friendly… simple workflow, interface, well-defined up-to-date documents. I really do not want to maintain custom logic around this — if there's no tool that works, then we need to figure out how to solve this with ansible and their modules or third party roles or collections." | G1 widened from "gita vs git" to "find a maintainable existing manager"; bespoke engine off the table without explicit exception; seeded R9 |

## 2026-09-24

| # | Question | Answer | Effect |
|---|---|---|---|
| 4 | "Use this model instead" — which model ID for delegated agents? | Never answered; superseded | Logged unresolved; later superseded by the council spec (hosted models, $5 cap). Do not re-ask |
| 5 | Does a small Ansible task sequence (built-in modules + Git commands) count as an acceptable fallback if no maintained third-party tool meets the full workflow? | "yes, but remind me the full work flow and a link to leadimmg candidates for third party tools i can review" | Task-level Ansible orchestration accepted as fallback; the complete workflow and candidate links must be presented for the final tool split |
| 6 | How should the deep search be run? | "Run sonar-deep-research here" | One pre-authorized sonar run via `llm -m openrouter/perplexity/sonar-deep-research`; policy check first |
| 7 | Where should the requirements directory live? | Option 1 "but put under a docs/research/repo-manager directory for now, since this isn't an established workflow yet" | `dotfiles/docs/research/repo-manager/` in this repo, provisional; migrates wholesale if Path B wins |
| 8 | Weight candidates by upstream-contribution viability, or fit only? | "Contribution-friendly" | R10: contribution viability is a ranking criterion |
| 9 | Which secrets sources must day-one injection support? | "All three managers" (1Password CLI work, Bitwarden CLI personal, OS keychain runtime) "and I would prefer to do this without needing things like github service tokens; if I do need them, that's fine, but call it one of the tie-breakers we can use for top vs secondary candidates" | R8 binding; no-service-token preference is a top-vs-secondary tie-breaker, not a disqualifier |
| 10 | Council composition and cap? | "4 critics, $5 cap" | Four hosted critics, $5 total across rounds |
| 11 | (adjust round) Council earlier, language tie-breaker | "Bringing in the council sooner… I don't want to get hung up on the language used, but a medium tie-breaker… python/ruby, then rust, then go, in a rough-but-not-rigid order. Python and bash are my main fluencies" | Council Round 0 before research spend; R11 recorded |
| 12 | "I will use tools from any lang ecosystem: python, rust, go, ruby, even clang" | (statement, not answer) | R11 never disqualifies; it only orders otherwise-equal candidates |
| 13 | Council round structure? | "Early only, round 2 optional" | Round 0 mandatory pre-spend; Round 2 convenes only if evidence holds surprises |
| 14 | (handoff instructions, cutoff message) Own worktree+branch; detailed linked handoff including compaction; push; new agent works the branch exclusively as orchestrator creating local tasks, pushing tasks to fresh agent sessions, collecting results; each writer gets own worktree/branch with task-id prefix and subtask marker; subtasks combinable into the task outcome; fusion council of researchers allowed; later council rounds may recommend additional research questions; use the local questioning skills, question relentlessly (author, each other); researchers add open-question scenarios for anything findings couldn't answer; use plain-english/feynman explaining skills to match the author's level | (full instruction) | Sections 5–7 of PLAN.md; ROUNDS.md open-question rule; comms standard below |
| 15 | What explanation level for you and as the default instruction? | "I usually go for something between ages 21-25 flavored with option 3. Like a college sophomore or jr that's coded for at least 5-7 years" | ELI 21–25 + dev-level is the binding default for all author-facing explanations |
| 16 | Progressive disclosure for the plan | "make sure the plan is written out in full and referenced by the handoff — easier for me to keep that a separate and part of progressive disclosure" | PLAN.md carries the full plan; HANDOFF.md only links |
| 17 | Recruiter timing | "Round 0 only" | Recruiter runs once, before Round 0 convenes |
| 18 | What counts as an 'expert' the recruiter brings in? | "do NOT actually contact people — the recruiter role help us generate roles. That is the only purpose… NEVER actually contact people; but, utilize web searches to find individuals and content that help to flesh out and justify their contributions as experts to the meeting, or give us a more refined personality for existing roles" | Recruiter generates/refines personas grounded in public research; contact strictly forbidden |
| 19 | Recruiter budget? | "Separate small budget" → then "$5 cap" | Recruiter cap $5, separate from the critics' $5 |
| 20 | Execute the handoff? | "Approved — execute" (+ "beware a lot of changes are coming from main") | This branch and HANDOFF exist; main was fast-forwarded 87 commits first; next session syncs main before starting |

## 2026-09-29 (session-start blockers)

The three setup questions (git reconciliation, model access, process rule) were
asked and the author dismissed the prompt, then directed: "update handoff after
resolving and pushing resolution to blockers", "Be aware a lot of changes have
come to main", and "Keep all three. Plan approved." The rows below record how
each blocker resolved on that directive — as adopted defaults, not verbatim
answers.

| # | Question | Resolution | Effect |
|---|---|---|---|
| 21 | How to reconcile main before rebasing the branch? | Main had already fast-forwarded to `origin/main@61c50ff` (65 new commits since the branch's original base). `agent/repo-manager` rebased onto it; none of the 65 touched `dotfiles/docs/research/repo-manager/`. | Branch is current; nothing to reconcile main-side beyond the rebase. |
| 22 | Which process rule governs this thread's TASKS.md edits — the handoff's "main-side" wording or current main's branched rule? | Current main's rule (everything branched, append-only) governs. The handoff's wording predates it. | This thread's TASKS.md edits land on `agent/repo-manager` and merge promptly. |
| 23 | Sonar deep-research and the hosted council need OpenRouter, but only `claude` + `openai` keys are configured. Provide a key or block? | No key provided; block. Recorded, not treated as resolved-by-default. | Sonar + hosted council steps carry `[blocked: OpenRouter key]` until a key is supplied. |
| 24 | Authorize the paid stages (recruiter, Round 0, one sonar run) once the key is set? | "Let's sync the task lists for now; then ack (I also authorize another \$25 in spend reserve if we need it for any paid stages, but ask first if you need more for the research project)." | Recruiter (\$5) + Round 0 critics (\$5) + one sonar run authorized, plus a \$25 reserve above the stage caps; exceeding it requires asking first. The OpenRouter key is set and smoke-tested, clearing #23's block. |

## 2026-09-29 (Round 0 council questions)

Answers to the 11 batched decisions in ROUNDS.md § Round 0. Deferrals are
tracked below so Round 2 (or the requirements-finalize diff) re-raises them
rather than re-asking cold.

| # | Question | Answer (verbatim, lightly normalized) | Effect |
|---|---|---|---|
| 25 | Null baseline: current manual repo-sync cost? | "this a guess, but I end up having to resolve repo syncs via opencode and chezmoi directly at least once a day and for almost every AI agent session I run. Some of this is expected and desired. But let's call it at least 15–30 mins a day, maybe as much as 1+ hrs." | Baseline ≈15–30 min/day, up to 1+ hrs; frames whether any automation clears its own cost. |
| 26 | Define a "good run" independent of exit 0? | "defer with recommendations, along with a deep inspection of how the architecture works right now for the topic-based advanced dotfile format (yes the architecture is messy and needs to be cleaned up, too)" | Deferred; gated on an architecture inspection of the current topic dotfile format — a distinct task. |
| 27 | "No local pick" → block install or only actions? | "defer and then review again with the council" | Deferred; re-raised with the council (Round 2). |
| 28 | Which source files required vs optional? | "yes required. defer for holding tokens, but no probably not — secrets managers instead" | Files required = yes; token-holding deferred, leaning "no — use secrets managers". |
| 29 | Timers: `off`-stays-off, clone-new, fork/template, keyring? | "defer" | Deferred. |
| 30 | "Empty required source" for the backup guard? | "defer — I don't remember or know what that means." | Deferred; explanation owed to author (see orchestrator elaboration). |
| 31 | Permission allocation (G2/BK2 read denials)? | "defer and elaborate to help me remember this." | Deferred; explanation owed to author (see orchestrator elaboration). |
| 32 | R7 remote-normalization algorithm? | "defer, but preference for ssh and host aliases" | Deferred; preference recorded: SSH + host aliases. |
| 33 | R10 contribution-viability weight vs contract-fit? | "defer" | Deferred. |
| 34 | R6 state store URL/token-free? | "agreed" | Agreed: R6 state carries no URLs/userinfo. |
| 35 | Accept macOS/Linux keychain asymmetry? | "defer, but yes likely we should accept" | Deferred; likely accept as a documented constraint. |

## 2026-09-29 (post-sonar candidate notes)

Author's standing observations after the sonar round (recorded, not questions):

- **mu-repo** — "while I like mu-repo as an option, it looks like it's not
  really an active project or, to put it kindly, barely in 'maintenance mode',
  risking becoming abandonware." Effect: deprioritize; verify maintenance status
  for the record, revisit only if a later round needs it.
- **repoman (basti1302)** — "the repoman found is plain JavaScript and also
  doesn't seem that well maintained, which are a turnoff." Effect: dropped as a
  candidate (wrong language per R11 + maintenance signal).
- **Multi-tool composition** — "I see us having to learn and use a lot more tools
  — using more than one tool to cover one job looks concerning, but not off the
  table in terms of my options." Effect: a multi-tool Path A composition carries
  a real integration/learning cost that weighs against it; it is not disqualified.

## 2026-09-29 (naming decided)

The tool is named **`redge`** (the binary / command), with **`redge-cli`** as the
full namespace for package registries.

- Author: "i've decided it has to be redge. redge-cli will be the full tool
  namespace for package registries and i'll want to grab both the crate and pypi
  spaces asap." `redge-git` was raised and rejected ("don't like that name as much").
- Verified free (2026-09-29): `redge-cli` on PyPI and on crates.io. Bare `redge` is
  taken on PyPI by an unrelated denoising-diffusion research package — the `-cli`
  compound is the disambiguation that keeps the `redge` binary.
- Effect: the naming thread is closed. Reserve `redge-cli` on PyPI + crates.io as
  an immediate author action; design/architecture/SPEC/bootstrap proceed as `redge`.

## Standing context the answers imply

- Commit authority granted to the orchestrator covers faithful
  transcription/decision-recording on main; anything that changes scope or
  introduces a new implementation decision returns to the author.
- The author's fluencies are Python and bash; R11 exists so glue contributions
  (Path A) are likelier to land in a language they can maintain.
- "I don't want to get hung up on the language" — R11 is a medium tie-breaker;
  language choice never blocks adoption of a better tool.
