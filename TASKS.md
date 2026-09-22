# TASKS.md

Shared work queue for this repo. Agent sessions keep their own in-memory task
lists, which fragment the moment more than one is running — this file is the
durable version. Read it at the start of a session; update it before you finish.

Keep it short. This tracks *open* work and cross-session hazards, not history —
`git log` already has history, and duplicating it here just creates drift.

## Conventions

- **Editing this file: bound deletions by section, not by item.** Removing a
  task by slicing from its start to the next line beginning `- ` has destroyed a
  whole section three times, because the task being removed was the last in its
  section and the next such line was in the following one. Bound by the next
  item **or** the next `## ` heading, whichever comes first, and check
  `tests/tasks_doc` before committing — it caught the third one and was ignored.
- **Three tiers, and the test between them.** If you can write "done when X" in
  one sentence it is a task; if you cannot, it is an idea and belongs in
  `ROADMAP.md`. Among tasks, **Now** is the handful actually next and **Planned**
  is everything else. Promote from Planned into Now rather than working straight
  out of Planned — if everything is Now, nothing is.
- **Task or roadmap item?** If you can write "done when X" in one sentence, it
  is a task and belongs here. If you cannot, it is direction and belongs in
  `ROADMAP.md`. Nothing else distinguishes them — not size, not importance, not
  how soon. An item here is finished when it moves to `TASKS-RESOLVED.md` — a stopgap until the process refactor lands; a roadmap item is never finished.
- One line per item, imperative, with enough context to pick it up cold.
- **Captures commit immediately.** Anything an agent queues here or captures
  for later gets its own commit, straight to main, the moment it is written —
  so it exits the conversation and cannot be lost to session context, even
  when nothing else will be done with it. Kept separate from in-flight work.
  **One task, one commit** — queueing two tasks is two commits, and amending a
  queued task is another, never a rewrite of the commit that added it. When
  creating a single task genuinely needs several commits (the task plus the
  convention doc it depends on, say), put them on a branch rather than
  interleaving them with in-flight work on main.
- Mark **[blocked: reason]** rather than deleting — a blocked item that vanishes
  gets rediscovered from scratch.
- Mark **[inferred]** for anything reconstructed from repo evidence rather than
  stated by the author. Those may be wrong; correct them rather than trusting them.
- When you claim an item, say so in the line. When you finish it, move the
  line to `TASKS-RESOLVED.md` with its outcome and evidence — a stopgap until
  the process refactor lands, after which this rule follows the design.
  Either way the commit is the record.
- **Work done by an agent or subagent gets its task written first.** Before the
  agent starts, the line says what it is doing and what done means. Fanning work
  out across several agents is several tasks, not one — an agent whose unit of
  work was never defined returns something plausible that nothing can check.
- Assigned work names its owner: `[agent: <who>]` for a subagent or named
  session, `[me]` for the author. An unassigned task is a backlog item, not
  work in flight.

## Claimed

Sessions run in parallel and cannot see each other. Add a line when you start on
anything that touches a file in **Cross-session hazards** below, or that will hold
a global resource (ollama, `chezmoi apply`) for more than a minute. Delete your
line when you stop — including when you stop without finishing.

Append; never reflow or reorder this section. Two sessions editing the same lines
is exactly the collision it exists to prevent.

Format: `- <UTC start> — <what> — <files or resource>`

A stale claim is not a lock. If a line looks abandoned, check `git log -3` on the
file and whether a process is still running before assuming it is safe — then
delete the line and say so in your commit.

## Where things stand — 2026-09-22 (the session handoff)

A handoff snapshot. Delete and rewrite it rather than appending; a log of
snapshots is worse than none.

**Recommended model for the next session.** `spec.md` § Models forbids
justifying a model by recall or leaderboard, and the screen has not been run —
so this is a task-shape constraint, not a quality ranking. The next session
needs very long context (this handoff + TASKS.md ~1,900 lines + spec.md 543 +
AGENTS.md 974 + PRD.md), multi-constraint instruction-following, and a
willingness to say "unverified." House policy: local Ollama first, then
Anthropic or Google via llm-openrouter; no hosted GPT/Grok as a default. Primary:
Anthropic Claude Opus-class (longest sustained multi-constraint reasoning);
cross-check: Google Gemini Pro-class (independent lineage, long context). The 7
local tags (all 9–10 months old, unmeasured for this task class) are not
recommended. Get exact ids from the live catalogue — format is
`openrouter/anthropic/...`; vendor-native ids resolve to nothing.

**Objective.** Build a multi-agent coordination layer: an orchestrator decomposes
tasks, fans out parallel sub-agents that write in isolation, consolidates their
work without corrupting git history, and escalates to the human only when
necessary. Bootstrap here, extract to a copier template later. Order changed this
session: multiagent work is #1; governance-docs consolidation is #2.

**Phase 0 (cleanup) — already complete, verified at session start.** No
`agent/exp_s1*` branches, no worktrees (`git worktree list` shows only `main`),
and the `.worktrees/` line is gone from `.git/info/exclude`. An empty
`.worktrees/` directory remains on disk; `rmdir .worktrees` is safe.

**Commits landed** — all verified ancestors of `main`, each via
`git commit -o TASKS.md` with `tests/tasks_doc` green before it:

| SHA      | What |
|---|---|
| 155c51a  | queue the multi-agent coordination layer as #1 |
| 590f1b4  | queue the prek switch, stash question settled |
| 574fb5f  | record verified sandbox isolation findings |
| fc180fa  | resolve swarm + commit-granularity into sub-items (a)–(g) |

Not pushed. `main` has since advanced seven commits (the deb-get/bitwarden/
1password work from another session) — outside this handoff's scope. Three files
remain modified by another session (`dotfiles/executable_install.sh`,
`dotfiles/executable_update.sh`, `executable_update.sh`) — do not stage them.

**Verified facts** (evidence, not recall):

| Fact | Evidence |
|---|---|
| bwrap available, unprivileged userns works | `/usr/bin/bwrap`; `user.max_user_namespaces=115796`; both restriction knobs absent |
| podman/docker/systemd-run/unshare/qemu present; firejail/lima/colima absent | `command -v` |
| overlay module present | `modinfo -F name overlay` |
| chezmoi ignores dot-prefixed source dirs | probe: `.probe_wt/dot_probefile` appeared in neither chezmoi managed nor status |
| prek uses patch-to-cache, never git stash | `keeper.rs`: write-tree + diff-index --binary → `~/.cache/prek/.../patches/{millis}-{pid}.patch`, dir 0700, git apply on drop, ctrl-C handler. Zero git stash in git.rs/keeper.rs. Verified against master, not installed 0.5.3 |
| pre-commit also patch-to-cache | observed live 4× |
| `.git/worktrees/` keys on basename only | 3 worktrees → admin dirs exp_s1, exp_s1_sub_a, exp_s1_sub_b |
| single-branch lock is real | `fatal: 'agent/exp_s1_sub_a' is already used by worktree at ...` |
| git 2.55.0; rerere unset; core.hooksPath unset; only merge.tool meld; no .gitattributes | git config, ls |
| `.venv/` and `__pycache__/` gitignored (.gitignore:9, :1) | venvs never merge |
| uv 0.12.17; cache ~/.cache/uv; same filesystem as repo (device 64513) → hardlinks work | `stat -c %d` |
| only tools/skill-trust/uv.lock exists; no root project | find |
| 28 topics declare topic_requires, 28 topic_provides; resolver derives provides_map_all/provides_map_run/requires_map | `grep -l`; roles/topic-resolution/tasks/main.yaml |
| no separate dotagents topic — it's `npx -y @sentry/dotagents@latest --user` at apps/opencode/tasks/install.yaml:98 | find, grep |
| `@sentry/dotagents@3.1.0` is MIT, public on npm — passes the litmus test, clears skill-trust | npm registry |
| no task rule in either versioned config | grep both files |
| `.worktrees/` not in tracked .gitignore | needs adding |

**Private-index disclosure — decided.** `tools/skill-trust/uv.lock` pins a
private corporate index — `https://sfw.security.sentry.io/pypi/simple` in
source, sdist, and every wheel URL. Three problems: employer-identifying
infrastructure in a tracked file (PRD forbids); breaks offline provisioning for
anyone without access to that host; contradicts pyproject.toml's stated
git-subtree-split purpose. Declared dep is only `pyyaml>=6`, so a re-lock against
public PyPI changes nothing functionally. **Resolution (author): this is
machine-specific.** Re-lock to public PyPI for this machine, and add a way for
the work machine to permit the Sentry index — resolved per-machine, never pasted
as a literal URL into the tracked lockfile. Distinct class from dotagents (a
public MIT package name); this one publishes a private URL. Fix before the
worktree experiments, or each new venv bakes it in; the re-lock is itself the
first provisioner-path exercise (Phase 2).

**Settled decisions**

 1. Worktrees in-tree at `.worktrees/` (chezmoi-invisible, probed); add to tracked .gitignore
 2. Flat, never grouped — `.worktrees/<sid>`, `.worktrees/<sid>_sub_<slug>`. Grouping collides admin dirs across sessions and destroys the admin-dir→path mapping exactly when debugging a wedged session
 3. Underscore, never slash, in branch names — refs are files; `refs/heads/agent/x` and `refs/heads/agent/x/sub_a` cannot coexist
 4. Sub-worktrees branch off the parent branch, not main
 5. Many readers, one writer per worktree. In a shared tree no worker can validly verify its own change — Class B corrupted evidence arriving structurally
 6. Patch-producing writers rejected — a diff is good transport, bad execution environment. Patches only for read-only subagents proposing edits they never ran
 7. `UV_LINK_MODE=copy` for sub-agent venvs — independent bytes, so a sub-agent can uv add/remove without corrupting the cache or a sibling
 8. Venvs never merge; only declarations do (pyproject.toml, uv.lock)
 9. Lockfile conflicts: regenerate, never hand-merge. Merge pyproject.toml, then `uv lock`. Add `uv.lock merge=binary` to .gitattributes. Pin uv **at the system layer** (`bootstrap.sh`), not mise — the mise config comment (`dotfiles/apps/mise/files/config.toml:77-82`) documents uv as intentionally not mise-managed, precisely so `mise upgrade` never churns it (the lockfile carries a format revision; version skew churns it, so pinning still matters — just at the layer that owns uv).
