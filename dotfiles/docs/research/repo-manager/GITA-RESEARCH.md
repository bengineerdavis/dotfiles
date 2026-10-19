# G1 — repository discovery and sync research

Research dates: 2026-09-23, expanded 2026-09-24. **Recommendation for review;
author decision pending.**
Assigned in main `TASKS.md` at `eb58cca` to `gita-plan_sub_g1`. This report is
the research deliverable, not completion of G1's author-decision gate.

## Conclusion

The expanded search found useful tools for parts of the job, but no established
one that meets the approved workflow end to end. **If the author accepts the
topic owning a declarative Ansible workflow, use `gh` for discovery and
`ansible.builtin.command` for explicit fetch/status/fast-forward steps. Use
`ansible.builtin.git` for clone-only work after path and remote checks. Keep
gita only for registration/overview if that separate human-facing function is
still wanted; never use it as the sync caller.** This
avoids a new executable or unreviewed Galaxy dependency; repo-specific policy
would live in ordinary Ansible tasks and still needs tests and maintenance. It
is not zero customer logic, so this remains a recommendation for the author's
decision, not implementation approval.

`gitup` is the closest established, human-friendly updater, but its current source
does not return a failed fetch to its caller or mark the run failed. It cannot
drive the topic's unknown-on-failure reporting. `repoman` is the closest
all-in-one multi-machine manager, but its repository is very new, its `pull`
skips dirty repos before fetching, and its shared host manifest does not match
the approved split of committed personal data from local work entries. Google's
`repo`, myrepos, ghorg, vcstool, mani, batchfetch and the desktop GUI are also
assessed below; each misses either the approved branch-safety semantics,
machine/work-data boundary, GitHub discovery, unattended reporting, or the
requested simple workflow.

The earlier ghorg/Gita report remains useful input. Its individual findings and
first-ranked primitives were not a final recommendation: the expanded search
was required after the author clarified that avoiding customer-maintained
repository logic is a deciding requirement.

## Requirement and fixed boundaries

Discover and sync the machine's selected repositories on Linux and macOS,
fetching even dirty repositories, fast-forwarding only safe working copies, and
reporting each outcome without letting a repository problem abort the topic;
incomplete discovery or a failed fetch must never become a claim of success.

The approved `HANDOFF.md` decisions 1–29 supply the comparison criteria:

- Named sets with a local pick; committed personal catalogue, separate local
  private/work entries, and a separate machine-written discovery/state file.
  No local pick means report and do nothing.
- Match existing clones by normalized remote before cloning. Adopt the existing
  gita baseline; recurse for registration, avoid `.venv`, preserve unambiguous
  membership, and report misplaced clones rather than relocating them.
- Discovery modes are `add`, `report` (default), and `off`. Timers always use
  report mode. At most ten additions per run; archives excluded by default;
  forks/templates use their approved layout types. An exclude prevents rediscovery.
- Missing gh, unavailable authentication, rate limits and truncation mean
  unknown discovery. Explicit entries still sync. Clones are never deleted;
  unregistering undeclared entries is opt-in. Host keys are never auto-trusted.
- Sync separates fetching from merging. Dirty/conflicted, detached, no-upstream
  and mid-operation repositories are reported and skipped for merging. Fetch
  failure means unknown freshness. The topic exits zero for repository problems;
  provider/configuration defects retain their approved failure behavior.
- Per-repository fetch and blocked timestamps feed the scheduled warning.
  Backup and restore gates still precede real machine-file data.

This research does not reopen those decisions. The provisional choices concern
the discovery tool, sync caller and the uncovered implementation boundary.

## First-pass alternatives (superseded by the expanded comparison below)

Ranked by fit to reliable, non-destructive per-repository reporting, then by how
much additional logic and configuration ownership they introduce. These are
qualitative judgments, not measured performance scores.

| Rank | Candidate | Fit and remaining gap | Disposition |
|---|---|---|---|
| 1 | Thin gh + Ansible calls, direct git for sync | gh exposes repository metadata as JSON. Individual git calls expose their own exit status. Ansible can register each result and continue. Completeness checks, remote matching, safe-update classification and timestamp state remain our responsibility. | First-pass recommendation only; expanded comparison below supersedes it. |
| 2 | ghorg 1.11.15 | Built for bulk organization/user discovery and cloning; supports multiple forges, exclusions, dry run, archives/forks filters and configurable aggregate failure exits. Its update modes do not implement the approved fetch-all-then-safe-ff workflow. | Reject as the working-copy sync engine. Discovery-only use adds another config/auth layer while still needing adaptation. |
| 3 | vcstool 0.3.0 | Recursive multi-repo operations and a path-keyed YAML manifest avoid basename ambiguity. It is a useful manifest-oriented alternative. It does not supply GitHub source discovery or the approved verdict/freshness policy. | Reject replacing the settled gita registry for this task; reevaluate for a portable manifest-centric workflow. |
| 4 | mani 0.32.1 | YAML projects/tags, parallel tasks, dry run and continue-on-error. `sync` primarily clones and manages project metadata; custom tasks would still contain our sync policy. | Reject a second repository/task catalogue without removing the bespoke work. |
| 5 | gita 0.16.8.2 as the bulk sync caller | Existing registry and grouping are useful. Final git failure statuses are discarded and there is no structured command-result interface in the inspected CLI. | Keep registration/overview; reject automated sync through `fetch`, `super` or `shell`. |
| 6 | `ansible.builtin.git` as the whole sync engine | Established checkout deployment module, with structured module results and check mode. Updating existing developer working copies can reset branches; dirty copies fail before fetching. | Use only for an appropriately guarded clone-new operation, not the approved sync algorithm. |

