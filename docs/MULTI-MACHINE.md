# Contributing from multiple machines

Research record, 2026-09-12. The review-best-practices discipline applies:
the requirement is named first, claims are verified against artifacts, options
are ranked against what disqualifies them, and rejected options stay recorded
so no one re-litigates them blind. A panel-of-judges council reviews this
record and its design (see the final section); implementation tasks queue only
after that verdict.

## The requirement

Contribute to this repository from multiple machines such that every committed
artifact is **environment-general**: no machine-identifying content, and no
obfuscation-signaling content — nothing from which a hostile reader of the
public-or-leaked history could deduce machine topology, machine count, or that
sensitive work exists or existed. ZDR-policy engagements carry their handover
context locally by default, discardable, promotable only after
pseudo-anonymization and an explicit selection by the author. The threat model
is forced disclosure (compelled access to the repository), not casual snooping:
obfuscation that signals itself fails, which is why the design generalizes
rather than hides.

## What the audit found (verified 2026-09-12)

Machine-adjacent content already committed, by severity:

| Finding | Where | Why it matters |
|---|---|---|
| Employer-adjacent paths: `~/code/work/sentry/`, `sfw.security.sentry.io` | `TASKS.md` lines 150, 305 | The strongest topology signal; already scheduled for purge under § Private tasks |
| Employer-adjacent path in **functional config**: `chrome_unpacked_root` under `~/code/work/sentry/` | `dotfiles/apps/chrome/defaults/main.yaml:43` | Missed by the first audit pass, caught in review — unlike prose, this needs a variable fix, not a rewrite; inside the § Private tasks purge scope |
| Bare work-directory references: `~/code/work/` | `TASKS.md` lines 714, 813 | Employer-free but topology-shaping; the sweep generalizes these |
| § Private tasks describes the work it points to | `TASKS.md` § Private tasks | The reader learns sensitive purging was planned — obfuscation that signals itself |
| Environment mentions: "work machine", "the second machine", "a Seer clone", "the work workspace" | `TASKS.md` 146, 842; `MODEL-ACCESS.md` 34 | Accumulates a topology picture across documents |
| Session claims that narrate provenance | `TASKS.md` § Claimed line 60 ("separate session, reported by the author") | Trains a pattern; provenance narration belongs in local state |
| Time-zone forensics | commit metadata (-0700) | Cannot be removed without corrupting evidence; residual accepted, countermeasure is reducing what prose corroborates |

Not leaks, verified: hostnames appear nowhere in git data (the repo is
deliberately machine-neutral); `~/.local/state/chezmoi/` is unversioned and
not even referenced by git; `.chezmoi.toml.tmpl` is committed but carries only
email/name, no machine identity.

## The survey

- **This repo's own rules, extended.** `spec.md` § Data — the repository does
  not identify the employer — already established the string test: *could this
  have been found or used without being part of a company?* The design
  generalizes the same test twice: not the employer, **the environment**. A
  committed line passes when it could have been written by someone with any
  machine in any setting.
- **Chezmoi practice.** Chezmoi's official multi-machine story is per-machine
  config data in `.chezmoi.toml.tmpl` — a file that is committed. This repo's
  stricter variant (machine facts in unversioned `~/.local/state/`) is a
  strengthening, not a deviation: chezmoi itself documents that machine-specific
  data can be kept out of the source state entirely. No upstream template
  practice for handover context exists — nothing to adopt wholesale.
- **Git's own mechanisms.** `git notes` are the designed home for metadata
  that should not rewrite history and need not be pushed (this repo already
  uses `refs/notes/` for PROVENANCE). Notes are per-clone until pushed —
  the natural place for *local* verification trails. Commit signing and
  mailmap are identity *consolidation* tools, not pseudonymity tools; neither
  hides topology.
- **Ansible fleet practice.** Inventories routinely separate committed
  group definitions from unversioned `host_vars`/secrets. The same seam —
  committed structure, local identity — is the precedent for the group work's
  `machines.yml` staying generic.

## The design

**Privacy by generalization.** Committed text speaks in environment-general
classes: "a machine", "a work-managed environment", "a clone". The test for
any line: *could a reader with no knowledge of the author's machines write
this same sentence about their own setup?* If yes, it is safe; if it only
makes sense about *this* author's machines, it generalizes or moves local.

### The local mechanics (all unversioned, chezmoi-only for now)

- **`~/.local/state/chezmoi/machines.toml`** — per machine: `local_label`
  (plain: "primary", "laptop"), hostname, clone path, os_family. Written at
  machine setup, consulted by local tooling, never read by committed content.
  The deployed permission baseline denies agents this path — deliberate.
- **`~/.local/state/chezmoi/handoff/`** — the ZDR handover store. One file per
  engagement, written locally, discardable, never committed raw. Promotion
  workflow: draft → pseudo-anonymize with `bin/pii-redactor` (this repo's
  three-layer tool) → author selects what survives → sanitized text enters
  committed documents through normal review → local copy discarded or retained
  per the engagement's retention rule. `private-tasks.md` falls under these
  rules; its § Private tasks pointer gets rewritten to a bounded one.
- **Claims stay duration-bound and content-bound.** § Claimed keeps in-flight
  claims only (timestamp — what — paths; no machine, no session narration).
  Attribution beyond that is local.

### Residual risk, stated honestly

Commit timestamps carry time zones and reveal activity windows; that is
metadata corruption to fake, so it is accepted and named rather than
mitigated. The design reduces what the *prose* corroborates — a reader with
timestamps but no environment-general prose has activity curves, not topology.

## Rejected, with reasons

| Option | Why rejected |
|---|---|
| Committed role codenames for machines ("foothold", "bastion") | Withdrawn from an earlier draft of this plan. Codenames invite the exact deduction they exist to prevent — a reader asks *why machines are codenamed*, which signals obfuscation more loudly than a hostname would. |
| Chezmoi-template binding of machine identity | Crosses planes: chezmoi templates dotfiles; machine identity is Ansible-side and local-state. Also `.chezmoi.toml.tmpl` is committed. |
| Fake or normalized timestamps | Corrupts evidence and violates `spec.md` § Evidence. Accepted as residual instead. |
| Private ledger committed as an encrypted blob | Signals the same "there is something here" as plaintext; a committed encrypted blob is itself a disclosure. |
| Inventories with named hosts | Fights the self-applying `hosts: localhost` design (resolved 2026-09-12 — see TASKS.md § Topic bundles); identity belongs to `ansible_facts['hostname']` at run time, not to committed names. |

## Open questions — for the council, not guessed

1. Does environment-general prose have a leak channel through *shape* (how
   many machines a claim implies, how a removal is phrased)?
2. What is the minimal bounded pointer for local handoff that informs a
   legitimate collaborator without signaling an obfuscator?
3. Should the committed-tree sweep be enforced by a test, and what is its
   allowlist? (The sweep itself is queued as its own item.)
4. Does ZDR handover promotion need an approval step in review-best-practices
   or the questioning skill, or is the pii-redactor gate sufficient?

**Standardization TODO (author direction, 2026-09-12):** the handover store is
chezmoi-only now; a separate item standardizes local-state layout across repos
(the library will need the same for its skill-authoring engagements).