10. Two task classes — consumer (UV_OFFLINE=1, --frozen, parallel) vs provisioner (network, serialized). The path-intersection guard enforces this automatically
11. Commit granularity: keep one-decision-per-commit; add never mix mechanical and semantic change in one commit (mechanical first). --no-ff merge per work item = bisect-fine inside + revert-coarse outside + --first-parent narrative. "Every intermediate state works" applies to first-parent commits only, which legitimizes WIP checkpoints
12. Whose decision is a commit: the branch, not the subagent. Decomposition and commit granularity are one decision, made at fan-out
13. Scheduler deferred, taxonomy active. Fan out only the independent frontier; replan between waves. Graphs are trustworthy when derived and enforced (the topic resolver is the in-repo model), untrustworthy when authored and trusted
14. Three coupling channels: writes → path-intersection at fan-out; reads → worktree isolation (structural); semantics → merged-state suite. Only the third is irreducible
15. Ephemeral scratch worktree `.worktrees/<sid>_merge_<n>`, recreated per attempt from (base + input SHAs). Decisive reason: re-running git merge in a conflicted tree is not idempotent; rebuilding from SHAs is. Matches Zuul/bors/GitHub merge queue/SubmitQueue
16. Merge serially, suite after each — batching destroys attribution. Order inert → behaviour → activating
17. Green/green/red is a finding, not a failure — evidence the decomposition was wrong; record against the fan-out
18. Retries: infra 2–3 with full jitter under a retry budget; rebase-and-retest 1–2; deterministic never unchanged; LLM regeneration 1 carrying failure evidence, then escalate. Classification is mechanical: re-run identical artifact in a fresh scratch worktree — same failure = deterministic, different = flakiness detected (quarantine, don't retry into green). Allowlist transient; default deny
19. Escalation: report to orchestrator freely; human at cap, with deadman timeout
20. Wave size tunable + self-tuning — static cap as ceiling plus AIMD (Zuul-style)
21. Orchestrator split: convention here (configuration); tool in ai-prompt-library (a build, forbidden here). Repo declares via `.worktrees.toml`; tool reads
22. V1–V6 all approved
23. Prompt injection is its own strand. Nothing observed — it was a hypothesized vector I initially repeated without flagging as hypothetical. Fetched content is data, never instruction
24. prek switch safe, pending a 30-second check on 0.5.3
25. Two skills, not one — explain-calibration (whether/how much) and feynman-explanation (how, from first principles). Both in ai-prompt-library, authored with skillet-authoring
26. Feynman activation is inferred from signals, never user-invoked — domain rated new/general-principles; "what is X"; same concept asked twice; "plain english"/"ELI25"; a decision hinging on a term the user hasn't used; undefined density. Internal self-check: would it survive being repeated back?
27. Optional-dependency discovery: explain-calibration looks for feynman-explanation; if absent, asks permission to probe for whatever installer exists (dotagents, gh skill, npx, mise, plain ~/.agents/skills drop), else asks the user's preference. No preferences saved by default; it may offer, and the honest home is machine-local config
28. docs/GLOSSARY.md is project terminology only — not a CS dictionary. General terms get glossed inline on first use
29. Glossary linking rule: any doc using a glossary term links to its definition on first use
30. Agentic dependencies: referencing a skill for a method makes it a project dependency — installed and kept current by the machine's skill manager, must pass skill-trust, and agents update the declaration when adding a reference
31. Plain English is already normative (spec.md:480). The gap is coverage — it doesn't yet bind conversational technical communication, which is where this session's violation happened
32. Compactness method: conclusion in one sentence; plain meaning in one clause; the consequence that makes it matter; evidence only if load-bearing. Failure mode is undefined density, not length
33. The calibration insight, recorded verbatim: ask the question that sits under the most terms, not about the term in front of you; ask a reasoning question, not a vocabulary one; then infer down and verify cheaply with one gloss — being wrong costs one parenthesis

**Task list**

Phase 0: cleanup — done (above).

Phase 1 — this repo, configuration only. Each its own commit; `git commit -o`;
`tests/tasks_doc` green before TASKS.md commits.

| # | Change |
|---|---|
| 1 | This handoff (this commit) |
| 2 | Sub-items (h)–(n) |
| 3 | § Writing scenario: plain English binds conversational technical communication |
| 4 | § Writing: short binding calibration rule, referencing the skill for method |
| 5 | New § Agentic dependencies |
| 6 | Glossary linking rule |
| 7 | docs/GLOSSARY.md — project terms only |
| 8 | docs/WORKTREES.md — naming contract, lifecycle |
| 9 | `.worktrees/` entry |
| 10 | task block (the queue above) |
| 11 | One line: dotagents is MIT + public |
| 12 | Task: author explain-calibration |
| 13 | Task: author feynman-explanation |
| 14 | Task: declare both skills as agentic dependencies |

Sub-items (a)–(g) are committed. (h)–(n) are designed, not written:

- **(h) Lifecycle** — spawn/fanout/provision/collect/reap; ephemeral merge worktree; serial merge + suite; retry table; bisect a failed wave; never `git branch -D` (only after `merge-base --is-ancestor`); crash recovery via `remove --force` + prune
- **(i) Declaration merge policy** — regenerate lockfiles; .gitattributes; pin uv; register pyproject.toml/uv.lock as hot files
- **(j) Three coupling channels + unconditional gate** — no diff may touch gating tests or policy code (workers can attack their own verifier — a correctness requirement)
- **(k) Capability manifest per subtask** — paths, refs, commands, egress, secrets, limits, runtime. "read/write/both" is too coarse. Three layers: declare / sandbox / gate. Log via git notes
- **(l) Contracts-first** — interoperating pairs land their interface before fan-out
- **(m) Verifier health first** — flake rate + mutation sensitivity before the orchestrator
- **(n) Irreversible agent effects** — a change reaching the deployed tree (`~/bin`, `~/dotfiles`) cannot be undone by git revert. Agent-concurrency scope only; Ansible plan-vs-apply drift explicitly out

Phase 2 — experiments, in sequence (your choice): happy path (two disjoint sub-agents, simultaneous suites, prove offline, then uv cache clean one package and confirm the offline run fails); the guard seen to fail (path overlap refused, then check disabled to confirm it was the guard; extended with two sub-agents adding the same topic_provides from different files — path intersection empty, resolver must reject the merged tree); provisioner path (uv add, merge back, re-lock; then two provisioners refused).

**Corrections to earlier claims**

- The external_directory deny lives in the global config, is final, not ask-gated — no interactive prompt ever surfaced
- Gemini's claims about zerobox/heimdall-sandbox/sandkasten being cross-platform abstractions, and "Zerobox powers OpenAI Codex," appear nowhere in the ~90-project survey. Unverified; Opus's account is better supported
- Three different projects are named sandbox-runtime. Don't match by substring
- The orphaned autostash stashes are not from either hook runner. Dropping them is a one-off, not policy
- Cleanup was already complete when this session started — no worktrees or agent branches to remove (see Phase 0 above).

**Gotchas**

- Never `git add -A` or bare `git commit` — index is shared. Use `git commit -o <paths>`; for TASKS.md use `git add -p` + bare commit
- Agents never run `chezmoi apply`; status/diff encouraged
- `ollama ps` before benchmarking — model memory is global
- Test command needs all seven `--with` flags or parts of the suite silently skip
- `tests/tasks_doc` guards TASKS.md section boundaries
- `.worktrees/` is currently excluded only locally via `.git/info/exclude` (previous session's change, to be replaced by the tracked entry)
- `chezmoi add` on a `.tmpl` can overwrite `{{ }}` with literals — always `git diff` after

**Resolved this session — the eight open questions**

 1. Private index in uv.lock — fix, machine-specifically: public PyPI here, a per-machine permit for the work machine's Sentry index (see the disclosure above).
 2. Experiment subject — keep `tools/skill-trust/` after the re-lock.
 3. uv pin — at the system layer (`bootstrap.sh`), not mise (corrects settled decision 9).
 4. Best-of-N racing — defer; note as a future screen arm.
 5. Model-screen budget — ~$10 for the 20-item run.
 6. --no-ff per item — agent multi-commit items only; keep straight-to-main for solo work.
 7. (g) mutation trailers — land now, as one small standalone change.
 8. "general" egress — ask (fail-closed), consistent with "everything else asks" (PERMISSIONS.md).

## Picking this back up

Say any of these and the thread resumes where it stopped:

| Say this | Resumes |
|---|---|
| **"layout"** / **"standardization"** | `docs/LAYOUT.md` plan — next is the second-machine inventory, then its migration |
| **"topical"** or **"A9"** | The next build step: the manager-aware generator reading `managers.yaml` |
| **"the template work"** | Same as A9 — that is what it refers to now |
| **"voice typing"** / **"openwhispr"** | The voice topics; architecture is settled, `.deb` via `ansible.builtin.apt` |
| **"claude-code topic"** | Extending it to Debian via the signed apt repo |
| **"the sunset plan"** / **"A10"** | Retiring the six `~/bin` names, blocked on the dispatcher working |
| **"ansible user"** | The privileged-update service, scope the sudoers grant first |
| **"llocallabs"** | The anchor repo and strategy/policy agent — the collection consolidating the AI work |
| **"sandboxing"** | The two-phase agent-sandboxing research project |
| **"session management"** / **"handoff protocol"** | The research feeding the TASKS.md process design; advisor review of handoffs is part of it |
| **"rag"** / **"knowledge graphs"** | Preprocessed agent-context research |
| **"gita"** | The multi-machine repo-manager study and its topic |
| **"metamorphic"** | The metamorphic-testing research for the test suites |
| **"pkgup"** | The Debian package-updater study, blocked on become privileges |
| **"r&d factory"** | The llocallabs exploratory pipeline — scratchpad experiments promoted by test suites, not vibes |

The design decisions behind all of it are in `dotfiles/docs/ROADMAP-topic-cli.md`
§ Amendment — read that before writing any `topical` code, since several of them
reversed earlier positions on purpose.

## Now

The handful actually next. Keep this short — if everything is Now,
nothing is.

- **Bootstrap the multi-agent coordination layer — worktrees, frozen leases,
  risk-tiered merge gates — then extract it to the copier template.** [#1,
  reordered ahead of the governance consolidation by the author 2026-09-20]
  Design settled this session with the author and a three-model council.
  Structure: one worktree per agent session (its own index — the actual fix
  for the `b3ad740`/`5692a86` mixed commits), one branch per task with
  subtasks as *commits* rather than sub-branches, `.git` read-only inside
  worktrees (Codex forces this; worktrees share `.git`, so a stray `gc` or a
  `.git/hooks` write hits every agent), `rerere` on globally, and a
  protected-ref deny so nothing irreversible lands unreviewed. Leases stack
  rather than compete: the resolver *authors* an expansion from `topic.yml`
  declarations, which is then **frozen** to a literal path list plus the
  metadata commit hash, resolver version and a TTL — enforcement reads the
  frozen artifact and never calls the resolver, which removes the TOCTOU hole
  where a lease silently widens when someone else's merge lands. Bounds:
  computation may only narrow (`effective = computed ∩ reviewed envelope ∩
  policy`); dependency edges grant **read**, not write (transitive closure is
  the canonical over-broadness bug); a commit may not widen the lease it was
  made under; and a literal deny-list — policy paths, egress paths, secrets,
  the deployed tree, resolver code, the lease store — outranks everything and
  *is* the mechanical definition of the always-human-review tier. Conflict
  detection is mechanical first (trial-merge plus duplicate `provides`, unmet
  `requires` and cycles as hard errors on the **merged** tree, which no
  per-branch gate can see), semantic later. **Measure merged-items-per-hour at
  2, 3 and 5 agents before building anything for 10** — throughput in agent
  count is plausibly non-monotonic, and if the curve flattens at 4 then most
  of the machinery is solving a chosen problem rather than a real one. Done
  when: worktree-per-agent is in use with `.git` read-only and `rerere` on; a
  push-time path gate rejects out-of-lease paths and **has been seen to fail**
  against a deliberately out-of-scope commit; the resolver rejects a
  duplicate-`provides` merged tree; provenance trailers record
  session/agent/model per commit; and the measured throughput curve is
  recorded. [me]

  Sub-items, settled with the author and a three-model council 2026-09-20:

  - **(a) Swarm shape inside one worktree: many readers, one writer.** A
    worktree is one index plus one mutable filesystem, so N writers in it is
    shared-memory concurrency with no memory model. The first thing lost is not
    commit correctness but the ability of any worker to *verify its own
    change* — the suite runs against a tree someone else is mutating, so green
    and red are both unattributable. That is the ledger's Class B (corrupted
    evidence) arriving structurally rather than by misconduct. So: fan out
    read-only subagents freely inside one worktree (search, analysis, review,
    "does this claim hold across the 40 topic files"), and give every *writer*
    its own worktree. Patch-producing writers are a trap — a diff is good
    transport and a bad execution environment; the moment a worker must test,
    it needs a tree, and a tree wants a branch. Patches are right only for a
    read-only subagent proposing an edit it never ran. Done when the roles are
    written down, the read/write split is enforced, and a deliberately
    concurrent write is shown to be rejected rather than merged.
  - **(b) Deterministic index, via git's own primitives.** Commit
    construction becomes a pure function of (base tree, file contents) with
    `GIT_INDEX_FILE` pointing at a private index plus plumbing —
    `hash-object -w`, `update-index`, `write-tree`, `commit-tree`,
    `update-ref` — needing no working tree and no shared lock. Claims belong
    in refs, not prose: `git update-ref refs/claims/<item> <sha> ""` fails if
    the ref already exists, which is an atomic compare-and-swap and therefore
    a real mutex, unlike a § Claimed line two sessions can both believe they
    won. Two traps: `index.lock` failures look transient so agents retry, and
    a retried `git add` after a partially applied operation stages a
    *different* set — the retry is the bug, not the lock; and hook frameworks
    that stash unstaged changes can eat or resurrect a concurrent writer's
    work in the same tree (benign here, since this repo's hooks only check,
    but not in ai-prompt-library where formatters run).
  - **(c) The real parallel ceiling is the machine, not git.** A worktree
    virtualizes the source, not the host. Anything touching `$HOME` is
    unparallelizable regardless of git — and in a dotfiles repo that is most
    of it: the deployed tree, `~/bin`, `~/.binned/config.toml`, apt/brew
    locks, mise, ollama's global model memory. True parallel width is the
    number of in-flight tasks needing no global resource; model each global as
    a semaphore. Estimated real ceiling here is 2–3 writers. Prerequisite for
    any parallelism: sandbox the tests that touch `$HOME`
    (`HOME=$(mktemp -d)`, chezmoi `--source`/`--destination`, `--dry-run`).
    Until that holds, `pytest-xdist` is off the table.
  - **(d) The subtask dependency graph is deferred, with the condition for
    revisiting it stated.** Graphs work where they are *derived and enforced*
    and fail where they are *authored and trusted*: Bazel/Buck/Nix are
    trustworthy because a sandboxed action physically cannot read an
    undeclared input, and an agent that reads the whole repo violates
    hermeticity by construction — so a hand-drawn agent DAG is advisory only,
    never proof of independence. Snakemake and Nextflow derive their DAGs from
    declared file patterns; Airflow bolted on dynamic task mapping in 2.3,
    Prefect 2 dropped static DAGs, and Temporal's position is that the
    workflow *is* code and the graph is discovered by executing it. Closest
    transferable prior art is Git's own "What's cooking" — a human-curated
    queue of topic branches that scales with no scheduler at all, i.e. this
    file. Conditions for it to beat a lock and a list: sustained parallel
    width ≥ 2 *on the critical path* (decision-led work is a chain, and § How
    work runs here pushes it further that way by leading with deciding
    items); node duration ≫ integration cost; cheap per-node verification;
    nodes that genuinely partition files; and a human who is expensive to
    consult, which one developer at this machine is not. Note also that
    building a scheduler here would be a **build, not configuration** — per
    the AGENTS.md ladder it belongs in ai-prompt-library or nowhere. Order:
    shrink suite runtime and conflict rate first. [blocked: instrument the
    four numbers in (f) first]
  - **(e) Commit granularity: keep the rule, add the prohibition, and let a
    merge carry both views.** "One reviewable decision" is scale-relative and
    therefore nearly unfalsifiable — a Debian systemd-timer choice is a
    decision and so is a variable name inside it, so nesting lets the rule
    justify any split. It also loses outright on large mechanical changes: a
    rename across 40 files plus a behavior change is *one* decision that must
    become three commits (add new, migrate callers, delete old) because the
    intermediate states must work — and that split criterion is mechanical,
    not semantic. The resolution: **bisect wants fine, revert wants coarse,
    and a `--no-ff` merge per work item gives both** — fine granularity
    inside, one `git revert -m 1` handle outside, and `git log --first-parent`
    as the clean history on demand. Require "every intermediate state works"
    of first-parent commits only; branch-internal commits need merely not be
    broken on purpose, which legitimizes the WIP checkpoint commits agents
    need anyway when they die of context exhaustion mid-task. Criteria become:
    revertible alone with a coherent result; passes the suite; the why fits in
    ~2 sentences (measured — 232-word median against a house 114); and **never
    mix mechanical and semantic change in one commit**, ordered mechanical
    first (Beck's "tidy first", Fowler's preparatory refactoring). That last
    rule is mechanically checkable and does more for blame, review and
    conflict rate than any theory of decisions. Whose decision is a commit
    when agents run in parallel: **the branch, not the subagent** — subagent
    boundaries are an artifact of how the work was parallelized, which is
    exactly what history should not preserve. Also adopt
    `.git-blame-ignore-revs` with `blame.ignoreRevsFile` so mechanical churn
    is skippable.
  - **(f) Instrument four numbers before building any of it.** Suite
    wall-clock, conflict rate, rebases per merged item, and author review
    minutes per item. Every question above resolves differently depending on
    them, and none are currently measured. Review is the likely bottleneck
    rather than generation: with one reviewer, agents past ~3 queue in front
    of the human and their branches rot — raising WIP without raising review
    throughput raises latency, and latency becomes staleness, rebases, and
    void test evidence. Cheapest controls, needing no code: an explicit WIP
    cap, and a max branch age (a branch older than a day has void test
    evidence — rebase or abandon).
  - **(g) Make the "seen to fail" evidence mechanical.** Commit trailers
    (`Mutation:`, `Failing-test:`) via `git interpret-trailers` are greppable
    and auditable; prose in a commit body is not. The highest-severity
    incident class in the trust ladder is currently detectable only by a human
    redoing the work. Related: the mutation state that proves a test must
    never be committed, so the evidence can only ever live beside the commit,
    not in it.

- **Consolidate the governance docs — PRD as the constitution, spec as the
  derived statutes, conventions as the how-to.** [#2, was #1 until the author
  reordered the multiagent work ahead of it 2026-09-20] Decided with the author
  2026-09-16: PRD states each requirement once; spec derives its testable
  SHALL/BDD form and cites the principle back; AGENTS-referenced convention
  docs explain how to comply. The four docs are currently peers with no stated
  precedence, and PRD has smuggled constraints (the provision-vs-logic rule,
  the verification governor) that belong in spec — the drift behind the
  changelog "discipline gap" (d1f10ff). Items, in order: (1) derivation-graph
  inventory — map every spec.md behavior to its PRD.md principle and back,
  marking orphans and unstatuted principles; (2) write the precedence rule into
  the docs; (3) prune the drift — move smuggled statutes into spec with
  citations; (4) retire the stale root docs/ tree (edit dotfiles/docs/ only);
  (5) review TASKS.md § Now/Planned against the consolidated requirements.
  Done when every spec behavior cites a PRD principle, PRD holds no testable
  statutes, one maintained copy of each doc exists, and the open task list has
  been re-reviewed. [me]

- **Switch the hook runner to prek and retire the pipx pre-commit.** Verified
  2026-09-20: prek's unstaged-change mechanism is patch-to-cache, not
  `git stash`. `crates/prek/src/cli/run/keeper.rs` captures unstaged work with
  `git write-tree` + `git diff-index --binary`, writes it to
  `~/.cache/prek/.../patches/{millis}-{pid}.patch` in a `0700` directory,
  cleans the tree, runs hooks, then `git apply`s it back on drop — reverting
  the hook's own changes first if they conflict, and restoring from a ctrl-C
  cleanup handler. Neither `git.rs` nor `keeper.rs` contains `git stash`, so
  the switch does not put hook runs on the shared `refs/stash` that already
  holds two orphaned autostash entries — the one risk that gated this. prek
  also disables `core.fsmonitor` for its own git calls and handles
  `GIT_DIR`/`GIT_COMMON_DIR` worktree separation, which is useful precedent
  for the coordination work. State today: `.git/hooks/pre-commit` is
  pre-commit's (pipx 4.6.2, hardcoded interpreter), prek 0.5.3 is installed
  via mise and wired to nothing. Done when one runner is installed and the
  other removed, and a run against a tree with unstaged edits prints prek's
  "Temporarily saving them to" line while `git stash list` stays unchanged —
  the mechanism was verified against `master`, not the installed 0.5.3, so
  that check is the confirmation. [me]

- **Input to the normative topic spec: lift the settled herdr decisions from
  `dotfiles/docs/TOPIC-RECIPES.md` and `dotfiles/apps/herdr/README.md`.**
  Queued 2026-09-19: the spec session should absorb the install-mechanism
  chooser, the catalogue pattern (with its skip-vs-raise doctrine), the
  service-ownership rules and the test-first swarm recipe from those two docs
  rather than re-deriving them; `dotfiles/docs/JUDGE-SELECTION.md` feeds the
  panel-of-judges measurement item. Done when the spec either expresses these
  or records a reasoned rejection. [me]

- **Write the normative spec for topics — a `spec.md` for the topic unit.
  More urgent than the design work below it.** Queued 2026-09-17 ahead of
  the downstream-IDE wiring so that work lands against a settled constraint
  layer rather than after it. House spec form (SHALL/MUST with BDD
  scenarios, skillet-validatable, carrying its `skillet-version` comment),
  a sibling to the root `spec.md`: what a topic is and must remain — the
  lifecycle contract, the CRUD ownership invariant, `topic.yml` as the
  schema of record, template conformance, shared-dep teardown rules, the
  guard doctrine. `TOPICS.md` then reduces to plain explanation that links
  to the spec for binding wording — two normative statements of one rule
  drift; an explanation plus a link does not. **Input to the spec, by the
  author 2026-09-17:** the vscode↔cursor downstream-IDE design below is a
  deliberate probe of how upstream/downstream relationships between topics
  should be declared and governed — its settled outcome normalizes "topics
  as a format" and must be expressible in the spec's terms. Done when the
  spec exists, `skillet validate` passes on it, `TOPICS.md` cites it
  instead of restating its SHALLs, and the author's adopt call is
  recorded. **In progress elsewhere** (author, 2026-09-17) — do not start
  from another session. [me]
- **Design the cadence by which topics pull in and refresh official
  upstream references, so topics track their tools proactively.** Queued
  2026-09-17 by the author: topics bind to external tools whose docs,
  changelogs and release feeds move, and today the repo learns of upstream
  change only reactively — the skillet pin needed a changelog read before
  moving, `docs/REFERENCES.md` records "when last checked" by hand, and
  cursor/vscode extension availability is being verified per editor only
  because something broke. The design must settle: what each topic declares
  about its upstream (a source list in the topic — docs URL, changelog or
  release feed, the `REFERENCES.md` row it feeds); what cadence means here
  (per-topic intervals, one repo-level sweep tied to `--tags upgrade`, or a
  machine timer — noting launchd on macOS and the systemd *user* timer rule
  on Debian); where fetched deltas land so they become work (a queue line,
  a report, a drift subcommand in the topical CLI) rather than vanishing;
  and how it composes with the extension-manifest design above, whose
  per-extension availability verdicts are the first instance of this same
  problem. **The cadence fetcher is a build** — the AGENTS.md ladder
  applies: route it (ai-prompt-library, llocallabs, or the topical CLI
  work) before any code is written here; machine-side wiring such as a
  timer is the only part that provisions. Done when a written design
  answers those questions with the destination decided through the ladder,
  and the wiring lands as queued tasks. [me]
- **Spec the zsh tooling standard — author interview first, then a
  review-best-practices pass, then council critique.** Queued by the author
  2026-09-16, from the LANGUAGES.md zsh row: ~90 `.zsh` files are zsh
  lifecycle fragments, the extension marks how a file is used rather than a
  distinct language, and the bash standard already applies de facto — the
  pre-commit shellcheck hook matches `types: [shell]` and identify tags
  `.zsh` as `shell`. Interview first: fragment-vs-script semantics, which
  bash tools are trusted on zsh, tolerance for zsh-specific false positives
  (shellcheck does not support zsh — `typeset`, `${~spec}`, `=cmd` are known
  mismatch classes), whether `zsh -n` should gate commits, and where the spec
  lives (a `docs/LANGUAGES.md` row vs a new `docs/ZSH.md`). Then a research
  pass verifies the "zsh can use bash tools" claim rather than assumes it,
  with ranked options and rejections recorded. Then fresh-context subagents
  red-team the draft (the panel-of-judges question is itself unsettled; using
  the pattern here is the author's call). Done when a written recommendation
  exists with rejections recorded, the author's adopt/adapt/reject decision
  is recorded, and any wiring lands as queued tasks. [me]
- **Extract the incoming-changes review into a reusable agent capability,
  with a specification.** High priority, queued by the author 2026-09-15,
  from this session's review pattern: on `git fetch`, before any merge, the
  agent verifies the incoming claims against this machine (`chezmoi status`,
  `ollama list`, path existence), classifies findings as blocking /
  question / nit with file-and-line evidence, and recommends resolutions.
  Routing: with no blocking findings, pass the changes in (fast-forward
  merge); with any, hand the merge to a human via **meld** — `git
  mergetool` or merge-with-conflicts opened in meld — and report the
  finding list for them to resolve. The specification (SHALL/MUST + BDD
  scenarios, house spec style) must fix: the trigger point (post-fetch,
  pre-merge); the verification classes; the conflict taxonomy and what
  counts as blocking versus advisory; the human-handoff via meld and how a
  run resumes after the human resolves; idempotency on repeated runs; and
  the pass-through policy — which gates turn a question into a block.
  Destination per the AGENTS.md ladder (likely a skill/spec in
  ai-prompt-library or llocallabs); any machine-side wiring here is
  provisioning. Done when the spec is written and validated, and the
  capability runs end-to-end against both a deliberately conflicting merge
  (hands to meld) and a clean one (passes through).
- **Inventory the second machine's divergent trees for the layout
  migration.** Queued by the author 2026-09-15 (standardization interview):
  the migration plan must not guess what the other machine holds. On the
  next session there, inventory `~/code/projects/personal/` (at least
  `llocallabs-capture`), `~/code/try/` (copier-stamps, git-ai-plugin,
  openrouter-tools per the merged queue), and any other dir outside this
  Mac's layout; record each with its proposed type under the standard
  (work/personal/try/captures/templates/forks/archive). Done when the
  inventory is written into the migration section of the layout plan and
  every divergent path has a destination type. [agent: second-machine
  session]
- **Handle machine-specific directory exceptions and their state backup in
  the layout standard.** Deferred by the author 2026-09-15 from the
  standardization interview: some directories will exist on one machine
  only, yet their state should still be backed up to config. Design how the
  standard declares a per-machine exception without breaking sameness
  elsewhere, and how the exception trees' state plugs into the
  backup-design item in § Planned. Deferred deliberately so the interview
  can settle the shared-layout core first.
- **Research when LSP servers earn their keep with opencode — a deeper
  answer than the docs' best-practices page gives.** High priority, queued
  by the author 2026-09-15. The page (https://opencode.ai/docs/lsp/, fetched
  2026-09-15) says LSP is disabled by default, lists 30+ built-in servers
  that auto-start on matching extensions, and concludes that lint/typecheck
  CLIs documented in AGENTS.md or skills often beat language-server
  feedback. That is the hypothesis to test, not to accept. The research must
  settle: per-language payoff (pyright wants a project dep, several
  auto-install, `OPENCODE_DISABLE_LSP_DOWNLOAD` gates downloads); the real
  cost terms (memory, version skew, out-of-sync servers) weighed against
  agent-loop value; where `lsp` config should live per repo and per topic
  here; and which repos actually earn enablement. Route it as a
  review-best-practices pass — what exists, what practitioners do, ranked
  options with rejections recorded — and it feeds the llocallabs topic
  design. Done when a written recommendation says when LSP earns its keep
  here, per language, and the author has made the adopt/adapt/reject call.
  [me]
- **Configure opencode LSP profiles for Python and Bash projects — ty or
  pyrefly alongside ruff and the other servers that matter — if we are not
  doing that already.** Queued by the author 2026-09-15; the concrete
  follow-on to the research task directly above — that one settles WHEN
  LSP earns its keep with opencode, this one settles WHICH servers for
  Python/Bash and wires them. Verified 2026-09-15: we are not doing it
  already — neither `dot_config/opencode/opencode.jsonc.tmpl` nor the
  project `opencode.json` has an `lsp` section (rg finds none), so LSP is
  disabled-by-omission; ruff is mise-managed (`ruff = "latest"`) but wired
  to nothing per docs/REFERENCES.md; `ty` and `pyrefly` are both absent
  from the mise config (a § Later task queues installing `ty`); bash
  linting today is shellcheck in pre-commit. The docs
  (https://opencode.ai/docs/lsp/, fetched 2026-09-15) say `lsp: true`
  enables all 30+ built-ins and the object form configures per-server
  `command`/`extensions`/`disabled`/`env`/`initialization`; built-ins
  relevant here: pyright (.py, wants a project dep), bash (auto-installs
  bash-language-server), yaml-ls (auto-installs);
  `OPENCODE_DISABLE_LSP_DOWNLOAD=true` gates the auto-downloads. The work:
  decide ty vs pyrefly — pick one, not both (ty is pre-1.0 but the house
  toolchain names it; the queued install task owns the install, this owns
  the LSP wiring); decide where the profile lives — the chezmoi-managed
  global template (all projects, effective on apply + restart) versus
  per-repo `opencode.json`; and decide whether server downloads are
  permitted given bash-language-server and yaml-ls auto-install. Done when
  the chosen servers are configured in the chosen location, an opencode
  session on this repo shows Python and Bash server feedback, and the
  download policy is recorded. [me]
- **Create the first llocallabs.ai repository — the collection that will
  consolidate the author's AI tooling and agent projects.** The milestone
  (2026-09-14): AI research, testing and benchmarking move out of this
  repo — it carries the machine trunk and is overloaded with strategy work
  that wants isolation. The first repo anchors the collection: document set
  first (PRD what-for, spec, ROADMAP, TASKS, AGENTS — the separation this
  repo runs on), then it queues its own move-manifest work. Two questions
  settle at creation: scaffold by hand versus the general copier template
  queued in § Planned (llocallabs would be its first real consumer — that
  coupling may be the reason to build the template now), and where it lives
  (`~/code/personal/` beside ai-prompt-library and impromptu is
  the precedent — verified on this Mac 2026-09-15; the
  `~/code/projects/personal/` form in 984df10 was the author's other-machine
  path, incorrect here, and the author confirmed reverting it). This repo's recently-queued research (sandboxing, session
  management, metamorphic testing) and the benchmarking tooling
  (`bin/model-bench`, `bin/binned`, the eval harness) are candidates for
  the move manifest — nothing moves until that manifest lands. Done when
  the repo exists, carries the document set, passes `skillet validate`, and
  its TASKS.md queues the move-manifest and strategy-agent work. [me]
- **Stand up the llocallabs strategy/policy agent.** At least one separate
  agent that works on tooling and decisions about the author's personal AI
  strategy and policy — the role this repo was never meant to play (PRD:
  provisioning is the trunk; strategy is a branch). Its definition, context
  and tooling live in llocallabs, not here; the machine-side part —
  registering it in opencode/claude config, its permissions — is a follow-on
  task here once the definition exists. It consumes the research projects
  this repo queued (sandboxing, session-management handoff, metamorphic
  testing) as strategy inputs, and its policy decisions feed back through
  the over-arching-policy contract in ROADMAP.md. Done when the agent
  answers a real strategy question with a recommendation and rejected
  alternatives, running from its own repo rather than this one. [me]
- **Build the llocallabs R&D factory — an exploratory pipeline from
  scratchpad experiments to durable, reusable elements, in service of the
  long horizon: autonomous knowledge projects.** The author's recurring
  trouble, named 2026-09-14: classifying the different modes of research
  (ideation, brainstorming, stress-testing, fact-checking — not
  exhaustive), recruiting the right experts for each, and trying out
  agents, skills and workflows in a low-stakes environment where useful
  experiments become durable quickly and dead ones cost nothing. First
  evidence of the friction, same day: the author's Google AI research on
  Caliber lived only in a conversation until captured by hand to
  `~/code/personal/llocallabs-capture/` — and `~/code/try/` already
  holds the author's ad-hoc experiments (copier-stamps, git-ai-plugin,
  openrouter-tools), making it the embryonic scratchpad; research captures
  route to the capture store beside the personal projects until the
  factory's own pipeline exists. This task
  is stage one, **gated on the anchor repo existing** — the factory belongs
  to the collection, not here. Stage one classifies: inventory the author's
  actual research modes from what the queues already show (the
  council-pattern deep-research projects, the eval-gate doctrine, the
  `agentic-context-engineer` role), map each mode to the agents, skills and
  workflows it needs, and record which experts — human or model — belong to
  which mode. Stage two, queued by stage one's output, is the scratchpad:
  disposable environments where an experiment runs with a lightweight eval,
  and the promotion gate into a durable element (a skill, an agent, a
  workflow) is a passing test suite — never vibes. Done when stage one's
  classification exists, the author has corrected it, and the
  scratchpad/promotion stages are queued in llocallabs with their own
  gates. [me]
- **Research metamorphic testing for this repo — generally and against our
  actual suites — and decide whether it complements or should refactor the
  current test tooling.** Run it as a review-best-practices pass (what exists,
  what practitioners do, ranked options with rejections recorded), questioning
  the author liberally before scope settles. Anchors: the property suites
  (`tests/ollama_evals`, `tests/binned`), hand-rolled mutation checks
  (AGENTS.md § Prove the test fails), the fuzz guidance (§ Properties and
  fuzzing), and relations already in place unnamed — `nudge_whitespace`
  preserving content under spacing perturbation is one. Candidate seams: the
  model-output boundary, case-YAML ingestion, the policy layers. Done when a
  written recommendation exists — which seams fit, which do not, what adoption
  would refactor, and the author's adopt/adapt/reject call. [me]
- **Close out the 12 environmental suite failures — the pii half is now
  diagnosed.** The advisor pass found what this queue called undiagnosed:
  the two `tests/pii_redactor` llm failures are model-absence, named by the
  error itself — the conftest (`tests/pii_redactor/conftest.py:29`) requests
  `qwen3.5:4b-mlx-bf16` through the real `llm` CLI and gets
  `Unknown model`; no qwen3.5 model is installed. The snapshot's "runs
  against a mock" claim was wrong for these two tests and is corrected.
  **Machine-stamped:** the absence is the second machine's, 2026-09-14 —
  this Mac HAS the tag (`ollama list`, 2026-09-15), so here the diagnosis
  is unconfirmed until the two tests are re-run.
  Remediation is the author's call: install that model (space
  consideration) or make the conftest skip-with-reason when the integration
  model is absent. The 10 `tests/clipped` failures remain clipboard/TTY —
  each gets an environment skip naming the missing capability or a fix if
  the test is wrong. Run clipped and pii_redactor in SEPARATE pytest
  invocations: one invocation aborts at collection (conftest name
  collision, `from conftest import CLIPBOARD_CONTENT`). Done when a
  headless full run reports zero failed with skips named, and a capable run
  still exercises what was skipped. [me]