Switching to a new registry earns its cost only if it removes the uncovered
policy/state work while preserving gita adoption, remote matching and the
approved machine-file ownership. None of these candidates establishes that.

## Expanded comparison — 2026-09-24

The author clarified that the choice must minimize customer-maintained logic
and be human-friendly, with a simple workflow and current, usable documentation.
The complete handoff remains the fit test; a convenient bulk `pull` is not enough
if it can overwrite work or turn a failed fetch into “up to date”.

| Candidate | What it solves | Disqualifying gap or cost | Disposition |
|---|---|---|---|
| **[`gitup` 0.5.2][gitup-readme]** | Established cross-platform Python CLI, concise path/bookmark workflow, recursive repo discovery under a directory, all-remotes fetch, safe fast-forward of branches where possible, and dirty/diverged/detached skips. Its repository had source changes on 2026-09-02; PyPI's 0.5.2 release is from 2025-06-09. | Source prints failure text but exposes no per-repo result or non-zero exit. `_fetch_remotes()` returns on the first remote failure, then `_update_repository()` continues using whatever tracking refs exist; callers do not receive a failed state. It can therefore report branch status after an incomplete fetch and exit successfully. README says Python 3.10+ while package metadata allows Python >=3.8. It has local bookmarks, not a machine-selected catalogue or GitHub-org discovery. It also fast-forwards every eligible local branch, not just the checked-out branch. | **Reject for automated topic sync.** Good human-facing bulk updater, but its errors cannot drive the timer or freshness record. |
| [`repoman`][repoman-readme] (main at `b43f62d`, 2026-09-10) | Closest overall shape: per-host manifest, local status, clone-missing, parallel fast-forward-only pull, per-repo skipped/failed counts and clear command examples. | Started March 2026; GitHub shows one contributor, no releases, one star and no CI workflow in the inspected tree ([metadata][repoman-api], [contributors][repoman-contributors], [releases][repoman-releases]). `pull` checks dirty state and skips before invoking `git pull`, so it does not fetch dirty repos. `init` scans only one directory level and `Upsert` keys entries by basename, retaining any existing remote; remote identity/collisions are not reliably resolved. It scans existing clones, not GitHub sources. The shared manifest attaches repo membership to pinned host identities; these could be set to semantic names, but the design is host→repo rather than the approved local selection among named sets. It has one synchronized manifest, so it does not supply the separate local-only work file. Its optional Restic features also do not replace the settled Borg/1Password design. | **Do not adopt as the fleet foundation.** It is the closest candidate to follow or discuss upstream, but fails current fetch, inventory, data-boundary and support requirements as written. |
| [Google `repo` manifest tool][repo-manifest] | Maintained manifest-and-groups model; can define projects once, select groups during sync, and add machine-local projects with local manifests. Per-project paths and independent remotes are supported. | It is a multi-project source-checkout system with its own commands and manifest workflow, not a simple GitHub catalogue. `repo sync` converges checkouts to manifest revisions rather than merely fetching every current branch then fast-forwarding clean repositories. It adds substantial workflow and does not discover repositories from GitHub or provide the required per-repo fetch-age records. | **Reject for this task.** Strong for coordinated source builds pinned to a manifest, not a small personal repository manager for existing arbitrary branches. |
| [`myrepos` (`mr`)][myrepos-home] | Simple, documented command that runs VCS actions across registered directories; supports hierarchical config and per-repo commands. | Its published default Git update is `git pull`; the manual config would have to implement this task's fetch/dirty/fast-forward/result rules per customer. Project news is old (latest listed release 2018; page last edited 2024). No declared machine sets or GitHub source discovery. | **Reject.** The extension point moves the maintenance into our `.mrconfig`; it does not supply the needed safe policy. |
| **[vcstool][vcs-readme] / [mani][mani-readme]** | Human-readable manifests, multi-repository operations and options for continuing/reporting command failures. | The reviewed implementations do not provide the handoff's safe fetch-all / fast-forward-only contract, source discovery, or the local work-data split. They leave the same policy in custom task configuration. | **Reject as the manager.** Keep as relevant examples of manifest and batch-runner interfaces, not as the solution. |
| [`ghq`][ghq-readme] | Excellent, actively maintained clone-location convention; matches remote identity to a canonical host/owner/repo path, can find existing clones, and offers `ghq get -u` for one selected repo. | It does not enumerate an owner's repositories, maintain per-machine declared sets, or update all local repos with per-repo outcomes. Its canonical directory layout would conflict with the settled `~/code/<type>/` layout unless repositories were moved. | **Reject as the source of truth or updater.** Useful only as an optional clone helper, and the current path layout removes its main benefit. |
| **[ghorg][ghorg-readme]** | Organization/user clone discovery, filters and exclusions. | Its standard update path cleans/resets; its safer modes do not give the approved fetch-first/ff-only behavior or persistent per-repo outcomes. | **Reject as the working-copy manager.** Discovery-only use adds a second source configuration without removing later policy work. |
| [Multigit GUI][multigit-readme] | Human-friendly graphical fetch/pull and status across many repositories; mature in its Windows-first environment. | No unattended topic/timer interface or machine-selected catalogue; Linux is documented stable with small user base and macOS working with limited user base ([status and platform statement][multigit-readme], [repository metadata][multigit-metadata]). It cannot feed the required state records. | **Reject for the fleet workflow.** Could help a person operate a local workspace, not provision or schedule it. |
| [Batchfetch][batchfetch-readme] | YAML file describes multiple clone/update jobs; parallel execution, per-task options and simple examples. | The declared strategies are merge, rebase or reset (default merge), not the approved fetch-then-ff-only rule. It has a destructive `delete` task option, expects its own repo-list file, and does not provide per-machine work-data separation or GitHub source discovery. Dirty-tree and machine-readable per-repo error behavior were not demonstrated in this review. | **Reject for the complete workflow.** It can clone/update a fixed add-on list but does not remove the main inventory and safety gaps. |
| **[optorun/ansible_git role][optorun-role]** | Common plus host-specific repo lists, clone/update loop, destination override. | The inspected repo has 8 commits, 0 stars, no releases and last push 2026-09-12 ([metadata][optorun-role-metadata]). Its metadata lists Debian bullseye/bookworm and EL 8, not Darwin. It calls `ansible.builtin.git` with `accept_hostkey: true`, which disables SSH host verification, contrary to handoff decision 13. It has no dirty-fetch continuation, per-repo timestamp behavior or test suite in its small tree. Galaxy exact-name search found only older unrelated roles. | **Reject.** The host-key setting and platform scope alone disqualify it. |
| **[`ansible.builtin.git`][ansible-git-doc]** | Official, documented module with full check-mode support and before/after revisions. Appropriate for declarative clone operations. | It deploys a checkout at a requested revision; it is not the handoff's fetch-dirty, inspect-each-working-copy, ff-only updater. `force: false` protects dirty trees by failing rather than fetching them; `force: true` discards local changes. Its update/version flow is not an acceptable replacement for explicit sync. | **Use for clone-only work** after validating the destination/remote; do not use it as the sync policy. |

