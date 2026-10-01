# Council rounds — repo-manager thread

One section per round, appended in order. Each entry records: date, panel
(with any recruiter-proposed additions and why), the critique or findings,
researcher verdicts, open-question scenarios (anything the findings could not
answer, phrased as investigable questions), and the author answers captured
in response ([AUTHOR-ANSWERS.md](AUTHOR-ANSWERS.md) holds them verbatim).

Panel composition and recruiter authority are defined in
[PLAN.md](PLAN.md) § 6.

## Round 0 — Recruiter (2026-09-29)

Recruiter ran first, per PLAN.md § 6 (Round 0 only, $5 cap). Public research
only; no contact. One addition proposed below, **pending author approval**.
Spend: one hosted-model run (opus-4.8); not precisely logged, estimated well
under a dollar of the separate $5 recruiter cap.

### Roster review — the four critics sharpened

- **Adoption skeptic** — anchor on the *real* Ansible fallback's cost:
  `ansible.builtin.git` has no ff-only-with-dirty-fetch contract, so R4/R5 fall
  on hand-rolled `command:`/`failed_when:` blocks. Cost *that* wrapper, not an
  imagined turnkey tool. (ansible.builtin.git module docs)
- **Contribution pragmatist** — per-candidate maintainer signals, not open-source
  optimism. gitup (earwig: single maintainer, 842★, slow PR cadence) vs ghorg
  (gabrie30: 2154★, more triage, but the missing ff-only safe mode is a large
  behavioral-default PR). Ask: CONTRIBUTING present? review turnaround? precedent
  for behavioral defaults merging?
- **Build-cost skeptic** — repoman is the "someone already tried Path B" datapoint:
  1★, 1 contributor, no releases/CI, and already wrong on R4 (skips dirty repos
  before pull) and R7 (basename-keyed registry). Under-scoping is a real risk,
  not a strawman.
- **Security/secrets reviewer** — test each candidate against `op run` / `bw get`
  / git-credential-helper injection; flag any candidate that *requires* a persisted
  token or writes plaintext (e.g. `~/.netrc`); note R6'd persistent state is itself
  a leak vector.

### Proposed addition (approved 2026-09-29 — panel is now five)

**"GitHub API truncation / rate-limit correctness reviewer"** — R3 is unowned by
the four critics and is the most easily-botched requirement (Search returns
`incomplete_results: true` silently; rate-limit and pagination-truncation must read
UNKNOWN, never "empty"). Grounded in GitHub's own API reference rather than a named
individual — a stronger, neutral anchor. Discriminates the live candidates directly:
ghq/ghorg enumerate via API, gitup is local-only. Author approved; joins the panel
for Round 0.

### Open questions (feed REQUIREMENTS.md + later rounds)

1. Who validates the interactive **and** automation duality of R2 groups?
2. The R7 remote-normalization algorithm (SSH vs HTTPS, trailing `.git`, host
   aliases) is unowned — repoman's basename-keying is a known failure.
3. R10's contribution-viability weight (how much it moves ranking vs raw
   contract-fit) is unquantified.
4. R6 state-store durability/format across two OSes is unowned.
5. R8 cross-OS parity (macOS keychain vs Linux Secret Service) is unproven.
6. The true null hypothesis — continued manual operation — is uncosted.

## Round 0 — Council critique (2026-09-29, five critics)

Five critics ran fresh-context against the R1–R11 draft, the candidate ledger, and
the C1–C4 combination hypotheses. Spend: five hosted runs, well within the $5 critcap.

### Verdicts by critic

- **Adoption skeptic** — favours **C3 (Path B)**. R4/R5 don't shrink under adoption:
  you still hand-roll fetch-then-ff-only-then-verdict in `command:`/`failed_when:`,
  so Path A *duplicates* that work beside a tool you now also maintain glue for. R6
  is hand-rolled in every path. Calls C1/C4 false economies; "contribute until the
  tool absorbs the work" against repoman (1★) means *you* become maintainer.
- **Contribution pragmatist** — favours **C2**. Path A's core PRs are
  *behavioral-default* changes (the hardest to merge); smallest/safest is gitup's
  exit-report (additive, non-breaking), but gitup/earwig is single-maintainer with
  no redundancy, and ghorg/gabrie30 is responsive yet scope-misaligned. Trap: R10
  conflates "responsive to bug PRs" with "will merge a default-behavior change" — no
  candidate scores high on both. Upstream absorption is "unfundable"; treat
  contribution as nice-to-have, not the plan.
