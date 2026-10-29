# Interchangeable components for agent work

**Decision report · checked 2026-09-24 · local, uncommitted**

Researcher: `general/sandbox-components`, OpenCode, `openrouter/openai/gpt-6-astra`.
Brief: independently replace task storage, orchestration, workspace allocation,
sandbox enforcement, and environment setup on macOS and Debian, using native
or container-backed execution. A tool
that requires ownership of an adjacent layer must justify that coupling.
Inputs: the approved brief, targeted local instructions/code/research, upstream
source and documentation, practitioner issues, and disposable synthetic probes.

## Recommendation

**Keep a command-and-directory boundary, with one explicit owner per layer.**
Use Backlog.md for the first human-reviewed queue pilot, the existing coordinator
for dispatch, Worktrunk for convenient workspace allocation, and mise for tools
and setup. Keep herdr optional as the persistent terminal/session interface.
Pass the selected directory to a separately selected sandbox command. No new
adapter framework or scheduler is needed to test this composition.

**Author clarification, 2026-09-24: non-root containers are first-class options
when they take very little configuration to apply.** This includes Sandcastle's
approach. The initial comparison weighted native execution too heavily. Select
the runtime by workload fit, setup effort and replaceability; require native
macOS execution only for tasks that need it. Container startup has not yet been
measured here, so the evidence does not establish a setup-effort winner.

**Consider Anthropic Sandbox Runtime (SRT) for selective-network native execution.**
It accepts an existing directory and arbitrary command without owning Git,
task storage, or the terminal. Its macOS enforcement passed the synthetic
allow/deny probes below. However, package 0.0.77 reports a SIGTERM-killed command
as exit 0. It is therefore **not ready for unattended exit-driven task closure**.
Require an upstream correction and repeat the lifecycle test before that use.

The incumbent has an important additional option: **mise 2026.9.12 already
contains optional Seatbelt/Landlock sandboxing**. Use it as the first low-cost
candidate for trusted-configuration, offline builds/tests. Bare `mise exec`
does not enable those controls. Its network allow-host option failed on this
Mac and is explicitly unsupported on Linux. It does not replace SRT for the
selective-network requirement, and it leaves Unix sockets available.

For concurrent autonomous claiming, **Beads is the stronger queue candidate**:
current source provides atomic claims, heartbeat leases, recovery, dependencies,
JSON and API surfaces. Its Dolt storage is a larger operational commitment.
Start with one authoritative store, not independently writable replicas whose
claims merely synchronize later. Backlog assignment and GitHub assignees do
not establish the same lease semantics.

Rank by these integration requirements: externally supplied workspace;
arbitrary command; explicit failure instead of capability downgrade; retained
artifacts after interruption; human-controlled integration; support for the
required workloads on both hosts. Native versus container-backed execution is
a capability distinction. Cross-platform labels do not establish equivalent
policies. Low configuration is an explicit selection criterion: account for
host prerequisites, per-project files/settings/commands, reusable images or
templates, credential wiring, and maintenance after the first successful run.

## Local prior art and constraints

Local evidence keys resolve to exact paths, revisions, and lines in Appendix A.

* **Machine management [L1].** The queued coordination design specifies frozen
  path leases, one writer per workspace, semaphores for global resources, and
  merged-tree integration checks. These are requirements/planned work, not a
  verified installed scheduler. The provisioning repository may install and
  invoke tools; their runtime logic and state belong elsewhere.
* **Workspace readiness [L2].** The existing mise task creates a worktree and
  generates/checks its local guard. The generator resolves canonical inputs
  through `git-common-dir`. The September 24 Worktrunk trial proves setup-hook
  sequencing, a failed-creation resume gap, shared HOME, and a loopback port
  collision. It does not prove process confinement. The environment-fixture
  backlog remains separate.
* **herdr [L3].** The implemented topic installs `herdrdev/herdr` through mise,
  manages a native per-user service on each target, and wires agent lifecycle
  integrations. Tests describe installation/removal and catalogue contracts.
  Installed version is 0.9.1. This is session infrastructure, not a task store.
  No service, live pane, or session record was inspected or changed here.
* **Prompt/research library [L4].** A post-hoc research-isolation checker exists;
  preventing a web-only analyst from accessing local material remains queued.
  Its history specification separates reusable prompts from session artifacts.
  Wrapping the analyst's entire process addresses a different boundary from
  merely assigning a different cwd or forbidding reads in its brief.
  Source caveat: the checked-in checker's file-input branch references `Path`
  without importing it (`isolation_check.py:27–31,88`). Its presence is not
  proof of a working file-input gate; that branch was not executed here.
* **Collection anchor [L5].** The local `llocallabs` README describes task
  directories, Worktrunk hooks, and a guard. This checkout has no commits;
  only README/PRD are untracked, `tasks/` is empty, and the named hook/guard
  files are absent. Treat that architecture as a scaffold proposal. Its nested
  worktree naming also differs from the dotfiles flat-path convention.
