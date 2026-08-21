# Goals

What this system is for, and the one test that decides what may live in it.

This document is deliberately employer-agnostic. It should read the same on the
first day of a job and the last, and require no edit in between.

## Purpose

Keep the knowledge and lessons — including good skills and the automation that
makes them better — across every context the author works in.

The failure this guards against is not losing files. It is *re-deriving the same
understanding from scratch* because the last version of it was entangled with an
employer, a machine, or a tool that went away. Capability should be portable by
construction, not by an act of remembering to extract it.

Three consequences follow, and they are the whole design:

1. **The lesson is the artifact.** A skill, a convention, a checklist, a script
   — the durable output is the generalisation, not the case that produced it.
2. **Portability is not a migration step.** If carrying the work forward
   requires a scrubbing project at the end, it will not happen. The boundary is
   enforced continuously, at the point material enters.
3. **Automation over discipline.** Rules that depend on the author correctly
   remembering them at 2 a.m. are not controls. Where a rule can be checked by a
   tool, it must be.

## The provenance test

The question is **where a thing came from**, not whether anyone could tell.

> May this be retained?
> **Yes** if it was *synthesised* — written from general understanding the
> author holds independently of any particular employer material.
> **No** if it was *derived* — produced by reading, transforming, summarising,
> or abstracting employer material, regardless of how little of the original
> survives.

De-identification does not convert a derived artifact into a synthesised one.
Scrubbing changes how *recognisable* something is; it does not change where it
came from. A perfectly anonymised summary of a confidential document is still a
summary of that document.

This is a stricter test than "could someone identify the source?", and it is
chosen deliberately, because the looser test cannot be applied honestly by the
person who most wants the answer to be yes.

### What it looks like in practice

| Situation | Verdict | Why |
|---|---|---|
| "Retries need jitter or they synchronise" — learned at work, written from memory | **Retain** | Synthesised. A general fact about distributed systems. |
| A runbook rewritten from an internal one, names removed | **Do not retain** | Derived. Provenance is the internal document. |
| A prompt that worked well, rewritten generically from scratch | **Retain** | Synthesised, if genuinely rewritten and not transformed. |
| An eval case built from a real ticket, entities replaced | **Do not retain** | Derived. Replacement is scrubbing, not synthesis. |
| An eval case written to exercise the *same class* of problem | **Retain** | Synthesised. The problem class is general knowledge. |

The last two rows are the whole distinction. They can produce near-identical
files and still land on opposite sides, because the test is about the path
taken, not the destination reached.

### Applying it honestly

The test is only useful if it can return "no". Two habits keep it honest:

- **Ask before creating, not after.** Provenance is knowable at the moment of
  authorship and becomes a guess soon after. A file whose origin is already
  unclear is answered "derived" by default.
- **Prefer writing from memory over editing a source.** If the general lesson
  cannot be reconstructed without the original in front of you, that is
  evidence it was not yet general knowledge.

## Retain / do not retain

**Retain** — generalisations, portable by construction:

- Skills, specs, and prompts that describe a capability
- Conventions and the reasoning behind them
- Tooling, configuration, and automation
- Measured facts about public tools — benchmarks, prices, defaults, versions
- Lessons stated as general claims, with the reasoning that supports them

**Do not retain** — regardless of transformation applied:

- Employer or customer data, in any form
- Anything derived from either, including summaries and abstractions
- Internal identifiers: names, handles, ticket ids, URLs, hostnames, codenames
- Configuration containing employer-specific endpoints or credentials

**Machine-local only** — real but not portable:

- Operational logs, traces, and telemetry containing prompt or response bodies
- The machine's own reading of its employer's policy
- Anything awaiting a retention decision

## How the rules are enforced

Three layers, resolved in order. The first that speaks, wins.

```
ethics   →  company   →  personal
```

- **`ethics`** — versioned, portable. Commitments that hold regardless of
  employer or policy. Never relaxed by a lower layer.
- **`company`** — machine-local, unversioned, one per machine. An operational
  paraphrase of the governing policy, never a copy of it. Restrictions only:
  no field in it authorises anything.
- **`personal`** — versioned, portable. The author's own preferences, applying
  only where neither layer above has spoken.

**Fail closed.** A missing, unparseable, or silent rule denies. This makes the
absence of configuration safe, which is what allows the same tooling to run on a
machine that has no company layer at all.

**The company layer is regenerated, not migrated.** It is written per machine
against whatever policy currently governs it, and it is the only layer that
changes when the employer does. That is what makes the rest of this repeatable:
a new job means writing one new file, not auditing everything else.

## What this is not

- **Not legal advice, and not a compliance artifact.** It is an operating
  discipline. Where it and a governing policy disagree, the policy wins.
- **Not a claim about what is permitted.** Nothing here grants permission. The
  layers can only restrict.
- **Not a product.** This is personal infrastructure for working well. It is not
  offered as a service and produces nothing for sale.
