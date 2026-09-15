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
  how soon. An item here is deleted when finished; a roadmap item is not.
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
- When you claim an item, say so in the line. When you finish it, delete the line
  — the commit is the record.
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


- 2026-08-27T18:20Z — adding the pre-egress review gate (as in bin/trace-public) — bin/executable_pii-redactor
- 2026-09-10T21:25Z — adding a chrome browser topic (separate session, reported by the author) — dotfiles/apps/chrome, install/remove tasks

A stale claim is not a lock. If a line looks abandoned, check `git log -3` on the
file and whether a process is still running before assuming it is safe — then
delete the line and say so in your commit.

## Where things stand — 2026-09-14 (the session handoff)

A handoff snapshot. Delete and rewrite it rather than appending; a log of
snapshots is worse than none.

**Nothing is mid-flight; the working tree is clean.** The two machines' work
met here: this session's commits (cosine fix, queue updates, the skillet pin
resolution) merged with the other machine's 43, conflict confined to TASKS.md
as predicted, and **pushed** — nothing lives on one machine only. What *is*
outstanding is applying: `chezmoi status` shows **51 drifted entries** — the
whole `apps/claude-code` topic, the opencode changes, `managers.yaml`,
`ROADMAP-topic-cli.md`, the docs trio, `tools/` (skill-trust), and tonight's
cosine fix among them. Nothing live is broken, but `~/dotfiles` is behind the
source on both machines' work until the author applies. Review list before a
full apply is down to one file: `.zshrc` (see the git-ai task in § Planned).

**The suite's one failure was fixed tonight — the skepticism was right to
raise, and the answer went the other way.** `test_cosine_is_bounded` failed on
a hypothesis counterexample and sat untracked for three days on the theory
that the property might be over-strict. It is not: cosine similarity does
guarantee the bound in real arithmetic, and floating point honours it except
when a norm's square is subnormal — then sqrt stops round-tripping and the
quotient escapes Cauchy-Schwarz (`cosine([1.0], [1.2794807103967847e-160])`
returned 1.000070683603874). Fixed in 6c3079b: return 0.0 when either norm's
square is below `sys.float_info.min`, counterexample pinned as its own test
beside the property, mutation recorded (reverting the guard fails exactly that
test and nothing else).

The full suite **was** re-run tonight with the full dependency set: 454
passed, 12 failed, 13 skipped. The 12 are environmental, not regressions: 10
in `tests/clipped` (clipboard/TTY in a headless context) and 2 in
`tests/pii_redactor` llm. Do not read green past them; do not chase them from
a TTY-less shell either. Without `--with pillow` you still get 28 collection
errors that look like breakage and are not.

**Landed today, and where the reasoning lives:**

| What | Where |
|---|---|
| opencode installed at last; Homebrew 7 needs a tap trusted *before* tapping | `apps/opencode/CHANGELOG.md` |
| opencode's permission paths were hardcoded to another machine's home | `dot_config/opencode/opencode.jsonc.tmpl` |
| `apps/claude-code` — both casks, plus clearing a mise shim that shadowed brew | `apps/claude-code/` |
| Machine-specific values get resolved, never written out | `AGENTS.md` § Machine-specific values |
| Every topic carries its own changelog, antsibull categories | `docs/TOPICS.md` § Per-topic changelog |
| Presence and currency are different guarantees | `docs/TOPICS.md` § Presence vs currency |
| Queueing a task is its own commit | `TASKS.md` § Conventions, `AGENTS.md` § Commits |
| A1 answered; the CLI is now `topical` and agent-first | `dotfiles/docs/ROADMAP-topic-cli.md` |
| What each dependency manager requires of a topic | `dotfiles/managers.yaml` |
| Cosine returns 0.0 when a norm's square is subnormal — the 3-day failure, fixed and mutation-proven | `apps/ollama/files/executable_ollama-evals`, `tests/ollama_evals/test_harness_property.py` (6c3079b) |

**Where the `topical` work stopped, and what is next.** A1 is answered and
deleted. The design is amended: one CLI with deterministic and agent verbs,
written in **Typer** so `pycli-mcp` can derive the MCP tool list by reflection
rather than anyone maintaining two surfaces. A8 is delivered as
`dotfiles/managers.yaml`. **A9 is the next piece of work** — a generator that
reads that data and emits only the blocks a topic needs. Its first target is
recorded: `template_dir/` scaffolds a `snap` block that zero topics use, which
is most of 37 commented-out module lines now sitting in topics that never
wanted them.

**Standing hazards:**

- **Agents are still denied `chezmoi apply`,** and the rule fired again today as
  designed. The author applied by hand. The rule stands on its own merits — one
  deployed tree that cannot be branched.