* **Prompt product [L6].** Standalone `impromptu` is README-only here. The
  nested library subproject contains seed/bootstrap material and a provisional
  project/workspace/state design. Neither establishes an implemented generic
  queue or sandbox dispatcher.
* **Other work repositories [L7].** The extraction-workbench design calls for
  source-separated sessions and a non-model orchestrator transporting opaque
  artifacts; its enforcement items remain unchecked. The named utilities
  directory contains HAR tools, with no relevant orchestration surface found
  in the inspected top-level material. These are requirements/reference work,
  not reasons to introduce another task database.

Two local assumptions need explicit revision in the owning research task.
The September 20 Linux measurements cannot be attributed to this Mac. Also,
“nothing supports per-agent path subsets” is false at the runtime layer:
SRT successfully confined writes to one subtree inside the same workspace.
That does **not** make multiple writers sharing an index or test tree safe.
Nor does a commit-time path gate protect untracked files or the deployed tree.

## Layer ownership

| Layer | Owns | Suitable replaceable surface | Coupling to avoid |
|---|---|---|---|
| Task source | Identity, specification, dependencies, accepted status | Backlog CLI/JSON/MCP; Beads CLI/API; `gh`; Markdown | A pane ID or branch name becoming the task's identity |
| Dispatch/orchestration | Claim, launch attempt, concurrency, retries, verification | Existing coordinator invoking commands; optional Sandcastle library | Treating agent “done” or process exit as acceptance |
| Session/UI | Terminal, input/output, native session reference | herdr socket JSON/CLI; terminal multiplexer | Restore bypassing the selected sandbox |
| Workspace | Path, base revision, ownership, retention | Worktrunk; workmux headless; Git; independent clone | Two tools both merging or removing the checkout |
| Sandbox | Enforced read/write/network/IPC bounds | SRT CLI; nono CLI; explicit container/VM invocation | Silent fallback, writable policy, host-control sockets |
| Environment | Tool versions, setup, cwd-scoped environment | mise tasks and `mise exec` | Calling environment selection process isolation |
| Integration | Review, protected refs, merged-tree checks | Existing human/Git/PR workflow | Sandbox cleanup automatically merging work |

### Task and orchestration choices

All source-only claims below are unrun locally unless marked otherwise.
Repository metadata records September activity for Backlog, Beads, Taskwarrior,
workmux and herdr; Sandcastle's latest push was June 29. Workmux and Sandcastle
are MIT-licensed; herdr is Apache-2.0. All three support macOS/Linux hosts,
with Sandcastle's actual execution platform determined by its provider.

| Component and pin | Surfaces and state | Claim, dependencies, resume/provenance | Fit |
|---|---|---|---|
| **Backlog.md 1.53.0**, `c310b708` [U1] | Markdown files; CLI; versioned JSON reads; JSON watch; MCP; local web API; macOS/Linux; MIT | IDs, assignees, status, readiness/dependency graph, notes/final summary, Git history. Source tests serialize concurrent edits and report contention. No worker lease/claim-if-unassigned contract found in reviewed CLI/MCP docs | Best human-readable queue pilot. Pin one authoritative backlog location; copied branch files are not shared claims |
| **Beads**, `c507f3b4` [U2] | `bd ready/show/update/close --json`; library/HTTP; Dolt embedded or server; macOS/Linux; MIT | Atomic `update --claim`; heartbeat/reclaim; task graph and audit. Leases are node-local; actor is caller-asserted provenance, not authentication | Best concurrent-claim candidate. Current upstream is `gastownhall/beads`, redirected from `steveyegge/beads`; JSONL is interchange, not authoritative storage |
| **GitHub Issues**, REST `2026-03-10`, local `gh 2.101.0` [U3] | REST/GraphQL, webhooks, `gh issue view --json`, edit/comment/close; hosted store | Repository-qualified issue ID/URL; dependencies/sub-issues; comments/events. Assignment is not an exclusive lease. A webhook is notification, not ownership | Best representative API-backed substitution. Coordinator owns dispatch and credentials; store pointers to local artifacts, not private payloads |
| **Taskwarrior**, `e47c664b` [U4] | Local store, JSON export/import, UUID, hooks, synchronization; macOS/Linux; MIT | `start/stop/done`, dependencies, annotations. No exclusive worker lease established by reviewed interface | Good personal/offline task store; use UUID, not display index. Less suited to autonomous multi-worker claims |
| **Repository Markdown** [L1,L4] | Files, explicit item IDs/anchors, Git and handoffs | Human ownership and history; no transactional claim or automatic dependency enforcement | Valid zero-migration source for one dispatcher; avoid parsing prose into an invented scheduler |
| **workmux 0.1.266**, `267bfc44` [U5] | Worktrees, multiplexer panes, prompts/stdin JSON lines, bounded batches, hooks, optional Docker/Podman/Apple Container/Lima | Agent status and window lifetime, `open/close/resurrect`; not a durable queue or claim service. `merge` integrates and removes resources | Strong bundled workflow alternative. `add --headless --json` genuinely separates allocation from terminal ownership; tested in upstream source, not here |
| **herdr 0.9.1**, installed [U6,L3] | Existing `--cwd`, shell panes, `pane run`, agent prompt/wait, JSON socket API, session restore | Stable runtime/session references; lifecycle state. Metadata TTL/sequence numbers are display freshness, not task leases; `agent wait` is not per-turn verification | Keep optional. Use `workspace create --cwd` for borrowed directories; `workspace close` differs from `worktree remove` |
| **Sandcastle 0.12.0**, `e99f832f` [U7] | TypeScript agent/sandbox providers, prompts, hooks, abort signals, streaming, result commits, session capture; requires Git | No mandatory task store; GitHub/Beads scaffolds. Resume depends on agent provider; OpenCode provider lacks session capture/resume | Useful if programmatic multi-step orchestration earns its cost; not the default composition layer |

