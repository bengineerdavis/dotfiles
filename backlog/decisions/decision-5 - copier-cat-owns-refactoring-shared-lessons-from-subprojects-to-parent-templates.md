---
id: decision-5
title: copier-cat owns refactoring shared lessons from subprojects to parent templates
date: 2026-11-15 21:50
status: proposed
---

## Context

Conclusions reached in this repo keep earning a place in the templates that
stamped it, and nothing carries them there. Ten tasks promise upstream
extraction — DOT-57, 208, 209, 210, 242, 307, 322, 326, 360, 361 — and each
promise is prose in a task body that no mechanism collects. DOT-326 built the
discovery half (find shareable practice, classify it, emit a routing list) and
stopped before anything was submitted anywhere.

The question is where that mechanism lives. This repo looks like the obvious
host because it has the deepest agentic use of any project here, so the
candidates and failure modes surface here first. That makes it the right place
to *find* them and the wrong place to *own* the machinery, because every other
stamped project needs the same path upstream and none should import dotfiles
to get it.

Two things are true at once, and an earlier draft of this record kept only the
second. This repo's practice does carry **more weight** than a peer's: it has
the most agentic experience and the most proven conventions of any project
here, so a convention that survived here is better evidence than one proposed
cold. That earns its findings influence, not authority — the receiving
template's scope still decides, per CCC-23.

The general case is wider than this repo all the same, and naming it as "the"
prototype would be too narrow. **Any child repo downstream of a template, or
of copier-cat itself, can become the accidental prototype**: the problem appears
wherever the work happens, and the subproject holds the context that makes it
legible — the failing case, the surrounding code, the reason the template's
assumption did not hold. Sometimes it holds the fix too. That context is
exactly what a parent repo lacks when a finding arrives as a bare description,
and it is why the finding has to travel with its evidence rather than as a
summary of it.

Which end should prototype looked unsettled from here, and copier-cat has
already ruled on it. CCC-23 (maintainer, 2026-11-14) states the principle
directly: useful behaviour begins in the project that needs it, then moves
through recorded lineage, proposing each suitable parent in turn and stopping
when the feature no longer fits that template's scope — explicitly so that no
permanent home must be chosen before the first useful implementation. Its
constraints add the corollaries: do not delay a useful local implementation
waiting for a universal taxonomy, and do not equate inheritance with
ownership. For defects the rule differs — reproduce at successive layers and
fix the earliest layer that exhibits the bug.

That answers the grey area without needing the shared-context hypothesis to
resolve it. Shared context may still be the right mechanism, but it is now a
question about how hoisting is implemented, not about where prototyping
belongs.

copier-cat already claims the role, and more of it is designed than a glance
at the CLI suggests. Verified 2026-11-16 against the repo: `spec.md` § C2
specifies contribute in detail — reuse copier's own update computation as the
diff source rather than forking merge logic, derive ownership from the render,
map rendered paths back to template source by re-rendering with the recorded
answers, never ask the template to cooperate. Its queue carries CCC-21
(contribution candidates must follow the *target's* contributor conventions,
read from the target's own docs), CCC-23 (feature hoisting through the
template inheritance graph) and CCC-19 (lineage tracking), all To Do. The
shipped CLI is `merge`, `mergers`, `adopt`, with contribute described as
"phone home, planned".

So the gap is implementation, not design, and this repo should not re-specify
what C2 and CCC-21/23 already settle.

## Decision

**copier-cat is the subject-matter expert for refactoring shared lessons from
subprojects to their parent templates** (author ruling, 2026-11-15). Design
questions about how a lesson travels upstream are answered there, not
re-answered per repo.

Refined 2026-11-16: that expertise is specifically the **child-parent
relationship** — the lineage from a subproject through the template that
stamped it and its own parents. **pif drives the movement** of a finding to
any target repository; copier-cat answers which parent should receive it.