Expanded comparison sources: [`gitup` README/source/package metadata][gitup-readme]
([update implementation][gitup-update], [CLI][gitup-cli], [PyPI][gitup-pypi],
[changelog][gitup-changelog]); [Repoman README and pinned command/manifest
sources][repoman-readme] ([pull][repoman-pull], [Git helpers][repoman-gitx],
[manifest][repoman-manifest], [discovery scan][repoman-init], [clone][repoman-clone],
[current metadata][repoman-api], [contributors][repoman-contributors],
[releases][repoman-releases]); [Google repo manifest format][repo-manifest];
[myrepos documentation/news][myrepos-home] ([news][myrepos-news]); [ghq README][ghq-readme];
[Multigit README and repository metadata][multigit-readme] ([metadata][multigit-metadata]);
[Batchfetch README/source/package][batchfetch-readme] ([Git behavior][batchfetch-source],
[package metadata][batchfetch-pypi]); and [optorun role/tasks/platform metadata][optorun-role]
([tasks][optorun-role-tasks], [metadata][optorun-role-meta],
[Galaxy search][galaxy-role-ansible-git]).

### Ansible fallback that avoids a bespoke executable

No third-party role found removes more maintenance than the current
`ansible.builtin` modules. The smallest supportable fallback is an Ansible topic
that owns only the machine-specific orchestration:

1. `roles/repo-context` resolves the selected personal catalogue plus
   machine-local entries into `(path, expected remote, type, source)` records.
2. `ansible.builtin.git` clones only a missing declared path, with
   `update: false`; before acting on any existing path, compare its configured
   remote to the declaration and report a mismatch rather than changing it.
3. An included task file loops once per path. `ansible.builtin.command` runs
   `git fetch --all` first for every repository, including dirty ones, and
   stores its `rc` with that path. A failed fetch is UNKNOWN and is never passed
   to the merge phase.
4. For successful fetches, commands inspect cleanliness, detached HEAD and
   upstream. Only a clean attached branch with an upstream may run
   `git merge --ff-only @{u}`. Capture its result per repo; diverged, detached,
   dirty, no-upstream and in-progress states become explicit skips. A loop's
   nonzero result is captured (`failed_when: false`) so other repos still run;
   the final report names each result while the topic exits 0 for repo-local
   problems. Malformed input and missing required providers remain fatal.
5. Write last-fetch/blocked-since/last-good timestamps to the separate
   machine-written state file already required by G4/G5, using Ansible's
   registered results and copy/template modules. Do not derive “good” from
   the task's exit 0 alone.

This is still topic-specific Ansible workflow, but it uses standard commands
and FQCN modules instead of a new customer-maintained program or third-party
role. It is not zero logic: source matching, verdict classification and durable
timestamps remain explicit, tested Ansible tasks. `ansible.builtin.git` alone
cannot meet the sync contract. If “no custom logic” also rules out declarative
Ansible tasks for these checks, the requirements have no currently verified
implementation and the author must choose which contract to relax or which
upstream project to sponsor.