Backlog's `--watch` produces successive complete JSON documents, not one event
per edit or newline-delimited records. Its edit lock protects a mutation, not
an hours-long worker claim. Beads supplies that latter concept, but its leases
do not create a distributed mutex across disconnected replicas. These
differences must remain visible when replacing the queue.

## Sandbox and workspace comparison

“Recent push” below means GitHub repository metadata, not a maintenance or
security guarantee. Exact source links and full key hashes are in Appendix B.

| Runtime | macOS / Debian backend | Existing cwd + arbitrary command | Policy and lifecycle limits | Licence; recent push; verdict |
|---|---|---|---|---|
| **SRT 0.0.77** [U8] | Seatbelt / bubblewrap, proxy, optional seccomp | Yes: `srt --settings FILE -- COMMAND ARGS`; library also available | Reads allowed by default; explicit denies/re-allows; write allowlist; domain proxy. Linux write-glob limits; missing seccomp warns and leaves Unix sockets unrestricted. Signal-exit defect reproduced | Apache-2.0; Sep 23; preferred selective-network pilot |
| **mise 2026.9.12** [U9] | Seatbelt / Landlock + seccomp | Yes: `exec/run` sandbox flags | Preparation/config evaluation runs outside child sandbox; system/tool/temp exceptions; Unix sockets remain. Per-host net rejected on Linux and failed here on Mac | MIT; installed release; first offline/trusted-setup candidate |
| **nono**, `775e5154` [U10] | Seatbelt via `sandbox_init()` / Landlock + seccomp | Yes: `nono run … -- COMMAND`; profiles and bindings | Fine-grained capabilities, dry-run/why, credential proxy and controlled child-tool policies. Kernel/IPC differences; Linux pathname-socket mediation opt-in. Source supports network fallback/refusal beyond stale docs | Apache-2.0; Sep 24; strongest second native pilot, unrun |
| **Agent Safehouse**, `e376993e` [U11] | Seatbelt / none | Yes | Deny-first composable profiles. Auto-worktree handling adds shared Git metadata and sibling reads; review those grants | Apache-2.0; Sep 22; macOS-specific alternative, not fleet answer |
| **cco**, `26927b88` [U12] | Seatbelt / bubblewrap; Docker selector | Yes: `--command`; externally owned checkout | Native reads broad by default; full network deliberately allowed; agent state and shared Git exceptions; explicit backend selection available | MIT; Sep 12; convenient launcher, fails selective-egress requirement |
| **opencodebox**, `1e49b58a` [U13] | None / bubblewrap | Existing project yes; command is OpenCode | Extra binds, namespace isolation, mise mounts; shares OpenCode state/SSH agent; optional seccomp warns when missing; no verified egress allowlist | MIT; Sep 17; Debian/OpenCode-specific, not interchangeable runner |
| **Treebeard**, `7f7018d2` [U14] | macOS 15+, macFUSE + Seatbelt / no verified Debian backend | Arbitrary child yes; owns ephemeral worktree/overlay | Auto-commit/cleanup, ignored-file overlay, hook failures warn and continue. Network allowed by default | MIT in LICENSE despite API `NOASSERTION`; Jan 6; reject for layer coupling and platform gap |
| **nixcage**, `33d07de9` [U15] | Shared Linux VM / systemd-nspawn or microVM | Yes, project directory and command | Current project is Nix/container/VM infrastructure, not the older bwrap/Seatbelt description; owns persistent homes and host setup | GPL-3.0; Sep 24; defer unless Nix environment is separately chosen |
| **sandnix**, `0a05a4fb` [U16] | Seatbelt / landrun (Landlock) | Wraps a declared program; dynamic sandbox args Linux-only | Nix flake-parts packaging and policy; not bubblewrap | GPL-3.0; Apr 30; defer rather than replace mise |
| **Docker/Podman or Lima** [U17] | Linux VM on Mac / containers or VM on Linux | Yes: mounts/workdir/argv; Lima `shell --workdir` | Independent HOME, service/network namespaces; a Linux guest cannot run native Mac provisioning. Egress and host mounts still need policy | Docker engine/Podman/Lima open-source components; Lima Apache-2.0, Sep 22; fallback for concrete runtime needs |
| **Coasts**, `a62f5121` [U18] | Container runtime, VM-backed on Mac | `coast exec`; assignment to worktrees | Service/port/database lifecycle. Local prior research identifies privileged Docker-in-Docker; do not call that an adversarial sandbox | MIT; Apr 28; defer until parallel service stacks exist |

