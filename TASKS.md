# TASKS.md

Shared work queue for this repo. Agent sessions keep their own in-memory task
lists, which fragment the moment more than one is running — this file is the
durable version. Read it at the start of a session; update it before you finish.

Keep it short. This tracks *open* work and cross-session hazards, not history —
`git log` already has history, and duplicating it here just creates drift.

## Conventions

- One line per item, imperative, with enough context to pick it up cold.
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

## Open

- **FIRST.** Set responsible agent permission defaults. The committed
  `.claude/settings.json` has **88 allow rules, 0 deny, 0 ask** — an allow-list
  grown one prompt at a time until it no longer restricts much. Concretely, it
  already permits arbitrary code execution: `Bash(python3 -c ' *)` and
  `Bash(python3 -)` between them allow any Python at all, and `Bash(pip
  install *)` and `Bash(uv run *)` allow arbitrary packages and commands. It
  also permits `Bash(chezmoi apply *)`, which directly contradicts `AGENTS.md`
  § Applying is main-only, agreed today. `Bash(git add *)` and
  `Bash(git commit -m ' *)` allow staging and committing anything, which sits
  badly beside `spec.md` § Change records.
  Review best practices before designing this — do not invent a scheme. Then:
  - **deny is the half that matters and is currently empty.** It should cover
    the Class A incidents in `AGENTS.md` § Trust ladder, since those are the
    ones that do not reverse: egress of work content, and anything that writes
    outside the repo and its data stores.
  - **ask** is the right tier for irreversible-but-legitimate actions — pushing,
    history rewriting, applying, installing packages.
  - Prefer narrow allows that name a command's purpose over wildcards that name
    its prefix. `Bash(uv run *)` reads as "run the test suite" and means "run
    anything".
  - Settle what belongs in committed `settings.json` versus gitignored
    `settings.local.json`, which currently holds 25 more allow rules nobody
    reviews.
  Done when the allow-list is rebuilt from intent rather than pruned, deny and
  ask are populated, and no rule contradicts a convention in `AGENTS.md`.
  Note this is the permission layer, not the policy layer — `bin/policy` governs
  what may be done with data, this governs what the agent may run at all. They
  should not be conflated, and neither substitutes for the other.

- Add a cheap gate in front of the LLM judge panel: generate and run the script's
  tests, use real pass/fail as the signal, escalate to judges only when the result
  is inconclusive. Treat formatting/lint as fix-as-you-go, not gate criteria. The
  accept-vs-revise signal in git history is training data for it.
- Evaluate frontier cloud alternatives to OpenAI/Grok as judge and generation
  candidates — Qwen, DeepSeek, Moonshot Kimi, Z.ai GLM, MiniMax, Mistral,
  ByteDance Seed, Cohere are all on the existing OpenRouter account. Rank them
  with `model-bench`, not by assertion: several post-date any model's training
  cutoff, so relative quality is genuinely unknown until measured.
- Symlink the two new skills into `~/.claude/skills` on each machine that wants
  them: `ln -s ~/code/personal/ai-prompt-library/skills/<name> ~/.claude/skills/`.
  Per-machine because `~/.claude` is chezmoi-ignored. Skills are `pii-redaction`
  and `commit-hygiene`.
- File the upstream issue on `simonw/llm-pdf-to-images`: it does `import fitz`,
  and PyMuPDF's shim prints a deprecation notice to **stdout**, corrupting any
  captured `llm` output. Draft is written; one-line fix is `import pymupdf`.
  **[blocked: `gh auth login` — the device flow expired]**
- Decide whether `docs/CONVENTIONS.md` needs the commit rules at all. They now
  live in `AGENTS.md` (`git commit -o`, then `git show --stat HEAD`), which is the
  right home for agent process; CONVENTIONS.md § Commit granularity still covers
  only granularity and messages. Leaving it split is defensible — just do not let
  the two drift.
- Wire `--no-log` for work-tagged prompts, gated on `bin/policy`. The resolver
  exists now and already answers correctly:
  `policy check boundaries.llm_processing.log_bodies_allowed` exits 2 (unknown ->
  denied), because the field is still TODO in company.yaml. What is missing is a
  caller — nothing consults it yet, so work content still reaches the `llm` log.
  Callers must treat exit 1 and 2 identically; `check` cannot return 0 while the
  layers stay restrictions-only.