- **Build-cost skeptic** — favours **C2**, warns hard against C3. repoman is proof:
  a solo tool already got R4 and R7 wrong. R3 tri-state, R5 partial-failure matrix,
  R6 durable state, R7 normalization are each a hidden multi-hour cost; maintenance
  is forever against a user count of ~one.
- **Security/secrets reviewer** — favours **C3** (thin owned tool centralises
  "never persist, always inject"). Flags: ghorg reads `GHORG_GITHUB_TOKEN` from
  `conf.yaml` (persisted plaintext); `gh auth login` writes `hosts.yml`; R6 state
  must be URL/userinfo-free (fetch-failure records are the classic token-leak slot);
  headless Linux timers cannot unlock Secret Service (cross-OS parity gap).
- **API truncation/rate-limit reviewer** — favours **C3** for R3 correctness. Three
  distinct UNKNOWN signals: Search `incomplete_results:true` (not exposed by
  `gh search --json`); `--paginate` partial-walk emitting a truncated list as
  complete; secondary rate-limit 403+`Retry-After` with no `X-RateLimit-*`. ghq does
  no enumeration (neutral); ghorg's exit semantics must be verified.

### Cross-critic disagreement (dissent to preserve)

- **Path B (C3)** — endorsed by adoption, security, and API-correctness critics.
- **C2 (thin Ansible engine + ghq/ghorg discovery, upstream = nice-to-have)** —
  endorsed by contribution and build-cost critics.
- Nobody advocates adopting any single tool as-is. The honest split is *"own the
  R4/R5/R6/R7 core"* (B) vs *"own a thin engine, borrow discovery"* (C2).

### Author-decision questions (batched to the author)

The council's individual questions are merged and re-keyed below; answers are
recorded verbatim in AUTHOR-ANSWERS.md.

1. **(null baseline, was Q-l)** what is the current manual repo-sync cost (approx.
   time/week)? Without it no automation can be shown to pay off.
2. **(good run, Q-c)** define "last good run" independent of exit 0 — including
   first-run/missing timestamps and when `blocked-since` resets.
3. **(no local pick, Q-a)** prevent tool install too, or only repo actions?
4. **(source files, Q-b)** which of `machine.yaml`/`private.yaml` are required vs
   optional — and confirm neither may ever hold a token (security critic).
5. **(timers, Q-d)** does discovery mode `off` stay off; may timers clone
   newly-declared explicit repos; fork-vs-template type precedence? Plus: how do
   headless Linux timers unlock Secret Service without a plaintext fallback?
6. **(backup guard, Q-e)** what counts as an "empty required source" — and is a
   discovery UNKNOWN distinct from it?
7. **(permissions, Q-f)** confirm G2 machine-path read denial and BK2 backup-store
   denial.
8. **(remote normalization, Q-h)** who owns the R7 normalizer, and write the
   algorithm (SSH vs HTTPS, trailing `.git`, host aliases) before any build estimate.
9. **(contribution weight, Q-i)** does R10 distinguish "responsive to bug PRs" from
   "will merge a default-behavior change", and how much weight vs contract-fit?
10. **(state store, Q-j)** R6 location + format; must be URL/userinfo-free.
11. **(keychain parity, Q-k)** accept the macOS/Linux credential asymmetry as a
    documented constraint rather than a runtime surprise?

### Research questions (for sonar + source verification, not the author)

- Does ghorg expose partial-page / `incomplete_results` on its discovery path, or
  collapse auth/rate-limit failure into "zero repos"?
- Does `gh search repo --json` expose `incomplete_results` (critic asserts it does
  not) — forcing `gh api search/repositories` instead?
- Any precedent PR in gitup/ghorg where the maintainer merged a *default* safety
  change (not an opt-in flag)?
- Confirm ghorg `conf.yaml` / `gh hosts.yml` credential persistence, and whether
  env-only injection is a supported path.

## Round 2 — Council (2026-09-29, five critics)

Convened by the author: re-critique after research, and review policy direction.

### Unanimous convergence

