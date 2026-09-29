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

### Proposed addition (pending author approval)

**"GitHub API truncation / rate-limit correctness reviewer"** — R3 is unowned by
the four critics and is the most easily-botched requirement (Search returns
`incomplete_results: true` silently; rate-limit and pagination-truncation must read
UNKNOWN, never "empty"). Grounded in GitHub's own API reference rather than a named
individual — a stronger, neutral anchor. Discriminates the live candidates directly:
ghq/ghorg enumerate via API, gitup is local-only.

### Open questions (feed REQUIREMENTS.md + later rounds)

1. Who validates the interactive **and** automation duality of R2 groups?
2. The R7 remote-normalization algorithm (SSH vs HTTPS, trailing `.git`, host
   aliases) is unowned — repoman's basename-keying is a known failure.
3. R10's contribution-viability weight (how much it moves ranking vs raw
   contract-fit) is unquantified.
4. R6 state-store durability/format across two OSes is unowned.
5. R8 cross-OS parity (macOS keychain vs Linux Secret Service) is unproven.
6. The true null hypothesis — continued manual operation — is uncosted.