- Scope and apply retention to the 8 rows of work content already in the `llm`
  log. `company.yaml`'s `open_questions.indefinite_local_log` defaults to
  `treat_as_non_compliant`, so the current state is the non-compliant one by our
  own reading. Blocked on the resolver only for automation — the rows can be
  scoped by hand first.
- Add tests for `bin/triage`. It has none, which is why a `platform=None`
  reporting bug reached the deployed script and was caught by a manual smoke test
  rather than the 218-test suite. The env/flag/fallback resolution is the obvious
  first case.
- Run the eval suites for the two skills in `~/code/personal/ai-prompt-library`
  (`pii-redaction`, 6 cases; `commit-hygiene`, 5). Both pass `skillet validate`,
  which checks grammar, frontmatter and coverage only — no case has ever been
  executed, so the skills are unproven against a real agent. `skillet eval` spawns
  agents per case and costs real time; `--baseline` compares pass rates without
  the skill installed, which is the number that says whether either earns its
  keep. Expect to fix cases, not just read results.
- Document that `git add -p` and `git commit -o` do not compose, in AGENTS.md
  § Working alongside other sessions. It currently recommends both, but `--only`
  commits the **working-tree** content of the named paths and discards partial
  staging — so `git add -p TASKS.md && git commit -o TASKS.md` quietly commits the
  other session's hunks too. For a co-edited file it has to be `git add -p`, then
  a bare `git commit` with nothing else staged, verified immediately with
  `git show --stat HEAD`.

- Add refactoring principles to `spec.md` for the two failure modes we can
  already see coming: a test suite that grows faster than the behaviour it
  covers, and features that overlap until no one can say which one owns a
  concern. The suite is 218+ tests and every new guard adds two (refuse and
  relent), so growth is structural, not accidental. Wanted: a rule for when a
  test earns its place, a rule for collapsing near-duplicate cases, and a
  redundancy check that runs on demand rather than by vibes.
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
  `docs/CONVENTIONS.md` § Commit granularity, and the changelog standard have to
  intersect without contradicting. Note this repo deliberately has no
  `CHANGELOG.md` — `git log` is the changelog — so this governs release notes and
  any user-facing summary, not a file we keep.
  **[open question: "the 2.0 changelog standard" needs pinning down. Keep a
  Changelog is at 1.1.0 and has no 2.0; `ai-prompt-library/CHANGELOG.md` cites
  1.0.0. Common Changelog is the other candidate. Confirm which before writing
  the rule.]**

- Install `ty` and typecheck the Python. Named in the house toolchain and
  currently absent — not installed, zero references in the repo. 32 test files
  and 36 PEP 723 scripts are unchecked. Note `ty` is pre-1.0; decide whether it
  gates commits or just reports before wiring it into `prek`.
- Wire `ruff` into `.pre-commit-config.yaml`. It is installed and the toolchain
  names it, but the hook config runs shellcheck and bats only, so no Python file
  in this repo is linted on commit. Settle the ruleset first — 36 scripts written
  before any linter will not pass a default config cleanly.
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

### Refactor A — the `topic` CLI (provisioning config, state, bootstrapping)

Design already exists: `dotfiles/docs/ROADMAP-topic-cli.md`, marked "designed,
not built", written 2026-09-09. **Do not redesign it.** MVP is two commands and
the roadmap says to resist a third. These items implement it. Read the roadmap's
§ Constraints that are verified, not assumed before starting — they were checked
against this machine and must not be re-litigated.

- A1. Answer the roadmap's § Open questions for whoever picks this up, and decide
  § Where `topic` itself lives. Blocks everything below, because it fixes the
  install path and the language. Done when each open question has an answer
  recorded in the roadmap rather than in a conversation.
- A2. Build `topic new <name>`. Replaces `init-config.sh`, which copies
  `template_dir/` and stops, leaving every `topic.yml` field and five lifecycle
  stubs to be hand-edited. Done when scaffolding firefox needs no hand-editing to
  reach a valid, installable topic — and when the generated topic carries its own
  removal path, per `spec.md` § Layering — teardown changes with the thing it
  creates. That property is the main reason this tool is worth building.