The concrete design still needs tests against dirty-but-fetchable repos,
failed fetches, detached/no-upstream/diverged states, current and inactive
branches, failed `ff-only`, and no-op up-to-date results. That proof belongs to
G4, not to this source review.

## Deciding evidence: gita loses command failures

Inspected release: **0.16.8.2**, PyPI upload 2025-11-17; Git tag
`v0.16.8.2`, commit `756dbd2f7448510bd33f3a9b0f3881f61ee65cf6`.
The tag-to-HEAD comparison at
`062a5e1ed56cad9b5f81c63791cd4ab130f175d9` (2026-03-31) showed no changes to
the inspected execution files. This is upstream source evidence, not a claim
about the currently installed binary on either target.

| Execution path | What the upstream code does | Consequence |
|---|---|---|
| `utils.run_async()` | Captures stdout/stderr, prints repo-prefixed text, and returns the path when the child return code is nonzero. | There is internal per-repo failure detection, but not an exposed final result record. |
| `f_git_cmd()`, one repo or async-disabled command | Calls `subprocess.run(...)` without checking or returning `returncode`. | Calling gita once per repo does not repair error propagation. |
| `f_git_cmd()`, parallel command | Collects failed paths from `exec_async_tasks()`, retries those commands synchronously, then discards each retry result. | The initial failure list is neither final nor exported; retries may also prompt. |
| `f_super()` / `f_shell()` | `super` delegates to `f_git_cmd`; `shell` captures and prints output but ignores the status. | Neither is a machine-readable failure workaround. |
| `main()` | Calls `args.func(args)` without propagating a result; no JSON/results option in the parser. | An ordinary failed git child can leave gita exiting successfully. Argument errors and Python exceptions can still produce nonzero exits. |

Sources: [async runner][gita-utils], [dispatcher, shell and super][gita-main],
[CLI parser and dispatch][gita-parser], [default commands][gita-cmds],
[PyPI metadata][gita-pypi], [tag-to-HEAD comparison][gita-compare].

`cmds.json` is command configuration, not a result format. `repos.csv` and
`freeze` describe repositories, not fetch success. Parsing terminal error text
would lose silent failures, confuse successful git stderr with failure, and
couple the caller to localized output. Importing gita's internal coroutine or
adding a custom status-emitting shell command would itself create an adapter;
direct git is the simpler boundary.

Also, gita's default `merge` is `git merge @{u}`, without `--ff-only`.
Supplying ff-only through `super` fixes that argument but not result handling.
The approved exit-zero topic policy requires recording failures accurately
*before* deciding to continue; gita's lost status cannot satisfy it.

**Registration observation for G3:** the same release's `_make_name()` adds one
parent component on basename collision. That is not general uniqueness: two
different paths can still have the same parent/basename pair, and `add_repos()`
builds a dictionary keyed by that name. Preserve the handoff's collision rule
and verify adopted registration identities. Merely assuming every basename
collision is either always handled or always dropped would misstate the code.
See [registration naming code][gita-names].

## gh discovery: limits, truncation and visibility

The load-bearing source read is **gh v2.100.0**, matching the handoff's reported
install. GitHub's latest release response was **v2.101.0** (2026-09-15).
The comparison to that release contains no changes to `repo/list/list.go` or
`repo/list/http.go`. No upgrade is required or performed by this report.

1. **30 is the default maximum result count, not the API page size.**
   `NewCmdList()` sets `--limit` to 30 and rejects values below one.
   `listRepos()` requests `min(limit, 100)` per page and follows cursors until
   the overall limit or end of the connection. A large limit can span pages;
   a response below that limit can only establish completeness within the
   selected endpoint and token's visible scope.
2. **JSON hides completeness metadata.** The exporter writes only
   `listResult.Repositories`, not `TotalCount`, `FromSearch` or `pageInfo`.
   Reaching the requested limit is not itself an error. Treat a result count
   equal to the limit as *possibly truncated/unknown*, even when the owner
   might coincidentally have exactly that many repositories. Count before
   local archive/exclude filtering. Never unregister from that result.
3. **Some filters switch APIs.** `--archived`, `--no-archived`, language, topic,
   and internal visibility route to Search. The source explicitly warns of
   Search's 1,000-result maximum only for a limit above 1,000. Worse, the JSON
   exporter returns before that warning. Thus `--limit 5000 --no-archived
   --json ...` can produce fewer than 5,000 results without proving completeness.
4. **Preserve the bounded approach in the handoff by avoiding Search.** List
   the owner with an explicit positive limit and JSON fields, then filter
   `isArchived` locally. The inspected `RepositoryFields` includes
   `nameWithOwner`, `sshUrl`, `isArchived`, `isFork` and `isTemplate`, covering
   owner-qualified identity, clone URL and classification. Avoid Search-triggering flags on
   this path. A saturated limit leaves discovery unknown and explicit sync
   continues; do not silently raise it indefinitely.
5. **Account scope is independent of pagination.** `repo list OWNER` means
   repositories owned by that user/organization, not every repository the
   account can access. Record the authenticated API identity and host used
   for the listing. A successful short list cannot prove private repos hidden
   by another account, token scope, SSO or installation permissions do not
   exist. Label the report with that visibility scope; authentication failure
   is unknown, not an empty catalogue.
