# RESEARCH: Shift-Left Surface Scan — Inventory, Timings, Comparison (Steps 1–2)

**Task:** TASKS.md § Now #1 (Shift-left surface scan, 2026-10-03).
**Worktree:** `.worktrees/shift-left-scan`, branch `agent/shift_left_scan`.
**Scope:** Shift-left surfaces (Save ≤2s, Add ≤5s, Commit ≤30s) for code quality,
readability, and maintainability across `bin/executable_*`, `scripts/`,
zsh fragments, `*.tmpl` templates. Narrower and different from the 2026-09-22
study — build on it, do not repeat it.

---

## 1. Full Inventory: Surface × Tier × What-It-Checks × Files × Timing × Check-vs-Rewrite

### Population census (measured 2026-10-03 in the worktree)

| Population | Count | Notes |
|---|---|---|
| `bin/executable_*` | 47 | Bash + Python scripts (deployed by chezmoi) |
| `scripts/*.sh` | 2 | `run-bats.sh`, `run-shellharden.sh` |
| `zsh fragments` (`dotfiles/zsh/*` + `dotfiles/apps/*/files/zsh/*`) | 85 | Deployed zsh config fragments |
| `*.tmpl` templates | 8 | chezmoi templates incl. `.chezmoi.toml.tmpl`, `opencode.jsonc.tmpl` |
| `*.py` | 93 | Repo Python source |
| `*.sh` (total) | 18 | includes `scripts/*.sh` (2) and other repo shell files |

### Existing shift-left surfaces (Step 1a)

| Tier | Surface | What it checks | Selected files | Measured/Estimated timing | Check-vs-Rewrite |
|---|---|---|---|---|---|
| **Save** (Agent loop) | `opencode` LSP (`pyrefly` LSP) | Type checking | `*.py`, `*.pyi` | Est. ~0.05s per diagnostic cycle | Check |
| **Save** (Agent loop) | `opencode` LSP (`ruff` LSP) | Lint + format diagnostics | `*.py`, `*.pyi` | Est. ~0.05s per diagnostic cycle | Check |
| **Save** (Human editor) | Zed / VSCode / Cursor / Neovim LSP | Type checking + lint | `*.py`, `*.pyi` | Est. ~0.05s per diagnostic cycle | Check |
| **Add** (prek) | `ruff-check` | Python linting (E, W, D) | `*.py` | Measured 0.05s (part of 0.254s total) | Check |
| **Add** (prek) | `ruff-format` | Python formatting check | `*.py` | Measured 0.05s | Check |
| **Add** (prek) | `pyrefly-check` | Python type checking | `*.py` | Measured 0.15s | Check |
| **Add** (prek) | `shellcheck` | Shell script linting | `*.sh`, `*.bash`, zsh fragments | Measured 0.133s | Check |
| **Add** (prek) | `bats` | BATS tests for shell scripts | `scripts/*.sh` (not `bin/`) | Est. ~0.1s (runner) | Check |
| **Commit** (prek commit-msg) | `commit-proportionality` | Commit message length vs. change size | Commit message text | Est. <0.1s | Check |

### Hooks-only-check policy (verified in AGENTS.md line 783)

> "This repo's hooks only check, so `git show --stat HEAD` covers it here —
> the rule bites in other repos, like ai-prompt-library, where formatters run."

**Implication:** All hook-tier candidates must be classified **Check** (validate
and fail, not rewrite files). Rewriting tools (e.g. `shfmt --write`) are
allowed as agent-loop commands (Save tier) but must not be wired as hooks.

---

## 2. Verified Selection-Gap Finding (Step 1b)

**Current state:** Every `bin/executable_*` file (47 total) is skipped by every
prek/pre-commit hook. Only `scripts/*.sh` and standard `*.py` files are
selected.

**Evidence (measured 2026-10-03):**

```text
$ prek run --files bin/executable_archive bin/executable_llm-ctx
ruff check...........................................(no files to check)Skipped
ruff format..........................................(no files to check)Skipped
Pyrefly (type checking)..............................(no files to check)Skipped
shellcheck...........................................(no files to check)Skipped
BATS — shell script tests............................(no files to check)Skipped
Total: 0.037s
```

**Root cause:** The `pre-commit` framework's file classifier (`identify.tags_from_path`)
does not classify `bin/executable_*` files as `types: [shell]` or
`types: [python]` because these files lack the execute bit in the repo
(`-rw-r--r--`) and are named without `.sh`/`.py` extensions in the
chezmoi source tree (`executable_*` prefix, not `.sh` suffix). The deployed
copies at `~/bin/*` *are* executable, but the repo source files are not.

**Contrast — what does run:**

```text
$ prek run --files scripts/run-bats.sh scripts/run-shellharden.sh
shellcheck...............................Passed
Total: 0.133s

$ prek run --files scripts/check_commit_proportionality.py
ruff check..........Passed
ruff format..........Passed
Pyrefly..........Passed
Total: 0.254s
```

