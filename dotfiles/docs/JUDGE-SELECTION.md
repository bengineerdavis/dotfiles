# JUDGE-SELECTION — measuring which models judge agent work

This file records the rules and the measured results for choosing judge models
when an agent-built artifact (a topic, a test suite) is reviewed by a panel
rather than by its author. Settled 2026-09-19 with the author, motivated by the
herdr test program (see `dotfiles/docs/TOPIC-RECIPES.md` § test-first recipe).
It feeds the queued panel-of-judges measurement item in TASKS.md § Planned.

## The rules (locked by the author 2026-09-19)

1. **A judge never shares a model family with the implementer.** The code
   under review must not be graded by the model that made it. A family that
   wrote the code is excluded from the judge pool unless there is very strong
   *measured* evidence to the contrary — the burden is on the evidence, not on
   preference. For the herdr program the implementer ran on
   `openrouter/z-ai/glm-5.3-flash`, so all z-ai/glm ids are excluded from
   judging.
2. **No hosted GPT or Grok as a default, recommendation, or fallback.**
   Legitimate as **benchmark subjects** only (bin/model-bench); the line is
   hosted-vendor dependency, not the name. They may appear in calibration
   results as measured rows, never as the picked judge.
3. **Quality is measured by calibration, never asserted.** A small
   injected-defect set is derived from the artifact's contract: known-good
   content plus deliberately broken copies (guard inverted, guard removed,
   unknown turned into a claim, an assertion that cannot fail). A judge scores
   catch-rate and false-positive rate against that set. `bin/model-bench`
   scores judges on calibration the same way — magnitude-rewarding generosity
   is the failure it exists to catch.
4. **Local Ollama first for cheap passes**, exact `ollama list` tags only
   (never match by substring); OpenRouter for hosted candidates. Check
   `ollama ps` before any local run — model memory is global.
5. **Panel shape: single judge for mid-rounds, fusion panel for final
   sign-off.** Mid-rounds are cheap and directional; the final round gets 2–3
   calibrated models plus optionally a local one, majority verdict with
   **dissent recorded** — disagreement is the signal the panel-of-judges
   research item wants measured, not noise to average away.
6. **Rounds are capped** (≤3 OpenRouter rounds for the herdr program) and the
   convergence criterion is explicit: two consecutive rounds with no new
   high-severity gaps.
7. **The judge-pool config is the author's hand.** `~/.binned/config.toml`
   holds the live judge pool and is agent-unreadable by permission rule; this
   file delivers the dated recommendation and the author applies it.

## Calibration method

1. Derive the defect set from the topic contract before the suite exists
   (defects: an unconditional guard, a never-firing guard, "unknown becomes a
   claim", a test that greps empty output, a teardown missing an entry).
2. Ask each candidate judge to review the same compact dossier: the test
   files' intent, the run output, and the coverage map.
3. Score: catches / true defects (catch-rate), and flags raised on
   known-good content (false-positive rate). A judge that catches everything
   but flags everything is unusable; so is the opposite.
4. Record per-model rows with date, model id, and the defect set version.

## Results

*(pending — filled by the calibration run, 2026-09-19; candidates:
`openrouter/anthropic/claude-opus-4.7`, `openrouter/anthropic/claude-fable-5.1`,
`openrouter/google/gemini-pro-latest`, `openrouter/deepseek/deepseek-pro-latest`,
`openrouter/moonshotai/kimi-latest`, local `qwen3.6:35b-mlx`,
`gemma4:31b-mlx`; GPT/Grok rows measured as subjects only.)*

## Recommendation

*(pending — same run; updates land here with a date, and the author applies
any pool change to `~/.binned/config.toml` by hand.)*

## See also

- `dotfiles/docs/TOPIC-RECIPES.md` — the process this methodology sits inside
- `TASKS.md` § Planned — panel-of-judges measurement item this file feeds
- `bin/model-bench` — the calibration scorer this method reuses