6. **A failed listing stays unknown.** In `listRepos()` and `searchRepos()`,
   an API error returns an error rather than the accumulated list. The caller
   still needs to validate exit status and JSON shape before using output.
   GitHub documents GraphQL rate-limit errors with HTTP 200 and resource-limit
   failures with partial data plus errors; HTTP success alone is insufficient.

Sources: [list CLI/exporter][gh-list], [pagination and Search routing][gh-http],
[JSON field declarations][gh-fields], [version comparison][gh-compare],
[GraphQL limitations][github-limits].

### Existing option for explicit pagination

`gh api --paginate` already follows REST pagination and GraphQL cursors;
`--slurp` wraps pages in an outer array. A GraphQL query must accept
`$endCursor` and request `pageInfo { hasNextPage endCursor }`. This can expose
`totalCount`, page metadata and the viewer identity rather than dropping them.
It is the strongest next option if bounded `repo list` routinely saturates.

It is not a reason to hand-write an HTTP pagination client or to amend the
approved bounded behavior silently. A paginated design would still need
bounded resource use, rejection of partial/error responses, deduplication and
account-scoped reporting. It must finish validation before adding anything;
page-one success followed by page-two failure is unknown for the source.
See the [official gh api manual][gh-api].

## Why ghorg and the other tools do not close the gap

### ghorg

The **v1.11.15** README explicitly positions repeat runs as refreshing clones
and warns that default operation overwrites local changes. The code confirms
the distinction:

- `handleStandardPull()` checks out the selected clone branch, cleans, resets,
  then pulls. `GitClient.Clean()` runs `git clean -f -d`;
  `Reset()` runs `git reset --hard origin/<clone-branch>`; `Pull()` does not
  supply `--ff-only`. This is not a safe update of the current developer branch.
- `--protect-local` checks before fetching and can skip dirty repositories
  altogether. A failure to determine unpushed commits is treated as no detected
  local changes. It does not supply the required fetch-first/unknown behavior.
- `--no-clean` avoids that update path; `handleNoCleanMode()` fetches only when
  `GHORG_FETCH_ALL` is enabled. It supplies no fast-forward step. This is a
  useful safer mode, but still needs our safe-update engine.
- `--dry-run` prints URLs and a summary. The source returns before cloning.
  The documented JSON filter-hook interface is for selecting/modifying clone
  inputs, not per-repo sync outcomes. The documented CSV stats are run-level
  counts, not the per-repo fetch/blocked history the warning requires.
- Clone errors and informational problems have configurable aggregate exit
  codes. A wrapper can keep the Ansible run alive, but aggregate status alone
  is insufficient to update each repository's freshness correctly.

Sources: [README][ghorg-readme], [repository processor][ghorg-processor],
[git commands][ghorg-git], [dry-run and exit handling][ghorg-clone].

