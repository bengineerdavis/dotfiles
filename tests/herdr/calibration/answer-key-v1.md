# Answer key — defect set v1 (NOT sent to judges)

Kept beside the dossier so a re-calibration scores against the same version.
The dossier sent to judges is `defect-set-v1.md` alone: contract + excerpts,
no ground truth (v1's first run leaked the key into the prompt and one judge —
fable-5.1 — noticed it; the key was also internally inconsistent about E).

| Item | Verdict | Why | Severity |
|---|---|---|---|
| A | SOUND | Proceeds direction asserted; companion proves the decline direction (rc=1 → SKIPPED, exit 0). Both directions covered | — |
| B | DEFECT | Decline-only: a guard hardwired to skip everything passes it. House rule: a mechanism that can decline is proven to relent BOTH ways | medium |
| C | DEFECT | Uninstalls every catalogue-claimed id — no intersection with actually-installed, no `herdr_remove_integrations` gate. Would uninstall integrations the topic does not own | high |
| D | SOUND | Teardown ordering asserted with a mutation companion proving the reverse fails — falsifiable both ways | — |
| E | DEFECT | The oracle is a line-for-line copy of `resolve_slice`: the property recomputes the function under test, proving code equals itself (spec.md § Verification). `st.just` on the ignored list also fixes a should-be-generated input | high |
| F | DEFECT | Parse failure silently becomes "nothing installed", exit 0 — unknown becomes a claim; the failure class the house doctrine singles out | high |

Score: catches / 4 defects = catch-rate; flags on A/D = 2 false-positive
opportunities. Run 1 was contaminated (key in prompt) and is discarded for all
judges; run 2 is the scored one.
