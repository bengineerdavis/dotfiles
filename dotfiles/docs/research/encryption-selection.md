# Research assignment: choosing local encryption for a single-practitioner toolchain

Run with: `ask-research start dotfiles/docs/research/encryption-selection.md --session enc`

## Who you are

Answer as three people who have already argued this out between them:

- **A cryptography engineer** who cares about construction, key handling and
  format stability, and who is allergic to "military-grade AES-256" as an
  argument for anything.
- **A data-protection engineer** who has operated retention and deletion under
  a real policy, and who knows the difference between "deleted" and "no longer
  indexed".
- **A long-term maintainer** who has inherited ten-year-old encrypted archives
  and had to open them with whatever was on the machine at the time.

Where they disagree, show the disagreement rather than averaging it. The
maintainer and the cryptographer will not agree about OpenPGP; that argument is
useful, so include it.

## The one thing this must produce

**A defensible tool choice for two distinct jobs, and an explicit statement of
which requirements drove it.** Not a feature matrix. If two tools are close,
say what would break the tie and how to test it in an afternoon.

## Operating rules

- **Primary sources.** Project documentation, source, specifications, release
  notes, licences. Label anything vendor-sourced as such.
- **Label every non-trivial claim twice** — confidence (`verified`,
  `single-source`, `reasoned`) and source authority (`primary`, `secondary`,
  `tertiary`). Three blogs agreeing is `verified`/`tertiary`, not `primary`.
- **Give a verification recipe** for anything below `verified`/`primary`: the
  exact command, file, or page that settles it.
- **Pin versions and dates.** Formats and defaults change; an unpinned claim
  cannot be rechecked later.
- **"No reliable source found" beats a plausible guess.** Earlier research on
  this project quoted aggregators that were wrong by up to 84% against the
  vendor's own API. Do not repeat that.
- **You cannot ask questions.** Where an answer depends on something unstated,
  state the assumption you used *and* list the question you would have asked.
- **Simplicity is a requirement, not a preference.** One person, two machines.
  A design needing a daemon, a service, or a cluster to stay correct has failed
  regardless of its cryptography.

---

# R0 — Review the requirements before answering anything else

**This section matters more than the tool comparison.** The requirements below
were written by the people who will use the result, which is exactly why they
should not be trusted uncritically.

For each requirement: is it a real constraint, an inherited assumption, or a
solution smuggled in as a requirement? Say which, and why.

Then answer:

- **What is missing?** Which requirement should exist and does not?
- **Which are in tension?** Name the trade explicitly rather than resolving it
  quietly. Suspected tensions: hardware-bound keys vs. machine loss;
  verifiable deletion vs. deduplication; simplicity vs. per-file access.
- **Which are over-specified?** Where has a preference been written as a
  constraint, narrowing the field for no security gain?
- **Is the two-job split itself correct?** It is asserted below, not proven.
  Argue for or against one tool covering both.

## The requirements as currently stated

| # | Requirement | Stated rationale |
|---|---|---|
| 1 | Terminal-first; every operation scriptable | Automation, and no GUI-only recovery path |
| 2 | Recoverable by hand years later, without the wrapper tooling | Tools get abandoned |
| 3 | No telemetry or network calls anywhere in the chain | Hard gate |
| 4 | Open source, permissive licence preferred | Auditability, no vendor dependency |
| 5 | Writing must not require a secret; reading must | Unattended writes; vault-gated reads |
| 6 | Deletion must be verifiable — one operation, no residue | Retention is policy-driven, not cosmetic |
| 7 | No kernel extensions | macOS Apple Silicon requires lowering system security for FUSE |
| 8 | No ambient plaintext | A mounted volume exposes plaintext to every process |
| 9 | Metadata leakage minimised — filenames, sizes, structure | Paths can identify a subject as surely as contents |
| 10 | Key recoverable if a machine is lost | Solo operator; key loss is likelier than compromise |

Requirement 5 is the least conventional. Interrogate it: is a
recipient/identity split genuinely valuable here, or is it elegance in search
of a threat? What attack does it actually prevent, and how likely is that
attack relative to the complexity it adds?