- **Give topics an integrations phase, and make `apps/opencode` own its
  OpenRouter wiring as the first case.** `dot_config/opencode/opencode.jsonc`
  already points `model` at `openrouter/z-ai/glm-5.3-flash` and `small_model`
  at `ollama/qwen3:8b`, while `apps/opencode` declares `topic_requires:
  [homebrew, node]` and checks neither provider — auth is a manual `opencode
  auth login` that the README leaves to the reader. A freshly provisioned
  machine therefore deploys a config whose default model cannot answer, and
  nothing in the run says so. The convention to write into `docs/TOPICS.md`:
  when a tool needs a provider or CLI at **runtime** rather than to install
  (openrouter, ollama), the tool's own topic decides on it and acts — it checks
  whether the dependency is reachable and owns the logic to add the integration
  and to take it back out, rather than delegating either to the provider's
  topic. Integrations stay separate from installation: they run only **after**
  the tool is installed, and are skipped and reported — never failed — when the
  tool is absent or the user declined it. That ordering is why this is a phase
  of its own and not more `install.yaml`. Go through **`ori`** rather than
  hand-rolling provider config: `ori opencode` is OpenRouter's own supported
  path for pointing opencode at its models, and `apps/ori` already declares
  `topic_provides: [ori]`, so the integration can require it through the
  existing dependency graph instead of a PATH probe. The two failure modes are
  deliberately not the same: a missing or declined **opencode** is a skip, while
  a missing `ori`, or an `ori` that runs and cannot complete the integration, is
  **raised** — the run fails with the named fix, or the agent surfaces it, rather
  than leaving a half-wired provider behind. Mind the auth constraint the ori
  README already records: `ori login` is interactive and deliberately not
  automated, and an inherited `OPENROUTER_API_KEY` beats whatever it stores — so
  the integration must work from that key and fail loudly, naming it, when
  neither is present. Done when `apps/opencode` wires OpenRouter through `ori`,
  confirms it with a check whose pass/fail the run reports (`opencode auth list`
  at minimum, a one-token completion if that proves too weak), skips cleanly
  where opencode was never installed, raises rather than skips when `ori` is
  absent or fails, takes the integration back out under `--tags remove`, and
  `docs/TOPICS.md` states the convention so the next tool follows it without
  re-deciding.
- **Prove topic idempotency with a second-run check, and make `--check` work
  again first.** Measured 2026-09-14 by dry-running
  `--tags "upgrade,install,minimal"`: `ok=104 changed=6 failed=1`. The good
  news is that **no package install task reported changed** — `state: present`
  converges as advertised, so adding `install` to `./update`'s tags would add
  missing topics without reinstalling present ones. The six that did change:
  two are the homebrew upgrade tasks doing their job; `apps/ollama` "Download
  latest Ollama Zsh completion to temporary path" fetches to a fresh tempfile
  every run and so reports changed forever; and three script/agent installs
  (`ollama` launchd agent, `clamav` daily script, `lynis` monthly script) need
  checking for real drift versus a check-mode artifact. The blocker is
  `failed=1`: `roles/guards/tasks/dotagents-approved-sources.yaml:59` dies under
  `--check` because the `tempfile` task above it is skipped, leaving
  `guard_trust_config` a dict with no `.path` — so the repo cannot currently be
  dry-run at all. `check_mode: false` is the fix and the repo already uses it
  four times (`apps/homebrew/tasks/upgrade.yaml:19` is the precedent). The
  standard for the test itself is molecule's `idempotence` action — run converge
  twice, fail if the second reports changed — which needs no molecule adoption
  to copy. Done when `--check` completes clean across all topics, a second
  consecutive real run reports `changed=0`, and the check runs per topic so a
  failure names which one. Pairs with the per-topic suite task below.
- **Adopt molecule for topic testing, with the vagrant driver where macOS is
  required.** Approved 2026-09-14. Molecule is the standard Ansible role test
  harness and its `idempotence` action is precisely the converge-twice check the
  task above wants, so this supersedes hand-rolling one. It also fits two
  decisions already made: scenarios live at `apps/<topic>/molecule/default/`,
  inside the topic, matching the co-location rule; and molecule is the
  conventional harness for collections, which is the direction the portability
  research points. Split the drivers by what they can actually reach — measured
  from `topic_os`: **19 topics are `[Darwin]`-only, 6 are both, 2 are
  `[Debian]`-only.** The docker/podman drivers are Linux containers and cover
  the 8 Debian-capable topics cheaply; the 19 Darwin-only ones — casks, launchd
  agents, `monitorcontrol`, `rancher-desktop` — cannot be containerised at all
  and need vagrant against a macOS VM. Unknowns to settle first, because they
  decide whether the Darwin half is affordable: which vagrant provider works on
  Apple Silicon (tart, UTM, Parallels — VirtualBox does not), image size, and
  Apple's licensing limit of two macOS VMs per host. Do not convert all 27 at
  once. Done when one Debian topic and one Darwin topic each have a scenario
  that converges and passes `molecule test`'s idempotence step. **herdr is
  the named first consumer** (judge round 1's accepted high gap: no
  automated converge; its pytest suite already covers everything molecule
  does not), the per-driver
  choice is written into `docs/TOPICS.md`, and the pytest suite still owns
  everything molecule does not — molecule tests convergence on a machine, not
  the repo's own logic. [blocked: needs the `--check` fix above, since a run
  that cannot dry-run cannot be trusted to converge twice either]
- **Sweep the remaining hardcoded `/home/bdavis` paths out of
  `dot_zshrc.tmpl`.** Four of them, all inside the `{{ if eq .chezmoi.os
  "linux" }}` block (lines 69–459), so none render on macOS and none are broken
  today — they are correct only because the Debian box's username happens to be
  `bdavis`, which is precisely the failure the new convention in `AGENTS.md`
  § "Machine-specific values are resolved, never written out" exists to stop.
  Lines 331 and 355 both prepend `/home/bdavis/.local/bin` to `PATH` and can
  simply go: `~/.local/bin` is already on `PATH` via `zsh/path.zsh`, verified on
  this Mac. Line 381 sources the broot launcher by absolute path and needs
  `{{ .chezmoi.homeDir }}` or `$HOME`. Lines 89 and 267 are cosmetic — a
  compinstall marker and a shellcheck `source=` hint — and the real `source` on
  267 already uses `~`. Cannot be verified from this Mac: the block only renders
  on Debian, so `chezmoi execute-template` with a forced OS, or a check on the
  box itself, is the proof. Done when no `/home/` literal remains in the
  template and the rendered Debian output still sources broot and resolves
  `~/.local/bin`.
- **Give every topic a TDD-style test suite, and make editing a topic require
  its tests.** `tests/topics/` holds exactly one file — `test_zsh_layout.py`,
  about zsh fragment placement — against the 27 topics under `dotfiles/apps/`,
  so nothing tests what a topic's lifecycle actually does: that every state
  install creates has a teardown in remove (the CRUD invariant `docs/TOPICS.md`
  asserts but nothing checks), that `topic_os` and `topic_requires` match what
  the tasks really use, that `--tags upgrade` touches what it claims and no
  more. Nothing links a topic edit to tests either — the `bats` pre-commit hook
  matches `^(bin|scripts)/` shell scripts only, so changing a topic's YAML runs
  nothing and prompts nothing. **A topic's tests live with the topic** —
  `dotfiles/apps/<topic>/tests/`, not a central `tests/topics/` — so a topic
  stays portable: copy or extract the directory and its tests come with it,
  which is also what makes the `ai-strategy` bundle and the Refactor B
  extraction below movable rather than a re-write. Three things that costs, all
  of which the implementation has to answer: `pytest.ini` sets
  `testpaths = tests tools`, so topic-local suites are not collected today and a
  bare `pytest` would silently pass while testing none of them; `.chezmoiignore`
  ignores a bare `tests/`, so confirm whether that already excludes topic-local
  test dirs from the deployed tree and decide whether it should, since
  portability argues for shipping them so a provisioned machine can verify
  itself; and `dotfiles/template_dir/` has no `tests/`, so the scaffold must
  grow one or topic 28 starts untested by default. Tests first on the next topic
  changed, per the pytest doctrine in `AGENTS.md` and `docs/PYTHON.md`, then
  backfill rather than pausing to write 27 suites up front. **herdr is the
  proven instance** (2026-09-19): full test-first via the author-swarm +
  judge loop, 116 tests in central `tests/herdr/` — the destination stays
  topic-local suites over a shared harness, and the enforcement gate (a
  topic edit forces its tests) is the unlanded half. Done when a
  per-topic suite lives beside its topic over a shared harness (so topic 28
  inherits it instead of re-inventing it), collection reaches those suites, a
  staged change under `dotfiles/apps/<topic>/` runs that topic's tests and fails
  the commit when they are red or absent, and the tap-trust fix in `e60982c`
  has the regression test it went in without — trust-before-tap ordering, and a
  teardown that clears both the tap and the formula trust entry.