### SRT is not Claude Code's Bash sandbox

SRT can wrap the **whole OpenCode process**, including its direct file tools and
descendants. Claude's built-in sandbox instead surrounds selected command
tools; in-process tools follow Claude's permission system. Current Claude docs
also describe unsandboxed retries and warning-only unavailable-backend defaults,
with `allowUnsandboxedCommands` and `failIfUnavailable` controls. Those
integration choices must not be attributed to standalone SRT [U8].

SRT requires Node 20.11+; its standalone Linux backend needs bubblewrap and
socat, with ripgrep documented for path discovery. macOS uses the built-in
`sandbox-exec`. Backend availability and required seccomp capabilities must be
checked separately: a successful launch with a warning is insufficient when
Unix-socket denial is part of the requested policy.

Neither native wrapper reserves ports or isolates every host service. A
network domain allowlist also cannot distinguish a permitted API operation
from a destructive operation at the same destination. Keep protected-ref and
integration controls. Avoid host-control sockets as “tool compatibility” grants.
SRT's macOS local-binding and Apple Events escape-enabling options require
separate decisions; the probes used neither.

Nono merits a second test because its delegated-tool policies and credential
proxy may fit frozen scopes better. However, its own Seatbelt internals page
still says network filtering is binary, while current README/source describe
proxy policies. Linux source also implements seccomp fallback where an older
doc says “warn.” Pin and test actual builds; do not compose from those stale
sentences. Debian's actual kernel/ABI must be checked locally before selection.

### Sandcastle's useful boundaries and costs

The pinned package exports Docker, Podman, Vercel, Daytona, and `noSandbox`
providers. There is **no shipped native bwrap/Seatbelt provider**. Adding one
through `createBindMountSandboxProvider` is custom code with streaming, execution,
transfer, and cleanup obligations, not an existing integration [U7].

The author's container acceptance removes the need to build a native provider
to consider Sandcastle. Evaluate its shipped non-root container path directly.
The next walkthrough should establish what `init` supplies, what the user must
still configure, and what can be reused across projects. Include runtime/image
setup, agent authentication, external queue intake and a borrowed workspace.
Record the container's actual execution identity and lifecycle behavior during
that trial. A scaffold command alone does not establish low ongoing effort.

Externally allocated work is still possible: top-level `run` accepts `cwd`,
and the `head` strategy uses that directory directly. Supply a separately
owned clone/worktree there. `createWorktree()` creates/manages a Sandcastle
worktree; its reusable handle is not evidence of a public import-any-path API.

Choose lifecycle explicitly. Bind-mount `run` defaults to `head`; isolated
providers default to `merge-to-head`. Worktree `interactive()` defaults to
`noSandbox()`. Clean managed worktrees can be removed on close; dirty ones
are normally preserved. A source path treats failure to inspect dirtiness as
false, then attempts removal with errors swallowed. Retention therefore needs
its own trial. Use borrowed `cwd` plus explicit strategy, or assign Sandcastle
sole workspace ownership. Do not combine automatic merging with human gates.

### Workspace alternatives

| Provider | Boundary obtained | Setup/ownership consequence |
|---|---|---|
| Worktrunk 0.79.0 | Git-linked checkout/index; hooks and navigation | Retain mise setup; validate every launch, including existing paths. `hash_port` is not a reservation; tether is cleanup |
| workmux headless | Git-linked checkout plus JSON provisioning receipt | No multiplexer required. Upstream tests assert rollback of failed provisioning; replacement pilot could beat Worktrunk on automation receipts |
| Raw Git 2.55.0 | Same Git-linked checkout without convenience layer | Explicit `worktree add/list --porcelain/remove`; setup and resume validation stay separate. `worktree lock` prevents pruning/removal, not concurrent writing |
| **Independent clone** | Independent refs, objects, index, config and hooks | More storage/setup; avoid `--shared` alternates and use `--no-hardlinks` for local independence. Queue identity stays external |
| Existing non-Git directory | No allocation or Git requirement | Caller owns retention; SRT/nono/mise accept cwd. Backlog `--no-git`, Taskwarrior, Beads explicit store, or API queue can serve it |

The clone substitution exposes a real local dependency: `git-common-dir` in a
clone points to that clone. It cannot discover another checkout's private guard
inputs. A trusted preparation step must provide the required derived guard or
an explicit approved input source. This is a setup contract gap, not grounds
to copy all ignored data. Also, read-only shared `.git` and autonomous commits
are conflicting requirements: choose coordinator-owned commits or isolated
clone metadata before promising both.

## Minimal handoff contracts

