# Architecture inspection — the topic-based dotfile format (2026-09-29)

Read-only inspection requested by the author to ground the repo-manager "good
run" definition and to record cleanup findings. Scope (author, "a"): the whole
topic system — `topic.yml` schema, role/topic resolution, `roles/topic-resolution`,
the catalogue pattern, the chezmoi/Ansible deploy layers, and the machine/state
seam. No changes were made; cleanup is listed at the end, not implemented.

## 1. The model — how the topic system works today

One picture, verified against the docs and the live tree:

- **Three tools, three concerns.** chezmoi is the driver (owns files in `$HOME`,
  renders OS templates, bootstraps a machine). Ansible is the provisioner
  (installs packages, sets system state; its tree is deployed to `~/dotfiles`).
  zsh is the runtime (sources each topic's `files/zsh/*.zsh`). `ARCHITECTURE.md`
  states the boundary; the invariant is "one concern per layer".
- **A topic is an Ansible role under `apps/<topic>/`.** Required files:
  `topic.yml` (metadata), `CHANGELOG.md`, `tasks/main.yaml` (lifecycle router)
  plus the five tagged lifecycle files `bootstrap` / `prerequisites` / `upgrade` /
  `install` / `remove`. App-tier topics stub the first three; `remove` is tagged
  `never` so a bare run never tears a topic down.
- **`topic.yml` schema (5 keys, uniform across all 32 topics).** `topic_name`,
  `topic_provides`, `topic_requires`, `topic_os`, `topic_tier`
  (`pkg-manager` / `runtime-manager` / `app`). Verified: all 32 `topic.yml`
  files use exactly these five keys and no others, so the schema is well-conformed
  in practice.
- **Tiers and OS gating.** The parent playbook discovers every `topic.yml`, orders
  by tier (then alphabetically), and skips topics whose `topic_os` does not match
  the host. One capability can have different providers per OS (`docker` ← `apps/docker`
  on Debian, `apps/rancher-desktop` on macOS).
- **Dependency resolution (`roles/topic-resolution`).** Builds `provides_map`
  (dep → providing topic) and `requires_map` (dep → every consuming topic), then
  resolves each `topic_requires` to `OK` / `TOPIC_NOT_RUN` / `NO_TOPIC`. The
  reverse index is what makes teardown safe (a topic must not uninstall a dep
  another topic still requires). The role is isolated and testable under both
  OS families (`tests/topic_resolution/`).
- **The catalogue pattern (`config/*.yaml` + `topic_subscribes`).** `editors.yaml`
  and `agents.yaml` are the two catalogues: committed, domain-owned lists; a topic
  subscribes (`topic_subscribes: [editors]`), the parent playbook resolves the
  subscriber's slice, injects it, and the topic installs only what it was handed.
  Threshold for a NEW catalogue is four tests (distinct domain, subscriber,
  domain-owned truth, not foldable).
- **The machine/state seam.** Committed `machines.yml` holds repo membership by
  layout type (`repos.personal/templates/try/captures/forks/archive`), with a
  machine-local overlay for work repos. `docs/LAYOUT.md` owns the standard;
  `docs/MULTI-MACHINE.md` owns the committed-neutrality rule.

## 2. The mess — verified findings

Each finding cites evidence; none is a guess.

### 2a. Committed machine identity in `machines.yml`

`dotfiles/machines.yml:14` commits a key `L37V3P6GQ3` with the comment `# this
Mac`. The value looks like an Apple hardware serial (not a hostname). This
directly contradicts `MULTI-MACHINE.md:38` — "hostnames appear nowhere in git
data (the repo is deliberately machine-neutral)" — and `spec.md` § Data's
"does not identify the employer/machine" string test. The gita-plan handoff's
side-finding #2 already flagged this same value ("looks like an Apple hardware
serial — unverified"). It is a genuine leak, not obfuscation-shaped prose.

### 2b. Three different local-state paths for machine data

The unversioned machine-state seam has no single owner:

| Path | Purpose | Cited by |
|---|---|---|
| `~/.local/state/chezmoi/machines.toml` | per-machine label/hostname/clone-path/os | `MULTI-MACHINE.md:77` |
| `~/.local/state/layout/machines.local.yaml` | work-repo overlay for the layout standard | `machines.yml:8` |
| `~/.local/state/machine/` | repo-manager picks + private/work entries | `REQUIREMENTS.md:16`, gita-plan decisions 2/6 |

Three namespaces split one concept ("machine-specific data that must not be
committed"). A future repo-manager has to pick which one it respects, and nothing
presently says which.

### 2c. `TOPICS.md` contradicts itself on where metadata lives

Three places disagree:

- `TOPICS.md:22-24` — "Our metadata lives at the role root (`topic.yml`) so it
  does not collide with Ansible's strict validation of `topic.yml`." (The last
  "topic.yml" reads like a typo for `meta/main.yml` — metadata inside `topic.yml`
  cannot collide with "validation of topic.yml".)
- `TOPICS.md:38-40` — "We deliberately do not use `topic.yml` because Ansible's
  role loader validates that file strictly." (Contradicts the document's own
  schema section and the actual tree, which uses `topic.yml` everywhere.)