- **Build a `dotfiles-triage` agent and the skill set it loads, so a failing
  `chezmoi apply` / `ansible-playbook` / `update.sh` run goes straight into
  troubleshooting instead of stopping at "non-zero return code".** The
  `apps/opencode` skill-sync failure on 2026-09-12 is the motivating case and the
  first eval fixture: Ansible reported a return code and nothing else, because
  the task read `.stdout` while dotagents writes errors to `.stderr` — finding
  the cause took reading the `@sentry/dotagents` source. The agent's first job is
  the cheap one: name which stream the message went to, which lifecycle tag and
  topic failed, and whether the deployed tree matches the chezmoi source. Then it
  works the known failure classes, one skill each, added as they are met —
  unmigratable state at a destination (`roles/guards/`), a missing dependency, a
  pinned ref that moved (`apps/chrome`), a source edited but never applied. Done
  when a deliberately broken topic run yields a named cause and a next action
  without a human opening task YAML. [me]
- **Extend `dotfiles-triage` from naming a cause to proposing the fix, as a
  guarded PR.** Build on the public, vendor-neutral prior art, not on Sentry's
  Seer: `getsentry/seer` is `visibility: internal` (confirmed 2026-09-12 via
  `gh api repos/getsentry/seer`), so it is not a source this repo may read from,
  and nothing about the pattern requires it. The documented loop is older and
  plainer than any product — fail, halt, investigate, produce an RCA, open a PR
  carrying the RCA as its description, let a human merge. Target CARM L3
  (diagnose + propose) and stop there: **never self-apply**, which is the same
  never-auto-repair rule `roles/guards/` already follows and for the same reason.
  Every guard in `roles/guards/` is a detector that already knows its own fix
  text, so they are the natural first inputs. Done when a deliberately broken
  topic run produces a branch and a PR whose description is the RCA, and no run
  can mutate the machine without a human merging.
  **Three controls make this safe enough to run on a work machine, and they are
  cheap.** (1) A source-provenance note per design decision, naming the public
  page it came from — the tractable half of clean-room, minus the pretence that
  one person can staff two teams. (2) An explicit read-exclusion list, not one
  path: `~/code/work/sentry/` (a Seer clone sits at
  `~/code/work/sentry/what-would-kobby-do/seer`) **and** the unlicensed internal
  skills now sitting in the user-global skill path. "Do not consult it" has to be
  a rule the tool enforces, not an intention. (3) The existing fail-closed
  resolver (`bin/policy`, ethics > company > personal) gates anything that
  matters off this machine: remote model calls, log bodies, reading outside an
  allowlist. Nothing new is invented for safety; it is provenance plus the gate
  already built and tested. [me]
- **Install `tools/skill-trust` from a topic instead of by hand.** The guard in
  `roles/guards/` now shells out to it, so a machine without it provisions no
  further — correct, but the fix is currently a human running
  `uv tool install <chezmoi source>/tools/skill-trust`. That is the bootstrapping
  shape `apps/opencode`'s brew check already has: a topic should own it, and
  `tools/` will grow more inhabitants with the same need. Decide whether that is
  a `tools` topic installing everything under `tools/`, or each consumer
  declaring what it needs. Note where it lands: `tools/` sits at the chezmoi *source root*, so it
  deploys to `~/tools/`, not to `~/dotfiles/tools/` beside the Ansible tree —
  a topic would install from `~/tools/skill-trust`. Worth deciding whether it
  should deploy at all: if the tool is installed rather than cloned, the copy
  in `$HOME` is redundant and `.chezmoiignore` should skip it. Done when a fresh
  machine gets skill-trust without anyone typing a uv command. [me]
- **Render `support-escalation`'s SKILL.md, or retire it.** Moving it into
  `ai-prompt-library` on 2026-09-12 revealed it had never been a working skill:
  spec.md, 5 eval fixtures and a legacy `.skillet.yaml`, but no SKILL.md, so
  nothing could load it — it sat in the user-global path for two weeks doing
  nothing. `skillet status skills/support-escalation` will report the legacy
  format first; migrate that before rendering. Until a SKILL.md exists dotagents
  cannot discover it, which is the correct state for something unfinished. Done
  when `skillet validate` passes and it installs from the wildcard, or the
  directory is deleted and this line with it. [me]
- **Make the commit-proportionality escape graduated instead of binary.**
  `Proportionality:` currently short-circuits `verdict()` before the budget is
  computed, so it does not tolerate variance — it switches the check off for that
  commit, permanently and invisibly. The evidence that this is the wrong shape is
  the usage record: **one use in 449 commits, and that one was unnecessary** —
  193 words against a 220 budget on 10ccccd, added pre-emptively after the
  previous commit was rejected. An escape easier than thinking gets used without
  thinking. Three changes, in this order:
  (1) **Bound it.** A trailer grants a multiplier on the budget, not exemption —
  and a hard ceiling no trailer can exceed, so an essay still fails.
  (2) **Type it.** A small vocabulary — `security`, `deletion`, `migration` —
  each with its own multiplier, free text after the category. That makes the
  *why* greppable, which is what turns the escape into something auditable rather
  than a hole. An unrecognised category earns no bonus, so the choice is a known
  reason or a split.
  (3) **Close the loop.** Report at commit time when an escape was not needed
  ("this would have passed with 27 words to spare"). Nothing today can notice a
  false positive, which is exactly why the only one went unnoticed.
  Deliberately **not** doing diff-derived modifiers (test ratio, additions vs
  deletions) yet: they sound the most contextual and are the most likely to be
  wrong. A test-ratio bonus would have penalised this session's best commits,
  which were mostly tests, and it is trivially gamed. Add derived signals only if
  the audit from (2) shows a category is systematically mis-sized. Use the
  existing `--calibrate` mode to check any multiplier against history before
  adopting it — and heed the script's own warning that fitting to the corpus
  encodes the habit as the standard. Done when a message over budget with a typed
  reason passes within its multiplier, the same message without one fails, an
  essay fails either way, and an unnecessary escape is reported as such. [me]
- **Define an `agentic-context-engineer` role and add it to the ai library.**
  A role, not a skill: it is invoked deliberately for open design questions,
  wants its own context, and returns a considered answer — where a skill changes
  how the current work is done. Distribute it as a `[[subagents]]` entry rather
  than hand-placing a file in `~/.claude/agents`, so it installs the same way the
  skills do and survives a rebuild (dotagents projects subagents to
  `~/.claude/agents/*.md` at user scope; confirmed 2026-09-12). The role must
  **compose** the existing method skills — `review-best-practices`,
  `interaction-questioning`, `no-ai-slop` — and add only framing and judgement on
  top; a persona that restates method it could have loaded is the failure mode
  here. Done when `/agentic-context-engineer` answers an open question with a
  recommendation and its rejected alternatives, and the definition installs from
  `ai-prompt-library` on a fresh machine. [me]
- **[4] Fill `~/.local/state/ai-policy/company.yaml`'s 22 TODO fields.** Decided:
  proceed top-down as proposed — `device.approved` gates the rest. Machine-local
  and unversioned, so it cannot be tracked here beyond this pointer. Agent-unreadable on this machine (permission rules) — existence is the author's to verify; do not treat as done-or-lost. Until it is
  filled, `fail_closed` means the company layer denies everything it is asked,
  which is safe and useless.
- **Work out why `fabric` on `$PATH` is 1.4.459, then retire that install.** The
  orphaned `v1.4.478` tree is gone (72M reclaimed, `mise` took its `v1`/`v1.4`/
  `vlatest` symlinks with it), leaving `1.4.459` beside the current `1.4.478`.
  `1.4.459` is not safe to remove yet: it is the copy on `$PATH` in at least one
  running shell, even though `mise which`, `mise env` and `mise ls` all agree on
  1.4.478 and nothing in this repo writes the stale entry. Looks like
  session-inherited env rather than config, but that was **not** confirmed — a
  clean shell had no fabric on `PATH` at all, so the test proved nothing. Done
  when a brand-new terminal is checked: if it reports 1.4.478 this was stale env
  and `mise uninstall github:danielmiessler/fabric@1.4.459` closes it out; if it
  reports 1.4.459 something is writing that path and the uninstall would break
  a working command.
- **Drop the `npm:@sentry/skillet` pin in `apps/mise/files/config.toml` to
  `latest`.** The pin sat at 1.7.0 since 2026-09-11 because mise's npm resolver
  (aube) could not fetch vite's 39 MB packument through
  `sfw.security.sentry.io` — `curl` and `npm` both can, so it is a mise-side
  limit, not registry or auth. **Resolved 2026-09-14: 1.8.0 verified working
  here** (`skillet validate .` exits 0; 1.8.0 was already installed, and `mise
  install` pruned 1.7.0 — reinstall it via
  `mise install npm:@sentry/skillet@1.7.0` if ever needed), committed as
  ee09e38. What remains before the pin drops to `latest`: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, decide
  whether the four `npx @sentry/skillet@latest` task aliases stay floating
  (they align once the pin is `latest`), and `spec.md`'s 1.7.0 pin plus the
  `docs/REFERENCES.md` row need aligning — that alignment is queued there
  already. Done when the config says `latest`, the pin-print tells the truth,
  and the spec/REFERENCES rows agree with it. **Changelog-read blocker,
  recorded 2026-09-15:** the REFERENCES standard (read the 1.7.0→1.8.0
  changes before moving the pin) cannot currently be satisfied from this
  machine — the source repo is not accessible (the getsentry org is
  SAML-blocked; npm metadata carries no repository URL) — so the pin stands
  on local evidence only and the read must happen from a machine with
  access. **Read DONE 2026-09-15, on this Mac after all** — the block was
  the second machine's. The 1.7.0→1.8.0 compare (5 commits) shows grammar
  and exit codes untouched; the change is diagnostics (the no-eval-case
  warning was deleted) and the authoring workflow (evals opt-in). Pin
  aligned at 1.8.0 across `config.toml` and the spec footer (94389a5);
  REFERENCES records the read. What remains of this task: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, and the
  four `npx @sentry/skillet@latest` aliases need a float-vs-pin decision.
- Install `ty` and typecheck the Python. Named in the house toolchain and
  currently absent — not installed, zero references in the repo. 32 test files
  and 36 PEP 723 scripts are unchecked. Note `ty` is pre-1.0; decide whether it
  gates commits or just reports before wiring it into `prek`.
- Wire `ruff` into `.pre-commit-config.yaml`. It is installed and the toolchain
  names it, but the hook config runs shellcheck and bats only, so no Python file
  in this repo is linted on commit. Settle the ruleset first — 36 scripts written
  before any linter will not pass a default config cleanly.
- Integrate `xdoctest` and make illustrative examples a tested part of the
  docs. Docstring examples in the 36 PEP 723 scripts and any Python modules
  run under pytest via the xdoctest plugin; docs (`dotfiles/docs/`, READMEs)
  carry code examples where they clarify, verified rather than trusted —
  written for humans first, machines as the proof they still work. Survey the
  ecosystem before building anything: xdoctest for docstrings, and for fenced
  blocks in markdown weigh sybil / pytest-examples / a pytest-markdown runner
  before hand-rolling one. Done when: xdoctest is in the documented pytest
  command (AGENTS.md § Commands), docstring examples in `bin/` are collected
  and green, `docs/PYTHON.md` records the convention (what must carry
  examples, how to write and run them), and a markdown-example mechanism is
  either adopted or consciously rejected with the reason recorded. Pairs
  with the plain-language standard item — examples are prose too.
- Make test conftests skip rather than error on a missing optional dependency.
  `tests/ollama_evals/conftest.py` loads the eval harness as a module, and the
  harness imports Pillow at module level, so without `--with pillow` the whole
  directory produces 53 collection errors instead of 52 passes — the suite
  aborts instead of running what it can. Same class as the hypothesis guard
  fixed today, one layer deeper: the import happens before pytest can skip
  anything. `pytest.importorskip` in the conftest is the likely fix, but check
  what else the harness pulls in at import time first.
- Check AGENTS.md and CONTRIBUTING.md for places the agent→function
  graduation policy should apply, and reference the policy artifact from
  `ai-prompt-library` once it exists. The bias: prefer a trusted function
  over agent judgment where the task is mechanical; agents stay for
  adaptability and interpretation (high-context tasks — deciding what to do,
  how to succeed). **[blocked: the threshold research and council decision
  are owned in ai-prompt-library's TASKS.md — no text lands here until the
  artifact exists.]**