---

# The system

One practitioner, two machines: a macOS laptop (Apple Silicon, FileVault on,
SIP enabled, Secure Enclave present) and a Linux workstation (LUKS available).
No shared infrastructure, no team, no CI.

Two jobs are believed to be distinct. **Test that belief.**

**Job A — local holding area ("quarantine").** A safety net for items removed
by a retention rule. Write-once, read-rarely, deleted on a clock.
Characteristics: a handful of entries; each held ~30 days; entries are
independent; total volume small (megabytes); read only when something was
deleted too early. Deletion must be verifiable because the whole point is that
data does not outlive its window.

**Job B — remote archive.** Periodic encrypted archive to cloud object storage.
Characteristics: large and growing; written repeatedly; long-lived; **the
provider is assumed actively hostile** — it may read, retain, analyse, be
compelled, or be breached. Client-side encryption only; no provider-side
feature requiring plaintext may be depended on. Assume ciphertext is retained
forever after deletion, so a key compromised in 2032 must not expose an archive
written in 2026.

Some content is governed by an employer policy that caps total retention
(currently 30 days) and forbids storage off approved devices. That cap is a
hard ceiling: any mechanism that *extends* retention — including holding an
encrypted copy — breaches it while appearing to add safety.

## Candidates

Verified present in Homebrew on the target machine, with version and licence as
of 2026-08-22. Treat these as a starting set, not a closed list — propose
anything missing, including things deliberately not packaged here.

| Tool | Version | Licence | Shape |
|---|---|---|---|
| age | 1.3.1 | BSD-3-Clause | stream encryption, recipient/identity |
| rage | 0.12.1 | MIT / Apache-2.0 | independent Rust implementation of the age format |
| age-plugin-se | 0.2.1 | MIT | Apple Secure Enclave-backed age keys |
| age-plugin-yubikey | 0.5.1 | Apache-2.0 / MIT | hardware token-backed age keys |
| gnupg | 2.5.21 | GPL-3.0-or-later | OpenPGP |
| sequoia-sq | 1.4.0 | LGPL-2.0-or-later | modern OpenPGP implementation |
| scrypt | 1.3.3 | BSD-2-Clause | passphrase file encryption |
| sevenzip | 26.02 | LGPL-2.1 / BSD-3 | archive format with AES-256, native directories |
| restic | 0.19.1 | BSD-2-Clause | dedup backup repository |
| borgbackup | 1.4.5 | BSD-3-Clause | dedup backup repository |
| kopia | 0.23.1 | Apache-2.0 | dedup backup repository |
| rclone | 1.75.0 | MIT | sync, with a client-side `crypt` backend |
| gocryptfs | 2.6.1 | MIT | FUSE encrypted filesystem |
| cryfs | 1.0.3 | LGPL-3.0-or-later | FUSE encrypted filesystem, hides structure |
| duplicity | 3.2.0 | GPL-2.0-or-later | encrypted incremental backup |
| sops | 3.13.3 | MPL-2.0 | structured-data secrets |

Also assess, though not packaged here: Kryptor, Picocrypt, encpipe, Cryptomator
(and its CLI), VeraCrypt, Tomb, and macOS-native `hdiutil` encrypted disk
images.

Current working choice for Job A is `age` + `tar` + `zstd`. **Argue against it.**

---

# Questions

## R1 — Threat model for these two jobs specifically

Construct it; do not assume one. Distinguish Job A from Job B — they likely
have different adversaries.

Consider at least: laptop theft while powered off; theft while unlocked; a
hostile or breached storage provider; a compelled disclosure; another process
running as the same user; the practitioner's own error (mis-scoped sync, key
lost, retention window wrong); and a future reader with the ciphertext but not
the tooling.

Deliver a compact table: asset × adversary × boundary × control. State clearly
what is **out of scope** and why — a threat model defending against everything
defends against nothing.

## R2 — What "deleted" means, per tool

This is the requirement most likely to be decided by implementation detail
rather than design.

- For each candidate holding multiple items, what exactly happens on delete?
  Distinguish: index entry removed, bytes unreferenced, bytes overwritten,
  bytes reclaimed.
