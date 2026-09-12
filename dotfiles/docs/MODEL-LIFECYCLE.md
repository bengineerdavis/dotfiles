# Model lifecycle

How models get discovered, judged, adopted, and retired here — and what has to
be true before any of those happen.

This exists because the failure mode is not picking a bad model. It is picking
one *confidently*: a release lands, it sounds impressive, it goes into the
manifest, and six months later nobody can say whether it is better than what it
replaced or what "better" meant. Every rule below is aimed at that.

`apps/ollama/defaults/main.yaml` is the manifest this governs. It holds the
roles, tiers, measured numbers, and capability gates; this document says how a
model earns a line in it.

## The one rule

**A quality claim must name the measurement that produced it.**

Not "qwen3.8 is better at code" — *"qwen3.8 scored X on case Y, measured on
this machine, on this date."* Anything unmeasured is a candidate, not a
recommendation, and is marked as such in the manifest.

This is stricter than it sounds. It rules out the model card, the benchmark
table in the announcement, the leaderboard, and my own recall — all of which are
someone else's measurement of someone else's question.

## Four stages

Models move Discover → Triage → Measure → Adopt, and each stage has to be
cheap enough that the previous one can afford to be generous.

```
Discover   automated, scheduled     → candidates
Triage     cheap, mechanical        → shortlist
Measure    expensive, on-machine    → evidence
Adopt      manual, reversible       → manifest change
```

### 1. Discover — scheduled, never accidental

Runs on a timer and produces a *list*, never a decision. Today this happens
when someone happens to read a release note, which is why the manifest tracked
`qwen3.6` while `qwen3.8` had been out a fortnight.

Sources, in order of authority:

| Source | Gives |
|---|---|
| `ollama.com/library?sort=newest` | new local models and families |
| OpenRouter models API | new hosted models, pricing, context, ZDR |
| `ollama list` vs the manifest | drift between declared and installed |

Output is a dated candidate file, machine-local. Discovery **must not** pull
weights, benchmark, or edit the manifest — it is allowed to be wrong, because
nothing downstream trusts it yet.

### 2. Triage — spend nothing to reject most of them

Mechanical filters, in this order. Each is cheap and each rejection is recorded
with its reason, so the same model is not reconsidered from scratch next month.

1. **Does it fit the budget?** Weights plus KV at the declared context, against
   `ollama_ram_reserve_pct`. A model that cannot load is not a candidate,
   however good.
2. **Is it a successor to something we run?** A new version of a family already
   in the manifest earns attention automatically. An unfamiliar name does not.
3. **Does it have a build we can use?** MLX on Apple Silicon, the right quant
   on Linux. No usable build, no candidate.
4. **Will the installed runtime load it?** New model formats routinely need a
   newer engine, and the registry rejects the pull outright — `qwen3.8` returns
   `412: requires a newer version of Ollama` against a 0.32.6 server. Check the
   *server* version, not the client: they drift independently, and a launchd or
   systemd agent keeps running the old binary until it is restarted. A runtime
   upgrade is its own change with its own risk, so it is a prerequisite to
   evaluate, never a step to fold silently into adopting a model.
5. **Is the licence acceptable?** Open weights, redistributable.
6. **Does it claim a capability we lack?** Longer context, vision, tool use.

What triage explicitly does **not** consider: benchmark scores, announcement
claims, or vibes. Those are not filters, they are marketing.

### 3. Measure — on this machine, on the task we care about

The expensive stage, so it runs only on the shortlist, and only for the role the
model is a candidate *for*.

**Measure what the role actually needs.** This is where the current tooling is
weakest and the discipline matters most:

- `bin/model-bench` scores models as **judges**, on calibration against a
  reference scorecard. That is the right measure for the judge pool and the
  wrong one for anything else.
- Nothing here yet measures **generation** quality. So a generation role cannot
  be promoted on bench evidence without importing a number measured on a
  different task — which is why `gpt-oss:20b` and `ministral-3:8b` sit at two
  stars marked provisional rather than being promoted.

Always measured, because they are cheap and objective:

- `gen_tok_s`, `prompt_tok_s`, `load_ms`, resident `gb` — the manifest's
  `ollama_model_perf` fields
- Whether the declared context actually loads within budget
- Capability probes via `ollama show`, never the tag name or model card

**Contention is a correctness issue, not a courtesy.** `ollama ps` before any
run: model memory is global, loading a second large model kills the server, and
it surfaces as a timeout that reads like a model fault. A cold load of an 18 GB
model can exceed a short timeout, and a warmup that times out cascades into
every subsequent run failing.

### 4. Adopt — one line, reversible

A model enters the manifest with:

- Its **exact** `ollama list` tag, case-sensitive. Never a substring, never a
  family name. `glm-4.7-flash:q4_K_M` was in the manifest for weeks while the
  real tag was `q4_k_m`; ollama tolerated it and `llm -m` did not.
- Its measured numbers and the date they were taken.
- A tier (fast / balanced / best / frontier) justified by those numbers.
- **Provisional** status if the evidence is partial, and the provisional marker
  says which measurement is missing.

Adoption is one commit that can be reverted without taking anything else with
it. The previous model stays installed until the new one has run for a while in
its role.

## Retirement

Models leave for stated reasons, and leaving the manifest is separate from
deleting weights:

- **Superseded** — a newer family member measured better in the same role.
- **Unused** — no role points at it, and nothing has for a release cycle.
- **Broken** — its tag no longer resolves, or a capability probe now fails.

Pruning the manifest does not free disk. Weights removed from the manifest are
uninstalled deliberately, because 740 GB became 410 GB only when someone went
looking.

## Cloud models

The same four stages, with different constraints:

- Triage adds **cost** and **ZDR availability**; a model without Zero-Data
  Retention routing is not a candidate for anything non-public.
- Measure adds **price per Mtok**, taken from the provider's own API rather than
  any aggregator. Aggregators have been wrong here by up to 84%.
- Adoption records the price and the date, because prices move and an unpinned
  cost claim cannot be rechecked.
- No hosted GPT or Grok as a default, recommendation, or fallback. They remain
  legitimate benchmark subjects; the line is hosted-vendor dependency, not the
  name. `gpt-oss:20b` is open weights and runs locally, so it is welcome.

## Invariants

Short list, all of them learned the hard way:

- Exact tags, case-sensitive, verified against `ollama list`.
- `ollama ps` before benchmarking.
- Never promote on a measurement taken for a different task.
- Never record a number this machine did not produce.
- Capability from `ollama show`, not from the tag or the card.
- Local first; hosted models are for what local cannot do.

## What is not built yet

Stated plainly so the gaps are not mistaken for decisions:

- **Discovery is manual.** The scheduled job described in stage 1 does not
  exist. `ollama-update-check` watches the Ollama *runtime*, not the catalogue,
  though its timer/service pattern is the obvious shape to copy.
- **Generation quality is unmeasured.** There is no equivalent of `model-bench`
  for the thing most roles actually do.
- **Triage is unautomated**, so budget arithmetic is redone by hand each time.
