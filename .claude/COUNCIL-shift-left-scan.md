# COUNCIL: Shift-Left Surface Scan — Decisions (Four Voices)

**Task:** TASKS.md § Now #1 follow-on (council on the scan's § 4 open questions).
**Input:** `.claude/RESEARCH-shift-left-surface-scan.md` (bf82be1), treated as authoritative framing.
**Worktree:** `.worktrees/shift-left-scan`, branch `agent/shift_left_scan`. Read-only over code; this file is the sole written artifact.
**Voices:** INCREMENTALIST · TRUST ARCHITECT · AGENT-WORKFLOW · FLEET/PROVISIONING.

**Evidence gathered for this council (measured 2026-10-21, worktree):**

| # | Fact | Method |
|---|---|---|
| E1 | `identify.tags_from_path` on `bin/executable_archive` → `{'text','non-executable','file'}` — no shell/python tag | `identify` lib, direct call |
| E2 | The **same file with exec bit set** → `{'text','shell','bash','file','executable'}` — the exec bit alone makes identify classify by shebang | `identify` on a chmod'd /tmp copy |
| E3 | bin/ shebang census: **28 `env bash`, 8 `python3`, 7 `uv run --script`, 1 `/bin/bash`, 1 `/bin/sh`, 1 comment-line (vscode-wait), 1 markdown block (READMD.archive.md)** | `head -1` over all 47 |
| E4 | `shellcheck` (0.10.0) over the 30 shell-shebang bin files: **all 30 fail today** (SC1046/SC1047/SC1128 among them). Flipping the exec bit *now* would turn every hook red | direct `shellcheck` run |
| E5 | `bin/executable_vscode-wait.sh` has its shebang on line 2 (comment on line 1) — SC1128; the file exists to wait for vscode but its own syntax is broken | `head -1` + shellcheck |
| E6 | `bin/executable_archive.bk` and `bin/executable_READMD.archive.md` are tracked junk (bk DIFFERs from archive; the .md is a stray doc named executable) | `cmp`, `head -1` |
| E7 | `shellcheck -s zsh` → `Unknown shell: zsh` on 0.10.0 — **shellcheck cannot lint zsh** in this version | direct run on 3 fragments |
| E8 | zsh fragments (86 files) are tagged `shell` by identify (via `.zsh` extension) → the shellcheck hook **selects and fails** on 68 shebang-less fragments (SC2148), measured live via `prek run --files dotfiles/zsh/executable_completion.zsh` | `identify` + `prek run` |
| E9 | `zsh -n` parses without executing (an `echo MARKER` file printed nothing, exit 0); real parse errors (bare `fi`, unterminated quote, missing `done`) exit 1 with a file:line message; **86/86 existing fragments pass**; ~7ms/file, 0.58s wall for all 86 | direct runs |
| E10 | shellharden has **no published pre-commit hook repo**; support is an open issue (#61, opened 2025-02-24, still open) | web search |
| E11 | shellharden IS in `dotfiles/apps/mise/files/config.toml` line 135 (`"cargo:shellharden" = "latest"`) — provisioned, not ad hoc | grep |
| E12 | `prek` with `language: system` and a missing binary **fails the hook (exit 2)**, does not silently skip — system-language hooks are fail-closed in prek, measured | scratch config in /tmp |
| E13 | `ty` 0.0.84 runs via `uv run --frozen ty check .` in 0.25s and reports **28 diagnostics** on the current tree; official hook repo `astral-sh/ty-pre-commit` exists (rev-pinned, runs `uv check`, whole-project, `pass_filenames: false` enforced upstream) | direct run + web search |
| E14 | ruff with a conservative error-only select (E4,E7,E9,F) passes on 2 of 3 sampled python bin scripts; `bin/executable_binned` has 2 fixable findings | direct run |
| E15 | shellharden `--check` over all bin bash files: 0.46s wall (loop incl. shebang reads) | timed run |

---

## 1. Decision table

### Q1 — Fix mechanism for the bin/executable_* selection gap

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | 1 | **Exec bit on all 47** (one commit, zero per-hook maintenance; identify then classifies by shebang). 2. Per-hook `files:` patterns. 3. Custom classifier — rejected, machinery for its own sake. |
| TRUST ARCHITECT | 1 | **Exec bit**, but *only after* the population is green (E4: all 30 shell files fail shellcheck today — flipping the bit unconditionally converts "skipped by every hook" into "failed by every hook", trading one silent defect for a loud but unusable gate). Requires a before/after selection census recorded on the commit. |
| AGENT-WORKFLOW | 1 | Exec bit at the hook level so agents inherit it; the agent pre-flight `prek run --files <changed>` habit stays as a safety net, not the fix. |
| FLEET | 1 | Exec bit — it travels in the git blob, zero provisioning, no wrapper script to install. Wrapper scripts are also repo content, so acceptable as a fallback, but the bit is cheaper. |
| **Council** | | **RESOLVED — exec-bit approach**, gated on a green-population sequence (see plan P1/P1a). Every voice ranked it first; disagreement was only about sequencing, not mechanism. Junk files E6 are removed in the same change so the census is honest. |

### Q2 — zsh fragments: shellcheck false positives + a real zsh candidate

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | 1 | Exclude `*.zsh` from shellcheck (one line). Defer zsh linting — 86 fragments all pass `zsh -n` today (E9), so there is no observed bug to justify a new hook. |
| TRUST ARCHITECT | 1 | Exclude `*.zsh` **and** add a local `zsh -n` check hook. E8 shows shellcheck currently *fails* on 68 shebang-less fragments — an always-red hook is as defective as a never-running one. E9 verifies `zsh -n` is parse-only (no execution), fail-closed on real syntax errors, ~7ms/file. Excluding without replacing recreates the selection gap for 86 files. |
| AGENT-WORKFLOW | 2 | Preferred zls in the editor tier only (Zed extension; opencode could wire it later); a hook is acceptable only because `zsh -n` is parse-only and cheap. |
| FLEET | 1 | `zsh -n` needs zsh, which is the login shell on both targets — zero provisioning. zls is a mise/Zevious addition, editor-tier only. |
| **Council** | | **RESOLVED — exclude `*.zsh` from shellcheck + add a local `zsh -n` check hook** (Add tier). zls stays editor-tier-only, deferred. The live SC2148 failure mode (E8) is a standing break that makes every zsh-fragment commit fail today; this is not optional cleanup. |

### Q3 — `ty` candidate

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | 1 | **Drop.** pyrefly already type-checks at 0.15s; a second type checker doubles surface for marginal gain. |
| TRUST ARCHITECT | 2 | Keep queued with a named unlock. The official hook (`astral-sh/ty-pre-commit`) is rev-pinned and uv-provisioned — **fail-closed, not a fail-open availability check** (E13). But 28 diagnostics exist (E13): landing it now guarantees a red gate. Unlock = disposition those diagnostics, then decide ty-vs-pyrefly as the sole checker. |
| AGENT-WORKFLOW | 2 | Editor/agent-loop tier only until diagnostics are dispositioned; never a gate before then. |
| FLEET | 2 | ty already rides in the repo's `uv.lock` lint group — travels with the repo, no mise entry needed. Provisioning is a non-issue. |
| **Council** | | **RESOLVED — keep queued**, vehicle verified fail-closed (ty-pre-commit), landing explicitly blocked on the 28 diagnostics (E13). Not dropped: ty and pyrefly overlap but a second checker catches classes the first misses, and the cost of keeping it queued is zero. Incrementalist dissent recorded. |

### Q4 — Dangling .pre-commit-config.yaml line-42 exclusion

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | 1 | Remove now — the excluded file is untracked, so the line matches nothing (dangling); inert change, kills the defect state. |
| TRUST ARCHITECT | 1 | Remove now; if the helper later lands *with* its bats file, the bats runner finds `tests/run-shellharden.bats` and no exclusion is needed. If the helper lands without tests, that is a separate decision to make then — an exclusion kept on spec is config that lies. |
| AGENT-WORKFLOW | 1 | No operational effect either way; removal is free. |
| FLEET | 1 | No provisioning effect. |
| **Council** | | **RESOLVED — remove now** (config change, one line, its own commit or folded into P3's landing commit). Unanimous. |

### Q5 — shellharden disposition

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | 1 | Keep as the agent-loop helper only; do **not** add a hook yet. The helper is untracked and unproven; gating on a tool that isn't committed inverts the order of operations. |
| TRUST ARCHITECT | 1 | **Dual disposition, sequenced.** E10 confirms no official hook repo exists, so `language: system` is the only vehicle — and E12 verifies prek treats a missing system binary as a **hook failure, not a silent skip**: the vehicle is fail-closed, contrary to the report's worry. The helper's population census + zsh-skip logic (read, in the untracked files) is exactly the fail-closed pattern this house wants. Commit the helper + its bats, then graduate to a prek local hook in `--check` mode. |
| AGENT-WORKFLOW | 1 | Dual: `--fix`/`--replace` stays in the agent loop where a session can inspect the diff (AGENTS.md § Commits — "rewriting hooks leave residue"); `--check` becomes a hook. |
| FLEET | 1 | Provisioning is already done — E11 shows shellharden in mise config.toml. The hook's only fresh dependency is the helper script itself being committed. |
| **Council** | | **RESOLVED — dual disposition**: (1) commit the helper + bats as the agent-loop tool; (2) add a `language: system` prek hook in `--check` mode calling the helper. Sequenced **after** P1, since shellharden's population is the same bin bash scripts the exec bit unlocks — landing the hook before the bit makes it a zero-selection hook (the exact gap pattern). Dissent noted (Incrementalist wanted helper-only first). |

### Q6 — Layered global user-level editor-tooling config (author-directed deliverable)

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | 1 | **Minimal V1 = opencode + Zed only** (the two actually used by agents and the author here). Defer VS Code/Cursor/Neovim until someone uses them. Also: opencode already has the layering pattern (`dot_config/opencode/opencode.jsonc.tmpl` deep-merges `.chezmoidata/opencode.yaml` common → os → host) — replicate that pattern, don't invent a second one. |
| TRUST ARCHITECT | 1 | Before any config lands, the topic must **declare ownership**: which files are chezmoi-owned globals vs. native per-project overrides. Without that boundary, a per-project file and a global default can silently conflict — the config-layer version of the selection gap. Require the topic README to name the override file for each tool. |
| AGENT-WORKFLOW | 1 | opencode is the agent's editor; its LSP config IS the Save tier. Priority 1 within the topic. Zed second (human editor). |
| FLEET | 1 | All four tools have **native per-project override files** (`.zed/settings.json`, `.vscode/settings.json`, `exrc`/`.nvim.lua`, per-project `opencode.json`), so the layering strategy is: chezmoi topic owns **user-level globals only**; per-project overrides use each tool's native mechanism; no chezmoi merge gymnastics. Caveat: VS Code/Cursor's settings live in `~/Library/Application Support/...` on macOS (not XDG) — if that tier ever lands, the chezmoi target path needs an OS-conditional template. Neovim and Zed are clean XDG. |
| **Council** | | **RESOLVED (scope) — V1 = opencode + Zed global defaults** in one topic; override mechanism = each tool's native per-project file, documented in the topic README (satisfies the Trust Architect's ownership declaration). **DEFER (inventory)** — which specific settings deserve global defaults requires a survey of the author's current configs; that survey is the first task of the topic, not a council guess. VS Code/Cursor/Neovim deferred out of V1; FLEET's XDG caveat recorded for when they return. |

### Q7 — Does the check-vs-rewrite split hold for every candidate?

| Voice | Rank | Recommendation |
|---|---|---|
| INCREMENTALIST | — | Holds; no candidate is a rewriter in hook mode. |
| TRUST ARCHITECT | — | Holds **provided the split is enforced in the hook config itself** (`shellharden --check`, `shfmt -d`), not by convention. A hook that runs a rewriter's write mode violates the policy even if nobody notices. |
| AGENT-WORKFLOW | — | Holds; rewrite modes (`shellharden --replace`, `shfmt -w`) belong in the agent loop where diffs get inspected. |
| FLEET | — | Holds; no provisioning interaction. |
| **Council** | | **RESOLVED — the split holds for every queued candidate**, with enforcement in the hook config (check-mode flags only). No dissent. |

---

## 2. Ranked action plan

| # | Action | Tier | Type | Expected timing | Notes |
|---|---|---|---|---|---|
| **P1a** | **Green the bin population**: fix shellcheck findings across the 30 shell-shebang bin files (E4: all fail today — includes real bugs, e.g. vscode-wait's shebang-not-on-line-1, E5); run ruff error-only select over the 8 python3 + 7 uv-script bin files (E14 baseline: passes with 2 fixable in binned). Mutations proven per fix. | Add | **code** | Pre-existing work; per-commit cost after landing ~0.2–0.5s extra for the newly-selected files — inside the ≤5s Add budget | The precondition for P1. Skipping it and flipping the bit anyway is the "hook that always fails" defect. |
| **P1b** | **Delete tracked junk**: `bin/executable_archive.bk` (DIFFERs from archive — stale) and `bin/executable_READMD.archive.md` (stray doc wearing an executable name). | — | **code** | 0 | Keeps the P1 census honest; junk files would otherwise enter the newly-selected population. |
| **P1** | **Flip the exec bit** on the remaining bin source files, one commit, with a recorded before/after selection census (`prek run --all-files` counts, both OSes where available). | Add | **code** | +0.2–0.5s worst case on shellcheck/ruff over ~47 files; pyrefly already project-wide | Closes the 47-file gap at the hook level for every hook at once, by making identify's classification true. |
| **P2** | **zsh**: add `exclude: \.zsh$` to the shellcheck hook (kills the live SC2148 always-red failure, E8) and add a local `zsh -n` check hook over changed `.zsh` files. | Add | **config** | ~7ms/file changed (E9); negligible | Two small config edits, one commit. Removes a standing break that currently makes every zsh-fragment commit fail. |
| **P3** | **Land the shellharden helper**: commit `scripts/run-shellharden.sh` + `tests/run-shellharden.bats` (population-census design preserved); drop the now-satisfied line-42 exclusion (Q4) in the same commit; then add the prek local hook (`language: system`, `--check` mode) — now meaningful because P1 has made bin files selectable. | Add (hook) + agent loop (--fix) | **code + config** | ~0.46s full-population --check (E15); per-commit only changed files | Dual disposition per Q5. Note the deliberate P1→P3 ordering: hook after selection exists, or the hook is a zero-selection no-op. |
| **P4** | **Editor-tooling topic V1**: survey the author's current opencode/Zed configs; scaffold `dot_config/`-based topic carrying global defaults for opencode + Zed; README declares the override file per tool (`.zed/settings.json`, per-project `opencode.json`). | Save/editor | **config + docs** | N/A (not a hook) | Per Q6. The survey (not a guess) decides which settings are global. VS Code/Cursor/Neovim deferred; XDG caveat recorded. |
| **P5** | **ty**: disposition the 28 diagnostics (E13); then either land `astral-sh/ty-pre-commit` (rev-pinned, fail-closed) or record the drop decision with reasons. | Add | **config** | 0.25s (E13) | Per Q3. Blocked until P5's first half is done; no time pressure. |
| — | shfmt, markdownlint, actionlint | — | — | — | **No council decision requested**; remain queued as in the scan report. shfmt carries the same check-vs-rewrite split (Q7) when it lands. |

**Sequencing rationale:** P1a→P1b→P1 is one logical unit (green population, then make selection true). P2 is independent and can land in parallel — it removes a live break. P3 depends on P1 only for the *hook* half; the helper commit itself can land anytime. P4 and P5 are independent of all of the above.

---

## 3. Dissent notes

- **Q1 (exec bit):** No voice dissented on the mechanism. The Trust Architect's condition — green the population first — is recorded as P1a and is the difference between a fix and a new outage.
- **Q2 (zsh):** AGENT-WORKFLOW preferred editor-tier-only (zls) and accepted the hook reluctantly; INCREMENTALIST would defer the hook entirely on "86/86 pass today". Council overrode both because E8 shows the shellcheck hook is currently *red* on 68 fragments — the status quo is already broken, and the cheapest honest fix is exclude + `zsh -n`. The dissent is live: if `zsh -n` never fires on a real fragment error in a year, the INCREMENTALIST position was right and the hook should be retired.
- **Q3 (ty):** INCREMENTALIST dissented from keeping ty queued ("drop it — second type checker, marginal gain"). Council kept it queued because the cost of queueing is zero and the vehicle is verified fail-closed; the dissent stands recorded and the P5 decision point is where it gets re-argued with data.
- **Q5 (shellharden):** INCREMENTALIST dissented from the hook half of the dual disposition ("helper-only until proven"). Council accepted the hook because E12 proves the `language: system` vehicle is fail-closed in prek and E11 proves provisioning already exists. The INCREMENTALIST constraint was partially honored: the hook lands only *after* the helper is committed and P1 has made its population real.
- **Q6 (editor topic):** FLEET wanted the layering mechanism defined for all four tools even if only two land in V1; council narrowed V1 to opencode + Zed (INCREMENTALIST position) but recorded FLEET's XDG caveat (VS Code/Cursor non-XDG on macOS) as a standing note so the deferred tiers don't rediscover it.

---

## 4. Sources

**Externally verified (web search / fetch):**

- shellharden — https://github.com/anordal/shellharden (v4.3.2; `--check` exit-2, `--replace` rewrite). **No pre-commit hook repo published**; pre-commit support is an open request: https://github.com/anordal/shellharden/issues/61 (opened 2025-02-24, still open at search time).
- ty official pre-commit hook — https://github.com/astral-sh/ty-pre-commit (rev-pinned; runs `uv check`; whole-project by design, `pass_filenames: true` will error). Hook initially declined in https://github.com/astral-sh/ty/issues/269 ("not ready for serious production"), published 2026-06-10 per that issue.
- shellcheck — https://github.com/koalaman/shellcheck (v0.10.0 locally; `-s zsh` → "Unknown shell: zsh", measured — no zsh dialect in this version).
- prek — https://github.com/j178/prek (v0.5.6; `language: system` with missing binary → hook failure, measured).
- identify — https://github.com/pre-commit/identify (`tags_from_path` classification: exec bit + shebang/extension → `shell`/`python` tags, measured).
- zsh `-n` — parses without executing (POSIX sh/zsh `-n` "read commands and check them for syntax errors, but do not execute them"; verified locally: parse-only marker not printed, parse errors exit 1 with file:line).
- zls — https://github.com/zigtools/zls (installable via mise, `zls@0.17.0` available, not installed locally).

**Measured locally (2026-10-21, this worktree):** all E-numbered evidence rows in the table above.