These are facts to record in existing task briefs and launch/results artifacts,
not a proposed new protocol implementation.

1. **Task and claim:** source-qualified ID/URL, specification revision, acceptance
   criteria, dependencies, owner, claim authority and release rule. Record whether
   ownership is serialized human dispatch or a native lease. A replacement with
   weaker claim semantics blocks autonomous dispatch.
2. **Workspace:** canonical path, provider, base commit if applicable, created
   versus borrowed, one writer, cleanup owner. Resolve shared Git metadata
   separately. Neither sandbox shutdown nor terminal closure authorizes deletion.
3. **Launch:** cwd, executable/argv, reviewed environment inputs, tool versions,
   task-brief path, setup/readiness result. Use argument boundaries rather than
   evaluating task text as shell. Environment setup must have a defined trust
   boundary; putting mise inside SRT also confines its preparation.
4. **Capabilities:** requested and effective paths/network/IPC, backend/version,
   frozen policy provenance/expiry, declared mismatches. Use existing runtime
   settings/flags. Missing enforcement is a failed launch, not a smaller success.
   Filesystem-policy changes require restart when the runtime cannot tighten live.
5. **Results:** launch-attempt identity, exit/signal/cancellation, artifact paths,
   base/result revisions, actual verification, review disposition. Task “done,”
   herdr idle, Sandcastle completion text, and exit 0 are distinct observations.
6. **Stop/resume:** stop only owned processes/resources; retain unfinished work;
   recheck claim, policy, setup and base on every resume. Do not replay a timed-out
   prompt blindly. Releasing a task lease is not proof its old worker has stopped.

herdr exposes a good removable UI boundary: `workspace create --cwd PATH`,
then `pane run` with the chosen launch command. Its typed `agent start --kind`
selects a canonical agent executable, not an arbitrary wrapper. Verify that
wrapped-agent detection and automatic native-session restore preserve sandbox
entry before enabling that combination. The server socket is a control surface;
do not expose broad pane-control authority merely to report task progress.

## Three substitution traces

**1. Backlog/file queue → GitHub Issues, unchanged runner.** A coordinator reads
`backlog task view TASK-42 --json` from the authoritative backlog, records the
claim, and passes a task brief plus cwd to the selected command runner. Replace
that intake with `gh issue view URL --json id,url,body,state,assignees,blockedBy`.
Keep the qualified source ID with the brief. The same workspace, mise setup,
sandbox command, and artifact check run. The coordinator reports through Backlog
notes/status or GitHub comments/state after review. **Interface-supported,
not exercised against task stores.** Native status values and lease capability
are not normalized away; use single-dispatch ownership for this pilot.

**2. SRT → another sandbox, unchanged task store.** The same synthetic cwd and
Python filesystem workload ran under SRT and then mise's explicit native
sandbox flags. Both allowed workspace I/O and denied sibling writes, secret
reads, and child writes. **This narrow substitution was exercised.** It fails
capability parity for selective networking: SRT allowed the synthetic endpoint;
mise's host exception failed. Source-supported container substitution is
`docker run --mount … --workdir … IMAGE COMMAND ARGS` with explicit environment,
or Lima `shell --workdir PATH INSTANCE COMMAND`. Keep intake/reporting on the
coordinator. Rebuild tool availability inside the guest; map artifact paths;
choose network-deny or a real egress proxy. No container/VM substitution ran.

**3. Worktrunk worktree → independent clone, unchanged queue semantics.** Keep
the same claimed task ID and brief. Replace allocation with an independent
`git clone`, record its absolute path/base, prepare it, and launch the same
cwd/argv interface. The queue remains in its authoritative location; Backlog
MCP can pin `BACKLOG_CWD`, and Beads can pin `BEADS_DIR`. Resume uses the same
task ID but a new attempt and workspace path. Cleanup belongs to the clone
owner. **Source-supported proposal, not a completed clone-swap test.** The
canonical-input setup gap above must be settled for the local guard workflow.

These traces establish practical replaceability, not hot-swapping every policy
with identical guarantees. No reviewed product provides all those semantics
automatically; small explicit invocations compose better than a new framework.

## Probe evidence and limits

Host: **macOS 26.6.2 (25G83), arm64**, Node **24.21.0**, Python **3.14.7**.
Scratch: `/Users/ben.davis/code/try/worktrunk-isolation-trial/sandbox-probes/`.
Files were authored with `apply_patch`. SRT was a pinned, disposable npm
dependency, installed with lifecycle scripts/audit/funding disabled, separate
cache and config. No agent, model, container, service, or remote task ran.

The package manifest/lock identify **0.0.77**, but its compiled CLI reports
**1.0.0**, hardcoded as a fallback in `dist/cli.js:147`. Upstream HEAD fixes
version reporting. Thus HEAD source and tested package are separate evidence.
The initial npm invocation also failed because one file cannot be both global
and user config; separate scratch config fixed that before installation.

