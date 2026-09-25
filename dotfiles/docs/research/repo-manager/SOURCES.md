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

## Rules for this ledger

- Nothing enters "verified" from a README's word; load-bearing claims get
  source-checked at a pinned version (the GITA-RESEARCH standard).
- Sonar output lands here as raw-pending first; verification promotes rows.
- Rejections stay recorded with reasons so the search is not re-run blind.