- `TOPICS.md:459-460` — "Adding a new topic" step 1 tells the reader to edit
  `apps/my-topic/meta/main.yml` to fill in `topic_name`/`topic_tier`/… — but the
  schema section says metadata lives at the role root, not `meta/`.

The intent (house metadata in a custom `topic.yml` so Ansible's `meta/main.yml`
validation is not in the way) is recoverable, but the doc is wrong in two of three
places and would mislead a fresh contributor.

### 2d. `topic_subscribes` is live but undocumented

The subscription mechanism is exercised for real — `apps/visual-studio-code/tasks/install.yaml`
consumes it, and `config/editors.yaml` / `config/agents.yaml` headers describe it —
but `TOPICS.md` and `ARCHITECTURE.md` never mention the key or the mechanism. The
catalogue pattern is the house's newest seam and its contract lives only in the
catalogue files' own comments.

### 2e. The topic system is mid-refactor (this mess is partly known)

`TASKS.md` § Planned already queues Refactor A ("the `topical` CLI" — provisioning
config/state/bootstrapping), Topic bundles (data-first grouping, which supersedes
the old hostname→groups binding), and Refactor B (factoring AI/LLM tooling out).
`managers.yaml` exists to feed the planned scaffolder (A8/A9) and documents drift
the current manual model allows (e.g. `meta/main.yml` vs role-root metadata). So
several findings above are symptoms of a migration in flight, not new discoveries —
but 2a and 2b are live problems today regardless of the refactor.

## 3. R6 / "good run" recommendation (grounded in PRD)

The binding rule is `PRD.md:78-80`:

> The provisioning layer may install a tool and trigger it. It must never contain
> that tool's logic or its state.

R6 — persistent per-repo `last-fetch` / `blocked-since` state — is **a tool's
state**, and "good run ≢ exit 0" is **a tool's logic**. Under the PRD rule, neither
may live in Ansible tasks or templates. The author-approved "Ansible fallback"
can therefore install the manager, inject its credentials, and trigger it — it
cannot *be* the manager, and it cannot own the fetch/blocked-since store. (The
adoption-skeptic critic sensed the cost — "R4/R5/R6 get hand-rolled in Ansible
anyway" — but the PRD rule is stricter: they must not be hand-rolled in Ansible at
all.)

Concrete "good run" semantics this implies, for whichever tool ends up owning it:

- **`last-fetch` advances only on a successful fetch** of that repo. A failed or
  unknown fetch leaves the prior timestamp intact — it never advances and never
  becomes a claim of freshness. First run / missing timestamp = "never fetched,
  warned" as a distinct state.
- **`blocked-since` records the moment a repo stopped being mergeable**, set on
  dirty / diverged / detached / no-upstream, and **reset when a clean `ff-only`
  merge succeeds** (the block reason cleared), not by the timer firing.
- **"Good run" is derived from the state records, never from the process exit
  code.** A run that exits 0 with zero successful fetches is not "good". A run
  that fetches 40 of 41 repos and reports the last as UNKNOWN is a *good* run
  (honest), not a failed one.
- **The staleness warning reads state only** — timestamps, no git, no network —
  so it cannot itself alter the state it reports on.

This reframes the Path A/B decision on architecture alone: the R6 state store
must be owned by a real tool (adopted or Path B), which is one more reason the
council's own split (Path B vs borrow-discovery C2) is the real fork, and why the
pure Ansible fallback is architecturally capped.

## 4. Cleanup — proposed, not implemented

Captured here for the author to triage; each belongs in `ROADMAP.md`/`TASKS.md`,
not in this thread:

1. **Remove/redact `L37V3P6GQ3` from `machines.yml`** (finding 2a). The gita-plan
   G2 item already drops hostnames from current files; the history scrub remains a
   separate "bounds future exposure" decision.
2. **Pick one local-state home for machine data** (finding 2b) and retire the
   other two paths, or document which is authoritative.
3. **Fix `TOPICS.md`'s three-way metadata contradiction** (finding 2c) — one
   sentence each; the intent is already clear.
4. **Document `topic_subscribes`** in `TOPICS.md` (finding 2d) so the catalogue
   pattern's contract has a home beside the schema it extends.
5. **Fold 2e** into the already-queued Refactor A / Topic-bundles work rather than
   opening a parallel cleanup.