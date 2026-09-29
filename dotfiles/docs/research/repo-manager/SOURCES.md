# Sources and candidate ledger — repo-manager thread

Aggregated from the two G1 research passes (2026-09-23 source-verified; the
2026-09-24 expansion by the orchestrator) and the BK1 research pass. Status
values: **VERIFIED** (claims checked against pinned source/docs in-session),
**DOC-CITED** (official docs read, source not pinned), **PENDING**
(agent-reported or sonar-reported; must be verified before it carries weight).

The full per-candidate evidence lives in [GITA-RESEARCH.md](GITA-RESEARCH.md)
(canonical copy in this directory). This ledger is the index and the
verification-status board for the sonar round to build on.

## Candidate ledger (as of handoff)

| Candidate | Version checked | Fit | Status | Killer gap |
|---|---|---|---|---|
| gita | 0.16.8.2 (PyPI 2025-11-17) | groups, registry, overview | VERIFIED (source-pinned) | Discards child exit codes; no ff-only default |
| repoman (klokie) | main `b43f62d` 2026-09-10 | closest overall shape | VERIFIED (source-pinned) | Skips dirty repos before pull; one contributor, no releases/CI; host-identity manifest; 1-level scan |
| gitup (earwig) | 0.5.2 (PyPI 2025-06-09; repo touched 2026-09-02) | best human bulk updater | VERIFIED (source-pinned) | `_fetch_remotes()` swallows failures; no per-repo results |
| ghorg | v1.11.15 | org/user discovery | VERIFIED (source-pinned) | Standard update path cleans/resets; safer modes lack ff-only |
| vcstool | 0.3.0 | manifest batch ops | VERIFIED (source-pinned) | Plain `git pull`; detached-HEAD zero; no discovery |
| mani | 0.32.1 | projects/tasks runner | VERIFIED (source-pinned) | Sync semantics not the contract; custom tasks still ours |
| ghq | master (active, 3.8k stars) | clone-path convention | VERIFIED (docs + repo metadata) | No owner enumeration, no per-repo update; layout conflicts with ~/code |
| Google repo | manifest-format docs (main) | manifest+groups model | DOC-CITED | Syncs to manifest revisions; heavy workflow; no discovery/freshness |
| myrepos | site (last edit 2024; release 2018) | simple multi-VCS | DOC-CITED | Default `git pull`; policy moves into our config |
| Multigit (idemia) | repo metadata (main) | GUI multi-repo | DOC-CITED | No unattended interface; small Linux/macOS base |
| batchfetch | main tree | YAML clone/update jobs | DOC-CITED | Merge/rebase/reset strategies; no per-machine split; delete option |
| optorun/ansible_git | 8 commits (last 2026-09-12) | Ansible repo lists | VERIFIED (source-pinned) | `accept_hostkey: true` (violates host-key rule); no Darwin |
| ansible.builtin.git | v2.19.0 source | declarative checkout | VERIFIED (source-pinned) | Not a fetch-dirty/ff-only updater; force semantics dangerous |
| GitHub API/GraphQL limits | official docs | discovery constraints | DOC-CITED | 1k search cap; gh JSON hides completeness metadata |

## Sonar seeds to verify next round

Zephyr `west`; `grm` (git-repo-manager); `mu-repo`; `gitws`; `polyrepo`;
GitKraken Workspaces; Ansible Galaxy git-clone-loop roles beyond
`casa_cloud.github` and `optorun/ansible_git`. Status: PENDING until checked
against source at a pinned version.

## Test-coverage notes to collect per candidate (R-brief requirement)

For every new candidate record: suite presence (NONE/LIGHT/SOLID), what the
tests actually exercise (dirty-fetch? failure paths? documented contracts?),
and documented-vs-implicit contracts (exit codes, config semantics, auth
storage). Existing notes live in GITA-RESEARCH.md § Expanded comparison.

## Backup-research sources (BK1 scope, separate thread)

BorgBase / rsync.net / Hetzner pricing; borg 1.4.5 + borgmatic 2.1.8 install
paths; Galaxy roles `borgbase.ansible_role_borgbackup` and
`kliwniloc.borgbackup` (both grade B upstream, rejected as complete roles);
Bitwarden recovery-code mechanics. Full report:
`.worktrees/gita-plan_sub_bk1` (branch `agent/gita-plan_sub_bk1`), committed
for durability. Status: agent-reported with doc citations; **PENDING** spot
verification before BK1 decision.

## Sonar round (raw-pending) — 2026-09-29

One `openrouter/perplexity/sonar-deep-research` run of the PLAN.md § 8 brief;
full transcript in [SONAR-RAW.md](SONAR-RAW.md). **Every claim below is PENDING
source verification.** Two cautions recorded up front:

- The transcript's `[1]…[20]` markers are **unbound** — no footnote/URL list
  was returned — so every source must be re-derived during verification.
