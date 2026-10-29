# `redge` bootstrap brief

The decision is recorded (AUTHOR-ANSWERS.md, ROUNDS.md): **Path B — build our own
tool**, named `redge` (binary) / `redge-cli` (package-registry namespace), in a
new repository outside this dotfiles tree. This brief is what the bootstrap
executes; it migrates with the rest of this directory.

## Identity

- **Name:** `redge` (the command) · `redge-cli` (PyPI + crates.io token). The
  binary name never depends on the registry token.
- **Language:** Python first; a Rust port is a stated possibility, which is why
  the name had to clear crates.io too.
- **License:** Apache-2.0 for now; a fair-source flavor is the intended end
  state and is its own later decision (touches the copyright/ASDLC workstream,
  recorded separately).

## Reserve the namespaces first (author action, accounts are yours)

Both tokens are free today and should be reserved before they drift.

**PyPI** — publish a `0.0.1` placeholder named `redge-cli`:

```bash
# in the new repo, once pyproject.toml carries name = "redge-cli"
uv build
uv publish            # authenticates once; then reserves the name on first upload
```

**crates.io** — reserve `redge-cli` with a `0.0.1` crate:

```bash
cargo new redge-cli --lib      # minimal placeholder
cargo login                    # crates.io token (yours)
cargo publish                  # reserves the name on first publish
```

The orchestrator supplies the layout and packaging files, not the credentials.

## Repository layout (first commit set)

```
redge/
├── pyproject.toml          # name = "redge-cli", [project.scripts] redge = "redge.cli:main"
├── src/redge/
│   ├── cli.py              # commands + JSON output contract
│   ├── manifest.py         # catalogue + local overlay + groups + pins
│   ├── registry.py         # Registry seam; GitHub first
│   ├── sync.py             # update / upgrade / lock / status (R4/R5)
│   ├── state.py            # R6 store (XDG_STATE_HOME, URL-free)
│   └── normalize.py        # R7 pure remote normalizer
├── tests/                  # mutation-proven per spec.md § Verification
├── role/                   # the Ansible role (install + trigger); graduates later
├── docs/                   # SPEC.md, PRIOR-ART.md, REDGE-ARCHITECTURE.md (migrated here)
├── README.md  LICENSE  CHANGELOG.md
└── .github/workflows/ci.yaml
```

The `docs/research/repo-manager/` directory here migrates wholesale into `docs/`
of the new repository (the docs already cite paths relatively).

## Sequencing (inert → behaviour → activating)

1. Repo + license + README + pyproject (inert).
2. `normalize.py` + property tests (pure, testable first).
3. `manifest.py` + `state.py` (the state contract before any sync).
4. `registry.py` (discovery, R3 discipline) — a GitHub-listing library.
5. `sync.py` (R4/R5) last, so the activating side is proven against tests.
6. `role/` for Ansible install/trigger, then CI.

## Verification bar (carried from this thread)

- A dirty repo is fetched and skipped; a clean one fast-forwards; a failed fetch
  cannot read "up to date" (mutation-proven, `Mutation:` / `Failing-test:`
  trailers).
- The normalizer is property-tested (SSH vs HTTPS, trailing `.git`, alias).
- The state store is URL-free and never advances on failure.
- `redge update` never mutates; `redge upgrade` performs only `git merge --ff-only`.

## Deferred, not forgotten

- The high-level task-runner/orchestrator layer (a later consumer of `redge`'s
  groups).
- The formal threat model.
- The fair-source license decision (with the ASDLC/copyright workstream).
- The five dotfiles-repo cleanup items (ROADMAP.md) — those live with the
  `topical`/provisioning track, not in `redge` itself.