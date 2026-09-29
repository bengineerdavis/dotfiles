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