- It **contradicts a pinned finding**: the summary table marks
  `community.general.github_repo` R3 (discovery) `MET`, but GITA-RESEARCH
  verified it has **no owner-list discovery** ("requires a known repository
  name… no owner-list discovery interface"). Treat the sonar's R3 verdicts as
  suspect until re-checked.

### New candidates surfaced (all PENDING source-verify)

The sonar added these beyond the existing ledger; verdicts are its doc-level
claims, not ours:

| Candidate | Language | Sonar's headline | Verify (load-bearing) |
|---|---|---|---|
| mu-repo | Python | `.mu_repo` manifest + `mu group` (R1/R2 MET); `mu upd`/`mu rb` rebase (R4 MISSING); no R3/R6/R7; delegates auth to git | `mu rb` really stashes+rebases? `mu upd` fetch-but-no-ff? any exit-code/JSON contract? |
| Zephyr west | Python | manifest+workspace (R1/PARTIAL R2); `west update` detached-head, `--rebase` (R4 PARTIAL); no R3/R6; R7 partial | `west update` semantics vs fetch-then-ff-only; machine-readable output? |
| repoman (basti1302) | ? | a *different* repoman than ledger's klokie/repoman | confirm identity; does it update via pull/rebase? |
| Linkorb multi-repo | ? | `lib` multi-repo runner; `git pull` (R4 MISSING) | pull semantics; group story |
| DevSwarm Multi-Repo | ? | GUI-ish; R5 MET claimed | verify machine-readable verdicts |
| GitKraken Workspaces | GUI | R3 MET (discovery); R8 MISSING (stores secrets); proprietary | discovery semantics + secrets storage |
| grm / gitws / polyrepo | — | "general knowledge to 2024-10 only" — thin | still UNKNOWN; needs a fresh look |

### Sonar's closest three (re-verify each)

**mani**, **mu-repo**, **west** — each meets R1/R2/R8/R9 and misses R3/R4/R5/R6/R7
to varying degrees; none satisfies the full contract. This matches the
GITA-RESEARCH conclusion (no tool meets end-to-end) while promoting mu-repo and
west to "closest" alongside mani.

### Combination hypotheses (to carry into the ledger)

1. **mani + ghq + Ansible discovery** — glue in Python scripts/Ansible for R4/R5/R6.
2. **mu-repo + vcstool + ghq + a thin Python tool** — the tool owns R3–R7.
3. **west + myrepos + a Python wrapper** — wrapper owns safe sync + staleness.

The sonar's Outcome A/B framing is recorded in SONAR-RAW.md; neither is decided —
that is the author's call after verification.

## Sonar candidates verified (2026-09-29)

The sonar's new candidates, checked against fresh GitHub metadata + pinned
source. The author's post-sonar maintenance filter is folded in.

| Candidate | Verdict | Evidence |
|---|---|---|
| **west** (zephyrproject-rtos/west) | VERIFIED (source-pinned) — **R4 MISSING** | Python, 369★, pushed 2026-09-24 (active — the one genuinely live new candidate). But `west update` is manifest-convergence, not fetch-then-ff-only: default detaches HEAD at the manifest revision (`src/west/app/project.py` checkout --detach), with `--rebase`/`--keep-descendants` as the alternatives. Same model as Google `repo`, already rejected on R4. Active + Python, but the sync engine does not fit. |
| **mu-repo** (fabioz/mu-repo) | VERIFIED (metadata) — **maintenance-mode confirmed** | Python, 368★, last push 2024-02-12 (~19 months). `mu rb` stash+rebases, `mu upd` not ff-only. Author flagged abandonware risk; metadata confirms dormant. De-prioritize; revisit only if a later round needs it. |
| **repoman (basti1302)** | **DROPPED** | JavaScript (R11 wrong), 43★, last push 2024-03-04. Author turnoff (JS + unmaintained) confirmed. |
| **github_repo** contradiction | **Resolved — sonar was wrong** | GITA-RESEARCH pinned `community.general.github_repo` 13.4.0: requires a known repo name, no owner-list discovery. Sonar's R3=MET is not supported by source; treat the sonar's other R3 verdicts as suspect. |

**Consequence for the combination ledger:** with mu-repo dormant and
repoman(basti1302) dropped, no *new* active candidate supplies R4/R5/R6/R7. The
borrowing set is unchanged in substance — `mani` (Go, active, sync-not-a-contract)
and `west` (Python, active, manifest-only). The "no tool meets end-to-end; R4/R5/
R6/R7 must be owned" conclusion holds, and the author's note that a multi-tool
composition carries real learning/integration cost now weighs more precisely:
the only composition left is glue over tools that each miss the core semantics.

## Rules for this ledger

- Nothing enters "verified" from a README's word; load-bearing claims get
  source-checked at a pinned version (the GITA-RESEARCH standard).
- Sonar output lands here as raw-pending first; verification promotes rows.
- Rejections stay recorded with reasons so the search is not re-run blind.
