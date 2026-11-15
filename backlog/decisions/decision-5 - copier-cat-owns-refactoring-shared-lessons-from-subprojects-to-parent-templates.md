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

The question is where that mechanism lives. This repo is the obvious host by
accident of history: it has the deepest agentic use of any project here, so it
is where the candidates and the failure modes appear first. That makes it the
right place to *find* them and the wrong place to *own* the machinery, because
every other stamped project needs the same path upstream and none of them
should import dotfiles to get it.

copier-cat already claims the role. Its README describes pushing "project
fixes back upstream as reviewable PRs through `contribute`", and verified
2026-11-15 its CLI ships `merge`, `mergers` and `adopt` while describing
contribute as "phone home, planned". The concept is owned there and unbuilt,
which is precisely the gap this work fills.

## Decision

**copier-cat is the subject-matter expert for refactoring shared lessons from
subprojects to their parent templates** (author ruling, 2026-11-15). Design
questions about how a lesson travels upstream — what gets submitted, how
submissions are tracked, how an adopted change migrates back — are answered
there, not re-answered per repo.

This repo prototypes. DOT-326 produces a working event-driven flow and the
evidence from running it, which becomes the spec for copier-cat's `contribute`.
The mechanism graduates upstream rather than hardening here; what stays behind
is configuration and the record of which submissions this repo made.

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
- Whether push-it-forward is a per-repo capability or a central service — the
  roborev-shaped question — is open and belongs to copier-cat's design, with
  the answer recorded there.
- A per-item judgement stands for each candidate: raise the issue alone, or
  carry the fix with it. The ask is cheaper, the fix is more useful, and the
  call travels with the candidate.
- Work that is genuinely dotfiles-specific stays here; this decision governs
  shareable practice only, and the classification step is what separates them.