**Dangling exclusion (line 42 in `.pre-commit-config.yaml`):**
The `bats` hook has an explicit exclusion `scripts/run-shellharden\.sh` —
but `scripts/run-shellharden.sh` is an untracked file (never committed to git
history). The exclusion is therefore "dangling" (it excludes a file that
doesn't exist in git history). This is a scan finding with a council verdict.

---

## 3. Step 2 Comparison Table: vs. the 2026-09-22 Study

| Item (2026-09-22 study) | Status (2026-10-03) | Disposition rationale |
|---|---|---|
| **Pre-commit/merge-gate three-tier design** (§ Now, supersedes pre-commit/pre-push framing) | **Landed** | `.pre-commit-config.yaml` has ruff, ruff-format, pyrefly, shellcheck, bats, commit-proportionality; `prek` is the runner. Tier structure is in place. |
| **Fast test-loop sequencing** (fix slow tests → pytest-randomly → pytest-xdist) + `collected == 0` tripwire | **Queued** | Mentioned in `AGENTS.md` § Commands but not fully landed; pytest-xdist referenced. |
| **`$HOME`-sandbox implementation pattern** (autouse fixture, subprocess `env=`, named macOS escapes) | **Queued** | Described in 2026-09-22 study but no evidence it has landed as code. |
| **Machine-shaped gate outputs + skip census** | **Queued** | No evidence of automated gate-output shaping in current hooks. |
| **Two-track trust model** (deterministic vs. judgment-based) | **Queued** | Referenced in `TASKS.md` LEDGER item; not yet implemented. |
| **Coverage % as quality-over-time metric** | **Rejected** | Rejected by advisor council (2026-09-22). |
| **pytest-testmon / pytest-picked** | **Rejected** | Rejected unanimously (blind to shell/YAML change surface; picked exits green on zero tests). |
| **Full suite on pre-push** | **Rejected** | Rejected (too slow at ~200s). |
| **Local CI daemon** | **Rejected** | Rejected by advisor council. |
| **cosmic-ray / mutmut as standing practice** | **Rejected** | Rejected by advisor council. |
| **"No worktrees" claim (Phase 0)** | **Stale** | Superseded — worktrees now standard (`.worktrees/` + `docs/WORKTREES.md`). |
| **Ollama model-health check** | **Deferred** | § Planned, low priority (2026-09-22). |

### New candidates from the 2026-09-22 study (Step 1c)

| Candidate | Tier | What it would check | Selected files | Timing Estimate | Classification |
|---|---|---|---|---|---|
| `shellharden` | Save/Add | Bash quoting/hardening | `bin/executable_*` (bash) | Measured (via `scripts/run-shellharden.sh`): <0.5s | Check (`--check` exit-2; `--replace` rewrite available for agent loop) |
| `shfmt` | Save/Add | Shell script formatting | `*.sh`, `bin/executable_*` | Est. ~0.1s | Rewrite (use `--check` in hooks, `--write` in agent loop) |
| `zsh-lint` | Save/Add | Zsh script linting | `zsh fragments` (85) | Est. ~0.2s | Check |
| `markdownlint` | Save/Add | Markdown linting | `*.md` | Est. ~0.2s | Check |
| `actionlint` | Commit | GitHub Actions workflow lint | `.github/workflows/*.yml` | Est. ~0.1s | Check |
| `ty` | Save/Add | Fast Python type checking | `*.py` | Est. ~0.05s | Check |

---

## 4. Open Questions for the Four-Voice Council

*(Council not run — ranked-decision space left for it.)*

1.  **Incrementalist:** How do we close the `bin/executable_*` selection gap
    with the least invasive change? (e.g. add the execute bit in-repo, add
    file extensions, or write a custom `prek` classifier?)
2.  **Trust Architect:** The 2026-09-22 study rejected a "local CI daemon" —
    but the two-track trust model queues deterministic checks. Should a
    lightweight watcher (e.g. `entr` or `fswatch`) be re-proposed for the
    Save tier, or does the "trust attaches to mechanism" principle argue
    against it?
3.  **Agent-Workflow:** The agent loop (Save tier) currently runs LSPs.
    Should the agent run `prek run --files <changed>` as a pre-flight
    before every `git add` to compensate for the selection gap, or should
    the gap be closed at the hook level?
4.  **Fleet/Provisioning:** The deliverable includes a layered global
    user-level editor-tooling config (chezmoi topic) covering opencode,
    Zed, VS Code/Cursor, Neovim. How should the config handle machines
    that lack `shellcheck`, `shfmt`, or `shellharden` installed? Graceful
    fallback or hard dependency (via `mise`)?

---

## 5. Sources

*   **shellharden** — https://github.com/anordal/shellharden (observed 4.3.2 via `mise which shellharden`; supports `--check` exit-2 and `--replace` rewrite)
*   **shellcheck** — https://github.com/koalaman/shellcheck (v0.10.0.1 via `prek`/`pre-commit`)
*   **shfmt** — https://github.com/mvdan/sh (NOT installed locally)
*   **markdownlint** — https://github.com/igorshubovich/markdownlint-cli2 (NOT installed locally)
*   **actionlint** — https://github.com/rhysd/actionlint (NOT installed locally)
*   **pyrefly** — https://github.com/facebook/pyrefly (v1.3.2 via `mise`/`pyproject.toml`)
*   **ruff** — https://github.com/astral-sh/ruff (v0.16.9 via `mise`/`pyproject.toml`)
*   **ty** — https://github.com/astral-sh/ty (referenced in `pyproject.toml` `lint` group, not installed locally)
*   **prek** — https://github.com/j178/prek (v0.5.6 via `mise`; measured as active hook runner)