- For deduplicating repositories, how long can bytes survive a logical delete,
  and what guarantees does compaction or pruning actually make? Cite the
  documentation, not the intent.
- What can be **proved** after the fact — and with what command?
- How does each interact with copy-on-write filesystems, snapshots, and SSD
  wear-levelling, where an unlink does not imply erasure? Be honest about the
  limits of any userspace claim here.

## R3 — Key management for one person

- Compare: passphrase; key file; password manager; Secure Enclave
  (`age-plugin-se`); hardware token. Name the failure mode of each.
- **Secure Enclave specifically.** What are the real properties — is the key
  extractable, what binds it to the device, what happens on OS reinstall,
  logic-board replacement, or restore-from-backup? Is a Secure Enclave key ever
  recoverable, and if not, what is the correct backup pattern?
- Multi-recipient as a redundancy strategy: encrypting to a hardware key *and*
  a recovery key. What does it cost, and what does it weaken?
- **Key rotation against permanently-retained ciphertext** (Job B). Per-archive
  keys, periodic re-encryption, forward secrecy — and be blunt about which of
  these one person will actually keep doing. A rotation policy nobody follows
  is worse than none, because it implies protection that is not there.
- State plainly which is the likelier catastrophe for a solo operator — key
  loss or key compromise — and let the recommendation follow from that.

## R4 — Longevity and format stability

- For each candidate format: is there a written specification? How many
  independent implementations exist? Has the format changed incompatibly, and
  how was migration handled?
- What is the realistic hand-recovery path in ten years, given only the
  ciphertext, the key, and a general-purpose machine? Write the commands.
- Which candidates depend on a language runtime, and does that matter?
- Assess OpenPGP honestly: thirty years of ubiquity against well-documented
  complexity and footguns. Does `sequoia-sq` change that calculus?

## R5 — One tool or two?

The two-job split is an assumption. Test it.

- What is the cost of using one tool for both — in complexity, in deletion
  guarantees, in recovery?
- What is the cost of two — in cognitive load, in duplicated key management, in
  the risk of using the wrong one?
- Is there a single tool that credibly covers both without compromising R2?
- If two, what should the boundary be, and how is a user stopped from putting
  capped-retention content into the long-lived store?

## R6 — Metadata leakage

- For each candidate, what is observable **without** the key: filenames, sizes,
  counts, directory structure, timestamps, access patterns, change frequency?
- Rank them. Where does the intuition "file-level encryption is more granular,
  therefore better" break down?
- How much does a single opaque blob per entry actually help, and what does it
  cost in access ergonomics?
- Which leaks matter given R1, and which are theoretical?

## R7 — Telemetry and network behaviour (hard gate)

For **every** tool recommended: does it make any network call by default —
version checks, crash reporting, usage statistics, update pings? What, where
to, and how is it disabled? Link the source or documentation that proves it.
An unverifiable answer is a disqualification. Note where a tool is permissively
licensed but its hosted service behaves differently.

## R8 — Recommend

Given R0–R7: name the tools and the design. Include what you would **not** do
and why. State confidence (high/medium/low) per recommendation and what would
change your mind. Where the honest answer is "test both", say that and give the
test.

---

## Output contract

1. **R0 first** — the requirements review, including anything you would add,
   remove, or reword. This is the deliverable everything else hangs from.
2. The threat-model table.
3. One section per R-number. Tables before prose. Recommendation last.
4. **Telemetry results as a pass/fail table** with a source link per row.
5. **Assumptions I made, and the questions I would have asked** — the ones
   whose answers would change the recommendation.
6. Confidence per recommendation.

## Before you answer, check yourself

- Did you challenge the requirements, or only answer against them?
- Is every non-trivial claim labelled on both axes?
- For deletion, did you cite documented behaviour rather than assumed
  behaviour?
- Does the design survive: laptop stolen, key lost, provider breached, tool
  abandoned?
- Can a human perform every operation from a terminal, without the wrapper
  scripts?
- Did you say what you could not find, rather than filling the gap with
  plausible text?