| Probe | Observed result |
|---|---|
| Unsandboxed filesystem positive controls | Workspace read/write, sibling write, synthetic secret read, child write all succeeded |
| SRT same filesystem workload | Workspace read/write succeeded; sibling write and secret read raised EPERM; child sibling write exited 1 |
| SRT `allowWrite: ["./allowed"]` | Subtree write succeeded; a write at workspace root failed |
| Local HTTP positive control / SRT deny / SRT allow | Exit 0 with fixture body / HTTP 403, curl exit 22 / exit 0 with same body |
| SRT direct network, proxy bypassed | curl exit 7 while the local endpoint was live |
| Missing explicit settings / invalid settings | Exit 1, no launch-marker output; the identical marker command ran with valid settings |
| Missing shell dependency through scratch-only PATH | Exit 1, `Shell 'bash' not found in PATH`; system backend was not removed |
| Whitespace and shell-metacharacter arguments | Exact arguments preserved; no evaluation of synthetic metacharacters |
| Normal nonzero exit / self-SIGTERM under SRT | Exit 7 preserved / **exit 0: lifecycle failure**, matching upstream #602 |
| Normal proxy cleanup | Captured proxy port refused connection after process exit; valid later invocation succeeded |
| mise filesystem first attempt | Exit 71 before workload: allowed canonical interpreter tree did not admit its alternate symlink spelling |
| mise canonical-interpreter retry | Workspace read/write succeeded; sibling/secret/child cases denied, same as SRT |
| mise network control / deny / host exception | Fixture body, exit 0 / curl exit 7 / **profile compile error, exit 65** |
| Coordinator follow-up: mise `--allow-net localhost` | Also failed with exit 65; mise rendered the same numeric-IP profile rule |
| mise self-SIGTERM | Python subprocess return code `-15`, preserving signal death |

Commands: `python3 probe.py`, `python3 edge-probe.py`, and
`python3 mise-probe.py`, from the scratch directory. Mise probes used
`MISE_NO_CONFIG=1`, scratch HOME/data/cache/state/config paths, `--no-deps`,
and explicit interpreter grants. They did not evaluate the parent project's
setup. Positive-control files remain in the disposable sibling directory;
denials were observed operation results, not inferred from file absence.
The npm dependency/cache and synthetic outputs remain for reproduction.

These are benign functional probes, **not an escape audit**. No Debian runner
was used. Missing bwrap, unavailable Seatbelt, descendant-daemon teardown,
interactive restore, symlink attacks, real credentials, DNS/UDP policy,
resource limits, full application setup, queue contention, and complete
end-to-end substitutions remain unverified. Native filesystem immutability
does not establish process-tree cleanup. No speed claims were measured.

### Coordinator review

On 2026-09-24 the coordinator read the probe sources and reran `edge-probe.py`
and `mise-probe.py` on the same host and versions. The subtree restriction,
SRT signal-exit defect, proxy cleanup, and mise filesystem/network results
reproduced. A follow-up replaced the numeric `--allow-net` argument with
`localhost`; mise still rendered `127.0.0.1:*` and failed profile compilation.
That case is now in the retained probe script. The original filesystem/network
positive-control script was reviewed but not rerun by the coordinator.

The queue and workspace swap traces remain proposals supported by interfaces,
not demonstrated end-to-end interchangeability. Candidate rankings are research
recommendations; selection of a live task store or runtime awaits the author.

## Candidate combinations after the container clarification

1. **Human-reviewed modular pilot:** Backlog.md or existing Markdown + current
   coordinator + Worktrunk/raw Git/borrowed directory + mise + a selected runtime;
   optional herdr. This fixes the replaceable boundaries, not the runtime winner.
2. **Low-configuration container candidate:** Sandcastle's shipped non-root
   Docker/Podman path with an external task source and explicit workspace
   ownership. Compare its scaffolded setup with workmux's container workflow
   and a native wrapper. Setup effort and container lifecycle remain unmeasured.
3. **Native selective-network candidate:** the same modular upper layers + SRT.
   Gate unattended use on its lifecycle correctness and actual restore behavior.
4. **Offline verification:** same upper layers + mise's explicit sandbox flags.
   Cheapest measured addition when configuration is trusted and Unix-socket
   access is acceptable. It cannot meet the selective-egress contract.
5. **Autonomous claims:** Beads authoritative store + the same command runner;
   test nono as an alternative policy/credential layer. Earn the database and
   proxy complexity through a demonstrated concurrent workload.
6. **Bundled terminal workflow:** workmux + mise, with its container backend or
   an explicit native wrapper command. Headless provisioning is a credible
   Worktrunk challenger; full mode deliberately couples worktrees and UI.
7. **Service-heavy/stronger isolation:** independent clone + mise inside a
   restricted container or Lima guest. Select Coasts for service lifecycle only.

These are workload-specific candidates. Their final ordering awaits the
container setup comparison; containers are not restricted to service-heavy use.

The immediate material decisions are: **human-serialized or autonomous claims;
whether workers may commit; required network/IPC capabilities; and which layer
owns resume and retention.** Native macOS work rules out a Linux guest for
those particular tasks, not for all tasks. VM unsuitability is workload-specific,
not established by the old general statement.

