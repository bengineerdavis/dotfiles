# Model eval cases

Cases the `ollama-evals` harness runs **against candidate models**, to answer
"is this model fit for this role?".

```sh
ollama-evals cases                          # what exists, and uncovered cells
ollama-evals run qwen3.8:27b-mlx            # all cases, one local model
ollama-evals run a b --role chat            # one row of the matrix
ollama-evals run a --property faithfulness  # one column
ollama-evals run openrouter/z-ai/glm-5.2    # a remote candidate (billed, prompts first)
ollama-evals run a --repeat 5               # n samples, to expose flaky passes
ollama-evals show --diff a.json b.json      # two saved runs
```

Local ollama tags and remote `openrouter/…` tags go through one interface, since
the fitness question is the same for both — and the manifest prices nine remote
models under a standing "Unevaluated on quality" note. Runs are saved to
`~/.local/share/ollama-evals/`.

Not to be confused with the skillet eval cases in
`ai-prompt-library/skills/model-fitness/evals/`, which test whether an *agent*
judges models correctly. Same word, different artifact: those check the
judgement, these produce the evidence it judges.

## Shape

    role:      which role this measures. Never combined across roles.
    property:  what it measures. One per case.
    prompt:    sent verbatim to the candidate.
    context:   optional text the answer must be grounded in.
    check:     python expression over `response`. Mechanical wherever possible.
    num_ctx:   optional per-case context window. A long-role case run at the
               CLI default measures truncation, not the model.
    filler:    optional {words, needle_at} — the harness synthesises a haystack
               of that many words from a fixed vocabulary and seed, and places
               `context` at that fraction through it.
    image:     optional {size, background, shapes} — rendered to a PNG by the
               harness and sent with the prompt. `shapes` are circles
               ({center, r}) and rects ({at, size}), each with a colour.
    vars:      optional names injected into the check's namespace, so a swept
               level can rebind what "correct" means.
    sweep:     optional difficulty ladder — see below.

`check` is deliberately a plain expression rather than a model call. Judged
scoring is a last resort, and no case here needs it yet — a requested shape can
be parsed, and a fact absent from the context can be searched for.

**A guard that fails closed looks identical to one that never runs.** Both
refuse. The only test that separates them is making the policy say *yes* and
checking that behaviour changes. `ask-research` shipped for one commit with its
policy helper defined after the call site: bash said "command not found",
returned 127, the guard refused, and every hand-test passed — while the resolver
was never consulted. See `tests/policy/test_policy_callers.py`, which asserts
both directions for exactly this reason. The same trap applies to the sweep
early-exit, the whitespace retry and the capability gate here: each has a
"declines to run" path that must be shown to relent.

**A check is code, so a check can be wrong — and a wrong check indicts the
model.** Treat the first FAIL from a new case as suspect until you have read the
response that produced it. `think-faithfulness` originally failed a completely
correct `deepseek-r1:32b` answer because its regex matched the model quoting a
premise back ("Ben paid more than 10 euros"). Before trusting a new check, run
it against both a crafted right answer and a crafted wrong one — and once real
output has broken it, keep that output as a test case.

`filler` and `image` are **generated, never checked in**. A haystack and a PNG
stop being reviewable the moment they become bytes in git; as a spec they stay
diffable, and the fixed seed makes them identical on every host. It also keeps
the provenance rule below trivially true — there is no material to launder.

## Sweeps

A pass/fail case answers "does this model clear the floor". Once every candidate
clears every floor — which is what happened here — the floors stop being a
comparison instrument. A sweep restores one: run the case at rising difficulty
and report **where each model breaks**. A break-point orders models that a floor
ties.

```sh
ollama-evals run a b --sweep      # climb the levels; report the break-point
ollama-evals run a b              # unchanged: base level only, same cost as before
```

Sweeps are opt-in. Without `--sweep` a case runs at its base parameters, so the
cheap floor check stays cheap and a sweep is always a deliberate spend.

Two forms:

    sweep: {param: "filler.words", values: [...], labels: [...]}   vary one path
    sweep: {levels: [{label: .., <case overrides>}, ...]}          vary anything

Use `levels` whenever difficulty changes more than one thing at once — a bigger
haystack also needs a bigger `num_ctx`, or it measures truncation rather than
recall, and a bigger `image` also needs a new expected count.

`ordered: true` (the default) declares difficulty monotonic, so the climb stops
at the first failure. **Set it false for axes that are not monotonic** — needle
*position* is the standing example, since middle positions are harder than late
ones ("lost in the middle"), and early-exit would misreport such a profile as a
clean break-point.