- **Resolved 2026-09-14, and the mechanism is the lesson.** `~/docs/CONTRIBUTING.md`
  was never "still being deployed" — root `CONTRIBUTING.md` was already in
  `.chezmoiignore:24`. It was an **orphan**: adding a file to `.chezmoiignore`
  stops chezmoi managing it but does **not** remove the copy already deployed,
  so it sat unmanaged and drifted to 364 diff lines while looking like a
  deployment problem. It self-declared "This file is superseded" at the top.
  Trashed (recoverable), not `rm`-ed. **Expect this class again** — every future
  `.chezmoiignore` addition leaves whatever it already deployed behind.
- Every new top-level file is chezmoi-managed by default. `dotfiles/managers.yaml`
  was placed beside `playbook.yaml` deliberately and **not** inside
  `template_dir/`, because `init-config.sh` copies that directory verbatim and
  it would have landed in every generated topic.
- **Two casks now self-update** (`Claude.app`, and superwhisper/openwhispr when
  those land), so brew's recorded version drifts from what is installed. Each
  topic's `known_issues` records it; no central list exists and probably should
  not.

**Resolved today:** the Debian box is **x86_64/amd64** (author, 2026-09-14), so
OpenWhispr's Linux builds apply and the `.deb` path stands. The habit that came
out of it is recorded in the task — check a release's architecture list before
choosing a package format rather than assuming parity with macOS.

## Picking this back up

Say any of these and the thread resumes where it stopped:

| Say this | Resumes |
|---|---|
| **"apply"** | The unapplied chezmoi source — 51 drifted entries from both machines; applying stays author-only |
| **"topical"** or **"A9"** | The next build step: the manager-aware generator reading `managers.yaml` |
| **"the template work"** | Same as A9 — that is what it refers to now |
| **"voice typing"** / **"openwhispr"** | The voice topics; architecture is settled, `.deb` via `ansible.builtin.apt` |
| **"claude-code topic"** | Extending it to Debian via the signed apt repo |
| **"the sunset plan"** / **"A10"** | Retiring the six `~/bin` names, blocked on the dispatcher working |
| **"ansible user"** | The privileged-update service, scope the sudoers grant first |

The design decisions behind all of it are in `dotfiles/docs/ROADMAP-topic-cli.md`
§ Amendment — read that before writing any `topical` code, since several of them
reversed earlier positions on purpose.

## Now

