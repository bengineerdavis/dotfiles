# Requirements — repository-fleet manager (DRAFT until Council Round 0)

Status: **DRAFT**. Council Round 0 critiques and sharpens this list; the
author acks the one-screen diff before the sonar brief runs. Each requirement
cites its source: an approved handoff decision (gita-plan `HANDOFF.md`,
`46042e9`) or a dated author answer ([AUTHOR-ANSWERS.md](AUTHOR-ANSWERS.md)).
The verification note says how a candidate is tested against it — what a
claim must show to count as MET.

## R1 — Declarative catalogue with local machine selection

Each machine declares which repositories it wants; the declaration is data,
not hostname-bound. Personal repos and remotes live in a committed catalogue
(`dotfiles/config/repos.yaml` shape, handoff decision 1); per-machine picks,
private entries, and work entries live in unversioned local files
(`~/.local/state/machine/`, decisions 2 and 6). Work entries never commit.

**Source:** handoff decisions 1–3, 6; author answer #3 (no custom logic).
**Verification:** a manifest/selection file can name per-machine sets without
committing a hostname; adding a repo = edit + run.

## R2 — Named groups (gita-style)

Repositories group by directory/layout type; groups work in both interactive
use and automation. Membership cites paths under the type dir, never bare
names (basename collisions are a known gita failure, handoff decision 15).

**Source:** handoff decisions 11, 15.
**Verification:** groups are first-class (listable, selectable, used by
update commands), not comments or naming conventions.

## R3 — GitHub discovery with truncation discipline

Enumerate a user/org's repositories via `gh` or the API: explicit limits,
truncation detected (a full page is UNKNOWN, not complete), auth/rate-limit
failure ⇒ UNKNOWN, never "empty". At most 10 adds per run; archived repos
skipped by default; account scope recorded.

**Source:** handoff decisions 24, 26, 27; GITA-RESEARCH.md § gh discovery.
**Verification:** the tool distinguishes saturated/failed listings from
genuinely empty results, and never unregisters from an incomplete listing.

## R4 — Safe sync semantics

Fetch EVERY repository including dirty ones (fetch never touches the working
tree), then fast-forward only clean, attached, non-diverged repos
(`git merge --ff-only`). Never merge, rebase, reset, or stash user work.
Failed fetch ⇒ UNKNOWN freshness, never "up to date".

**Source:** handoff decisions 17–19.
**Verification:** demonstrated behavior (code or tests) shows dirty repos are
fetched and skipped for merge; a failed fetch cannot produce "up to date".

## R5 — Per-repo verdicts, non-aborting

Every repo gets a verdict (fast-forwarded / skipped-with-reason / failed),
with reliable exit-code or machine-readable reporting; one repo's failure
must not abort the run. Repo-local problems exit 0; provider/config defects
fail the run. Gita fails here (discarded exit codes); gitup fails here.

**Source:** handoff decisions 18–19; GITA-RESEARCH.md § deciding evidence.
**Verification:** exit codes or structured output survive to the caller;
aggregate-only status does not count.

## R6 — Freshness state

Persistent per-repo last-fetch and blocked-since records (machine-written,
separate from hand-edited files, never backed up) feeding a staleness warning
(12h discipline). "Good run" must be defined independently of exit 0.

**Source:** handoff decisions 21, 23; G0b open questions (G4/G5).
**Verification:** timestamps written per run; failure leaves prior evidence
intact rather than advancing it.

## R7 — Remote-identity adoption

Match existing clones by normalized remote identity (host/owner/repo) before
cloning anything; the normalizer is pure and property-testable. Misplaced
matches are reported, never relocated (LAYOUT.md's no-self-healing rule).
Basename-keyed registries don't count (repoman's `Upsert` keys by name).

**Source:** handoff decision 12; GITA-RESEARCH.md expanded comparison.
**Verification:** a clone found by URL in the "wrong" directory is reported;
identity survives URL-form differences (SSH vs HTTPS, .git suffix).

## R8 — Secrets injection, no plaintext (binding + tie-breaker)

Credentials resolve at runtime from 1Password CLI (work machines), Bitwarden
CLI (personal), or the OS keychain (macOS Keychain / GNOME `secret-tool`).
The tool and its config never persist plaintext tokens; config references
secret sources. **Tie-breaker:** prefer candidates needing no dedicated
GitHub service token — the author's normal `gh auth` or SSH should suffice;
a token-requiring candidate cannot outrank an equivalent without one.

**Source:** author answers #9, #18; handoff decision 40 (read-denials).
**Verification:** where the tool stores any token it needs is documented;
a passcommand/credential-CLI injection path exists or can be added without
patching.

## R9 — Human-friendly, maintained, cross-platform

Simple workflow and interface; current, usable documentation; active
maintenance; macOS + Linux; permissive license. The author reads docs before
tools, so doc quality is a fit criterion, not decoration.

**Source:** author answer #3; handoff decisions 9, 16.
**Verification:** release/commit recency, contributor count, docs reviewed
for the R4/R5 semantics; platforms declared.

## R10 — Contribution viability (Path A depends on it)

Rank partly by how practical upstream contribution is: maintainer
responsiveness, CONTRIBUTING/governance, license, release cadence. A perfect
tool with a dead upstream can't absorb the Ansible work, which is the whole
point of Path A.

**Source:** author answer #8.
**Verification:** maintainer signals collected per candidate (issue response,
merge cadence, governance docs); recorded even when the verdict is "hostile".

## R11 — Language tie-breaker (rough, not rigid)

Prefer Python/Ruby implementations, then Rust, then Go, then other. The
author's fluencies are Python and bash; glue contributions (Path A) are
likelier to land in a language they can maintain. **Never disqualifying** —
the author uses any ecosystem; language only orders otherwise-equal
candidates.

**Source:** author answers #11, #12.
**Verification:** implementation language recorded; never a rejection reason
on its own.

## Outcome framing (assess both, decide with the author)

- **Path A** — Ansible composition now + upstream contributions until the
  tool absorbs the Ansible work (author-approved as the fallback shape,
  answer #5).
- **Path B** — our own tool in a new repo outside this one (AGENTS.md build
  ladder); this directory migrates to it.

## Open shape questions for Round 0 (from G0b, still standing)

- Does "no local pick" prevent tool installation too, or only repo actions?
- Which source files are required vs optional (machine.yaml/private.yaml)?
- Define "last good run" independently of exit 0; first-run/missing
  timestamps; when blocked-since resets.
- Timer runs: does `off` stay off; may timers clone newly declared explicit
  repos? Which type wins for a repo that is both fork and template?
- What counts as an "empty required source" for the backup guard (BK2)?
- Permission allocation: G2 machine-path read denial, BK2 backup-store denial
  — confirmed?
