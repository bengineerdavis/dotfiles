# CRUD invariant audit (2026-06)

Findings from auditing every topic in `apps/` against the CRUD ownership
invariant defined in [docs/CONVENTIONS.md](CONVENTIONS.md):

> Any state a topic creates in `bootstrap.yaml`, `prerequisites.yaml`,
> `install.yaml`, or `upgrade.yaml` must have a matching teardown in
> `remove.yaml`.

This document is **informational** — these findings are not addressed in
the upgrade-flow PR. They are candidates for follow-up work. Existing
`TODO` / `EMPTY` markers in the source files remain in place as guideposts
until the underlying work is actually completed.

## Summary

| Topic | Status | Issue |
|---|---|---|
| `apt` | ⚪ N/A | pkg-manager tier — install/remove of apt itself handled by the OS |
| `docker` | ⚪ N/A | pkg-manager tier — install/remove of Docker handled by Rancher Desktop |
| `homebrew` | ⚪ N/A | pkg-manager tier — install in `bootstrap.yaml`; uninstall is out of scope |
| `mise` | ❌ violation | `remove.yaml` is empty; `install.yaml` installs the binary and creates `~/.config/mise/` |
| `gnu-tools` | ⚠ no-op | `install.yaml` and `remove.yaml` are both empty (commented examples only) |
| `monitorcontrol` | ⚠ no-op | both empty (TODO markers in remove) |
| `rancher-desktop` | ⚠ no-op | both empty (TODO markers in remove) |
| `anki` | ✓ | install via cask, remove via cask |
| `cursor` | ✓ | install via cask, remove via cask |
| `eza` | ✓ | install via brew, remove via brew |
| `firefox` | ✓ | install via cask, remove via cask |
| `fzf` | ✓ | install via brew, remove via brew |
| `ghostty` | ✓ | install via cask, remove via cask |
| `meld` | ✓ | install via cask, remove via cask |
| `ollama` | ✓ thorough | install + remove are both substantive; remove handles launchd agent, completions, caches, conditional model removal |
| `rectangle` | ✓ | install via cask, remove via cask |
| `starship` | ✓ | install via brew, remove via brew (covers both macOS and Linux) |
| `tmux` | ✓ | install via brew, remove via brew |
| `trash-cli` | ✓ | install via brew, remove via brew |
| `visual-studio-code` | ✓ | install via cask, remove covers both macOS cask and Linux apt |
| `zim` | ✓ | install creates Zim.app wrapper + downloads Zim.zip; remove undoes both |
| `zoxide` | ✓ | install via brew, remove via brew |

## Real violators

### `apps/mise/`

`tasks/install.yaml` creates two pieces of state:

1. `mise` binary via Homebrew formula.
2. `~/.config/mise/` directory.

`tasks/remove.yaml` is empty. To restore the CRUD invariant:

```yaml
# apps/mise/tasks/remove.yaml (proposed)
- name: "Remove mise via Homebrew (macOS)"
  community.general.homebrew:
    name: mise
    state: absent
  when: ansible_facts['os_family'] == 'Darwin'

- name: "Remove ~/.config/mise directory"
  ansible.builtin.file:
    path: "{{ ansible_facts['env']['HOME'] }}/.config/mise"
    state: absent

# OPTIONAL — managed runtime tree. May be desired to keep (large; takes
# minutes to rebuild) or to wipe. Default to keep; surface as a prompt
# similar to ollama_remove_models.
- name: "Remove ~/.local/share/mise (managed runtimes) — optional"
  ansible.builtin.file:
    path: "{{ ansible_facts['env']['HOME'] }}/.local/share/mise"
    state: absent
  when: mise_remove_runtimes | default(false)
```

## No-op topic skeletons

`gnu-tools`, `monitorcontrol`, and `rancher-desktop` have:

- `install.yaml` with only commented-out examples (no real install task).
- `remove.yaml` with only commented-out examples (no real remove task).

Each likely has shell config (`.zsh` files) and/or templates, but the
Ansible-managed install pathway is not wired up. Two interpretations:

1. **The binary is intentionally installed via a different topic** (e.g.,
   `gnu-tools` may be implicitly satisfied by `apps/homebrew/tasks/install.yaml`
   if coreutils is listed there).
2. **The topic was scaffolded but never completed.**

Recommended follow-up for each:

- `gnu-tools` — confirm coreutils/gnu-sed/etc. are installed somewhere
  authoritative, then either complete `install.yaml` or remove the topic.
- `monitorcontrol` — currently has TODO markers; complete or remove.
- `rancher-desktop` — currently has TODO markers; complete or remove.

## Non-issues (asymmetric counts that aren't violations)

- **ollama**: install has 69 action-shaped lines; remove has 46. The line-
  count gap is misleading — install includes many `stat:` / `command:` /
  `debug:` inspections that don't create state (free-disk-space checks,
  RAM warnings, launchd plist presence checks). The state-creating actions
  in install are mirrored by removal actions, including comprehensive
  cleanup of `~/Library/Application Support/Ollama`, caches, launchd
  agent plist, and conditional model removal under `~/.ollama`.

- **visual-studio-code**, **starship**: `remove.yaml` has more uncommented
  task lines than `install.yaml` because removal covers both macOS and
  Debian package managers while install currently only covers one. Remove
  being broader than install is not a violation.

## Methodology

Audit was performed by:

1. Counting uncommented Ansible-action lines per lifecycle file:
   `grep -cE "^[^#]*ansible|^[^#]*community" apps/<topic>/tasks/*.yaml`
2. Reading the full content of each topic where the install/remove ratio
   was suspicious or where either file appeared empty.
3. Cross-referencing install side effects (file creation, directory
   creation, downloads, symlinks, launchd registrations) against remove
   tasks.

## Pre-existing data issues already patched during the upgrade-flow PR

These were unblocking fixes for verification, **not** part of the CRUD
audit scope, and are noted here for traceability:

- `apps/anki/tasks/install.yaml` — stripped LLM-generation header that
  broke YAML parsing.
- `apps/anki/tasks/remove.yaml` — same.
- `apps/starship/tasks/install.yaml` — was an LLM-truncated stub with an
  opening markdown fence and no real install task. Replaced with
  `brew install starship`.
- `apps/visual-studio-code/tasks/install.yaml` — stripped LLM trace and
  markdown code fences; kept the real cask install task.
- `apps/meld/tasks/remove.yaml` — restored `#` prefixes on a partially
  uncommented apt block that produced bare YAML keys.