Practitioner evidence supports the mismatch rather than proving a defect in
every release: [issue #629][ghorg-629] asks to keep the currently checked-out
branch, and [#630][ghorg-630] asks for separate fetch/pull controls. Both are
reports of desired workflows, not runtime tests of v1.11.15. The ranking rests
on the pinned source above.

### vcstool and mani

[vcstool 0.3.0][vcs-readme] recursively finds local repositories and imports
or exports path-keyed YAML manifests. That is good prior art for avoiding
basename collisions. It is not discovery of new repositories from a GitHub
owner, and supplying custom Git commands still leaves the guards and state
logic to us. It would add another representation alongside the approved gita
baseline without demonstrating less work.

It does handle aggregate failure better than gita: `simple_main()` returns one
if any job's `returncode` is nonzero. However, `GitClient.pull()` calls plain
`git pull`; after a failure it converts the result to zero if HEAD is detached.
That cannot distinguish a failed fetch on a detached repository from a benign
merge skip. This is an additional reason to prefer direct, separately observed
fetch/merge operations. Sources: [command runner][vcs-command],
[Git pull implementation][vcs-git].

[mani v0.32.1][mani-commands] supports project/tag targeting and
`--ignore-errors`; its documented task output formats are stream, table,
Markdown and HTML. Its `sync` command clones and can update `.gitignore` and
remotes. Neither that command nor the documented output contract establishes
the approved per-repository sync verdicts. Implementing them as custom mani
tasks merely moves our bespoke code to another runner. Sources:
[README][mani-readme], [output formats][mani-output].

## Docs and Galaxy search

This is a bounded search, not a claim that no suitable collection can exist.
The Galaxy v3 collection search using `q=gita` and `q=ghorg` returned no
matches. `q=github` with `is_highest=true`, `limit=100` returned 53 entries and
no next page; their advertised contents were screened for discovery, cloning
and repository management. Legacy-role exact-name queries for `gita` and
`ghorg` returned zero. Legacy `search=` and `name__icontains=` attempts returned
the unfiltered catalogue and were discarded as invalid search evidence.

| Existing module/collection | Evidence and fit | Adoption/support assessment |
|---|---|---|
| `ansible.builtin.git` | Docs show check mode and structured before/after results. In ansible-core v2.19.0 source, dirty copies with `force: false` fail before `fetch()`. `switch_version()` uses branch checkout/reset; `update: false` returns an existing checkout without checking remote identity. | Built-in, no new Galaxy dependency. Candidate for missing clones only after remote/path validation; disqualified for working-copy sync even with `force: false`. |
| `community.general.github_repo` 13.4.0 | Source requires a known repository name and supports only `present`/`absent`. It can create, edit or delete remote repositories. No owner-list discovery interface. | Already-used collection, wrong operation. Do not use check mode as an invented discovery API. No new adoption grade claimed. |
| `ansible.builtin.uri` / `command` | HTTP and command primitives; neither is a repo-context/safe-sync engine. `uri` would make this project handle auth and pagination that gh already handles. `command` exposes `rc`, stdout and stderr without a shell pipeline; its check-mode support is only partial. | Built-ins. CLI fallback still needs the author's pre-adoption ruling under TOPIC-RECIPES. |
| `compscidr.github_cli` 0.0.17 | Galaxy advertises gh and extension installation roles. | Installation, not source discovery/sync; G6 already has its install direction. Not adopted or support-graded. |
| `bodsch.scm` 1.12.0 | Galaxy advertises GitHub checksum/latest/release modules. | Release-artifact operations, not repository-source discovery. Not adopted or support-graded. |
| `casa_cloud.github` 1.0.0 | `git_clone_001` asserts input variables, calls bare `git` with repo/dest, then caches the result as a fact. It adds neither discovery nor safe sync. | Reject: wraps the already-available checkout module with its default update behavior. Source-only grade C assessment below. |

The [support-grade rubric][recipes] requires maintained code, tests, supported
status and honest check-mode behavior; roles also need a license check. No new
third-party dependency is recommended here, and no installed-copy support grade
was established. Finding a Galaxy listing is not evidence that those checks
pass. Any later adoption needs the four checks at the chosen version, with the
author consulted for grade B and grade C rejected.

For the plausible clone-role candidate, inspected upstream snapshot
`99ba4773b2ca621927c71fab64a3fb6552a63a70` (2025-10-25):

| Casa-Cloud role check | Evidence |
|---|---|
| Maintained | Named owner in source; no collection changelog or tests in the returned, non-truncated collection tree. Recent role-specific maintenance was not established. Unproven. |
| Tested or trivially thin | Thin wrapper around assertions, git and set_fact; meets the role-specific thinness alternative. |
| Supported tier | `meta/runtime.yml` declares Ansible >=2.13 and no removal; role metadata lists Ubuntu only. No removal found, but macOS support is unproven. |
| Interface honesty | Source shows update-enabled git and `cacheable: true` result state. README is a placeholder and documents no check-mode contract. Does not pass. |
| License | Role header, README and metadata declare MIT. Declaration checked; no package-wide license audit. |

At most two support checks pass: **provisional grade C; do not adopt**. This
assessment is of linked upstream source, not an installed copy or a verified
byte-for-byte match to the Galaxy tarball. That limitation cannot upgrade it
to grade A. Sources: [role tasks][casa-tasks], [README][casa-readme],
[role metadata][casa-meta], [runtime metadata][casa-runtime], [tree][casa-tree].

Sources: [built-in git docs][ansible-git-doc], [git source][ansible-git-src],
[command docs][ansible-command], [uri source][ansible-uri],
[github_repo source][ansible-github-repo], [Galaxy collection search][galaxy-search],
[gita collection query][galaxy-gita], [ghorg collection query][galaxy-ghorg],
[gita role query][galaxy-role-gita], [ghorg role query][galaxy-role-ghorg],
[Casa-Cloud version metadata][galaxy-casa].

## Implementation boundary and next decision

The [PRD provision/logic boundary][prd] and AGENTS.md's outsourcing ladder also
apply to logic written as Ansible tasks. The author explicitly requested that
Ansible modules/roles be assessed when no existing tool fits; this report gives
that path rather than proposing a new standalone program.

**Recommendation for the author:** keep the repo-context/catalogue contract;
use gh only for GitHub discovery; use `ansible.builtin.git` for missing-clone
operations after remote/path validation; and have the topic call Git's explicit
fetch/status/fast-forward commands per repository, keeping each registered
result tied to its path. Use `failed_when: false` only on the individual repo
operation and report the collected results; malformed inputs/provider failures
remain fatal. Persist timestamps from those results, not from overall exit 0.
This is standard Ansible orchestration, not a custom executable or third-party
role. It still carries a small amount of topic-specific policy in the role, so
the author must decide whether that is the intended reading of “use Ansible”
and of the provisioning/logic boundary.

Do not call gita as the sync provider; its failures are not machine-readable.
It can remain the registry/overview tool only if the author wants that separate
human-facing function. The original G3/G4/G7 tasks describe behavior and
acceptance criteria, not a required external engine.

Direct Git supplies the primitive guarantee: `merge --ff-only` refuses a
non-fast-forward and exits nonzero. It does not supply the whole safety policy:
Git can allow some non-overlapping dirty merges, so ff-only alone does not
replace the clean-working-copy check. The caller must distinguish fetch failure
from merge eligibility and must not report a successful no-op merge as
“fast-forwarded.” See [Git 2.50.0 merge documentation][git-merge].

Remaining author decisions before G2/G3:

1. Accept/adapt/reject using `gh` for discovery and the Ansible task sequence
   for clone/sync; decide whether gita still earns its separate registration
   and overview role.
2. Confirm that this topic-specific Ansible task sequence is the acceptable
   maintenance boundary for the Git safety checks and timestamps. The author
   directed Ansible as the fallback, but its tasks still encode repo policy.
3. Decide whether gita's registration/overview function earns keeping beside
   the topic-owned inventory, or whether Ansible should own both.

The orchestrator owns recording the decision and revising shared `TASKS.md`.
The approved backup order and G5 confirmation about classifying a new clone
remain in force.

## Evidence scope and follow-up checks

Checked: approved handoff and repository rules; versioned upstream execution
code for gita, gh, ghorg, vcstool, gitup, Repoman and Ansible git; official
`repo` manifest documentation; myrepos and Multigit docs; Batchfetch docs;
Galaxy catalogue/role metadata, Casa-Cloud source and the optorun role; and
the cited practitioner reports. Public metadata/source requests were
read-only. Conclusions about code paths are static analysis.

Not exercised: candidate binaries (including `gitup` and Repoman), fixture
repositories, real repository sync or discovery, target authentication/SSO,
rate-limit or truncation injection, private account visibility, Linux timers or
macOS behavior. The GitHub repository metadata for Repoman was checked, but no
runtime, release artifact, or target-platform claim follows from it. No
performance or end-to-end reliability claim follows from this research. No
installation, configuration/credential change, commit or push was performed.

Documentation validation: inspected the report diff and checked whitespace with
`git diff --no-index --check /dev/null dotfiles/docs/GITA-RESEARCH.md`.
Executable tests, mutation checks and deployment validators were not run for
this research-only change. Live documentation and catalogue URLs are snapshots
of the research date; pinned source links define the code conclusions.

Once authorized and routed, implementation checks need to show both successful
and failed fetches; dirty-but-fetched versus clean-fast-forwarded; detached,
no-upstream, mid-operation and diverged skips; equal/ahead no-op handling;
unknown discovery on auth/API/schema/truncation failures; and report-only timer
behavior. A failure must leave prior freshness evidence intact rather than
advance it. These are acceptance inputs for the later items, not tests run here.

[recipes]: TOPIC-RECIPES.md#recipe-docs-and-galaxy-first--the-module-vs-shell-ladder
[prd]: ../../PRD.md#architecture-provision-initialize-state
[gita-utils]: https://github.com/nosarthur/gita/blob/v0.16.8.2/gita/utils.py#L368-L411
[gita-names]: https://github.com/nosarthur/gita/blob/v0.16.8.2/gita/utils.py#L273-L324
[gita-main]: https://github.com/nosarthur/gita/blob/v0.16.8.2/gita/__main__.py#L423-L501
[gita-parser]: https://github.com/nosarthur/gita/blob/v0.16.8.2/gita/__main__.py#L509-L909
[gita-cmds]: https://github.com/nosarthur/gita/blob/v0.16.8.2/gita/cmds.json
[gita-pypi]: https://pypi.org/pypi/gita/json
[gita-compare]: https://github.com/nosarthur/gita/compare/v0.16.8.2...062a5e1ed56cad9b5f81c63791cd4ab130f175d9
[gh-list]: https://github.com/cli/cli/blob/v2.100.0/pkg/cmd/repo/list/list.go
[gh-http]: https://github.com/cli/cli/blob/v2.100.0/pkg/cmd/repo/list/http.go
[gh-fields]: https://github.com/cli/cli/blob/v2.100.0/api/query_builder.go#L476-L543
[gh-compare]: https://github.com/cli/cli/compare/v2.100.0...v2.101.0
[gh-api]: https://cli.github.com/manual/gh_api
[github-limits]: https://docs.github.com/en/graphql/overview/resource-limitations
[ghorg-readme]: https://github.com/gabrie30/ghorg/blob/v1.11.15/README.md
[ghorg-processor]: https://github.com/gabrie30/ghorg/blob/v1.11.15/cmd/repository_processor.go
[ghorg-git]: https://github.com/gabrie30/ghorg/blob/v1.11.15/git/git.go
[ghorg-clone]: https://github.com/gabrie30/ghorg/blob/v1.11.15/cmd/clone.go
[ghorg-629]: https://github.com/gabrie30/ghorg/issues/629
[ghorg-630]: https://github.com/gabrie30/ghorg/issues/630
[vcs-readme]: https://github.com/dirk-thomas/vcstool/blob/0.3.0/README.rst
[vcs-command]: https://github.com/dirk-thomas/vcstool/blob/0.3.0/vcstool/commands/command.py
[vcs-git]: https://github.com/dirk-thomas/vcstool/blob/0.3.0/vcstool/clients/git.py#L586-L612
[mani-readme]: https://github.com/alajmo/mani/blob/v0.32.1/README.md
[mani-commands]: https://github.com/alajmo/mani/blob/v0.32.1/docs/commands.md
[mani-output]: https://github.com/alajmo/mani/blob/v0.32.1/docs/output.md
[ansible-git-doc]: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/git_module.html
[ansible-git-src]: https://github.com/ansible/ansible/blob/v2.19.0/lib/ansible/modules/git.py
[ansible-command]: https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html
[ansible-uri]: https://github.com/ansible/ansible/blob/v2.19.0/lib/ansible/modules/uri.py
[ansible-github-repo]: https://github.com/ansible-collections/community.general/blob/13.4.0/plugins/modules/github_repo.py
[galaxy-search]: https://galaxy.ansible.com/api/v3/plugin/ansible/search/collection-versions/?q=github&is_highest=true&limit=100&format=json
[galaxy-gita]: https://galaxy.ansible.com/api/v3/plugin/ansible/search/collection-versions/?q=gita&is_highest=true&format=json
[galaxy-ghorg]: https://galaxy.ansible.com/api/v3/plugin/ansible/search/collection-versions/?q=ghorg&is_highest=true&format=json
[galaxy-role-gita]: https://galaxy.ansible.com/api/v1/roles/?name=gita&format=json
[galaxy-role-ghorg]: https://galaxy.ansible.com/api/v1/roles/?name=ghorg&format=json
[galaxy-casa]: https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/casa_cloud/github/versions/1.0.0/?format=json
[casa-tasks]: https://github.com/Casa-Cloud/CASACLOUD-ANSIBLE-COLLECTIONS/blob/99ba4773b2ca621927c71fab64a3fb6552a63a70/ansible_collections/casa_cloud/github/roles/git_clone_001/tasks/main.yaml
[casa-readme]: https://github.com/Casa-Cloud/CASACLOUD-ANSIBLE-COLLECTIONS/blob/99ba4773b2ca621927c71fab64a3fb6552a63a70/ansible_collections/casa_cloud/github/roles/git_clone_001/README.md
[casa-meta]: https://github.com/Casa-Cloud/CASACLOUD-ANSIBLE-COLLECTIONS/blob/99ba4773b2ca621927c71fab64a3fb6552a63a70/ansible_collections/casa_cloud/github/roles/git_clone_001/meta/main.yml
[casa-runtime]: https://github.com/Casa-Cloud/CASACLOUD-ANSIBLE-COLLECTIONS/blob/99ba4773b2ca621927c71fab64a3fb6552a63a70/ansible_collections/casa_cloud/github/meta/runtime.yml
[casa-tree]: https://github.com/Casa-Cloud/CASACLOUD-ANSIBLE-COLLECTIONS/tree/99ba4773b2ca621927c71fab64a3fb6552a63a70/ansible_collections/casa_cloud/github
[git-merge]: https://git-scm.com/docs/git-merge/2.50.0
[gitup-readme]: https://github.com/earwig/git-repo-updater/blob/7e8a3a4c303e3f1ee6d7994a88a8742c34fae645/README.md
[gitup-update]: https://github.com/earwig/git-repo-updater/blob/7e8a3a4c303e3f1ee6d7994a88a8742c34fae645/src/gitup/update.py
[gitup-cli]: https://github.com/earwig/git-repo-updater/blob/7e8a3a4c303e3f1ee6d7994a88a8742c34fae645/src/gitup/cli.py
[gitup-pypi]: https://pypi.org/project/gitup/0.5.2/
[gitup-changelog]: https://github.com/earwig/git-repo-updater/blob/7e8a3a4c303e3f1ee6d7994a88a8742c34fae645/CHANGELOG
[repoman-readme]: https://github.com/klokie/repoman/blob/b43f62d58617e596c747bd9626a4131f1de7054c/README.md
[repoman-pull]: https://github.com/klokie/repoman/blob/b43f62d58617e596c747bd9626a4131f1de7054c/internal/cmd/pull.go
[repoman-gitx]: https://github.com/klokie/repoman/blob/b43f62d58617e596c747bd9626a4131f1de7054c/internal/gitx/gitx.go
[repoman-manifest]: https://github.com/klokie/repoman/blob/b43f62d58617e596c747bd9626a4131f1de7054c/internal/manifest/manifest.go
[repoman-init]: https://github.com/klokie/repoman/blob/b43f62d58617e596c747bd9626a4131f1de7054c/internal/cmd/init.go
[repoman-clone]: https://github.com/klokie/repoman/blob/b43f62d58617e596c747bd9626a4131f1de7054c/internal/cmd/clone.go
[repo-manifest]: https://gerrit.googlesource.com/git-repo/+/refs/heads/main/docs/manifest-format.md
[multigit-readme]: https://github.com/idemia/multigit/tree/main
[multigit-metadata]: https://api.github.com/repos/idemia/multigit
[batchfetch-readme]: https://github.com/jamescherti/batchfetch/tree/main
[batchfetch-source]: https://github.com/jamescherti/batchfetch/blob/main/batchfetch/batchfetch_git.py
[batchfetch-pypi]: https://pypi.org/project/batchfetch/
[optorun-role]: https://github.com/optorun/ansible_git
[optorun-role-tasks]: https://github.com/optorun/ansible_git/blob/main/tasks/clone_update_git_repos.yml
[optorun-role-meta]: https://github.com/optorun/ansible_git/blob/main/meta/main.yml
[optorun-role-metadata]: https://api.github.com/repos/optorun/ansible_git
[galaxy-role-ansible-git]: https://galaxy.ansible.com/api/v1/roles/?name=ansible_git&format=json
[myrepos-home]: https://myrepos.branchable.com/
[myrepos-news]: https://myrepos.branchable.com/news/
[ghq-readme]: https://github.com/x-motemen/ghq/blob/master/README.adoc
[repoman-api]: https://api.github.com/repos/klokie/repoman
[repoman-contributors]: https://api.github.com/repos/klokie/repoman/contributors?per_page=10
[repoman-releases]: https://api.github.com/repos/klokie/repoman/releases?per_page=5
