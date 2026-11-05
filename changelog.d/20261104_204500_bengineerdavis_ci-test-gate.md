Added a CI job that runs the full suite and judges it by the known-failure
baseline rather than the count. Every other check in this repo was a
pre-commit hook, so a fresh clone — or a bypassed hook — reached `main`
untested.