The handful actually next. Keep this short — if everything is Now,
nothing is.

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
  (`~/code/personal/` beside ai-prompt-library and impromptu is the
  precedent). This repo's recently-queued research (sandboxing, session
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
- **Diagnose the 12 environmental suite failures, then make each pass or skip
  with a named reason.** From the 2026-09-14 full run: 10 in `tests/clipped`
  (clipboard/TTY — a headless shell cannot paste), 2 in
  `tests/pii_redactor` llm (cause undiagnosed; the conftest mocks a working
  model, so the failure is not obviously model-absence). Diagnose first and
  do not blanket-skip: each test either gets an environment skip naming the
  missing capability (same doctrine as the conftest-skip task, one level up:
  the missing thing is a pty or a clipboard service, not an import) or a fix,
  if the environment is actually fine and the test is wrong. Done when a
  full-suite run in a headless shell reports zero failed with skips named,
  and a capable run still exercises what was skipped. [me]
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
  that converges and passes `molecule test`'s idempotence step, the per-driver
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
  backfill rather than pausing to write 27 suites up front. Done when a
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
  and unversioned, so it cannot be tracked here beyond this pointer. Until it is
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
  and the spec/REFERENCES rows agree with it.
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
  `tests/tasks_doc` with the resolved-tasks stopgap retired. [me]
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
  panel-of-judges item below — settle that first or borrow its method. Done
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
  relying on it. The research learns the process and approaches first; the
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
- **Create a `git` topic that owns git config and extensions; git-ai is its
  first extension.** Git config is not managed at all today — no
  `dot_gitconfig` in the source, no `apps/git` topic — and the git-ai
  installer's edits are hand-placed: a `~/.gitconfig` written 2026-09-13
  (plain file, unmanaged), the `~/.git-ai/bin` PATH export appended to
  `~/.zshrc` (the one two-way-drifted file), plus any hooks or bin entries it
  installed. Audit everything the installer touched first, then build
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
  map is the precedent), never one flat list for the fleet. Done when
  existing-config detection is written, the per-machine inventory is
  recorded, and a decision — with the author — fixes the topic's shape:
  declared repo sets versus gita's group semantics, install via
  `topic_requires`, and where the config lives; queued as the
  topic-creation task it feeds. [me]
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
- Document that `git add -p` and `git commit -o` do not compose, in AGENTS.md
  § Working alongside other sessions. It currently recommends both, but `--only`
  commits the **working-tree** content of the named paths and discards partial
  staging — so `git add -p TASKS.md && git commit -o TASKS.md` quietly commits the
  other session's hunks too. For a co-edited file it has to be `git add -p`, then
  a bare `git commit` with nothing else staged, verified immediately with
  `git show --stat HEAD`.
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
  intersect without contradicting. Note this repo deliberately has no
  `CHANGELOG.md` — `git log` is the changelog — so this governs release notes and
  any user-facing summary, not a file we keep.
  **[open question: "the 2.0 changelog standard" needs pinning down. Keep a
  Changelog is at 1.1.0 and has no 2.0; `ai-prompt-library/CHANGELOG.md` cites
  1.0.0. Common Changelog is the other candidate. Confirm which before writing
  the rule.]**
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
  all verified in `docs/ROADMAP-topic-cli.md` § Migration inventory:
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
- A8. **Record what each dependency manager requires of a topic, as data the CLI
  can read.** Blocks A2 and A4: a scaffold cannot generate a valid topic, and
  `topical <name> add <package>` cannot edit one, without knowing what the chosen
  manager needs. Today that knowledge exists only as a pattern to be copied
  correctly from a neighbouring topic, and copying the wrong neighbour fails —
  `apps/claude-code` was scaffolded from `apps/opencode`, which installs no cask
  and so carries no `vars:` block, and the cask install died on
  `'user_appdir' is undefined` (fixed in `c988fef`). Four axes the data has to
  cover, each observed rather than imagined:
  - **Variables the topic must define.** Every cask-installing topic playbook
    repeats the same two lines — `homebrew_prefix` and `user_appdir` — in ten
    places, with the parent playbook holding an eleventh copy. Nothing declares
    that a cask *requires* them.
  - **Privilege.** brew must not run under `become`; apt must. A scaffold that
    guesses wrong fails at run time, not at generation time.
  - **Currency.** `brew upgrade` reaches formulae and casks, so those topics
    need no upgrade tasks; anything installed by mise, npm, cargo, ubi or a
    release tarball is reached by neither system role and must own its upgrade,
    as `apps/ori` and `apps/ollama` do. Nothing checks that a topic in the
    second group actually has one — see `docs/TOPICS.md` § "Presence vs
    currency".
  - **Channel and version selection.** The same idea has a different shape per
    manager: a brew channel is a *cask name* (`claude-code` vs
    `claude-code@latest`), while the apt equivalent changes both the URL path
    and the suite name. `claude_code_cask` has no Debian counterpart to reuse.
  Also needed: somewhere for per-manager exceptions to live. `homebrew_upgrade_cask_exclude`
  exists with a documented reason for `rancher` and has no counterpart for any
  other manager, so the next such exception will be invented somewhere new.
  Done when `topical new` generates a topic whose playbook, privilege and upgrade
  path are correct for its manager without the author consulting a neighbour,
  and when adding a package to a topic knows which manager it belongs to.
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
  documenting it.
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
machine→groups map is `machines.yml` kept as **plain data** (hostname →
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
  **The llocallabs cluster and its timing dependencies (recorded 2026-09-14).**
  Five queued items cite each other and must be classified together, in
  this order: (1) the anchor repo must exist before the manifest can classify
  anything *to* llocallabs — a manifest naming a nonexistent home is a guess;
  (2) the three research projects queued in § Now and § Planned (sandboxing,
  session-management handoff, RAG/graphs) are first-class llocallabs
  candidates — if the anchor exists before they start, start them there; if
  any starts here first, its outputs are manifest candidates, not resident
  work; (3) gita's per-machine inventory (§ Planned) must include the
  collection once it exists — its repos are exactly the share-across-machines
  set gita is meant to manage; (4) the strategy/policy agent consumes the
  research projects, so it cannot be stood up ahead of them; (5) B1's
  install-method answer still gates this manifest's "stays and installs
  back" column. Until the manifest lands, nothing in the cluster moves, and
  no item in it should be worked on the assumption it stays here forever.
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
- Resolve the three CONTRIBUTING.md files. `CONTRIBUTING.md` is the
  real one and `AGENTS.md` cites it. `CONTRIBUTING.md` is a stale copy in the
  older repo-root `docs/` tree, differing by 171 lines, which GitHub would surface
  if `CONTRIBUTING.md` did not now take precedence. Decide whether the
  whole repo-root `docs/` tree goes rather than patching one file — `AGENTS.md`
  already calls it an older copy kept but not maintained.

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
