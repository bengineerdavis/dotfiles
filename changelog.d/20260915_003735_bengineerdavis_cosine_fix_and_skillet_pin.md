**Fixed**

- `cosine()` in `apps/ollama/files/executable_ollama-evals` returned values
  above 1.0 when a norm's square underflowed to subnormal — floating point
  no longer honoured Cauchy-Schwarz there. It now returns 0.0 for norms
  that small, and hypothesis's shrunk counterexample is pinned as its own
  example test beside the property. Found by the 2026-09-11 suite run,
  untracked for three days, fixed and mutation-proven on 2026-09-14
  (6c3079b).

**Changed**

- The `npm:@sentry/skillet` pin moves 1.7.0 → 1.8.0 with verification
  recorded (`skillet validate .` exits 0; the dependency trouble behind the
  earlier rollback did not reproduce). Dropping the pin to `latest` stays
  gated on the upgrade.yaml pin-print, the npx aliases, and the spec.md /
  REFERENCES.md alignment (ee09e38).
