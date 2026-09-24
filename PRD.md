# PRD.md

What this repository is for, who it serves, and what it must never become.

This document began with an interview with the author on 2026-09-10.
Requirements trace to that interview or to later author-approved decisions,
dated where recorded. Nothing here was inferred from reading the repo — a
statement of purpose assembled from evidence would be a purpose nobody chose.
Where the author left something open, this says so instead of filling the gap.

It completes a set of four. `spec.md` says what must remain true. `AGENTS.md`
says how to work here. `TASKS.md` says what is in flight. This file says what the
project is **for**, which the other three assume and none of them state.

## The goal

**A machine that is ready to use.**

That is the north star, and it is the thing to measure against when a decision is
unclear. Not "configuration is applied" and not "packages are installed" —
*ready to use*. A machine that has every package and cannot do any work has not
met the goal.

## What "ready to use" means

Starting from bare hardware, all four must be true:

1. **Packages and dotfiles are installed and configured.** Shell, editor, CLI
   tools. This is what chezmoi and Ansible already do.
2. **Secrets are reachable.** Password manager signed in, SSH keys and tokens
   working. Most tooling is inert without this.
3. **Tools are initialized.** The things that need starting state have generated
   it — model weights pulled, indexes built.
4. **Prior state is restored.** Expensive machine-specific state is recovered
   from backup rather than regenerated.

A build that stops after step 1 is not finished. Initialization is required, not
optional: a machine is not provisioned until usable state exists.

## Who it serves

**Primary: the author, on the author's own machines.** This is the only group
with a real commitment behind it. Provisioning must work on the author's Mac and
the author's Linux box.

**Secondary: anyone who finds it.** They get a repository that is readable and
worth lifting pieces from. They get no promise that it bootstraps on their
hardware, and no test will ever assert that it does.

The asymmetry is deliberate. It means "it works on my machine" is a legitimate
standard here, while "someone else could read this and learn something" is a
requirement that shapes how things are written and named.

It is not a portfolio artifact and it is not expecting contributors. Legibility
is for the author's future self and for agents working here, not for an evaluator.

## What it is

**Dotfiles and machine provisioning.** That is the trunk.

Everything else is a branch, including the AI and LLM tooling — the policy
resolver, the eval harness, the usage profiler, the research tool. That tooling
is currently the most active area of the repository, and that is a distortion to
correct rather than a fact to enshrine.

## Architecture: provision, initialize, state

Three layers, and one rule that joins them.

- **Provision** — installs everything: packages, dotfiles, and any tool the
  machine needs, including tools that live outside this repository. Being
  factored out does not mean not installed.
- **Initialize** — runs those tools once, at a late stage, to generate starting
  state. This is what turns "installed" into "ready to use". It is required.
- **State** — machine-specific. Never versioned. Backed up, because
  regenerating it costs GPU hours and bandwidth.

**The rule: the provisioning layer may install a tool and trigger it. It must
never contain that tool's logic or its state.**

That rule is what keeps the separation honest. A provisioning layer that manages
a tool's state has taken on a responsibility it cannot discharge safely, and it
is how machine-specific data ends up somewhere it should not be.

### What this means for the AI tooling

It gets factored out into its own utility with its own data store. This
repository keeps installing it, pinned, like any other dependency, and keeps
triggering its initialization. It stops containing it.

The Ansible role stays. Installing a model runtime and pulling weights is machine
setup and belongs on the trunk. What leaves is everything that is about the
author rather than about the machine: policy layers, usage data, research tooling
and the eval harness.

This is the next substantive piece of work, ahead of further additions to the AI
tooling in place. Longer term the split is a direction the repository migrates
toward rather than a single change. Until it lands, this document describes a
target shape the repository has not reached — the present tense here is aspiration,
and `TASKS.md` holds the migration.

### Topics are installable modules

A topic — the unit that installs and configures one thing — should be
installable on its own. Someone should be able to borrow one piece of this
configuration without adopting the whole repository, and an agent should be able
to build a new one from a template rather than by copying a neighbour.

This sharpens the secondary audience promise. "Readable, not runnable" holds for
the repository as a whole; a topic is the level at which lifting something is
supposed to actually work.

The boundary is deliberately unsettled — what a topic may depend on, how it
declares that, and what happens to shared state like the zsh lifecycle files
and the manifest schema. `ROADMAP.md` holds it. It has to be settled before anyone
outside this machine depends on it, and not before.

### Bundles compose topics

Grouping is data-first, decided with the author on 2026-09-12: a bundle config
object names its member topics, their run order, shared configuration, and
machine targeting, and lives outside the topics it composes. Relationships
belong to the bundle, not to each topic — that is what keeps topics
standalone-installable and keeps grouping obvious without opening every topic.
Bundles complement `topic_requires` rather than replace it, and win on
conflict. The parent playbook runs bundle-limited install, update, and
teardown today; the `topic` CLI consumes the same bundle files after its MVP.
First use case: an AI-strategy bundle, composed per machine.

### Policy is general; topics consume it

Policy governs **actions on data**, not products. It answers questions like "may
this content go to a remote model?" and "may this body be logged?" — questions
whose answers do not change when the underlying tool does.