Current ladders: `long-faithfulness` 4k → 16k → 48k tokens (the top rung sits
just under the largest real prompt this host has logged — regenerate that
figure locally with `ollama-usage ctx`);
`vision-faithfulness` 3 → 6 → 10 circles; `think-correctness` 2 → 4 → 6 → 8
dependent reasoning steps.

### First sweep: every ladder topped out (2026-08-31)

| role | models | result |
|---|---|---|
| think | `gpt-oss:20b`, `glm-4.7-flash:q4_k_m`, `deepseek-r1:32b` | all `≥8-step` |
| vision | `qwen3.8:27b-mlx`, `qwen3.6:27b-mlx` | all `≥10` circles |
| long | `qwen3.8:27b-mlx`, `qwen3.6:27b-mlx` | all `≥48k` tokens |

**No model broke at any rung.** The mechanism is sound — the score denominators
(6/6, 4/4) confirm every level was climbed rather than skipped — but the ladders
are calibrated too low to separate current models. They are floors again, just
taller ones. Raising the top rungs (think to 12–16 steps, vision to 20+ circles,
long to 100k+) is the next move; each is a one-line edit to a `levels` block.

The `think` result is nonetheless decision-relevant. `think/best`
(`deepseek-r1:32b`, 5.2 tok/s) matched `think/fast` (`gpt-oss:20b`, 66.2 tok/s)
on **correctness through 8 dependent reasoning steps**, plus both quality floors.
A ladder cannot prove the slower model is not better — but after three
properties and a four-rung correctness ladder, no evidence produced here
supports paying 12.7x for it.

## Coverage — what real work has no test

`ollama-evals coverage` classifies the local `llm` log against the closed
taxonomy in `taxonomy.yaml` and prints **counts only**. Content is read,
classified and discarded in-process; nothing derived from it is written or
printed beyond per-category counts. See taxonomy.yaml's header for why the
category vocabulary must stay closed and hand-authored.

```sh
ollama-evals coverage                # counts per task type + the gap list
ollama-evals coverage --by-model     # cross-tab model against task type
```

**Classification method — a negative result worth keeping.** Embedding the
category descriptions and taking cosine to each prompt DOES NOT WORK here
(measured 2026-09-09):

- Raw cosine: every description is "do a technical thing with text", so a shared
  direction dominates and **97% of assignments beat the runner-up by <0.05** —
  coin flips wearing a table.
- Centroid removal fixes the margins but makes `vision-describe` an attractor
  that swallows most of the corpus, **including prompts sent to a text-only
  model with no vision capability at all**. That impossibility is what
  exposed it, and it is why `--by-model` exists.

The default is a small local instruct model choosing from the closed list.
Screened on 8 hand-labelled probes: `granite4.1:8b` **8/8**, `ministral-3:3b`
6/8, `granite4.1:3b` 3/5. **Do not shrink it for speed.** The embedding path
remains behind `--method embed` as a reproducible negative result.

Sanity-check any run with `--by-model` before believing it: each model's
dominant category should match what that model is for. If a text-only model is
being assigned vision work, the classifier is broken, not your logs.

## Capability gating

A case may declare `requires: [vision]`, and one carrying an `image` is inferred
to need vision. Before running, the harness reads the model's capabilities from
`/api/show` and reports inapplicable cases as `n/a (no vision)` rather than
running them.

This matters because a text-only model handed a vision case returns HTTP 400,
which the table used to show as an ERROR — indistinguishable from a broken
harness or a dead server. `gpt-oss:20b` collected three of those for lacking a
modality nobody claimed it had. `ollama-role` has always gated on capabilities
(`requires:` checked against `ollama show`, not against the tag name); the eval
harness now does too.

Remote `openrouter/…` models report no capabilities, so they are never skipped —
assumed capable and allowed to fail honestly.

## Formatting can decide the verdict

Measured 2026-09-10, and it is the most surprising thing this suite has found.
On `support-contradiction`, **one blank line at the context/prompt seam** flips
`glm-4.7-flash:q4_k_m` between looping to the token cap 5/5 with an empty reply
and answering correctly 3/3 in ~700-1100 tokens. Deterministic in both
directions; every other byte identical.

`gemma4:12b-mlx` shows the same sensitivity **in the opposite direction** on the
same case — it answers with one blank line and loops with two.

So there is no "safe" spacing to normalise to: any choice disadvantages one
model or the other. The harness therefore does NOT normalise. Instead, on a cap
hit it retries once with the seam nudged, and marks the cell `*` if the model
then converges — reporting *brittle about formatting* separately from *cannot do
the task*. Disable with `--no-ws-retry`.

Three failure modes that the results table used to render identically:

| mode | signature | seen in |
|---|---|---|
| whitespace-triggered | deterministic, flips on one character | `glm-4.7-flash` |
| cap-borderline | non-deterministic run to run at fixed spacing | `gemma4:12b-mlx` |
| real capability limit | fails regardless of either | — |

**Read every score as "at cap 8192".** `gemma4` cleared this case once in 3,503
tokens and exceeded 8,192 on identical input another time; a different cap would
give it a different score. That is a property of the measurement, not the model.

## Provenance

Every case is **synthesised** — written from general understanding of a problem
class. None is derived from real work material, and none may be: scrubbing a
real transcript changes what is recognisable, not where the case came from.
See `docs/GOALS.md` and the model-fitness skill.

When live use exposes an uncovered class, write a new case describing the class
from understanding. Do not import the material that revealed it.

## Coverage

Now **6 roles x 3 properties, partially filled** — chat, code, think, long,
vision and support, against instruction adherence, faithfulness and correctness.
It started at 2x2 (chat and code) and grew only where a decision needed it:
`correctness` exists because the `think/best` tier could not be justified
without it, and `support` because the coverage report showed a large share of
real traffic in a task type with no test at all. Run `ollama-evals coverage` for
the figures on this host; they are deliberately not committed. `embed` remains an uncovered gap — no pending
candidate, and its output is a vector, so neither property applies as written.
`audio` is out of scope: no local model can do it.

Note `support` is a TASK CLASS, not a routing role — `ollama_roles` has no
`support` entry. Results there inform whichever role serves support traffic;
they do not license a promotion in a role that does not exist.

### Faithfulness has two shapes, on purpose

A suite where every faithfulness case is answered by refusing rewards a model
that never answers anything. Measured: against the original 2x2, a null "model"
that ignores its input and always emits `"NOT STATED. NOT HANDLED."` scored
**2/2 — 100% of the faithfulness column.**

So the column is deliberately split:

- **refusal-shaped** (`chat`, `code`, `think`) — the fact is absent, and the
  model must decline rather than invent one.
- **answer-shaped** (`long`, `vision`) — the fact *is* present, and hedging
  fails. Exact-match recall of a needle, and a count only a model that looked
  can get right.

The same null refuser now scores **3/5** on that column and 3/10 overall. Keep
the shapes balanced when adding cases, or the metric drifts back toward
rewarding silence.

**These cases are floors, not a ranking.** Measured 2026-08-29, `ollama-evals`
at `--repeat 1`, temperature 0, per-case `num_ctx` as declared, both models MLX
on an idle M4 Max:

| | 2x2 (chat, code) | 5x2 (+ think, long, vision) |
|---|---|---|
| `qwen3.8:27b-mlx` | 4/4 | **10/10** |
| `qwen3.6:27b-mlx` | 4/4 | **10/10** |

Widening the matrix from 4 cells to 10 did **not** separate them — it produced
the same tie with more cells. That is the expected behaviour of a pass/fail
floor and worth stating plainly: *breadth does not discriminate, difficulty
does.* The 5x2 still earns its place, because each new row answers a fitness
question for a role that carries its own decisions; it just does not answer
"which of these two is better at chat".

Then every declared tier of the two heaviest-used roles was measured
(2026-08-30, same conditions), each model against **only** the role it is a
candidate for:

| role | tier | model | tok/s | score |
|---|---|---|---|---|
| think | fast | `gpt-oss:20b` | 66.2 | 2/2 |
| think | balanced | `glm-4.7-flash:q4_k_m` | 58.1 | 2/2 |
| think | best | `deepseek-r1:32b` | **5.2** | 2/2 |
| code | fast | `gemma4:12b-mlx` | 47.8 | 2/2 |
| code | balanced | `devstral-small-2:24b` | 23.0 | 2/2 |
| code | best | `qwen3.6:27b-coding-nvfp4` | 18.8 | 2/2 |

**Eight distinct models, every applicable cell, no failures.** The floors are
exhausted as a comparison instrument. Note especially `think`: the `best` tier
costs 12.7x the generation rate of `fast` and shows no measured advantage over
it here. That does not mean it has none — a floor cannot rank — but it does mean
the tier ordering currently rests on no evidence this harness has produced.

Separating models that all clear the floor needs a difficulty gradient —
sweeping a case parameter (haystack size, needle position, shape count,
reasoning depth) until each model breaks, and comparing break-points rather than
pass/fail. That is a change of method, not of coverage.

Separating two models that both clear the floor needs a difficulty gradient —
sweeping a case parameter (haystack size, needle position, shape count,
reasoning depth) until each model breaks, and comparing break-points rather than
pass/fail. That is a change of method, not of coverage.
