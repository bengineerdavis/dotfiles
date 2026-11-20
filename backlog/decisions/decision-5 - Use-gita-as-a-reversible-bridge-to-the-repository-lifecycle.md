---
id: decision-5
title: Use gita as a reversible bridge to the repository lifecycle
date: 2026-11-10 20:54
status: accepted
---

## Context

The gita registration implementation landed in PR #152. PR #156 and PR #169
changed its test availability in CI, not its lifecycle behavior. On 2026-11-10,
current `main` still reads Linux-layout paths from `config/repos.yaml` and
runs `gita fetch` followed by `gita pull` during `upgrade`. That pull delegates
to ordinary `git pull`; it does not enforce a fast-forward-only contract.

The author needs useful synchronization before `redge-cli` exists. Existing
clones also need shared or machine-specific declarations. `redge-cli` remains
the planned long-term repository tool. Its specification reserves declaration
CRUD, discovery, and repository logic for that tool rather than Ansible.

The shared catalogue must work before and after the Linux layout migration.
The author settled the scope on 2026-11-09 and 2026-11-10: both machines resolve
the same shared repository identities, while an absent clone is reported as
missing. Shared membership means manage the clone where it exists; it does not
mean clone it on every machine.

## Decision

1. **Use gita as a useful interim bridge.** Keep gita registration and the
   existing topic lifecycle commands. DOT-173 adds safe synchronization of
   existing gita registrations. `redge-cli` is not a prerequisite for this
   work, and automatic cloning remains DOT-172's separate outcome.

2. **Separate declarations, registrations, and synchronization.** Shared
   declarations live in one committed registry. Machine-specific additions
   live in an unversioned local overlay. Gita's CSV files describe observed
   runtime registrations. A registry change does not itself delete a clone
   or registration. Until `redge-cli`, the author changes shared and local
   YAML declarations explicitly; Ansible does not prompt for declaration CRUD.

3. **Resolve paths per machine, not shared membership.** DOT-306 selects
   option (b): shared repository identities resolve through each machine's
   layout. Rejected alternatives are requiring Linux relocation first and
   accepting unresolved repositories on one machine. Do not restore
   `machines.yml` repository membership. Do not relocate or unregister a
   repository because its expected path is absent. Automatic cloning stays
   out of DOT-306.

4. **Synchronize primary clones, not linked worktrees.** A primary clone has
   its own `.git` directory. A linked worktree has a `.git` file that points
   into its primary clone. Git owns linked worktrees; gita does not register
   or advance them independently. Synchronizing the primary clone still works
   when linked worktrees are ignored. Fetching updates shared refs without
   changing any checked-out worktree. The sync operation never merges,
   rebases, resets, stashes, or relocates local work.

5. **Preserve local-only and work registrations.** Synchronization covers
   existing primary registrations, including the recursively reconciled
   machine-local work group and manually registered local-only clones. Work
   repository names never enter committed data. An ignored linked worktree
   is not an unaccounted clone.

6. **Keep discovery read-only until `redge-cli`.** A separate reporting task
   covers unregistered primary clones, registry drift, missing clones, and
   classification coverage. Routine install and upgrade remain noninteractive.
   The report distinguishes shared, machine-specific, ignored, and unaccounted
   repositories without requiring the last category to be empty. Provider
   failures and unreadable state are errors, not empty results.

7. **Keep the lifecycle interface stable.** `run-role.sh gita install` and
   `run-role.sh gita upgrade` remain the current interface. The approved
   topic-CLI direction is `topical`, with `run-role.sh` as a compatibility
   entry point. `redge-cli` can replace the adapter without requiring a new
   user-facing lifecycle vocabulary. The existing repository `update`
   contract refreshes availability and reports reconciliation choices;
   explicit CRUD changes declarations and `upgrade` safely advances clones.
   No version counter is introduced by this decision.

8. **Record a bounded architectural exception.** The repository-manager
   specification forbids repository logic in Ansible. Until `redge-cli`
   exists, the gita topic MAY contain the per-repository Git safety operations
   required by DOT-173. This exception covers registration and safe
   synchronization only. It does not permit declaration CRUD, interactive
   adoption, or remote discovery in Ansible. `redge-cli` inherits the
   registry semantics and behavioral tests; its adoption removes this
   exception. This is a bounded exception, not permission to build a new
   repository manager in the dotfiles repository.

9. **Do not make `try/` a required management surface.** Existing `try/`
   clones need not enter either registry for the bridge to work. Do not add
   `try/worktrunk-isolation-trial` as a required declaration or promise its
   synchronization. A later explicit machine-specific declaration may manage
   it without making every experiment a fleet obligation.

## Consequences

- Add shared declarations for `personal/backlog-md-py`, `personal/flagship`,
  `personal/roborev`, `forks/loreai`, `forks/opencode`, and `forks/skillet`
  when DOT-306 resolves their paths. Their shared declaration does not
  automatically create a Linux clone.
- Ignore the linked worktrees `personal/ai-prompt-library-skill-validation`
  and `personal/ai-prompt-library-structure-authoring` for registry and gita
  purposes. Their primary `personal/ai-prompt-library` clone is already
  registered and remains the synchronization target.
- DOT-173 no longer waits for DOT-172. PR #152 supplies its registration
  prerequisite. A clean clone advances only through `git merge --ff-only`.
  A failed fetch leaves freshness unknown; a dirty clone remains untouched.
- The first VM verification combines registration and safe synchronization
  using synthetic local Git repositories. It proves clean advancement,
  dirty-tree preservation, failed-fetch reporting, and work-registration
  preservation. It does not require GitHub access or automatic cloning.
- The retired `agent/gita-worktree-replay` implementation line receives no
  new work. PR #152 carries its registration outcome; DOT-306 supersedes its
  catalogue re-point. Cleanup of its remaining artifacts is separate and
  requires confirmation.
- No live clone, gita registration, declaration, or deployed configuration
  changed as part of recording this decision.