So policy is defined once, generally, and topics consume it. A topic declares
which capability it exercises; the resolver answers; the topic obeys. Swapping
one local model runtime for another, or running two side by side, changes the
topic and leaves the policy untouched. The same holds for work policy: the rules
are about the data and the machine, not about any particular application.

Two things follow:

- No policy rule may name a product. A field that has a vendor in it is
  mis-scoped and will have to be rewritten the first time the vendor changes.
- No topic may carry its own copy of a rule. A topic that decides for itself
  whether something may be sent has become a second policy, and the two will
  disagree eventually.

This is why the policy layers leave with the factored-out utility rather than
living under any one topic. A policy that sits inside a provider's topic is a
policy that has to be duplicated the moment a second provider appears.

## How much process is enough

The repository carries a lot of verification machinery. Four reasons, all given
by the author:

- Most changes here are made by agents, whose work cannot be trusted on
  inspection alone.
- Every piece traces to a specific failure. None of it was built speculatively.
- It rehearses practices intended for higher-stakes environments.
- A broken configuration repository costs a working machine.

That machinery is also a named failure mode, so it needs a governor:

> **Verification effort scales with blast radius, not uniformly. Machinery is
> justified only where it lets an agent work unsupervised and be checked
> afterward. A routine change — adding a package, editing a dotfile — must never
> require touching `spec.md` or writing a test. Machinery is removed when the
> thing it guarded is gone.**

The last clause matters most. The tension is not only what gets added. It is that
nothing ever leaves.

## Constraints

### Data

- Machine-specific usage data stays on its machine. The code that derives it is
  publishable; its output is not.
- Back up only what is expensive to regenerate, including configuration that is
  hard to reconstruct. Everything else is regenerated on demand and never stored.
- Outside the configuration-backup rule below, **PII never leaves the internal
  disk** — neither external drive nor cloud.
- Outside that same rule, **on a machine the author does not own, backups go to
  the internal disk only** — neither cloud nor external drive.
- Otherwise, external disk or encrypted cloud is acceptable.

No backup mechanism exists today. Expensive state is currently unprotected, and
that is a known gap rather than a solved problem.

#### Configuration backups

Approved by the author on 2026-09-23. For configuration backups only, this rule
supersedes the internal-disk restrictions above:

- **Customer data from a work machine never leaves that machine.** It is never
  on the configuration capture list; its backup is the employer's concern.
- **Work-derived configuration lives only in the work secrets manager.** On the
  work Mac, machine-file backups go to work 1Password. No borg or personal
  backup tool runs on or uploads from that device.
- **Everything else is the author's data and may be backed up off-machine,
  encrypted.** Personal machine files use an explicit path allowlist, with
  local and independent remote backup repositories. Machine-written discovery
  and sync records are rebuilt rather than backed up.

Capture is limited to reviewed configuration paths, never home minus exclusions.
Backup and restore are built and tested before real data enters the new machine
files. This exception does not cover usage-derived data: `spec.md` § Data still
requires those figures to stay on their machine.

**Employer-risk dissent, recorded with the decision:** the employer's policy
sets the boundary, and even internal repository names may be confidential. A
personal tool uploading from a company-managed device creates an acceptable-use
risk. Work 1Password and the exclusion of personal backup tools address these
concerns; they do not establish employer approval. The `TASKS.md` review of what
may leave a machine the author does not own stays open.

### Work environments and intellectual property

The repository must not identify or entangle itself with any employer. The
working test is: *could this have been found or used without being part of a
company?* Generic products anyone can obtain stay. Work paths, work identifiers
and internal tool names do not.

Alongside it, a data clause: **no work or customer data ever lands in this
repository or its data stores.** The string test governs what is written down;
this governs what is held.

Two things follow, and both are deliberate:

- Requirements here are written for *work environments* in general, never for a
  specific employer. A requirement phrased around one company's policy is itself
  a disclosure.
- Any employer-specific policy or data filter is machine-local and generated,
  never committed. A filter list names what it filters for, so a versioned one
  leaks the thing it exists to catch.

This boundary has an unresolved external dependency: the governing policy for
machines the author does not own has not been authoritatively settled, and a
request that would settle it has not been sent. Tracked privately. Until it is
resolved, the rules above are the working position and not a cleared one.

## Non-goals

- **Not a product.** No support commitment, no users to keep working.
- **Not a portfolio piece.** Nothing is done here to look good to an evaluator.
- **Not clone-and-run for strangers.** Readability is promised; bootstrapping is
  not.
- **Not a home for AI tooling long-term.** That is a branch on its way out.

## What failure looks like

Four failure modes, all named by the author, all treated as equally real:

1. **Too complex to change.** The process outgrows the value and the author
   avoids their own repository. The governor above exists for this.
2. **Employer entanglement.** Something lands here that is not provably the
   author's, or that creates exposure.
3. **Abandoned and drifted.** Deployed machines diverge until the repository is
   decorative and `chezmoi apply` is no longer trusted.
4. **Locked to one machine.** So tuned to current hardware that a new machine
   cannot be provisioned from it.

Any change that makes one of these more likely needs a reason that is written
down.

## Known gaps

Open, and tracked in `TASKS.md`:

- No backup path for expensive state.
- The AI tooling factor-out has not started.
- No fresh-machine build has been verified end-to-end against the four
  conditions of "ready to use".
- The IP boundary has an unresolved external dependency.
- Data scattered across several stores with no owner and no retention rule.