Proposed follow-up sequence, requiring a later implementation decision:

1. Settle those four choices; record the allowed capability profile and one
   authoritative task store. Resolve the tooling home against [L1,L5]. Compare
   fresh-project configuration effort for Sandcastle's non-root containers,
   workmux's container workflow, and a native wrapper before choosing a runtime.
2. Run the same paired probes on authorized Debian hardware; add actual
   signal/descendant cleanup and policy-path cases. Recheck the SRT fix.
3. Exercise Backlog→API intake and Worktrunk→clone with a benign stub command,
   one task, explicit readiness, and retained failed state. Test workmux's
   headless receipt/rollback against the incumbent.
4. Test herdr wrapper detection/restore and claim expiry without launching
   real agent work. Then approve only the provisioning/configuration changes
   warranted by the winning combination.

## Appendix A: local evidence

Absolute paths are local-only references. Main was actively changing; line
numbers describe inspected working files, not a promise that all were clean.

| Key | Revision and exact inspected evidence |
|---|---|
| L1 | `/Users/ben.davis/.local/share/chezmoi`, HEAD `a4fbdbe3db729c4078dccefd55ca29a0af3e1931`; `PRD.md:66–100`, `spec.md:194–264`, `TASKS.md:172–198,333–443,1381–1469,2569–2628`. Assignment already recorded; source record left unchanged |
| L2 | `/Users/ben.davis/code/work/sentry/support`, HEAD `b384158339d0edc4ef09a9e2a036af2bf93f3d4d`; `mise.toml:13–25,103–125`; `scripts/gen-leak-rules.py:50–90`; `docs/research/worktree-runtime-isolation.md:97–185` (modified working file). Historical trial: Worktrunk 0.79.0, mise 2026.9.12, Git 2.55.0, synthetic clone at that commit |
| L3 | L1 `dotfiles/apps/herdr/README.md:3–7,25–79,113–145`; `defaults/main.yaml:10–35`; `tests/herdr/test_lifecycle_contract.py:1–46,67–79`. Tests inspected, not rerun. Maintained docs referenced by topic: `docs/TOPICS.md` and `TOPIC-RECIPES.md` |
| L4 | `/Users/ben.davis/code/personal/ai-prompt-library`, HEAD `c18d973c0f21c92b983b197db8cdb26c104decd3`; `AGENTS.md:13–24`; `TASKS.md:10–59`; `HISTORY-SPEC.md:5–26,28–41`; `skills/research/tools/isolation_check.py:1–24,56–75,78–116` |
| L5 | `/Users/ben.davis/code/personal/llocallabs/README.md:20–55`; `PRD.md:15–20,41–54`; `git status --short --branch`: no commits on main, README/PRD untracked. Directory inspection and direct reads confirmed absent advertised guard/hooks/instructions |
| L6 | `/Users/ben.davis/code/personal/impromptu`, HEAD `c34e86e675ec00db041fe8a7539af6c84622c8f0`, `README.md:3–20`; nested `/Users/ben.davis/code/personal/ai-prompt-library/impromptu/README.md:21–37,66–81` at L4 HEAD |
| L7 | `/Users/ben.davis/code/work/distill`, HEAD `a8343acf8481971e75bd1e3d91f2ea43a189fbac`; `AGENTS.md:24–37,49–74,130–150`; `TASKS.md:110–134`. `/Users/ben.davis/code/work/mytools/HARHAR/README.md:1–5`; no Git HEAD at inspected HARHAR directory |

## Appendix B: upstream evidence and pins

All checked 2026-09-24. Repository `pushed_at` and licence metadata were read
through `gh api`; versions came from manifests or installed `--version`.
Upstream tests were read as specifications, not claimed as locally passing.

