# Judge rounds — herdr test program (2026-09-19)

The record of the measured judge loop (method: `dotfiles/docs/JUDGE-SELECTION.md`;
pool locked from the calibration in this directory). Raw outputs are session
artifacts under the tool-output dir; this file is the durable summary.

## Round 1 — mid-round judge: `~deepseek/deepseek-pro-latest`

Dossier: `judge-dossier-r1.md`. **Verdict: ITERATE** — 2 high, 3 medium, 1 low.

| # | Gap | Severity | Resolution |
|---|---|---|---|
| 1 | No automated converge of the Ansible topic | high | ACCEPTED — owned by the repo-queued molecule adoption (TASKS.md § Now); herdr a consumer, recorded in the topic README |
| 2 | Contract module unvalidated vs the real binary | high | RESOLVED — golden-transcript test against a real captured status output (home-redacted fixture) |
| 3 | Static scans don't expand Ansible loops/Jinja | medium | PARTIAL — real `--syntax-check` test added; full expansion stays with molecule. Wiring it exposed a latent double-escaping bug in the original remove.yaml regexes (unexecuted YAML — exactly the judge's point) |
| 4 | changed_when predicates untested | medium | ACCEPTED — settled by the author's idempotence pass, recorded in the topic CHANGELOG |
| 5 | CRUD invariant one-way | medium | RESOLVED — reverse-direction (orphan teardown) test added |
| 6 | Gate-default mutation evidence split | low | RESOLVED — the third test's mutation note now names its true subject |

## Round 2 — fusion panel: opus-4.7 + `~deepseek/deepseek-pro-latest` + local `qwen3.6:35b-mlx`

Dossier: `judge-dossier-r2.md`. **Verdict: SHIP — unanimous (3/3)**, no new
high-severity gaps. Only variance: gap 3 labelled RESOLVED (deepseek) vs
PARTIALLY RESOLVED + ACCEPTED (opus, qwen) — a naming nuance, recorded, not a
substantive disagreement. Local model participated as the free third voice at
the weighted-low tier the calibration assigned it.

## Learnings (what the loop itself taught)

1. **Golden transcripts pay for themselves immediately.** The real-binary
   fixture caught the `letta (experimental)` wire variant the upstream docs
   never showed, on its first run — and wiring the YAML-side grammar exposed
   a latent double-escaping bug the tests could never execute. Measure the
   boundary, don't assume it from docs (spec.md § Evidence, applied to wire
   formats).
2. **A judge that had the key once can be trusted to notice contamination.**
   Fable-5.1 flagged the leaked answer key in calibration run 1 unprompted —
   thoroughness signal; it stayed in the pool as reserve.
3. **Judges converge when gaps have named owners.** Both rounds' ACCEPTED
   items were accepted because they pointed at existing queued work (molecule,
   the author's passes), not because the judges were lenient.
4. **Spend:** one calibration round (6 judges) + one mid round + one panel
   round (3 judges) — within the ≤3-round cap; panel cost dominated by the
   dossier size, not the model tier.