This repo prototypes *this* instance, not every instance. DOT-326 produces a
working event-driven flow and the evidence from running it, which becomes the
spec for copier-cat's `contribute`. The mechanism graduates upstream rather
than hardening here; what stays behind is configuration and the record of which
submissions this repo made.

The same path is open to any downstream repo that hits a template-shaped
problem. dotfiles is first because it got there first, and the flow is built so
the next accidental prototype uses it rather than reinventing it — a
subproject-shaped finding is the normal case, not an exception to handle.

The trigger is event-driven first: a task reaching Done with a template-bound
note emits a candidate while its evidence is still attached. A cadence sweep
remains as a safety net for what no event emitted.

**What is settled here is the ownership, not the design.** Everything below is
a starting shape to stress-test, and this record is `proposed` for that reason.
A working sketch of three stages — prepare and submit the draft issue or PR;
respond to maintainer feedback and HITL events; migrate once the change merges
and releases — came out of conversation, not research. It may split finer,
collapse, or turn out to be the wrong decomposition entirely; the only part
with evidence behind it is that routing to a list is not a stopping point,
because the stalls happen after it. Treat the stages as a hypothesis the
prototype tests, and let what DOT-326 measures replace them.

The architecture, spec and principles get written from that evidence. Writing
them now would encode a flow nobody has run, which is the same trap that puts
a skill before the procedure it refactors.

## Consequences

- DOT-326 is the prototype and its output is a spec, so it is finished when the
  flow has run end to end and produced one, not when it is polished here.
- The stage decomposition is unproven and must be stress-tested before it
  becomes architecture: research what comparable projects do, run the flow on
  real candidates, and record what the sketch got wrong. A stage count that
  survives contact with ten real submissions is evidence; one that survives
  only conversation is a guess.
- The ten promissory tasks are the first run's input; collecting them is a
  concrete exercise of the flow rather than separate work.
- **Division of labour (author, 2026-11-16): pif drives, copier-cat supplies
  the lineage.** pif owns moving a finding to another repository — preparing
  the submission, publishing it, tracking the response, and queueing the
  migration after a merge — for any target, related or not. copier-cat owns
  what is unique to the child-parent relationship: which parent template
  stamped this project, which parent stamped that one, and therefore which
  template should receive a given lesson. That is the lineage graph CCC-19
  records and CCC-23 walks, and it has no meaning between two unrelated repos.
  The boundary follows from the subject matter: a submission to a stranger
  needs no inheritance graph, and a hoist without one cannot choose a parent.
- Whether pif is a per-repo capability or a central service remains open — the
  roborev-shaped question. The shared-context hypothesis bears on it: a
  mechanism holding both repos' context at once is easier to argue for as a
  service than as a capability each repo carries alone, but that is a reason to
  test the claim, not to assume it. The division above narrows the question
  rather than settling it, since either shape can consume copier-cat's lineage.
- The scale is ten agentic repositories, not one, surveyed 2026-11-16 and
  recorded in `docs/AGENTIC-REPOS.md`: seven live queues, 437 open tasks,
  four of the five template repos agentic themselves. That is the reason pif,
  copier-cat and flagship exist, and it means a per-repo capability has to be
  multiplied by ten while a service is written once — a cost argument the
  design session should price rather than assume.
- DOT-326's scope shrinks accordingly: it prototypes the *trigger and
  candidate capture* in a repo that has candidates, and stops short of
  re-specifying submission mechanics that spec.md § C2 and CCC-21 already
  define.
- A finding travels with its evidence, not as a summary. The subproject's
  context is usually the part that makes a template-shaped problem legible
  upstream, so a submission that drops it is asking the parent to re-derive
  what the child already knew.
- A per-item judgement stands for each candidate: raise the issue alone, or
  carry the fix with it. The ask is cheaper, the fix is more useful, and the
  call travels with the candidate.
- Work that is genuinely dotfiles-specific stays here; this decision governs
  shareable practice only, and the classification step is what separates them.