* **U1:** [Backlog source](https://github.com/MrLesk/Backlog.md/tree/c310b7087c3d8d618520bfe4b9918e1c8bc468c4), especially `CLI-INSTRUCTIONS.md`, README MCP roots/`BACKLOG_CWD`, and `src/test/atomic-task-edit.test.ts`. The latter also tests a legacy lock-bypass environment option; do not enable it for concurrent access.
* **U2:** [Beads source](https://github.com/gastownhall/beads/tree/c507f3b4c9ceb0a7f9ef0577796f8267aec9b89d), README storage/git-free sections, `issueops/claimer.go`, `internal/storage/issueops/lease.go` (five-minute default TTL, node-local leases, heartbeat/reclaim and replica caveats).
* **U3:** [GitHub REST issues](https://docs.github.com/en/rest/issues/issues), API version `2026-03-10`; installed `gh issue view --help` and `gh issue edit --help` verify JSON, dependency and assignment surfaces. Only public research issues were fetched.
* **U4:** [Taskwarrior commands](https://taskwarrior.org/docs/commands/), [source pin](https://github.com/GothenburgBitFactory/taskwarrior/tree/e47c664bdfb406e893d17997cd1644fbd0b9a0f0).
* **U5:** [workmux source](https://github.com/raine/workmux/tree/267bfc44ffc15e60acf1bd4c4b8cad5b56a7a2ad), README headless/stdin sections, `tests/test_workmux_add/test_headless.py`, `docs/src/content/docs/guide/sandbox/index.mdx`. Container networking differs from Lima's unrestricted networking; host hooks/RPC are outside confinement.
* **U6:** [herdr CLI 0.9.1](https://herdr.dev/docs/cli-reference/), [socket API](https://herdr.dev/docs/socket-api/); upstream HEAD observed `8d95e9bd45338c43091e04ef0c976086bb09163a`. Installed help/version verified; live API not queried.
* **U7:** [Sandcastle source](https://github.com/mattpocock/sandcastle/tree/e99f832f26dc9d245c019a9ddd19fa5dee792427), `package.json` exports/version, `src/SandboxProvider.ts`, `src/createWorktree.ts`, `src/AgentProvider.ts`, README `run`/branch/lifecycle contracts. Custom-provider support is not a shipped native provider.
* **U8:** [SRT source](https://github.com/anthropics/sandbox-runtime/tree/ddbeb74711c4097014ef3056791efa83f553116c), `src/cli.ts`, README, `src/sandbox/linux-sandbox-utils.ts:1016–1085`; [Claude integration](https://code.claude.com/docs/en/sandboxing). Practitioner issues: [#602, false-success signal exit](https://github.com/anthropics/sandbox-runtime/issues/602) reproduced; [#157, argument quoting](https://github.com/anthropics/sandbox-runtime/issues/157) fixed and probe passed; [#596, path canonicalization](https://github.com/anthropics/sandbox-runtime/issues/596) not reproduced here, older reported version.
* **U9:** [mise sandbox guide](https://mise.jdx.dev/sandboxing.html), [exec](https://mise.jdx.dev/cli/exec.html), [release source](https://github.com/jdx/mise/tree/v2026.9.12), `src/sandbox/macos.rs` and `src/env.rs` (`MISE_NO_CONFIG`). Installed help confirmed sandbox flags.
* **U10:** [nono source](https://github.com/nolabs-ai/nono/tree/775e515477e100bb6fd04f5a187f08e1ba9bb9d3), README, `crates/nono/src/sandbox/linux.rs`, `crates/nono-cli/src/sandbox_prepare.rs`, `docs/cli/internals/{landlock,seatbelt}.mdx`. Source wins over noted doc drift. No nono runtime measurements.
* **U11–U16:** [Safehouse](https://github.com/eugene1g/agent-safehouse/tree/e376993ee8e15c4e4b3aa3a2ee282f15f6e3c680), [cco](https://github.com/nikvdp/cco/tree/26927b88f08429549ab41bc1cf37f320e6a36744), [opencodebox](https://github.com/fityannugroho/opencodebox/tree/1e49b58ae22f96f9b0bfc6d0554ac980beed92bc), [Treebeard](https://github.com/divmain/treebeard/tree/7f7018d28ed4892a1036aaad76bbf6807fe8236c), [nixcage](https://github.com/hamidr/nixcage/tree/33d07de99bfce1f81e29eeb5bcdb9e6eef58d19d), [sandnix](https://github.com/srid/sandnix/tree/0a05a4fbdf0fc98157a4efd6f4738fd1c2d995a8): pinned READMEs and repository metadata; Treebeard LICENSE read directly.
* **U17:** [Docker command/mount/workdir contract](https://docs.docker.com/reference/cli/docker/container/run/); [Lima shell](https://lima-vm.io/docs/reference/limactl_shell/), HEAD `928babab2139418b5733cf0ee39cd568ce8e065c`. [Lima practitioner account](https://bogoyavlensky.com/blog/sandboxing-ai-coding-agents-with-lima/) explains mounting and egress tradeoffs; its performance claims were not adopted.
* **U18:** [Coasts](https://coasts.dev/), [source](https://github.com/coast-guard/coasts/tree/a62f5121ab60ec0b418a0baac5aa0a17c728c045). Service isolation retained as a distinct concern.
* **Primitives:** [Git worktree 2.54 manual, unchanged for 2.55](https://git-scm.com/docs/git-worktree); [bubblewrap policy responsibility](https://github.com/containers/bubblewrap/blob/main/README.md); [Landlock kernel ABI/inheritance documentation](https://docs.kernel.org/userspace-api/landlock.html). New kernel features do not imply the selected runtime or Debian kernel uses them.

Tested SRT tarball integrity from the disposable lockfile:
`sha512-uOe6kkAbo91r5shXXBxZ1DKbOpWmnXkNDDujXrFJRaHSG7D7s8b7Yfsu0pGDkYFgKZ2ECtVCNisl6pCYcaMF7A==`.
The lockfile and compiled source remain under `sandbox-probes/runtime/`.
Report deployment exclusion was checked at this worktree's
`.chezmoiignore:16–20`; no live configuration was changed.
