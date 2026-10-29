# `redge` — requirements specification

Normative statement of what `redge` must do, settled after Council Rounds 0 and 2
and the sonar/source verification. This supersedes the REQUIREMENTS.md draft; that
file remains the dated history. Article in the imperative: SHALL is a hard
requirement, SHOULD a preference that ordering may not silently override, MAY an
allowed extension.

## R1 — Declarative catalogue with local selection

The tool SHALL read a declarative catalogue of repositories, and SHALL let each
machine select its own set locally without committing a hostname. Personal
repositories and remotes SHALL live in a committed catalogue; private and work
entries SHALL live in an unversioned local overlay; work entries SHALL NOT be
committed. Adding or removing a repository SHALL be an edit plus a run, and SHALL
NOT require a hostname to change.

## R2 — Named groups, first class

Repositories SHALL group by named sets usable in both automation and interactive
use. Membership SHALL cite paths under the type directory, never bare basenames
(a known collision source). A group SHALL be listable, selectable, and addressable
by every command that operates on more than one repository.

## R3 — Discovery with truncation discipline

Discovery SHALL enumerate a user/org through `gh`/the API. It SHALL use list
endpoints, not Search (Search caps at one thousand and returns
`incomplete_results` the JSON does not surface). A full or truncated page, an
auth failure, a rate limit, or a secondary rate limit SHALL read UNKNOWN — never
"empty" — and SHALL NEVER unregister from an incomplete listing. At most ten
repositories SHALL be added per run; archived repositories SHALL be skipped by
default; the account scope of the listing SHALL be recorded.

## R4 — Safe sync (the binding safety contract)

Every repository SHALL be fetched, including dirty ones (fetch never touches the
working tree). The tool SHALL fast-forward only a clean, attached,
non-diverged repository, and SHALL use `git merge --ff-only` to do it. The tool
SHALL NOT merge, rebase, reset, or stash local work, and SHALL NOT enforce a
pinned revision by rewriting the tree.

A repository SHALL be classified per run:

- **clean + ahead-only** → fast-forwarded.
- **dirty** → fetched, not merged, verdict `skipped: dirty`.
- **diverged** (ahead and behind, or upstream force-pushed) → `blocked-since`
  set, verdict `skipped: diverged`, tree untouched.
- **detached HEAD / no upstream / mid-operation** → `blocked-since` set, verdict
  `skipped: <reason>`.
- **failed fetch** → UNKNOWN freshness; `last-fetch` not advanced.

Submodules are out of scope in v1 and SHALL be treated as the superproject only,
with that limitation stated.

## R5 — Per-repository verdicts, non-aborting

Every repository SHALL produce a verdict, reported through a stable exit-code or
machine-readable scheme. One repository's failure SHALL NOT abort the run. A
repository-local problem SHALL exit `0`; a provider or configuration defect SHALL
fail the run.

## R6 — Persistent freshness state

The tool SHALL write per-repository `last-fetch` and `blocked-since` records to a
machine-local state store, SHALL NOT commit, sync, or back them up, and SHALL
store no URLs or userinfo in them. `last-fetch` SHALL advance only on a
successful fetch; `blocked-since` SHALL reset only when a clean `ff-only` merge
clears the reason. "Good run" SHALL derive from these records, never from the
process exit code.

## R7 — Remote-identity adoption

The tool SHALL match existing clones by a normalized remote identity
(`host/owner/repo`) before cloning, SHALL report a clone found in the wrong place
rather than relocating it, and SHALL NOT key a registry by basename. The
normalizer SHALL be a pure function covering SSH vs HTTPS, the trailing `.git`
suffix, and host aliases, and SHALL be property-tested.

## R8 — Secrets injection, no plaintext

Credentials SHALL resolve at run time from the 1Password CLI, the Bitwarden CLI,
a git credential helper, or the user's existing `gh` auth; the tool or its config
SHALL NOT persist a plaintext token. A candidate design needing no dedicated
GitHub service token SHOULD be preferred over an otherwise-equal one.

## R9 — Human-friendly and maintained

The workflow SHALL be simple; the documentation SHALL be current; the project
SHALL support macOS and Linux and SHALL use a permissive license. Documentation
SHALL state the R4/R5 semantics explicitly.

## R10 — Borrowed blocks, not adopt-a-tool

`redge` SHALL NOT adopt a whole existing tool. When a component is borrowed
(registry listing, path convention), its maintenance and license SHALL be
checked; contribution viability SHALL rank among borrowed blocks only, never as
a reason to outsource the core.

## R11 — Language

The implementation SHALL be Python now. A later Rust port SHALL reuse the same
`redge-cli` registry namespace where the registries permit, and the name SHALL
clear both PyPI and crates.io from the start.

## The pinning split (update / upgrade / lock)

The tool SHALL expose three motions: **update** refreshes what is available and
never touches a working tree; **lock / unlock** records or clears a pinned ref;
**upgrade** fast-forwards toward the locked/upstream ref and advances the pin only
when that merge succeeds. The pin is a record, never a constraint enforced by
mutation.

## Boundary

The provisioning layer (chezmoi/Ansible) MAY install `redge` and MAY trigger
runs; it SHALL NOT contain `redge`'s logic or state. The Ansible role that
installs `redge` is a sibling artifact inside the `redge` repository.

## Outcome

Build our own tool (`redge`, shipped as `redge-cli`), in a new repository outside
the dotfiles tree.