- Sweep committed machine-adjacent strings, per the audit in
  `dotfiles/docs/MULTI-MACHINE.md` (2026-09-12). The audit found: employer-
  adjacent paths (`~/code/work/sentry/`, `sfw.security.sentry.io`), the §
  Private tasks section describing the work it points to (obfuscation that
  signals itself), environment mentions ("work machine", "the second
  machine", "a Seer clone", "the work workspace"), and session-claim
  provenance narration. Rewrites generalize to environment-neutral classes;
  the purge of employer strings itself stays under § Private tasks. Done
  when a grep over the committed tree for the audit's patterns comes back
  clean and the MULTI-MACHINE design's generalization test is applied to
  every rewritten line. **Wait for the council verdict first** — the council
  may change what "bounded pointer" means before the sweep rewrites
  pointers.
- Decide when `scriv collect` runs. The changelog exists and fragments
  accumulate, but nothing says what a "release" is for a dotfiles repo that does
  not release. Candidates: on a cadence, at each machine rebuild, or never —
  leaving everything under Unreleased, which is legitimate and costs nothing.
  Until this is settled the changelog grows one section and is still readable.

## Planned


- Reconcile `tests/permissions/test_permission_tiers.py` with the deliberate
  settings change `9df508d`: history rewriting (`git filter-repo`) moved from
  deny to ask in `.claude/settings.json`, but the tier test still asserts
  deny — so the full suite reports 1 failed / 631 passed (observed 2026-09-19
  during the herdr work; the failure is environmental, not new). Decide
  whether the test follows the settings (policy intent: ask) or the settings
  revert (policy intent: deny) — that is a PERMISSIONS.md decision, not a
  test-side edit.

- Migrate the mise `python.uv_venv_auto` setting before mise 2027.7.0 removes
  it — mise warned the deprecation during the herdr work (2026-09-19:
  `python.uv_venv_auto=true` must become `python.uv_venv_auto="create|source"`
  or `"source"` in `apps/mise/files/config.toml`).

- **Build the subscription machinery: `topic_subscribes` + playbook
  resolution + injection.** The mechanism half of the adopted system-config
  model (resolved council entry, `TASKS-RESOLVED.md` 2026-09-17): a topic
  declares `topic_subscribes: [<catalogue>]` in `topic.yml`; the parent
  playbook validates each subscribed catalogue exists as
  `dotfiles/config/<catalogue>.yaml` (unknown catalogue fails loudly naming
  both sides), resolves each subscriber's slice — entries matching that
  consumer, availability verdicts applied — and injects it as a var;
  topics carry only a thin install-and-report loop over the list they were
  handed, so unresolvable verdicts fail at the playbook layer before
  anything installs. Resolution lives in `roles/`, per the
  `roles/topic-resolution` precedent (playbook pre_task logic extracted
  2026-09-15 so the playbook stays readable and the logic is testable —
  `tests/topic_resolution/` is the shape to follow). **Gated on the
  normative topic spec landing first** — the subscribes key is `topic.yml`
  schema the spec governs — and on the catalogue seed in § Now. Tests
  first and mutation-proven per `spec.md` § Verification; the resolution
  filter is pure set/merge logic, so it takes a property test. Done when
  resolution is tested, the playbook fails loudly on an unknown catalogue
  or an unresolvable verdict, and the injected-var contract is documented
  in `dotfiles/docs/TOPICS.md`. [me]
- **Switch the visual-studio-code topic from the interim direct read to
  playbook injection.** The topic is already wired (2026-09-17, § Now):
  install/remove/upgrade consume `config/editors.yaml` through a
  role-relative direct read with the thin loop and gated teardown. When
  the subscription machinery above lands, replace the direct read with
  `topic_subscribes` + the injected slice — behavior must not change, and
  the switch is proven by being a no-op on the converged machine. Done
  when the direct read is gone, `--check --tags provision` still converges
  (changed=0), and the topic's CHANGELOG records the switch. [me]
- **Wire the cursor topic and align it with the catalogue contract.** Same
  contract as vscode: thin loop, gated `cursor_remove_extensions`,
  currency — wired interim by direct read like vscode, switching to
  injection when the machinery lands. The first real run settles the
  pylance-class verdicts live and exercises the `substituted` tolerance
  for `anysphere.cursorpyright` (probe evidence in the topic's CHANGELOG;
  its catalogue entry sits in `editor_extensions_ignored`). Done when
  `run-role.sh cursor` converges from the catalogue (author applies),
  verdict lines print per entry, and the topic's CHANGELOG records the
  contract. [me]

- **Decide whether to add the `opencode-sentry-monitor` plugin to the
  `apps/opencode` topic, and if so how.** Queued 2026-09-16 from the author's
  request, which the agent stopped on. The npm package (MIT, v0.1.7,
  `opencode-sentry-monitor`, by Scott Tolinski) is an OpenCode plugin that
  captures session lifecycle, tool-execution spans, and token usage, and by
  default also tool inputs/outputs and model request/response text
  (`recordInputs`/`recordOutputs` default `true`), then ships them to a Sentry
  project. That is an egress path, and `dotfiles/policy/ethics.yaml` forbids
  egress that is automated end-to-end or bypasses human review
  (`egress.may_be_automated_end_to_end: false`,
  `egress.may_bypass_human_review: false`) while `spec.md` § Policy requires
  every sending tool to consult `policy check` and treat unknown as denied. A
  third-party plugin cannot call the resolver. **Do not add it without the
  author's explicit decision — the telemetry is the whole question.** If
  approved, the shape is an npm entry in `apps/mise/files/config.toml` plus a
  `plugin` entry in `dot_config/opencode/opencode.jsonc.tmpl`, with the egress
  override recorded as an author decision and the recording flags settled.
  Done when the author has answered and the answer is recorded or the plugin
  is wired. [me]
- **Make opencode permission rules deterministically editable, per config
  (project or global).** Queued 2026-09-16 as the other half of the
  permission fix. Hand-editing the JSONC is error-prone in a specific,
  demonstrated way: opencode matches the **last** rule (`evaluate` uses
  `findLast`; `fromConfig` keeps declaration order), so a trailing
  `"*": "ask"` silently shadows every allow above it and every `deny`
  carve-out anchored below it. The global config shipped that bug until
  2026-09-16 — `git`, `find`, `wc` and `echo` were declared but inert, and
  `find . -delete` fell through to `ask` instead of the intended `deny`. The
  tool must read and write JSONC without dropping comments or reordering
  keys; set or update a rule in a named config (a project `opencode.json`, or
  the global `~/.config/opencode/opencode.jsonc`, which here is a chezmoi
  templated source); normalise the ordering invariant (catch-all first,
  carve-outs after the allow they narrow); and report the merged effect of
  global + project rules for a command, since the scopes deep-merge and the
  project scope wins. **Not the right place to build this now.** It is a tool
  build (AGENTS.md ladder, so route before writing code), it belongs with
  `topical` — the CLI the ROADMAP gives the "abstracts configuration
  management and updates" job, itself scheduled A1–A7 and unlanded — and it
  depends on `apps/opencode` owning its own config (the integrations-phase
  task in § Now) and on the tooling destination (ai-prompt-library /
  llocallabs, per the move manifest). If that route is declined, say so in
  this line rather than starting a script here. Done when the destination is
  decided and a command idempotently updates a named opencode config's
  permission rules, preserves the file's comments and key order, enforces the
  ordering invariant, and is proven by a test that catches a reintroduced
  trailing catch-all. [me]
- **Design the replacement for the TASKS.md state-and-handoff process.** The
  queue has become a second codebase: a handoff snapshot two machines rewrite
  under each other (the 2026-09-14 merge conflict was predicted and then real),
  resolved tasks with no home (the stopgap `TASKS-RESOLVED.md` exists for
  exactly that), claims, hazards, standing reminders, and five governance docs
  all pointing at each other. Design what replaces it — what state lives
  where, how two machines merge without hand-reconciling prose, how resolution
  is recorded without growing a second file — and get the author's approval
  before cutting TASKS.md to match. Done when a written design exists, the
  author has approved it, and the re-cut file (or its successor) passes
  `tests/tasks_doc` with the resolved-tasks stopgap retired. Handoffs get an
  advisor review before taking effect — the 2026-09-14 review ran with the
  producing agent alone, exactly the self-certification the panel-of-judges
  item warns about — so the design must make the advisor pass real rather
  than optional. **Advisor pass v1 has now run** (2026-09-15): three
  fresh-context subagents — records auditor, red-team critic, cold-start
  usability — reviewed the session's records and decisions; intra-model by
  weights, independent by context and brief, and it caught real errors the
  self-review missed (a wrong diagnosis, an asymmetric routing test, a
  bypassed verification standard). Findings are applied or queued in this
  file. The design must still supply an independent-model pass and must NOT
  pre-commit whether multi-agent review beats self-review — that is the
  panel-of-judges research's measured question. [me]
- **Research agent sandboxing for projects and user tasks on this machine —
  deep research, debated with a council of advisors, delivered as a two-phase
  project with a spec binding them.** The permission tiers in
  `docs/PERMISSIONS.md` gate what tools agents may run but do not isolate
  what a permitted tool can touch — sandboxing is the layer they cannot
  provide. **Phase 1 — requirements.** Write the spec: what is being
  sandboxed (agents working in project directories, agent-driven user tasks
  on the machine), against which threats (egress, writes outside declared
  scope, credential access, machine-config mutation), under which constraints
  (macOS and Debian targets, one machine-management repo, the existing
  `bin/policy` boundary model, agents never applying chezmoi). Debated with
  the council before the author approves it. **Phase 2 — apply.** Update the
  spec with what the research taught and land the background knowledge where
  it is consumed: `bin/policy` boundary keys, the agent permission layers,
  and topic/machine configuration — as queued tasks citing the spec, never
  implemented silently. Initial leads, author-provided 2026-09-14, fetched
  and verified that day: wincent's "Coding Agent Sandboxes — Comprehensive
  List", a taxonomy from OS primitives to policy layers
  (https://gist.github.com/wincent/2752d8d97727577050c043e4ff9e386e);
  "Sandboxing AI coding agents with Lima", VM-grade isolation with
  near-native UX, naming egress and forwarded secrets as the unsolved gaps
  (https://bogoyavlensky.com/blog/sandboxing-ai-coding-agents-with-lima/);
  and `nono`, least-privilege per-agent and per-tool sandboxes with a
  credential proxy and L7 filtering, Apache-2.0, from the Sigstore team
  (https://github.com/nolabs-ai/nono). The council debate pairs with the
  panel-of-judges item below — settle that first or borrow its method.
  Lead from the second research capture (2026-09-14,
  `~/code/personal/llocallabs-capture/`): Omnigent —
  **[verified]** Apache-2.0 and active — claims bubblewrap (Linux) /
  Seatbelt (macOS) sandboxing with cost tracking across agent CLIs.
  **A lead, not a selection** — the capture's other options were routed by
  subject and verification: nono and Lima remain the primary leads
  (capture #1); Caliber generates config rather than sandboxing (its own
  evaluation task); AgentMD is a claimed-frozen spec; OpenCtx is archived
  in favour of MCP; ctx-open is unlicensed and stale (reference only);
  Backlog.md and `handoff` are session-state tools (routed to the
  session-management research); Podman-on-macOS is a constraint input, not
  a candidate. Verification so far is first-order only — existence,
  licence, activity; Omnigent's enforcement claims and its claimed
  Databricks backing are UNVERIFIED and come from the same AI-generated
  source that produced the Caliber npm-scope discrepancy.
  **Post-advisor demotion:** the routing test was applied asymmetrically —
  Omnigent's own description is orchestration-first with sandboxing as one
  feature, so it fails the same subject test that excluded Caliber. Treat
  it as contextual reference for the debate, not a peer lead, and note the
  lead-admission bar silently moved from author-provided to capture-sourced:
  capture-sourced leads need deeper verification before entering the
  council debate. The Podman-on-macOS constraints (hidden Linux VM, nested-virtualization
  limits, network rules applied inside the machine rather than the host)
  still stand as phase-1 requirements for the macOS target. Lead from the
  author 2026-09-15, verified same day: `opencodebox`
  (https://github.com/fityannugroho/opencodebox) — MIT, a bash wrapper
  running opencode inside a bubblewrap sandbox with namespace isolation,
  read-only system mounts, per-project read-write binds, a seccomp filter
  for recent socket CVEs, and refusal to run from sensitive dirs.
  **Linux-only** (bubblewrap needs Linux namespaces), so it is a Debian-side
  candidate, not a macOS answer — and a concrete reference for the
  per-project bind-mount shape on that target. Small and new (3 stars, 34
  commits): first-order verification only, like the other capture-sourced
  leads. Done
  when the phase-1 spec exists, the council debate is recorded, the author
  has approved the requirements, and phase 2's changes are queued rather
  than imagined. [me]
- **Research agent session management and inter-session handoff — deep
  research with expert involvement at both ends: shaping the questions, then
  debating, reviewing and critiquing the author's ideas.** The motivation is
  this repo's own pain: a handoff snapshot two machines rewrite under each
  other, sessions keeping private in-memory queues, a stopgap archive for
  resolved work, and the TASKS.md process-refactor design queued above —
  this research feeds that design. Author-provided starting point
  (2026-09-14, verified): the video "/handoff is my new favourite skill"
  (https://www.youtube.com/watch?v=dtAJ2dOd3ko); the author's accompanying
  skills links were shared as a YouTube redirect to
  `https://aihero.dev/s/YL1zWx`, which 404s — re-fetch or re-share before
  relying on it. A second research capture the same day supplies candidate
  tools to evaluate rather than rediscover: Backlog.md (**[verified]** MIT,
  active — git-native tasks with a drafts→tasks promotion flow and MCP
  exposure), the `handoff` CLI's six-file `.handoff/` session-state layout,
  the `.context/` directory convention, and ctx-open (**[verified]**
  unlicensed and four months stale — design reference only under
  absent-is-not-permissive); raw material in
  `~/code/personal/llocallabs-capture/2026-09-14-agent-tooling-research.md`. The
  research learns the process and approaches first; the
  council's role is two-sided: weigh in on WHAT the deep research should
  ask, then debate, review and challenge the author's candidate ideas with
  critique before any task is cut. Done when the findings exist, the
  council's question-shaping and critique rounds are recorded, and — with
  the author — a decision is made whether to queue configuration tasks for
  AI and agents here, which would touch AGENTS.md § Working alongside other
  sessions and the TASKS.md process design. [me]
- **Research RAG and knowledge graphs for preprocessed agent context —
  deep research with expert involvement at both ends, same pattern as the
  sandboxing and session-management projects.** The problem: knowledge the
  agents rely on — this repo's governance docs, the policy layers,
  dependency research, eval histories — is reprocessed from raw tokens
  fresh in every session, expensive and bounded by context limits.
  Preprocessing it into well-structured, fetchable context (retrieval,
  graphs, or whatever the research supports) trades a one-time build cost
  for a per-session saving. Learn the approaches first; the council shapes
  what the deep research asks, then debates and critiques candidate designs
  before anything is built. Any build is a llocallabs candidate — it is AI
  tooling — while the consumption points are here and in the llocallabs
  agent. Pairs with the `agentic-context-engineer` role queued in § Now,
  the hand-rolled ancestor of the same idea. Done when findings exist, the
  council rounds are recorded, and — with the author — a decision lands:
  adopt, adapt, or reject, with any follow-on tasks queued citing the
  findings. [me]
- **Verify and evaluate Caliber (`caliber-ai-org/ai-setup`) as an
  agent-config generator.** Lead from the author's research capture,
  2026-09-14, raw paste preserved at
  `~/code/personal/llocallabs-capture/2026-09-14-caliber-ai-setup.md`: a
  MIT-licensed CLI that scans a codebase locally and generates agent config
  files (AGENTS.md, .cursor/rules, CLAUDE.md), claiming a generic mode,
  BYO-key deep generation, and opencode/dotagents compatibility. The
  capture is an AI-generated summary — **UNVERIFIED**, and the
  load-bearing claims are exactly what `review-best-practices` exists to
  check: the local-vs-API split, the npm scope (`@rely-ai/caliber` in the
  paste vs `caliber-ai-org` on GitHub — one is wrong), the claimed
  `.skill.md` export for dotagents, and — decisive for this repo — whether
  it overwrites or respects an existing hand-maintained AGENTS.md, which
  would disqualify it here while leaving llocallabs's scaffold as a
  legitimate consumer. Second capture, same day: the npm scope is explained
  as the **for-profit entity behind the tool** (`@rely-ai`, enterprise
  portal at trycaliber.ai with a sales desk) — so the scope mismatch is an
  open-core-trajectory question to track, not just a typo; `caliber
  refresh` drift protection via pre-commit hooks and MCP recommendations
  are further claims to check. **[verified 2026-09-14 via `gh api`: MIT,
  not archived, but last push 2026-07-26 — ~7 weeks stale by the 30–45-day
  maintainership criterion.]** Coupling: the general copier template queued
  below generates the same class of files, so this evaluation answers for
  both. Done when the claims are checked against the actual repo, a
  use/don't-use decision is recorded with the author, and any adoption is
  queued as tasks. [me]
- **Create a `git` topic that owns git config and extensions; git-ai is its
  first extension.** Git config is not managed at all today — no
  `dot_gitconfig` in the source, no `apps/git` topic — and the git-ai
  installer's edits are hand-placed: a `~/.gitconfig` written 2026-09-13
  (plain file, unmanaged), the `~/.git-ai/bin` PATH export appended to
  `~/.zshrc` (the one two-way-drifted file), plus any hooks or bin entries it
  installed. **Machine-stamped:** that installer ran on the *second machine*
  — this Mac has no `~/.git-ai` and no git-ai block in `~/.zshrc`
  (verified 2026-09-15), so the audit starts there, not here. Audit everything the installer touched first, then build
  `dotfiles/apps/git/`: it owns the gitconfig as a chezmoi template where
  machine-specific, installs extensions as declared dependencies rather than
  curl-installers, and carries the shell integration the installers keep
  hand-appending — the PATH line moves into the topic's shell-integration
  fragment (or `zsh/path.zsh` if it stays a zsh concern), never the deploy
  target. This supersedes the earlier zsh-fragment framing: git-ai is a git
  extension and belongs beside git config, not scattered into zsh.
  **Open research question — settle before writing install tasks:** is git-ai
  provisioned machine-globally, or per project? Per-project config on this
  machine lives exclusively in the mise `config.toml` files at each project
  root, so a per-project answer must route through that file (mise
  `[tools]`/env/tasks) rather than a global gitconfig hook. Research what
  git-ai actually scopes — global hook, per-repo config, PATH shim — and what
  mise's per-project config can express, then take the decision to the author.
  The answer decides what replaces the installer's hand edits. Until it
  lands, a full `chezmoi apply` would delete the installer's lines from
  `~/.zshrc`, so apply everything else selectively (`chezmoi apply ~/dotfiles
  ~/.config/opencode ~/tools`) and leave `~/.zshrc` out. Done when `apps/git`
  installs cleanly on this machine, git-ai works from a fresh shell with no
  hand-edited line left in `~/.zshrc`, `diff <(chezmoi cat ~/.zshrc) ~/.zshrc`
   no longer shows the git-ai block, and the live `~/.gitconfig` is the one the
   topic owns. [me]
- **Study `pkgup` and turn its migration to the topic format into a queued
  collection of tasks.** The script is not in this repo — it is the Debian
  box's package updater (nothing named `pkgup` in the source, `~/bin`, or the
  zsh fragments on this Mac; the macOS sibling here is `~/bin/upgrade-all.sh`,
  which orchestrates `softwareupdate` and `brewup.sh`). The study is the
  initial task: read the script where it lives, inventory every package
  manager it drives, compare each against the existing topics (`apps/apt`
  exists; brew's upgrade path lives in the homebrew topic), then queue one
  migration task per manager or coherent clump — each in the topic format
  with `topic.yml`, the install/upgrade/remove lifecycle, and a per-topic
  test suite. **[blocked: root-level become permissions — an unattended
  topic cannot run apt until the dedicated-ansible-user task's sudoers grant
  enumerates the package-manager commands; do that privilege work first.]**
  Done when the collection is queued in TASKS.md, each task names its
  manager, its topic home and its teardown, and any non-manager logic left
  in the script has an owner or a retirement note alongside A10's `~/bin`
  sunset. [me]
- **Study gita across the machines and decide its topic's shape.** The
  author wants `gita` to manage the set of repositories that should be
  shared or present on one or more machines — add and update flows through
  one tool instead of ad-hoc clones. Two things before the topic exists:
  detect what already exists (gita config at `~/.config/gita/` on each
  machine is unmanaged today and may not exist on both), and build the repo
  inventory per machine — which repos exist, which are wanted where, at
  what remotes — because the topic can only declare what the agent
  understands. Machine granularity is the design constraint: the repo set
  is a per-machine decision resolved on the target (the machines.yml group
  map is the settled design — the file now EXISTS, created 2026-09-15 as
  `dotfiles/machines.yml` under `docs/LAYOUT.md`, with this Mac's
  membership recorded), never one flat list for the fleet.
  **Learnings from the 2026-09-15 registration pass on this Mac — the
  topic's config must encode these so they are not re-learned:**
  (1) `gita add <dir>` without `-r` registers only depth-1 repos and
  reported "No new repos found" while 48 repos sat 2-4 levels deep under
  `~/code/work/` — the topic's registration flow must recurse.
  (2) Duplicate basenames collide silently: one registration per name, the
  second repo dropped (`symbolicator`, `sentry-docs`,
  `sillysnakes-python-sdk-playground-1-29-26` across org dirs). The
  inventory must detect dupes and either rename or declare the drop
  deliberate; membership lists cite paths, not names (LAYOUT.md).
  (3) Recursive discovery must exclude `.venv` — the generator's find
  swallowed pip-vendored content (`temporalio/bridge/sdk-core` inside a
  virtualenv); same filter class as `.chezmoiignore`'s `**/.venv`.
  (4) `gita ls` prints all names space-separated on ONE line — verify
  counts with `wc -w`, never `wc -l`.
  (5) `~/.config/gita/repos.csv` is unmanaged today; this session's
  51-repo registration is the de facto baseline the topic's inventory
  should ADOPT, not rediscover. Done when
  existing-config detection is written, the per-machine inventory is
  recorded, and a decision — with the author — fixes the topic's shape:
  declared repo sets versus gita's group semantics, install via
  `topic_requires`, and where the config lives; queued as the
  topic-creation task it feeds. Collision surface, named per the
  decomposition rules: `apps/git` (the git-ai topic task above) is also
  git-adjacent — decide whether gita's config rides in it or a second topic
  coexists, before either is scaffolded. [me]
- **Harden cosine beyond the subnormal guard: the overflow tail and scale
  invariance.** The advisor pass found what 6c3079b's guard missed. Two
  tails: an overflow tail where sums overflow to inf and the quotient
  becomes NaN — and the coverage classifier counts NaN as classified
  (`nan < args.min_margin` is False), the exact "unknown becomes a claim"
  shape; and the guard breaks scale invariance (parallel tiny vectors score
  0.0), which no property test pins and which the centroid classifier hits
  for near-centroid prompts by construction. Candidate fix: max-abs
  pre-scaling (preserves invariance, fixes both tails), plus a
  scale-invariance property, a NaN-cannot-classify assertion, and an eval
  case pinning near-centroid behavior. Done when the properties exist, the
  counterexamples are pinned, and the mutation check shows the old guard
  failing them. [me]
- **Decide the capture-store contract: private/shareable separation,
  versioning, retention.** The llocallabs capture store
  (`~/code/personal/llocallabs-capture/`) is cited by five tasks as
  evidence, is unversioned and single-machine, and sits in one directory
  with private career notes — one careless copy puts private content in
  files future sessions are instructed to read. Decide: separation (a
  private/ subtree or a separate store), versioning or sync for cross-machine
  cluster work, retention and backup (feeds the backup-design item). Done
  when the contract is written, the author has approved it, and the store is
  reorganized to match. [me]
- **Run the lessons-learned advisor pass — captured 2026-09-15, deliberately
  not run to completion in its originating session.** The question: how to
  capture lessons from sessions, author-side (decisions, corrections, the
  30–60 second capture problem) and agent-side (the primary session and its
  advisor roles), such that they survive and become durable mechanisms. The
  complete advisor tasking — the ask plus two verbatim briefs (a designer
  and a red-team critic) and launch instructions — is preserved at
  `~/code/personal/llocallabs-capture/2026-09-15-lessons-learned-advisor-briefs.md`.
  A prior same-day run exists beside it as two per-brief files
  (`...prior-run-designer.md`, `...prior-run-redteam.md`, written by the
  advisors themselves): the re-running session runs the briefs FRESH and may
  use the prior output for comparison or ignore it — never as an anchor.
  Triage every finding through AGENTS.md § Observations are deliverables:
  edit the mechanism, queue a task with a done-condition, or drop. Feeds
  the R&D factory stage one and the session-management research — do not
  build a parallel system beside them. Done when both briefs have been
  re-run fresh, the findings are triaged with the author, and any mechanism
  edits are queued or landed. [me]
- **Extend `tests/tasks_doc` to fail on referenced paths that do not exist.**
  The advisor pass found dangling references a validator would catch
  mechanically: `run-role.sh` unprefixed in AGENTS.md, `machines.yml`
  described as existing when it was a design, `.chezmoiignore` line-number
  decay, a task line naming one file twice where two were meant. Scope:
  parse backtick-quoted repo-relative paths and check existence; fail on
  section-heading mismatches. Done when the validator catches a deliberately
  planted dangling path (mutation-checked). [me]
- **Bring the portable half of `~/.claude/` under chezmoi.** Deferred from the
  claude-code topic (`c988fef`), which owns the binaries and deliberately left
  config alone. Nothing there is versioned today, so user-global settings do not
  survive a machine. The work is the split, not the plumbing: `settings.json`,
  `CLAUDE.md`, `agents/` and `commands/` are portable, while `history.jsonl`,
  `projects/`, `session-env/`, `daemon/`, `backups/`, `file-history/` and
  `~/.claude.json` are machine-local and must never be committed — the last of
  those holds credentials. chezmoi owns the files once split, per the layering
  rule in `AGENTS.md`; the topic does not template them. Two hazards worth
  knowing before starting: the VS Code extension, the JetBrains plugin and the
  desktop app all write `~/.claude/`, so the directory is not Claude Code's
  alone; and `apps/opencode` already owns `~/.agents/skills` via dotagents,
  which Claude auto-loads, so nothing here may write skills. Done when the
  portable files deploy from the chezmoi source on a fresh machine, `chezmoi
  status` is clean afterwards, and no machine-local state or credential has
  entered git.

- **Extend `apps/claude-code` to Debian via the signed apt repository.** The
  topic is `topic_os: [Darwin]` because Homebrew casks are macOS-only, so the
  Debian box has no managed Claude Code at all. Upstream publishes a signed apt
  repo rather than expecting the native installer: keyring at
  `/etc/apt/keyrings/claude-code.asc`, fingerprint
  `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`, and — the part that bites — both
  the URL path *and* the suite name change between channels
  (`.../apt/stable stable main` versus `.../apt/latest latest main`), so
  `claude_code_cask`'s stable/latest choice needs a Debian equivalent rather
  than reuse. Needs `become: true` for the keyring and sources file, which no
  part of this topic currently requires. Note apt installs do not auto-update
  through Claude Code either, so currency still comes from the system upgrade
  pass. Done when the topic flips to `[Darwin, Debian]`, installs on the Debian
  box with the key verified before use rather than trusted blind, and
  `--tags remove` takes the repo file and keyring back out.

- **Extract the model benchmarking and scouting tools into their own repository.**
  Near-future and deliberate, not urgent — recorded now so it does not happen by
  accident. `bin/model-bench` is 1357 lines and `bin/model-scout` is 379, plus
  `apps/ollama/files/ollama-bench` and `ollama-evals`; that is a model
  evaluation toolkit living inside a machine-provisioning repo. It is also the
  clearest case of the `AGENTS.md` ladder: AI work belongs outside this repo,
  and benchmarking models is not configuring a machine. Same destination shape
  as `topical` — its own repo, installed back here as a normal tool by a thin
  topic, rather than vendored. Two things to settle before moving: the tools are
  referenced by name in `.claude/settings.local.json` allowlists and in launchd
  labels (`com.ollama-usage.snapshot`), so this shares the audit in A10 above;
  and `ollama-evals`/`ollama-bench` are topic-owned while the `bin/` pair are
  not, so the split is not along one clean line today. Done when benchmarking
  lives in its own repo, this repo installs it like any other tool, and nothing
  here imports it.
- **Create the `worktrunk` topic — the `wt` Git-worktree manager, installed
  via mise.** Parked by the author 2026-09-21 (write-and-forget, unassigned
  backlog). Binary through the mise `github:` backend per the
  `apps/mise/files/config.toml` convention (never `ubi:`); the mise registry
  entry is verified live — `mise ls-remote worktrunk` resolves through 0.79.0
  (checked 2026-09-21). `topic_requires: [mise]`, scaffolded per
  `dotfiles/docs/TOPICS.md`; settle the two chooser questions first (which
  machines run it, who upgrades — `dotfiles/docs/TOPIC-RECIPES.md`
  install-mechanism chooser) and apply the test-first recipe. [unassigned]
- **Add voice-typing topics: `apps/openwhispr` and `apps/superwhisper`, macOS
  first, with a Linux path that is not a cask.** Both exist as casks, verified
  2026-09-14: `openwhispr` 1.10.1 ("Privacy-first voice-to-text dictation with
  AI agents", open source, `OpenWhispr/openwhispr`) and `superwhisper` 2.18.3
  ("Dictation tool including LLM reformatting", commercial, macOS >= 14). Both
  declare `auto_updates`, so brew's recorded version drifts — the same
  `known_issues` entry `apps/claude-code` already carries for `Claude.app`.
  Start on Darwin because that is where the casks work; casks are macOS-only, so
  Debian needs a different mechanism and the honest first step is `topic_os:
  [Darwin]` rather than a half-built conditional, exactly as `apps/claude-code`
  did. For the Linux path, `whisper.cpp` is a cross-platform **formula** and is
  the likely base — note the handoff's "SoupaWhisper" sketch is essentially that.
  **An external briefing document exists for this work — not the session handoff
  above — and it does not describe this repo.** It assumes topics named `git/`, `zsh/`, `wayland/`, `macos/` and
  an `openrouter/` topic; this repo has Ansible roles under `dotfiles/apps/` with
  a fixed lifecycle, no `wayland` or `macos` topic, and OpenRouter reached
  through `apps/ori`. Translate it, do not follow it literally. What does carry
  over, and is worth keeping:
  - **No hardcoded credentials.** It wants `$OPENROUTER_API_KEY` from the
    environment rather than baked into a config file. That already matches
    practice here — `llm-openrouter` and `ori` both read it — and
    `AGENTS.md` § "Machine-specific values are resolved, never written out" is
    the rule it is reaching for.
  - **Wayland cannot be assumed.** Its text-injection rules (`ydotool`/`wtype`,
    `wl-clipboard`, adding the user to the `input` group for `/dev/uinput`)
    presuppose a Wayland desktop. **Verify the Debian box actually runs one
    before building any of it** — that is unconfirmed, and the whole Linux
    design rests on it.
  - **Hotkeys belong to the compositor, not the app**, with macOS parity via an
    Apple Shortcut or Automator action calling the same CLI. That shape is
    sound; it needs a real toggle command to exist first.
  **OpenWhispr on Linux is required, not optional** — Darwin-first is about
  sequence, not scope, and this one has to run on the Debian box too. Research
  it properly rather than assuming the cask story carries over; upstream already
  ships for Linux, verified 2026-09-14 against release `v1.10.1`:

      OpenWhispr-1.10.1-linux-amd64.deb        ← apt, matches apps/apt + become
      OpenWhispr-1.10.1-linux-x86_64.rpm
      OpenWhispr-1.10.1-linux-x86_64.AppImage
      OpenWhispr-1.10.1-linux-x64.tar.gz       ← tarball, the apps/ollama shape

  MIT, Electron, actively released. Prefer a package manager over a bare
  download — but note these are the *same* mechanism here, not alternatives:
  `ansible.builtin.apt` takes a `deb:` parameter and downloads it itself when
  given a URL, so "install via apt" and "fall back to the .deb" collapse into
  one task pointing at the release asset. Check first whether upstream publishes
  an actual apt *repository*, which would be better still since it makes
  upgrades ordinary; nothing in the v1.10.1 release assets suggests one, but
  that only rules out the release page. The tarball is the last resort and
  matches how `apps/ollama` already installs on Linux.

  **Architecture is confirmed: the Debian box is x86_64/amd64**, stated by the
  author 2026-09-14, so OpenWhispr's Linux builds apply and the `.deb` path
  stands. Worth keeping in view anyway, because it nearly went the other way:
  every OpenWhispr Linux artifact is x86_64 and there is **no arm64 Linux
  build**, while macOS ships both. Adopt the habit rather than the one-off
  answer — **check a release's actual architecture list before choosing a
  package format**, and prefer reading upstream's published metadata over
  assuming parity with macOS. `apps/ori` already does the honest version of
  this, resolving `arm64` vs `x64` from `ansible_facts` and verifying against a
  published `SHA256SUMS`. Second, the release carries
  `latest-linux.yml`, which is electron-updater metadata: the app self-updates,
  so it has the same two-owners question `apps/claude-code` answered for the
  desktop cask, and the answer has to be deliberate rather than inherited.

  Done when OpenWhispr installs, removes and upgrades cleanly on **both** this
  Mac and the Debian box — or, if the architecture rules it out, when that is
  recorded with the `whisper.cpp` alternative chosen — and superwhisper's
  Darwin-only status is stated as a decision rather than an omission.
- **Explore OpenTypeless before committing to it.** Named alongside OpenWhispr
  in the voice-typing handoff but not evaluated. Nothing is known here about its
  licence, its config format, whether it packages for macOS or Linux at all, or
  whether it duplicates what OpenWhispr already does. Deliberately an
  exploration, not an install task — `review-best-practices` is the shape, and
  the output is a recommendation with what was rejected, not a topic.
- **Give privileged topics a dedicated ansible user per environment, and a
  service that runs configuration updates.** Today the five apt-using topics
  (`docker`, `clamav`, `lynis`, `mise`, `ollama` — the only `become: true`
  topics, per `dotfiles/managers.yaml`) escalate through whoever happens to be
  running the playbook, which means an unattended update is impossible and an
  attended one carries the human's full sudo rights. A dedicated account fixes
  both: the service has an identity, and its powers can be smaller than a
  person's.
  **Scope the privileges before building anything.** A service that can apply
  machine configuration unattended is a standing grant, not a convenience — the
  sudoers entry should enumerate the specific commands the playbook actually
  needs rather than `NOPASSWD: ALL`, and `dotfiles/managers.yaml` already names
  which managers need escalation and which do not, so the list is derivable
  rather than guessed. `docs/PERMISSIONS.md` is the relevant prior art and is
  blunt that this layer stops accidents, not a misaligned or prompt-injected
  agent; a scheduled runner with root is exactly the thing that document warns
  is not contained by permissions. Decide deliberately whether the service ever
  runs agent-authored changes, or only reviewed ones.
  Per environment, because the two boxes differ: launchd on Darwin, systemd on
  Debian. Both have precedent here — `apps/ollama` installs a launchd agent and
  `apps/clamav` a systemd timer — so this is a new user and a new unit, not a
  new mechanism. Done when each machine has an ansible user whose sudo rights
  are enumerated and reviewable, a scheduled unit that applies configuration and
  reports what it changed, and a documented way to run it by hand.
- **Bootstrap a whole machine from chezmoi alone, including Ansible itself.**
  Later, deliberately. chezmoi ships as a self-contained static binary with no
  runtime, which makes it the one thing that can be present before anything else
  is — so `chezmoi init --apply <repo>` could pull the configuration *and* stand
  up the system dependencies it needs, rather than the current order where
  Ansible must already exist for the playbook to run. That removes the
  chicken-and-egg step in `bootstrap/` and shortens a new machine to one
  command. Worth checking before designing: chezmoi's `run_once_before_` scripts
  are the hook for this and already appear in the repo
  (`crontab/run_onchange_after_install-crontab.sh.tmpl`), so the mechanism is
  known rather than novel. The interesting question is what minimum must be
  bootstrapped — mise brings Ansible today, and mise itself has to arrive
  somehow.
- **Write a `ground-truth-a-dependency` skill from scratch.** The recurring need
  is what the 2026-09-12 dotagents failure took: reading a dependency's shipped
  source to find behaviour its docs never mention — an uncaught `SymlinkError`
  reaching stderr while stdout stayed empty. The method used that day is the
  whole content and owes nothing to any employer artifact: read the installed
  package rather than trusting docs, reproduce in an isolated `HOME` before
  believing a diagnosis, and mutation-test the resulting guard so a test that
  cannot fail is caught. **`what-would-kobby-do` is not a source** — it is an
  unlicensed internal tool, so it may not be read, quoted, paraphrased or
  "generalised". Name the skill for the work, not "reverse engineering", which
  drags in binary analysis and a legal frame that does not apply. Done when it
  takes an undocumented dependency failure to a cause with every claim tied to a
  file and line, authored in a session where the exclusion list below was in
  force.
- **[1] Promote `gpt-oss:20b` and `ministral-3:8b` in `bin/binned`.** Decided:
  use the cross-task evidence from judging. Record in the manifest that the
  number came from judging rather than generation, so the basis is not
  rediscovered as an error later.
- **[2] Repopulate `bin/binned`'s SaaS tier from the frontier evaluation.**
  Decided: repopulate rather than leave it thin. Depends on the frontier
  evaluation task, which needs OpenRouter calls and therefore an answer on cost.
- **[5] Give Ansible sole ownership of `_ollama_zsh_completion`.** Decided.
  chezmoi was involved because the file is a symlink; removing chezmoi's claim
  ends the dual ownership and the `chezmoi apply` reverts-a-re-download
  consequence documented in `apps/ollama/tasks/install.yaml`. Note the
  inversion while working: for this file the topic-root copy is live and the
  `files/zsh/` copy is dead, backwards from every other `*.zsh`.
- Evaluate frontier cloud alternatives to OpenAI/Grok as judge and generation
  candidates — Qwen, DeepSeek, Moonshot Kimi, Z.ai GLM, MiniMax, Mistral,
  ByteDance Seed, Cohere are all on the existing OpenRouter account. Rank them
  with `model-bench`, not by assertion: several post-date any model's training
  cutoff, so relative quality is genuinely unknown until measured.
- **Retired 2026-09-12 — do not hand-symlink skills into `~/.claude/skills`.**
  `apps/opencode` now declares `pii-redaction`, `commit-hygiene`,
  `review-best-practices`, `interaction-questioning` and `skillet-authoring` in
  its manifest, and dotagents installs them into `~/.agents/skills`, which
  `~/.claude/skills` is now a symlink to. The hand-made links were not merely
  redundant: they were the direct cause of the `dotagents add` failures on
  2026-09-12 (see `roles/guards/tasks/dotagents-skills-migration.yaml`), and
  dotagents silently replaces any it finds at the destination. If a skill really
  should point at a live working clone, declare it `path:.agents/skills/<name>`
  so dotagents adopts it in place — never `ln -s` by hand. `model-fitness` stays
  out: it is uncommitted in ai-prompt-library and belongs to another session.
  `no-ai-slop` remains a third-party vendored copy rather than a manifest entry:
  `gh api repos/petergyang/no-ai-slop/contents/skills/no-ai-slop/SKILL.md
  --jq .content | base64 -d`. See its `PROVENANCE.md` for the em-dash deviation.
- File the upstream issue on `simonw/llm-pdf-to-images`: it does `import fitz`,
  and PyMuPDF's shim prints a deprecation notice to **stdout**, corrupting any
  captured `llm` output. Draft is written; one-line fix is `import pymupdf`.
  **[unblocked: `gh auth status` reports a working keyring login as of 2026-09-11]**
- Move § Commit granularity and § Messages out of
  `dotfiles/docs/TOPICS.md` into `docs/COMMITS.md`. That document is
  titled "Topic conventions" and those two sections are not topic conventions —
  they are repository conventions that do not ship with the artifact, which is
  the split `docs/TOPICS.md` now describes. `AGENTS.md` § Commits cites
  them and would point at the new home.
  **Do it with the citation rewrite, not before.** 53 files reference
  `TOPICS.md`, 40 of them topic files using a deployed-tree-relative path,
  and those citations should be rewritten once rather than twice.
- Scope and apply retention to the 8 rows of work content already in the `llm`
  log. `company.yaml`'s `open_questions.indefinite_local_log` defaults to
  `treat_as_non_compliant`, so the current state is the non-compliant one by our
  own reading. Blocked on the resolver only for automation — the rows can be
  scoped by hand first.
- Add tests for `bin/triage`. It has none, which is why a `platform=None`
  reporting bug reached the deployed script and was caught by a manual smoke test
  rather than the 218-test suite. The env/flag/fallback resolution is the obvious
  first case.
- Define how this repo's policy reaches builders, and the save-back contract
  for tool-built policy. The author's requirement (2026-09-12): this repo may
  carry a policy that agents read or are fed; when a policy tool exists
  (impromptu), its output must have a known way to be saved into this
  machine-management repo where retention is wanted — or, if policy lives
  here, the tool takes over managing it. Done when the contract is written
  down: what a builder reads, from where, in what format, and what a tool
  must produce for this repo to retain it. The larger question this sits
  inside — whether over-arching policy is independent of this repo — is in
  `ROADMAP.md` § Over-arching policy and is the author's to settle.
- Run the eval suites for the library skills. **Re-homed 2026-09-12** to
  `ai-prompt-library` (its TASKS.md), per the author's scoping decision: AI
  work — skills, evals, policy, tooling — stops landing in this repository.
  This repo's provisioning (the dotagents topic, the opencode manifest)
  consumes the eval gate's verdicts but does not execute them.
- Evaluate whether contract testing earns its keep here. The candidate seams are
  real: `bin/policy`'s exit codes (0/1/2/3) consumed by several callers, the
  `ollama-evals` case schema shared by 25 YAML files, and the model-manifest
  shape that `sync`/`prune`/`status` all read. Today each consumer re-asserts the
  contract in its own tests, which is the duplication the item above is about.
  Decide: one contract per seam with consumer tests deriving from it, or leave it.
- Decide whether a panel-of-judges (LLM council) pattern earns its keep for work
  on this repo, specifically refactoring review and commit review, where a single
  model's agreement with itself is not evidence. Groupthink is the stated concern:
  one model, or several from one family, will ratify its own reasoning. Measure it
  rather than assume it — disagreement rate between judges is the signal that says
  whether the panel adds anything a single judge did not. Relates to the existing
  cheap-gate item above: the gate decides WHEN to convene a panel, this decides
  WHETHER a panel beats one judge, and they should be settled together.
- Adopt a technical plain-language standard as the default for technical docs in
  this repo, and sweep the existing ones to it. Exempt: `spec.md` and any skillet
  spec, which keep spec language (SHALL/MUST) and BDD scenarios — plain language
  and normative language are different jobs. Applies to `AGENTS.md`, `docs/*.md`,
  READMEs, changelog entries and user-facing output.
  **[open question: which published standard to cite — plainlanguage.gov's
  Federal Plain Language Guidelines and ISO 24495-1:2023 are the two candidates.
  Marked rather than guessed, per `spec.md` § Ambiguity is marked, not resolved.]**
- Reconcile changelog style: plain language, the house commit style in
  `docs/TOPICS.md` § Commit granularity, and the changelog standard have to
  intersect without contradicting.
  **[corrected 2026-09-16: the "no CHANGELOG.md — git log is the changelog"
  premise is stale. The repo adopted scriv (00e278e): fragments live in
  `changelog.d/` and collect into `CHANGELOG.md` on release, per
  `CONTRIBUTING.md` § Writing a changelog entry. Same session observed a
  second gap: sessions intermittently skip fragments — the 2026-09-16 opencode
  permission rework landed 14 commits with none, later backfilled — and nothing
  enforces one. The reconciliation should cover fragment *reliability*, not
  style alone.]**
  **[open question: which changelog standard to cite. `CHANGELOG.md` already
  names Keep a Changelog 1.1.0; `ai-prompt-library/CHANGELOG.md` cites 1.0.0.
  Common Changelog is the other candidate. Confirm which before writing the
  rule.]**
- Reconcile `prek` and `pre-commit`. Both are installed and both read
  `.pre-commit-config.yaml`. Pick one as the documented runner so hooks cannot
  pass under one and fail under the other, and say which in AGENTS.md § Commands.
- Add a pytest hook to pre-commit, or decide deliberately not to. The suite takes
  104s, which is too slow for every commit — the likely answer is the fast subset
  on pre-commit and the full run on pre-push, matching how the bats hook already
  declares `stages: [pre-commit, pre-push]`.
- Use local models to generate a machine-local policy layer from on-device
  policy documents. The source documents cannot leave the device, which is
  exactly why a local model is the right tool: it reads them in place and emits
  an abstracted set of principles that the resolver can consume. The generated
  layer is machine-local and never versioned, same as `company.yaml` today.
  Output must be principles, not quotations — a generated layer that reproduces
  source text has moved the document, not abstracted it.
- Design the state backup path, classified by machine ownership and data
  sensitivity. Back up only what is expensive to regenerate — model weights,
  eval results, benchmark history — and regenerate the rest. Rules that fall out
  of the author interview, in priority order: PII never leaves the internal disk
  under any circumstance; a machine the author does not own can use neither
  cloud nor external disk, only its internal disk; everything else may use
  external disk or encrypted cloud. No mechanism exists today, so expensive
  state currently has no backup at all.
- Review what may and may not leave a machine the author does not own, against
  the governing policy for that machine. Feeds both the backup design above and
  the generated policy layer. Existing work on this is scattered — collect it
  first rather than restarting.
- Add employer-specific data filters as a machine-local, generated artifact.
  They must never be committed: a filter list names what it is filtering for, so
  a versioned one leaks the thing it exists to catch. Same shape as the
  generated policy layer above.
- Generalise the work/AI policy so topics consume it rather than embedding it.
  Policy governs actions on data — remote inference, body logging, device
  suitability — and those questions do not change when the model runtime does.
  Today `bin/policy`'s FIELDS are already product-neutral, which is the good
  half; the gap is that no topic declares the capabilities it exercises, so
  consumption is by hand at each call site and nothing stops a topic deciding
  for itself. Wanted: a topic declares which capabilities it uses, the resolver
  answers, and adding a second local runtime alongside or instead of ollama
  requires no policy change. Pairs with `spec.md` § Shared code does not assume
  a provider, which states the rule but has no mechanism behind it.

### Refactor A — the `topical` CLI (provisioning config, state, bootstrapping)

Design already exists: `dotfiles/docs/ROADMAP-topic-cli.md`, marked "designed,
not built", written 2026-09-09. **Do not redesign it.** MVP is two commands and
the roadmap says to resist a third. These items implement it. Read the roadmap's
§ Constraints that are verified, not assumed before starting — they were checked
against this machine and must not be re-litigated.
- A10. **Plan the sunset of the six `~/bin` tool names, and connect it to the
  dispatcher work.** The design is explicit that `topical` adds a front door and
  does not close the old one, because renaming is a breaking change — but
  "never" is not the intent either. This is the deliberate, separate change the
  design says it must be. Four reference classes have to be audited together,
  all verified in `dotfiles/docs/ROADMAP-topic-cli.md` § Migration inventory:
  `playbook.yaml:291,303` calling `~/bin/ollama-models sync` in `post_tasks`;
  `apps/ollama/tasks/remove.yaml:160-161` removing tools by absolute path;
  `.claude/settings.local.json` allowlisting `ollama-role get *` and others **by
  name**, so a rename silently costs permissions; and launchd labels that embed
  the name, like `com.ollama-usage.snapshot`. The six are `browser-ext`,
  `ollama-models`, `ollama-role`, `ollama-usage`, `ollama-bench`, `ollama-evals`.
  Sequence matters: the front door must be proven before the old door closes, so
  this is blocked on the dispatcher actually working. Done when a dated plan
  exists naming which names go, which stay, and what each retirement touches —
  not when anything is renamed.
- A2. Build `topical new <name>`. Replaces `init-config.sh`, which copies
  `template_dir/` and stops, leaving every `topic.yml` field and five lifecycle
  stubs to be hand-edited. Done when scaffolding firefox needs no hand-editing to
  reach a valid, installable topic — and when the generated topic carries its own
  removal path, per `spec.md` § Layering — teardown changes with the thing it
  creates. That property is the main reason this tool is worth building.
- A3. Generalise `browser-ext` into `topical <name> ext add ...`. It already
  validates IDs, resolves names, pins tags and appends without destroying
  comments — but it lives inside the chrome topic and only knows browsers. Done
  when it serves chrome and firefox with no browser-specific code in the CLI.
- A4. Add dependency add/remove for non-extension topics, following the same
  comment-preserving edit approach. Done when adding a package to a topic never
  requires hand-editing YAML.
- A5. Add `topical bootstrap` — run a topic's install and its late-stage
  initialization, per `PRD.md` § Architecture. Done when a topic goes from
  scaffolded to "ready to use" through the CLI alone.
- A6. Make the CLI the path an agent drives, with the CLI remaining the human
  fallback. One implementation behind both. Done when an agent can add a topic
  end-to-end without editing a topic file directly.
- A7. Work the roadmap's § Migration inventory. Explicitly out of MVP — do not
  start before A2 and A3 are working.
- A9. **Make `template_dir/` manager-aware and fold it into the CLI, with an
  optional agent pass on top.** Consumes A8. Today the template is one shape for
  every topic, so `init-config.sh` copies a scaffold that is wrong for whichever
  manager the topic actually uses — no `vars:` block for a cask, no `become` for
  apt, an empty `upgrade.yaml` stub even when the manager's system role will
  never reach the topic.

  **Decided 2026-09-14: one template plus a generator that emits only what
  applies, not a set of per-manager variants.** Variants would be five
  near-identical scaffolds to keep in step, and `dotfiles/managers.yaml` (A8,
  delivered) already holds the differences as data for the generator to read.
  Write the generator to be carried into the separate `topical` project rather
  than as something thrown away here. **Review the choice after using it, not
  before** — variants read and diff more easily, so if the generator's
  conditionals grow hairier than five small directories would have been, that is
  the signal to switch. The trade is recorded so that comparison stays possible.

  First thing the generator should delete: `template_dir/` scaffolds a commented
  `snap` block that **zero topics use**, and that boilerplate is most of the 37
  commented-out module lines now sitting in topics that never wanted them.
  Emitting the one block a topic needs removes the category rather than
  documenting it. **Also sweep for scaffold-residue artifacts when A9 runs**
  (author, 2026-09-20): a topic-root `tasks.yaml` carrying unedited template
  boilerplate is the known instance (deb-get ships one beside its real
  `tasks/`; ollama carries the same leftover) — the sweep greps topics for
  the template's comment markers and strips what no topic ever filled in,
  rather than leaving dead boilerplate beside live tasks.
  **Do not build a second agent mechanism for the rest.** `migrate-to-roles.sh`
  already does this job and is the thing to absorb: it treats `template_dir/` as
  canonical, checks conformance with a **local** LLM (an Ollama chain —
  devstral-small-2, qwen3.5, mistral-small3.1, with deepseek-r1 and phi4 for
  reasoning), is re-runnable, has `--dry-run` and prompt previews, and already
  knows real legacy shapes: `uninstall.yaml` / `cleanup.yaml` / `teardown.yaml`
  as remove-task sources, stray root files belonging in `files/`, and the
  system-role topics that carry extra subtasks. That is the "migrations from
  older or unsupported formats" capability, built and working, sitting outside
  the CLI that should own it. A7 already covers the migration *inventory*; this
  is the mechanism.
  Keep the two passes separate and the second optional: the deterministic
  scaffold must produce a valid topic on its own, with the agent extending it
  only for cases the template does not encode — a manager nobody has written a
  variant for yet, a topic arriving in a shape the rules do not describe. An
  agent pass that is required rather than optional makes every `topical new`
  depend on a model being installed and answering, which is a worse failure mode
  than a scaffold that needs one manual edit. Done when `topical new` emits a
  topic correct for its manager without an LLM in the loop, `migrate-to-roles.sh`
  has no logic the CLI lacks, and the agent pass is reachable by an explicit flag
  that says what it changed.

### Topic bundles — data-first grouping

Design settled with the author 2026-09-12: bundles are data, not directories —
apps/ stays flat, a bundle config object names its members and relationships,
and relationships live in the bundle rather than inside each topic (the
author's modularity requirement). Topics keep minimal `topic_requires` so they
stay standalone-installable; bundles complement and win on conflict. If
nesting ever comes, it happens together with the queued TOPICS-citation
rewrite — never as two rewrites of 40 files.

**Binding resolved 2026-09-12, after the author's expert challenge:** the
machine→groups map is `machines.yml` — a file that does not exist yet, settled design rather than precedent — kept as **plain data** (hostname →
groups), slurped by the parent playbook exactly like `topic.yml` files are
today — no Ansible inventory semantics. Disambiguation is
`ansible_facts['hostname']` (gathered every run) intersected with the map;
an inventory of named hosts would fight the self-applying `hosts: localhost`
design and buys nothing for a one-machine-at-a-time fleet. Inventory
`children:` remains the upgrade path if this ever becomes a true multi-host
fleet — the map's shape ports 1:1. Vocabulary: the config object is a
**group**, the selector is `-e group=<name>`, unmapped machines keep
all-topics+warn. The items below still say "bundle" and `-e bundle=` —
rewritten when the schema item lands.

- Define the bundle schema and document it in `dotfiles/docs/TOPICS.md`. A
  bundle config object (e.g. `apps/bundles/ai-strategy.yml`) names member
  topics, run order, shared configuration, machine targeting (os/arch
  filters), and teardown semantics. Done when the schema is documented with a
  worked example and validated against the parent playbook's discovery
  (find recurse depth 2 already tolerates future nesting; layout stays flat).
- Add bundle-aware limiting to the parent playbook: `-e bundle=<name>` with
  `--tags install|upgrade|remove` runs only that bundle's members for this
  machine (os-filtered). Done when a limited install touches exactly the
  bundle's members here, and a limited remove still consults `requires_map`
  before tearing any shared dep.
- Create the first bundle, `ai-strategy`: ollama, mise, opencode (+ the
  dotagents topic when it exists), ordered so mise precedes opencode (node).
  Done when the bundle exists, a limited run selects exactly those topics on
  this machine, and the Mac case is documented (topic_os filtering does the
  per-machine part).

### Refactor B — factor the AI/LLM tooling out of this repo

Required by `PRD.md`: dotfiles and provisioning are the trunk, this tooling is a
branch, and the architecture rule says provisioning may install and trigger a
tool but never contain its logic or state. The Ansible role STAYS — installing a
runtime and pulling weights is machine setup. What leaves is everything about the
author rather than the machine.
- B1. Decide the new home and its install method. **Home decided by the author
  2026-09-12:** `ai-prompt-library` now (skills, evals, policy, tooling work
  lands there), `impromptu` eventually once the tool is built up. **Addendum
  2026-09-14, a candidate supersession:** the author announced `llocallabs.ai`
  — a collection of repositories consolidating the AI tooling and agent
  projects, starting with a new anchor repo, with AI research, testing and
  benchmarking moving out of this repo (tasks in § Now). ai-prompt-library
  and impromptu may consolidate under it; whether that replaces the 09-12
  home decision or sits above it is part of what B1 still answers. Still
  open, and deliberately so: the install method this repo pins (B1's other
  half), and whether policy management has full scope in any home — the
  author marked this unresolved; see `ROADMAP.md` § Over-arching policy.
  Blocks B2 below only on the install-method half.
- B2. Write the move manifest — every affected file classified as leaves, stays,
  or is deleted. Done when the list exists and later items cite it instead of
  re-deciding per file.
  **The llocallabs cluster and its timing dependencies (recorded 2026-09-14,
  corrected by the advisor pass 2026-09-15).** Six queued items cite each
  other. The gate structure has TWO independent roots, not one linear order:
  the manifest needs the anchor repo to exist (a manifest naming a
  nonexistent home is a guess) AND B1's install-method answer, which is
  deliberately still open. (2) The three research projects queued in § Now
  and § Planned (sandboxing, session-management handoff, RAG/graphs) are
  first-class llocallabs candidates — but which branch fires, start-there
  or start-here, is the AUTHOR'S call, made and recorded in the session
  that starts the work; without that arbiter two machines can pick opposite
  branches and both be following this file. (3) gita is a consumer, not a
  gate: its per-machine inventory must include the collection once it
  exists, but it waits on nothing here. (4) The strategy/policy agent
  consumes the research projects and cannot be stood up ahead of them.
  (6) The R&D factory is gated on the anchor repo and is the umbrella the
  research methods feed — it belongs to the collection from day one.
  Prerequisite the cluster silently assumed, now named: the capture store
  (`~/code/personal/llocallabs-capture/`) is unversioned,
  single-machine, and mixes private with shareable notes — before any
  cluster item starts on the second machine it must be versioned or synced
  AND separated (see the capture-store contract task in § Planned). Until
  the manifest lands, nothing in the cluster moves, and no item in it
  should be worked on the assumption it stays here forever.
- B3. Define the state contract for the new utility: one owner and one retention
  rule for data currently scattered across `~/.local/share/ollama-{usage,bench,
  evals}` and the `llm` sqlite log. This closes the standing data-ownership
  finding and is a precondition for the backup work, not a follow-up to it.
- B4. Topics consume policy through a declared capability, from its new home.
  One item, stated as the outcome rather than as its parts. It was originally
  cut as two — extract the resolver, then add the interface — and that cut was
  wrong: the first half alone relocates the call-site duplication instead of
  removing it, while looking finished. Take the resolver first inside this item,
  since it is the most self-contained piece and everything else depends on it.
  Done when the resolver runs from its new home, this repo installs it, topics
  declare the capabilities they exercise rather than deciding for themselves,
  and `tests/policy` passes against the moved copy with both directions still
  asserted.
- B5. Extract the eval harness — `ollama-evals`, cases, taxonomy. Largest surface
  and the most tests. Done when the suite is green from the new home.
- B6. Extract `ollama-profile` and `ask-research`.
- B7. Rewire the ollama role to install the utility pinned and trigger its
  initialization at a late stage, per `PRD.md`. Done when a fresh provision
  reaches "tools initialized" without this repo containing any tooling logic.
- B8. Delete the vacated code and update `spec.md`, `PRD.md` and `AGENTS.md` to
  point outward. Done when no AI tooling logic remains here and no doc describes
  it as if it were still local.
- Build a CLI that manages provisioning config and state, including
  bootstrapping. Think mise or apt, but for topics and their files: scaffold a
  new topic from a template, add or remove a dependency, run the bootstrap, and
  report state. One of the refactors named in `PRD.md`.
  Why it is worth building rather than tolerating:
  - It is what makes the PRD's complexity governor true instead of aspirational.
    The governor says a routine change must never require touching `spec.md` or
    writing a test — that only holds if a tool does the routine change correctly
    by construction.
  - It makes `spec.md` § Layering — teardown changes with the thing it creates
    structural rather than a discipline. A template that scaffolds install and
    removal together cannot forget the removal, which is the exact failure that
    rule was bought by: a hand-copied `launchctl unsetenv` list silently stopped
    covering a newly added variable.
  - Adding a topic by hand is the current cost, and it is being paid right now
    for the chrome topic. That is the motivating case, not a hypothetical.
  Target shape: the CLI is the trusted process, and an agent drives it rather
  than editing topic files directly. The CLI stays as the fallback for when the
  agent is not trusted or not present, so machine configuration can be updated
  as-you-go by either. Both paths go through one implementation, because two
  paths means two behaviours.
  Constraints it inherits: it belongs to the provision layer, so it may install
  and trigger but must never hold a tool's logic or state (`PRD.md`
  § Architecture). It must be topic-neutral — no topic gets special handling —
  and it consumes policy generally rather than embedding rules, per the policy
  generalisation item above.
- Research best practices for multi-agent branch orchestration, then design the
  state file. Wanted: a file the orchestrating agent maintains that records which
  branch each work item is on, what it is based on, and what needs rebasing when
  main moves — so a subagent is handed a rebase instead of discovering a conflict
  mid-task. Stress-testing branch-per-item already surfaced what it must handle:
  stacked branches for dependent items (A3 on A2), items that must not be split
  (the original B4/B5 cut), shared `conftest.py` fixtures, and governance-doc collisions across
  unrelated branches. Use the questioning skill in
  `~/code/personal/ai-prompt-library`. Should land before more than two agents
  run in parallel.
- Get a fast test loop. The full suite takes 104s, which is too slow to run per
  change — at that price the loop collapses into run-once-and-hope, which is
  precisely how regressions slip through. Target a change-relevant subset in
  around ten seconds. `-m "not llm_judge"` exists already; what is missing is a
  way for an agent to select the suites matching the files it touched.
- Put the AI tooling under characterization tests BEFORE starting refactor B, and
  use them as the parity bridge. Audit the existing behaviour, add tests that pin
  it, then let the reimplementation run against the same tests. Parity becomes
  proven rather than assumed, and the rewrite stops being gated on a human
  re-reading every line. B5 needs this most — the eval harness is the largest
  surface being moved.
- Build the LEDGER for the trust ladder. The ladder itself — rungs, promotion
  streaks, incident classes A-D, what is explicitly not an incident, and ageing
  — is defined in `AGENTS.md` § Trust ladder. What remains is the record. The ladder widens an agent's autonomy
  per task class and blast radius rather than globally; the ledger is what makes
  promotion evidence-based instead of felt. Rungs: 0 propose only; 1 branch and
  PR; 2 self-merge docs and tests; 3 self-merge code inside a named blast radius;
  4 unattended on a task class with an async report. `AGENTS.md` § Merge gates
  already describes rungs 2 and 3 — what is missing is the record to promote
  against. Ledger: one line per completed agent item recording the item, the rung
  it ran at, which gates passed, whether the author corrected it, and the class
  of any correction. Promote on a streak of clean items at a rung; demote one
  rung on a single incident of a defined class. The incident classes were defined before any
  promotion existed to argue about, which was the point. Note this is the same discipline `spec.md` § Evidence
  applies to measured numbers: a trust claim carries its conditions or it is an
  assertion. **[open question: whether the ledger is committed or machine-local.
  It records this repo's work rather than usage, which argues for committing it,
  but it is also a running record of agent-versus-author correction that may not
  want to be public.]**
- Factor a general git repository template out of this work, using copier
  (9.17.2, installed). **Its own repository at `~/code/personal/`**, alongside
  ai-prompt-library and impromptu — not a directory here, and not under
  `~/code/work/`. Name is not settled; it is the reusable half of this repo's
  practice, so something like `spec-driven-repo-template` describes it. What has
  earned its place and is not dotfiles-specific: the document set and its
  separation of concerns (PRD what-for, spec what-must-stay-true, ROADMAP
  what-is-next, TASKS what-is-now, AGENTS how), the RECL loop, the verification
  practices (both-directions, prove-the-test-fails, property and fuzz guidance),
  the branching and merge-gate conventions, and the Python toolchain section.
  Excluded: anything chezmoi, Ansible or model-specific, and anything
  language-specific — language conventions are a pluggable `<LANGUAGE>.md`
  chosen by copier prompt, so the template ships `docs/PYTHON.md` as one
  option rather than baking Python into AGENTS.md. `docs/` is the unit
  the template plugs into — adding a language means dropping one file there. That is what lets the template grow to
  cover other languages without a rewrite. This template IS the
  reusable AGENTS.md baseline, so the baseline-versus-overlay split happens here
  rather than separately. Done when a fresh repo scaffolded from it has the full
  document set, passes `skillet validate`, and asks its project-specific parts as
  copier prompts rather than leaving placeholders to hand-edit.
- Factor a copier template for the chezmoi-Ansible topic format. **Its own
  repository at `~/code/personal/`**, same placement as the general template
  above. It **builds on the general template rather than duplicating it** — but
  by composition, not inheritance. Verified against copier 9.17.2: there is no
  `extends`, `inherit`, `parent_template` or `base_template` keyword anywhere in
  the source. Three primitives do the job instead:

  - `answers_file` lets each template record its answers somewhere other than
    the default `.copier-answers.yml`. That is what makes two templates on one
    project possible, and `copier update -a <file>` then updates each
    independently.
  - `_external_data` (a name-to-YAML-path map, exposed to Jinja as
    `external.<name>`) lets the topic template READ the general template's
    answers file and reuse those answers instead of re-asking. Note the path
    must resolve inside the generated project unless `--trust` is passed, so
    the parent's answers file has to be committed there — which it is by
    default.
  - `_tasks` can shell out to `copier copy` of the general template. Available,
    and the most fragile of the three; prefer the first two.

  So: apply the general template first writing `.copier-answers.general.yml`,
  then the topic template writing `.copier-answers.topic.yml` and declaring
  `_external_data` against the first. The topic template contributes only what
  is specific to a chezmoi-Ansible topic.

  **The trap to avoid:** if both templates write to the same default answers
  file, the second silently overwrites the first's tracking and the general
  template can never be updated in that project again. Separate answers files
  are the whole mechanism, not a detail — and getting them right is what
  delivers the actual goal, which is that improving the general template later
  flows into every project built from it, topic repos included. Purpose is that someone can build a topic from scratch with an
  agent, and borrow one piece of this configuration without adopting the whole
  repo — see `PRD.md` § Topics are installable modules. Overlaps refactor A:
  `topical new` scaffolds a topic INSIDE this repo and this template scaffolds one
  for a repo that is not this one. They should share the canonical template
  rather than diverge — decide which owns it before the second is built. The
  module boundary itself is deferred to `ROADMAP.md` and is not a blocker; build
  against the format as it stands.
- Keep `docs/REFERENCES.md` current. The register exists and is verified
  as of 2026-09-11; what is missing is the habit. Re-check on quarter boundaries
  and whenever a listed tool is upgraded, updating `verified` even when nothing
  moved — a stale date is the signal, not the version. Two rows need action now:
  skillet 1.8.0 is out while `spec.md` pins 1.7.0, and ruff is installed but
  wired to nothing. **[open question: worth automating? A check comparing
  installed `--version` output against the register is easy; comparing against
  upstream release feeds is not, and would add network calls to the test suite.]**
- Build a dotagents topic and make opencode's skill set an optional dependency
  of it. **The manager decision is made — see
  `dotfiles/docs/AGENT-ARTIFACTS.md` (2026-09-12): dotagents installs, pinned
  refs and committed lock; agentskills.io is the tracked format standard;
  skills.sh is discovery only.** The topic owns: the dotagents declaration
  (currently mise-managed via config.toml — decide which topic owns it), the
  user-global skill declaration in `apps/opencode/defaults/main.yaml`, and
  the install/sync trigger. **That is no longer a per-skill manifest** (changed
  2026-09-12, another session): it is a list of approved *sources* plus a
  `[trust]` allowlist dotagents enforces itself, per-source `exclude` vetoes, and
  a `roles/guards/` check that shells out to `tools/skill-trust`. Three pieces
  move, not one — and they argue for this task rather than against it, since
  source trust and a provenance guard belong to a dotagents topic far more
  clearly than to opencode. opencode stays fully usable without it — the
  binary and config remain its own — and gets skills only through the
  dependency. Done when the skill manifest lives in the dotagents topic,
  skills install from it alone, and apps/opencode carries no skill manifest
  of its own. Open before building: run the skillet evals, since the eval
  gate is now policy. (The agents.lock verification resolved 2026-09-12: the
  lock records resolved commit SHAs — see the record's exit-path section.)
- Choose a project templating tool, and benchmark rather than assume. `copier`
  9.17.2 is installed and is the incumbent, so it is the baseline to beat, not
  the default to accept. Candidates worth measuring: copier, cookiecutter,
  cruft (cookiecutter plus the update story it lacks), projen, yeoman, plop,
  degit, cargo-generate, and plain GitHub template repositories via
  `gh repo create --template`.
  Rank on what this project actually needs, in priority order: **update after
  generation** — the ability to improve the template later and pull the change
  into projects already built from it, which is the whole stated goal and the
  thing most of these tools simply do not do; composition, since the topic
  template has to build on the general one; conditional prompts, for selecting a
  `docs/<LANGUAGE>.md`; language-neutrality; and dependency footprint.
  Do this BEFORE building either template, since the answer decides their shape.
- Rebuild the 64 allow rules in `~/.claude/settings.json`. One of four settings scopes on this machine (257 allow rules
  in total). Machine-local, applies to **every** project including work repositories, and deliberately left alone
  when the project config was rebuilt — changing it from inside this repo would
  have silently altered agent behaviour in `~/code/work/`. Same approach as
  `docs/PERMISSIONS.md`, but the allow set has to serve repos this one
  knows nothing about, so start by finding out which projects depend on it.
- Deal with `~/dotfiles/.claude/settings.local.json` — **80 allow rules in no
  repository at all.** `~/dotfiles` is the chezmoi deploy target and a separate
  Claude project scope, so an agent started there gets these rules and none of
  the project's. One of them is `Bash(chezmoi apply *)`, which is the rule
  `AGENTS.md` § Applying is main-only exists to prevent. Not git-tracked and not
  chezmoi-managed, so nothing versions it and no review has seen it. Decide
  whether agents should ever run there at all — if the answer is no, the fix is
  to stop, not to curate the file.
- Prune `.claude/settings.local.json` — 25 accreted personal allows that no
  review has seen. Lower priority than the two above because a local ALLOW
  cannot re-open what a project DENY closes, **assuming deny wins across cascade
  layers**. That assumption is unverified; confirm it in a fresh session before
  relying on it, and if it is wrong this item becomes urgent rather than tidy.
- Resolve the CONTRIBUTING.md question and the repo-root `docs/` topology.
  The stale root `docs/CONTRIBUTING.md` copy is already trashed (`db4fc0e`) —
  but the advisor pass found the "older copy" story is wrong for three LIVE
  files: `docs/PYTHON.md`, `docs/PERMISSIONS.md` and `docs/REFERENCES.md`
  exist only in the root tree while AGENTS.md directs editors to
  `dotfiles/docs/` copies that do not exist for them. Decide: consolidate
  the root tree into `dotfiles/docs/` or document the split honestly —
  includes the original question of whether the whole root `docs/` tree
  goes.

## History was rewritten on 2026-08-21 — reset before you resume

`main` was force-pushed. Every SHA from `bc72f5c` onward is new. Two mixed
commits were unscrambled: `b3ad740` split into a clamav half and a pii-redactor
half, and `5692a86` reworded to describe the 52 zsh deletions it actually
contains. Verified lossless — the tree is byte-identical to before, and the suite
is 218 passed / 7 deselected.

**Anything holding the old history must hard-reset, not pull.** A pull merges old
and new and resurrects the mixed commits.

```bash
git fetch origin
git reset --hard origin/main
git fetch origin 'refs/notes/*:refs/notes/*'   # notes are published now
```

Who needs this:

- **The second machine.** Not currently contributing, so no work is at risk — but
  it must reset before its next commit or it will reintroduce the old SHAs.
- **Any session idle-but-not-finished.** Reset before resuming; a commit against
  the old HEAD undoes the unscramble.

Pre-rewrite history is on `backup/pre-unscramble-272bdf7` if anything needs
recovering. Rollback is `git reset --hard backup/pre-unscramble-272bdf7` plus a
force-push, valid until someone pushes on top.

Each of the three commits carries a `git notes` PROVENANCE entry explaining the
split and pointing at the prevention. Read with `git notes show <sha>`.

## Private tasks

Some work cannot be described here without reproducing the thing it is trying to
remove. Those live in `~/.local/state/chezmoi/private-tasks.md` — machine-local,
never in git, same pattern as `~/.local/state/ai-policy/company.yaml`.

Currently one item there: a history-rewrite to remove an employer-domain string
from file contents. Scope, method and prerequisites are recorded in that file.

Note for whoever runs it: `TASKS.md` itself is in scope. An earlier revision of
this section quoted the target string literally before it was redacted, so the
purge must cover this file as well as the original.

Updated 2026-09-10 — the repo was public until that date and is now private, so
the rewrite is cleanup rather than mitigation; anything fetched during the window
is already out of reach. Scope grew: the `chrome` topic, added after the original
audit, carried more than the email. Its prose is fixed at tip, one functional
path is knowingly left, and a scoping test was agreed that settles the open
employer-URL question. Detail in that file. A committed doc for this was tried
and withdrawn — it reproduced the patterns, exactly as warned above.

## Decisions waiting on the author

None open. The five that stood here were answered on 2026-09-11 and became
tasks; see § Now and § Planned. Add new ones here rather than deciding them.

## Sandbox isolation — verified findings, 2026-09-20

Measured on this machine, for the coordination work in § Now. Recorded because
the next session would otherwise re-probe it, and the `external_directory` deny
makes that expensive.

- **This box supports unprivileged bubblewrap.** `bwrap`, `podman`, `docker`,
  `systemd-run`, `unshare` and `qemu-system-x86_64` are all on `PATH`;
  `firejail`, `lima` and `colima` are absent. `user.max_user_namespaces` is
  115796, and both `kernel.unprivileged_userns_clone` and
  `kernel.apparmor_restrict_unprivileged_userns` are absent — no
  Ubuntu-style userns restriction applies. The `overlay` module is present, so
  an overlayfs upperdir can serve as a write audit trail.
- **macOS has no equivalent, and that shapes the design.** No mount
  namespaces, no Landlock, no overlayfs. Seatbelt (`sandbox-exec`) is the only
  native path-level mechanism and is deprecated with an undocumented profile
  language, though Chromium, Bazel, Nix, Codex CLI and Claude Code all ship it.
  App Sandbox needs a signed bundle and cannot express an admin-supplied path
  list; Endpoint Security needs an Apple-granted entitlement and a system
  extension. So: **state the guarantee at the weakest platform**, make the
  portable git-level path gate the invariant, and treat bwrap/Seatbelt as
  defence in depth that turns a commit-time rejection into a write-time
  `EACCES`. A future `sandbox-exec` removal is then an inconvenience, not a hole.
- **A Linux VM on macOS is the wrong default for this threat model.** It buys a
  hypervisor boundary against motivated attackers, which is not the stated
  threat, and charges metadata-heavy filesystem performance plus unreliable
  inotify across the boundary. The fast configuration keeps the repo *inside*
  the VM, which converts the setup into remote development. Keep it as an
  optional high-assurance mode only.
- **Nothing in the ecosystem ships per-agent path subsets inside one shared
  checkout.** Three independent sources agree — a ~90-project survey
  (`webcoyote/awesome-AI-sandbox`), the shipping tools, and the council. Every
  implementation does whole-workspace confinement per worktree or container.
  Treat that convergence as evidence the original requirement was
  over-specified: worktree-per-agent plus the push-time gate is the design.
- **Adopt, don't build** (AGENTS.md ladder): `anthropic-experimental/sandbox-runtime`
  wraps a process in Seatbelt-or-bubblewrap from one policy;
  `treebeard` is an ephemeral git-worktree sandbox with copy-on-write and
  network restriction — closest to what § Now specifies; `nixcage` and
  `sandnix` are reference implementations of the two-backend split; `cco` is a
  backend selector. Writing a third implementation here would be a build.
  Name collision to avoid: three different projects are called
  `sandbox-runtime` (Anthropic's, `carderne/`, and a Rust crate).
- **Destructive git operations defeat any path allow-list.** `checkout`,
  `restore`, `reset --hard`, `clean` and a stray `gc` destroy other agents'
  work while touching only permitted paths. This is the strongest argument for
  worktree-per-agent and for `.git` read-only inside worktrees.
- **Allow-list directories, not files** — editors, formatters and compilers
  write temp-file-plus-rename, which needs write permission on the directory.
- **The cheapest high-value control is not confinement.** An out-of-scope write
  is recoverable from git; `push --force`, `gh pr merge` and `npm publish` are
  not. Deny push to protected refs and require human merge.
- **The chezmoi deployed tree is the gap the portable layer cannot see.**
  `~/bin` and `~/dotfiles` live outside the repo, so a git-level gate cannot
  detect a `chezmoi apply` violation — only OS confinement can. That is the
  strongest reason to keep bwrap despite its cost.

## Cross-session hazards

Files with more than one session touching them recently. Check `git log -3 <file>`
and `chezmoi status` before editing.

- `bin/executable_fetchurl` — actively developed; caused the only real merge
  conflict so far.
- `bin/executable_pii-redactor` — ported to Python, then extended with layered
  redaction by another session. Suite is 63 tests; run it after any change.
  Its conftest default mock is a *working* model, not `cat`: a pass-through mock
  plus exit-status assertions is green exactly when the tool leaks, which is the
  defect the layers exist to prevent. Ask for `mock_llm("cat")` explicitly.
- `bin/executable_model-bench` — multi-case judge suite; the reference scorecards
  in `CASES` must be re-derived if a case script changes.
- `dotfiles/apps/mise/files/config.toml` — two sessions edited it within an hour
  on 2026-09-11 (`b038cbe` removed two broken pipx tools, `907f3d0` pinned
  skillet). It rebased cleanly because the edits were in different regions, but
  it is a long flat list of tools that everything installs through, so the next
  pair of edits may not be so lucky. `~/.config/mise/config.toml` is a symlink
  to this file, so editing the source changes what mise reads immediately —
  before any `chezmoi apply`.

## Standing reminders

- `bin/` scripts are chezmoi source (`executable_<name>`); `~/bin/<name>` is what
  runs. Check `chezmoi status` before editing or you will silently revert the
  working copy.
- A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while
  testing almost nothing. Run it with `typer`, `questionary` and `hypothesis`
  present — see AGENTS.md.