- A3. Generalise `browser-ext` into `topic <name> ext add ...`. It already
  validates IDs, resolves names, pins tags and appends without destroying
  comments — but it lives inside the chrome topic and only knows browsers. Done
  when it serves chrome and firefox with no browser-specific code in the CLI.
- A4. Add dependency add/remove for non-extension topics, following the same
  comment-preserving edit approach. Done when adding a package to a topic never
  requires hand-editing YAML.
- A5. Add `topic bootstrap` — run a topic's install and its late-stage
  initialization, per `PRD.md` § Architecture. Done when a topic goes from
  scaffolded to "ready to use" through the CLI alone.
- A6. Make the CLI the path an agent drives, with the CLI remaining the human
  fallback. One implementation behind both. Done when an agent can add a topic
  end-to-end without editing a topic file directly.
- A7. Work the roadmap's § Migration inventory. Explicitly out of MVP — do not
  start before A2 and A3 are working.

### Refactor B — factor the AI/LLM tooling out of this repo

Required by `PRD.md`: dotfiles and provisioning are the trunk, this tooling is a
branch, and the architecture rule says provisioning may install and trigger a
tool but never contain its logic or state. The Ansible role STAYS — installing a
runtime and pulling weights is machine setup. What leaves is everything about the
author rather than the machine.

- B1. Decide the new home and its install method: separate repo, name, and how
  this repo pins it. Blocks everything below. Note the constraint that the result
  must be installable by the provisioning layer like any other dependency.
- B2. Write the move manifest — every affected file classified as leaves, stays,
  or is deleted. Done when the list exists and later items cite it instead of
  re-deciding per file.
- B3. Define the state contract for the new utility: one owner and one retention
  rule for data currently scattered across `~/.local/share/ollama-{usage,bench,
  evals}` and the `llm` sqlite log. This closes the standing data-ownership
  finding and is a precondition for the backup work, not a follow-up to it.
- B4. Extract `bin/policy` and its layers first. It is the most self-contained
  piece, has the best coverage, and everything else depends on it. Done when the
  resolver runs from its new home, this repo installs it, and
  `tests/policy` passes against the moved copy — both directions still asserted.
- B5. Land the capability-declaration interface from the policy generalisation
  item, so topics consume policy rather than embedding it. Do this WITH B4, not
  after: moving the resolver without it just relocates the call-site duplication.
- B6. Extract the eval harness — `ollama-evals`, cases, taxonomy. Largest surface
  and the most tests. Done when the suite is green from the new home.
- B7. Extract `ollama-profile` and `ask-research`.
- B8. Rewire the ollama role to install the utility pinned and trigger its
  initialization at a late stage, per `PRD.md`. Done when a fresh provision
  reaches "tools initialized" without this repo containing any tooling logic.
- B9. Delete the vacated code and update `spec.md`, `PRD.md` and `AGENTS.md` to
  point outward. Done when no AI tooling logic remains here and no doc describes
  it as if it were still local.

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
  (B4+B5), shared `conftest.py` fixtures, and governance-doc collisions across
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
  re-reading every line. B6 needs this most — the eval harness is the largest
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
  chosen by copier prompt, so the template ships `conventions/PYTHON.md` as one
  option rather than baking Python into AGENTS.md. `conventions/` is the unit
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
  `topic new` scaffolds a topic INSIDE this repo and this template scaffolds one
  for a repo that is not this one. They should share the canonical template
  rather than diverge — decide which owns it before the second is built. The
  module boundary itself is deferred to `ROADMAP.md` and is not a blocker; build
  against the format as it stands.
- Pin the version of every external standard this repo follows, and re-check
  upstream on a stated cadence. Today only skillet is pinned — `spec.md`'s footer
  says 1.7.0 and 1.8.0 is already available. The plain-language standard is
  unchosen, the changelog convention is unnamed, and PEP 723, copier and ruff
  versions are implicit. Wanted: one place recording standard, version, where it
  is used, and when it was last checked. A convention with no version silently
  means whatever its latest revision says, which is drift that produces no diff.