All five critics independently reach the same reading: the PRD rule
("provisioning may install a tool and trigger it; it must never contain that
tool's logic or its state") forces the manager to be a **real tool**, not Ansible
glue. R4 sync semantics are *logic*; R6 persistent state is *state* — so the
Ansible fallback is off the table as the sync/state owner. **Path B (thin owned
tool) becomes the default by elimination, not preference.** Upstream contribution
("until the tool absorbs the work") is dead for R4–R7 (west is manifest-
convergence, mani declares sync-not-a-contract); it survives only as block-level
borrowing: discovery, path convention, credential injection.

### Requirements under-specified (tighten before any build)

- R4: "non-diverged" undefined (ahead-only vs ahead+behind); force-push-upstream
  (fetch ok, ff-only fails) → blocked or dirty?; no-upstream; detached HEAD;
  submodules.
- R6: state-file location + schema unnamed; must be machine-local/gitignored and
  pass § Data; "good run" boundary vs the R5 report.
- R7: normalization algorithm (SSH vs HTTPS, trailing `.git`, case) unspecified.
- R3: list vs search split — Search carries `incomplete_results` + 1000-result cap
  and must not be authoritative; secondary rate-limit (403+`Retry-After`);
  `--paginate` partial-walk ⇒ UNKNOWN.
- R10: near-dead for whole-tool merge (no qualifying target); demote to
  block-level viability.
- Missing: concurrency / partial-network-failure as distinct from per-repo failure.

### Policy rulings to order (the "policy review" the author sensed)

1. **Egress** — does `gh`/API owner-list discovery count as permitted
   "public-facts-research", or does listing a private org need per-run human review?
2. **§ Data** — is the R6 state file (repo names + timestamps) a machine/employer
   identity leak, and where must it live so it is never committed/synced?
3. **R8** — does `gh`'s cached OAuth token (`~/.config/gh/hosts.yml`) satisfy
   "no plaintext / keychain", or must discovery credentials also come from
   1Password / OS keychain?
4. **R8 cross-OS keychain parity** — headless Linux (no Secret Service) must
   degrade to `op`/`bw`, never to plaintext.

### New author questions (batched)

1. Is Path B (owned thin tool) now the default — or is a thin wrapper over
   mani/ghq acceptable despite the two-tool cost?
2. R4 precise definition: force-push and ahead+behind cases; detached-HEAD and
   submodule handling.
3. R6 state location/schema (`XDG_STATE_HOME`?), never committed/synced.
4. Is gh/API discovery "public-facts-research" under the egress policy, and does
   reusing `gh` auth satisfy R8?
5. Headless Linux: is `op`/`bw` CLI a hard dependency, or is `gh auth` the primary
   credential path?

## Naming sessions (2026-09-29)

Four passes over the tool name (council stress-test, then researcher rounds), at
the author's request. All names collision-checked against PyPI + GitHub before
listing. Converged criteria (from the advisors): **legibility** (a stranger infers
"manages a collection of git repos"), **metaphor-integrity** (holds
`update/upgrade/lock/pin/sync/status` and carries the persistent-record idea),
**ownability** (single clean token, not a `git`/`repo` prefix-mash), and
**author taste** (spanning-layer / story-of-change / tidal-flow-and-record).

Findings that shaped it:

- Almost every evocative single word is claimed — `canopy` (PyPI client +
  `github.com/canopy` org), `grove` (a git-worktree tool), `garden`, `coppice`
  (git-worktree), `overstory` (AI orchestration), `radix`, `radicle` (a P2P git
  project), `watermark`, `driftwood`, `cairn`, `ledgerline`, `slackwater`-. . .
- The literal "record-keeper" family is mined too (`codex` → OpenAI Codex,
  `chronicle`, `folio`, `scribe`, `tome`, `vellum`, `palimpsest`).
- Bare `canopy` is **unownable** — the advisors were unambiguous; `gitcanopy` is
  the surviving way to keep the word.

Surviving shortlist (available on PyPI):

| Name | Lens | Note |
|---|---|---|
| **tideline** | tidal + record | the mark the tide leaves = persistent state; rhymes with timeline/baseline |
| **gitcanopy** | canopy compd | keeps the author's favorite; legible via `git-`; weak GH hit only |
| **repoledger** | literal/record | "the standing book of repos"; strongest legibility + record |
| **distributary** | water | "flows OUT" to the fleet; legible root, long word |
| **repofolio** | historian | "portfolio of repos"; clean |

Open: the author's final pick — decision pending, not recorded here (it lands in
AUTHOR-ANSWERS.md when chosen).

**Decided 2026-09-29:** `redge` (binary) / `redge-cli` (PyPI + crates.io
namespace); `redge-git` considered and rejected. Bare `redge` is taken on PyPI, so
the `-cli` compound keeps the binary name. Recorded in AUTHOR-ANSWERS.md § naming
decided.
