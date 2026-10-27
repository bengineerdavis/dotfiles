---
id: TASK-57
title: Bootstrap the multi-agent coordination layer — worktrees, frozen leases, risk-tiered
  merge gates — t
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
- blocked
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Bootstrap the multi-agent coordination layer — worktrees, frozen leases,
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
    a semaphore. Estimated real ceiling here is 2–3 writers — **flagged by the
    shift-left study's fusion council as circular: estimated from a $HOME-touch
    audit that doesn't exist yet, and hermetic HOME may dissolve the ceiling
    rather than just unblock xdist.** Prerequisite for any parallelism: sandbox
    the tests that touch `$HOME` (`HOME=$(mktemp -d)`, chezmoi
    `--source`/`--destination`, `--dry-run`). **Implementation pattern
    researched 2026-09-22:** an autouse conftest fixture pointing
    `HOME`/`XDG_*` at `tmp_path` via `monkeypatch.setenv` (auto-reverts, no
    manual teardown); the trap is modules that cache `os.path.expanduser("~")`
    at import time — those must be invoked as subprocesses with an explicit
    `env=` dict built from `tmp_path`, monkeypatching `os.environ` alone does
    not reach them. macOS-specific escapes to name and exclude, not silently
    tolerate: the system keychain and `dscl` ignore `$HOME`, and a subprocess
    that re-execs a login shell (`zsh -l`) re-sources zprofile and escapes the
    sandbox — a live Class-B channel (test passes while touching real state).
    chezmoi's own upstream suite isolates at the layer that resolves the path
    (in-process VFS + `testscript` txtar synthetic homes) rather than via env
    vars — same principle, different mechanism, worth the comparison before
    building. ~~Until this holds, `pytest-xdist` is off the table.~~ **Corrected
    2026-09-23:** the `$HOME` sandboxing is already done — policy, quarantine,
    binned and clipped all redirect via fixtures — and `pytest-xdist` is now
    measured working here (170s → 47s, `-n auto --dist worksteal`, same two
    pre-existing failures). The "2–3 writers" ceiling is about agents sharing
    `$HOME` resources and does not apply to tests, which are read-only apart
    from tmp dirs. The remaining shared resource is the uv cache lock, not
    `$HOME`.
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
    not in it. [done `a92489b` 2026-09-22]
  - **(h) Lifecycle: spawn, fan-out, provision, collect, reap.** Every
    worktree and branch passes through one lifecycle, so a wedged session is
    recoverable by inspection rather than archaeology. Merging uses an
    ephemeral scratch worktree `.worktrees/<sid>_merge_<n>`, recreated per
    attempt from (base + input SHAs) — re-running `git merge` in a conflicted
    tree is not idempotent, rebuilding from SHAs is (the Zuul/bors/merge-queue
    pattern). Merges are serial with the suite after each — batching destroys
    attribution — ordered inert → behaviour → activating. A failed wave is
    bisected, not retried wholesale; green/green/red is a finding recorded
    against the fan-out, evidence the decomposition was wrong. Retries follow
    the table: infra 2–3 with full jitter under a retry budget;
    rebase-and-retest 1–2; deterministic never retried unchanged; LLM
    regeneration once carrying the failure evidence, then escalate.
    Classification is mechanical — re-run the identical artifact in a fresh
    scratch worktree: same failure is deterministic, different failure is a
    flake, quarantined rather than retried into green. A branch is never
    `git branch -D`'d until `merge-base --is-ancestor` proves the work
    landed; crash recovery is `git worktree remove --force` plus
    `git worktree prune`. Escalation reports to the orchestrator freely and
    to the human at the retry cap, with a deadman timeout.
  - **(i) Declaration merge policy: regenerate, never hand-merge.** Venvs
    never merge — only declarations do (pyproject.toml, uv.lock). A lockfile
    conflict is resolved by merging pyproject.toml and re-running `uv lock`,
    never by editing the lock; `.gitattributes` carries `uv.lock merge=binary`
    so git never attempts a textual merge of it. uv is pinned at the system
    layer (`bootstrap.sh`), not mise — the lockfile carries a format
    revision, and version skew churns it. pyproject.toml and uv.lock are
    registered as hot files in § Cross-session hazards.
    **Not true yet, 2026-09-23:** the uv that runs is mise's
    `uv = "latest"`, not the bootstrap pin — (p) U1 fixes it.
  - **(j) Three coupling channels, and one unconditional gate.** Coupling
    between parallel workers travels exactly three ways: writes, caught by
    path-intersection at fan-out; reads, structurally isolated by worktrees;
    semantics, caught only by the merged-state suite — the irreducible
    channel, and the reason merges are serial with the suite after each.
    Over all three sits one unconditional gate: no agent diff may touch the
    gating tests or the policy code, because a worker that can edit its own
    verifier can pass anything. That is a correctness requirement, not a
    trust one.
  - **(k) Capability manifest per subtask.** Every subtask declares a
    manifest — paths, refs, commands, egress, secrets, limits, runtime —
    because "read/write/both" is too coarse to enforce and too coarse to
    audit. Enforcement is three layers: declare (the manifest), sandbox (what
    the environment permits), gate (what the merge refuses). Manifests are
    logged via git notes, so the audit trail travels with the refs.
  - **(l) Contracts-first.** Interoperating pairs land their interface
    before fan-out. The interface is a decision item — cheap to land, and
    unblocking; fanning out before it exists charges every downstream branch
    a rebase each time it changes.
  - **(m) Verifier health first.** The suite's flake rate and mutation
    sensitivity are measured before the orchestrator builds on it. An
    orchestrator multiplies whatever the verifier is, and a verifier that
    passes without exercising what it claims turns the merged-state gate
    into Class B evidence at scale. Builds on (f)'s instrumentation and
    (g)'s mutation trailers.
    Exhibit, 2026-09-23: `tests/chezmoi/test_governance_not_deployed.py:55`
    runs `chezmoi managed` without `-S`, and chezmoi's source directory is
    fixed, so from a worktree the guard checks main's source — a broken
    ignore list in the worktree cannot turn it red. Found by reading the
    code; (p) P2a proves it with a mutation and fixes it.
  - **(n) Irreversible agent effects.** A change that reaches the deployed
    tree (`~/bin`, `~/dotfiles`) cannot be undone by `git revert` — the
    revert restores the source, not the machine. Scope is agent-concurrency
    only: what the coordination layer must guarantee about effects it cannot
    take back. Ansible plan-vs-apply drift is explicitly out.
  - **(o) Phase 2 experiments — the design seen to work, in sequence.**
    Choose the order; each is evidence, not ceremony. **Happy path:** two
    disjoint sub-agents, simultaneous suites, prove the offline run works —
    then `uv cache clean` one package and confirm the offline run fails.
    **The guard seen to fail:** a path overlap refused at fan-out, then the
    check disabled to confirm it was the guard that caught it; extended with
    two sub-agents adding the same `topic_provides` from different files —
    path intersection empty, so the resolver must reject the merged tree.
    **Provisioner path:** `uv add`, merge back, re-lock; then two
    provisioners refused.
  - **(p) Make the repo a Python project: one root `pyproject.toml`, one
    committed `uv.lock`, the test environment rebuilt offline.** [agent:
    pyproject session, `.worktrees/pyproject` on `agent/pyproject`] Author
    request 2026-09-23: follow current PyPA/PEP practice, research first,
    critique by a council, propose any structural change before making it.
    The research ran before this line existed; it is recorded late rather
    than backdated. Decided with the author 2026-09-23: a root project that
    is never built or installed (no `[build-system]`, `[tool.uv] package =
    false`, PEP 735 dependency groups for the test deps), root-only
    `.chezmoiignore` entries, and a governance guard that works from
    worktrees; the `.chezmoiroot` move is a separate `ROADMAP.md` decision;
    uv's version authority is the bootstrap pin (U1). Rule-outs: nothing new
    in `$HOME`, deployed scripts run unchanged, frozen offline runs work,
    `tools/skill-trust` keeps its own lock. Rejected: packaging the repo
    (scripts must stay standalone), a uv workspace with skill-trust, a
    subdirectory `pyproject.toml` (tools look at the root), `pylock.toml` or
    requirements files (no `--frozen`, no groups), keeping the `--with` flags
    (nothing locked). Order: council C1–C5; then PR 1 — P1 docs
    (`docs/PYTHON.md`, `REFERENCES.md`, `LANGUAGES.md`), P2 baseline counts
    per test directory, P2a guard uses `chezmoi -S`, P2b one commit adding
    `pyproject.toml`, `uv.lock`, ignore entries, guard lists and
    `.gitattributes`; then PR 2 after `test-perf-xdist` merges — P3
    `pytest.ini` into `[tool.pytest]`, P4 `AGENTS.md` § Commands, changelog,
    hot-file registration. P1 shares `docs/PYTHON.md` with `test-perf-xdist`
    (its dependency paragraph) — rebase whichever lands second. Open for the
    author at P2b: `requires-python` `>=3.14` or `>=3.11`; ruff/ty pinned in
    lock groups or in mise. Done when `UV_OFFLINE=1 uv run --frozen pytest`
    reproduces the baseline recorded first — the same passes, and only the
    known failures, each named (author, 2026-09-23) — so (o) can use it as
    its consumer path.
    **Council verdicts 2026-09-23** (C1–C4 returned; C5 skipped, Exa key
    absent). Author decisions: `requires-python = ">=3.14"`; ruff/ty in
    lockfile dependency groups (lint/format libs in the lock); committed
    `uv.lock` yes; split P2b into two commits (deploy-hygiene vs project
    adoption); U1 step 1 before `uv lock` (lock format is uv-version-
    sensitive). Corrections: `test-perf-xdist` is merged (`118aaa6`) — PR 2
    no longer waits and the worktree needs rebasing; `tests/` has 44
    `test_*.py` not 40; `slow` marker does not exist; `GOVERNANCE_DIRS =
    []` makes one guard test dead code; `required-version` ships post-U1
    not in PR 1; P4 (AGENTS.md commands) moves to PR 1 tail. Full
    critiques in `.worktrees/pyproject/.council/`.
    **Landed 2026-09-25:** PR #17 (guard fix + leak cleanup), #18/#19
    (project: `pyproject.toml` + `uv.lock` + docs + commands) and #22 (P3:
    pytest config into `pyproject.toml`, `pytest.ini` deleted). P1–P4 done.
    Frozen run verified from main: `UV_OFFLINE=1 uv run --frozen pytest`
    resolves from the lockfile — the done-condition is met. Remaining: U1
    (author on both machines), C5 (blocked on the Exa key), strict-markers
    and `importlib` import mode (separate decisions, not started).
    - **(p) C1 — architect advisor.** [agent: fresh-context read-only
      subagent] Critiques the (p) brief on layering (chezmoi/Ansible/zsh),
      the `PRD.md` provision-versus-logic rule, `.chezmoiroot` versus the
      ignore list, and fit with this coordination work and Refactor B. Done
      when it returns agree/disagree per decision, risks missed and what
      would change its mind, then a round-2 reply to the other critiques.
    - **(p) C2 — pragmatist advisor.** [agent: fresh-context read-only
      subagent] Critiques daily workflow, the clash with `test-perf-xdist`,
      order of work and what breaks first. Done as C1.
    - **(p) C3 — skeptic advisor.** [agent: fresh-context read-only
      subagent] Attacks every claim in the brief with file:line evidence,
      hunts for tests that pass without checking anything, and asks whether
      a lockfile is needed at all. Done as C1.
    - **(p) C4 — second model, another vendor.** [agent: `ask-research
      --no-online --model openrouter/google/gemini-3.1-pro-preview`] Same
      brief, both rounds, zero-data-retention routing, web search off so
      nothing repo-derived reaches a search provider. The brief carries
      repo-relative paths only — no home paths, employer strings or usage
      numbers. The content is not work-tagged, so the author's go-ahead is
      the permission; record `policy explain
      boundaries.llm_processing.remote_model_allowed` with the run. Done as
      C1, with cost recorded; C4 and C5 together stay under $5 (author,
      2026-09-23).
    - **(p) C5 — practitioner survey.** [agent: `ask-research`, web search
      on] Public question only: how do public chezmoi repositories host
      Python tooling? Skipped, and the skip recorded, if the Exa key is not
      set. Shares C4's $5 cap. Done when a sourced answer or a recorded skip
      exists.
    - **(p) U1 — make the uv pin real.** [me — both machines] `bootstrap.sh`
      pins uv 0.12.17, but `apps/mise/files/config.toml:82` has
      `uv = "latest"` right under a comment (lines 77–81, `2f13ed2`) saying
      uv is not mise-managed; merge `57dd1dd` (2026-08-06) put the line
      back. On the Linux box, 2026-09-23, the `uv` on PATH is mise's
      (0.12.17) and no system uv exists, so bootstrap's `command -v uv`
      check passes and its pin never installs. Mac not checked. Order, so
      no machine is left without uv: (1) install system uv 0.12.17 on each
      machine, as `bootstrap.sh` does; (2) then claim `config.toml` in
      § Claimed and remove the mise line, fixing the comment or the line —
      the file is symlinked from `~/.config/mise/config.toml`, so the edit
      is live at once; (3) last, add `required-version = "==0.12.17"` to
      `[tool.uv]` — earlier, a mise uv floating to 0.13 fails every uv
      command here. The gita-plan session found the same mismatch (its G0
      side finding 1); this is the one task for it. Done when `command -v
      uv` is the system install on both machines, mise declares no uv, and
      `required-version` enforces the pin.
      **2026-09-28:** done on Linux — PR #25 merged, then `chezmoi init` +
      `mise reshim`; fresh shells resolve `uv` to system 0.12.17 and the
      `required-version` pin holds. The Mac's uv state is still unverified;
      it needs the same install-and-reshim. The stale mise uv installs
      (0.12.5, 0.12.18) remain orphaned on disk — `mise gc` could clear
      them, left as-is for now.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