- Decide the layout for installable skills and workflows, portable across agent
  tools. Research first, because the landscape is unsettled and half of what
  looks like a standard is one vendor's convention.
  What is actually known:
  - **`AGENTS.md` is the closest thing to a cross-tool open convention** and this
    repo already has it. Keep it canonical.
  - **MCP is a genuine open standard**, but for tools and servers, not for
    skills or instructions. `.mcp.json` is read by several clients.
  - **There is no open standard for SKILLS.** The `SKILL.md` format used here is
    Anthropic's, and `skillet` already validates it — which is an argument for
    keeping it canonical and adapting outward, not for pretending it is neutral.
  Approach: one canonical source, tool-specific files generated or symlinked from
  it. Never hand-maintain two copies — that is the drift the conventions test was
  just written to prevent.
  Verify what each tool reads BEFORE writing an adapter; these paths change
  release to release. Candidates to confirm: `CLAUDE.md`, `.cursor/rules/*.mdc`,
  `.github/copilot-instructions.md`, `.windsurf/rules/`, `.goosehints`, and
  aider's convention file plus `.aider.conf.yml`.
  Build adapters only for tools actually in use. Installed on this machine:
  claude, cursor, code, aider. Not installed: goose, windsurf, copilot CLI.
  **Name collision to resolve first:** aider conventionally reads a root
  `CONVENTIONS.md`; this repo has `dotfiles/docs/CONVENTIONS.md` and now a
  `conventions/` directory. Three things one word apart is a bug waiting to be
  filed. Rename or namespace before adding the adapter.
  Note skills currently live outside this repo — `~/.claude/skills` (2) and
  `ai-prompt-library/skills` (3) — so this decides whether they move in, stay
  out and get installed, or split. `PRD.md` § Topics are installable modules is
  the precedent to follow.
  Any new root directory needs a `.chezmoiignore` entry;
  `tests/chezmoi/test_governance_not_deployed.py` will catch it if forgotten,
  provided the directory is added to its GOVERNANCE_DIRS list.
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
  `conventions/<LANGUAGE>.md`; language-neutrality; and dependency footprint.
  Do this BEFORE building either template, since the answer decides their shape.

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

- `gpt-oss:20b` and `ministral-3:8b` sit at 2 stars in `bin/binned`'s
  `_RECOMMENDED_MODELS`, marked provisional. `model-bench` measures *judging*, not
  *generation*, which is what the stars document — so promoting them on bench
  evidence would import a number measured on a different task. Leave provisional,
  or build a generation-side test?
- `bin/binned`'s SaaS tier is down to five entries after the gpt-* rows were
  dropped. Repopulate from the frontier evaluation above, or leave it thin?
- Commit-granularity guidance now exists twice: `docs/CONVENTIONS.md` § Commit
  granularity (repo-specific — scope vocabulary, worked examples from this
  history, the don't-over-split floor) and the portable `commit-hygiene` skill
  with executable evals (message-size table, pathspec commits, verify-after).
  They cross-reference and roughly half overlaps. Keep both split by audience —
  humans in this repo vs agents in any repo — or consolidate? One commit message
  called CONVENTIONS.md "the single home", so this needs a decision, not a merge.
- `~/.local/state/ai-policy/company.yaml` has **22 TODO fields** awaiting the
  author's language. It is machine-local and unversioned by design, so it cannot
  be tracked here — only pointed at. Until it is filled, `fail_closed` means the
  company layer denies everything it is asked about, which is safe but not useful.
  Work top-down: `device.approved` gates the rest.
- `apps/ollama` writes `_ollama_zsh_completion` from Ansible to a path chezmoi
  also manages — dual ownership, deliberate, documented in `tasks/install.yaml`
  with its consequence (`chezmoi apply` reverts a re-download). Marked UNDECIDED:
  formalise by giving one tool sole ownership, or leave it? Note the inversion —
  for that file the topic-root copy is the live one, the `files/zsh/` copy is dead,
  which is backwards from every `*.zsh`.

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

## Standing reminders

- `bin/` scripts are chezmoi source (`executable_<name>`); `~/bin/<name>` is what
  runs. Check `chezmoi status` before editing or you will silently revert the
  working copy.
- A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while
  testing almost nothing. Run it with `typer`, `questionary` and `hypothesis`
  present — see AGENTS.md.
