# Roadmap: package-manager state importer

A follow-up to the upgrade-flow rework. Not in scope for the current PR.
This document captures every design decision made in conversation so a future
Claude / LLM session can pick the work up cold.

## Goal

Detect every package manager installed on the current machine, enumerate the
packages the user **explicitly requested** (not transitive dependencies), and
import that state into the topic-based Ansible setup so it becomes managed
configuration.

## Why

The dotfiles repo has ~20 hand-authored topics for "named" applications
(`apps/firefox/`, `apps/cursor/`, etc.) but hundreds of packages installed
via `brew`, `mise`, `mas`, etc. that are not declared anywhere. Drift between
what's installed and what's declared makes the system non-reproducible. The
importer closes that gap.

## Design decisions (locked in conversation)

### Q1 — Where does `mpm` itself live?

**Decision:** Install [meta-package-manager](https://kdeldycke.github.io/meta-package-manager/)
via mise + `uv tool install` (i.e., add `meta-package-manager` to the global
`uvx`-managed Python tools alongside `llm`, `uv`, `uvx`).

**Rationale:** mpm is a Python tool, and mise already manages other global
Python tools. Avoids creating a single-binary topic for what's really a CLI
utility.

**Concrete:** mise config should gain an entry equivalent to:
```bash
mise use -g uv:meta-package-manager@latest
# or
mise use -g pipx:meta-package-manager@latest
```
Check `apps/mise/` for the established pattern when this is implemented.

### Q2 — Granularity: explicit packages only

**Decision:** Detect **only the packages the user explicitly requested**. Do
not import transitive dependencies — the package manager itself tracks those
and will re-resolve them on the next install.

**This is the most important constraint.** mpm's default `installed` output
includes everything, not just explicit. The importer must dispatch per-manager
to filter to explicit-only:

| Manager | Explicit-only enumeration |
|---|---|
| brew (formulae) | `brew leaves` (formulae with no other installed formula depending on them) |
| brew (casks) | `brew list --cask` (all installed casks are explicit) |
| apt | `apt-mark showmanual` |
| flatpak | `flatpak list --app --columns=application` (apps only, not runtimes) |
| snap | `snap list` (all explicit) |
| mas | `mas list` |
| mise | `mise ls --installed --global --json` (parse for global tools) |
| cargo | `cargo install --list` |
| npm | `npm ls -g --depth=0 --json` |
| uv (tools) | `uv tool list` |
| pip | `pip list --not-required --format=json` (closest pip has to "explicit") |
| pipx | `pipx list --json` |
| dnf | `dnf history userinstalled` |
| pacman | `pacman -Qe` |
| nix | `nix profile list --json` |
| pnpm | `pnpm ls -g --depth=0 --json` |
| yarn | `yarn global list` (parse) |

Output of bulk topics should be a flat list of *names only*, not the full
mpm dump.

### Q3 — Interaction model: report first, then interactive (with batch flag)

**Decision:** Default flow is:

1. Detect all installed pkg managers (see Q4).
2. For each, enumerate explicit-only packages.
3. **Print a summary report** showing what would be imported, before any
   prompting. The user sees totals and the full list per manager and gets
   a chance to abort.
4. Then **interactive prompt** to confirm or skip each manager / package.
5. Write topics to disk only after confirmation.

`--batch` flag skips step 4 — same flow but auto-confirms everything and
writes results plus an `import-suggestions.md` for the user to review.

### Q4 — Coverage: detect every installed pkg manager, mpm or not

**Decision:** mpm is a helper, not the source of truth. The importer must
detect any pkg manager the user has installed, including ones mpm doesn't
support.

**Implementation:** two-layer detection.

1. **Authoritative layer — direct binary probes.** For each known manager,
   `command -v <binary>` (e.g., `brew`, `apt`, `flatpak`, `snap`, `mas`,
   `mise`, `cargo`, `npm`, `pnpm`, `yarn`, `uv`, `pipx`, `pip`, `dnf`,
   `pacman`, `nix`, `port`, `zypper`, `apk`, `xbps-install`, `eopkg`,
   `emerge`). This is the source of truth.

2. **Comparison layer — `mpm managers --output-format json`.** Run mpm
   and compare. If mpm reports a manager we didn't probe for, learn from
   it (add to the probe list). If our probe finds one mpm missed, log it
   as a known gap.

The importer reports both layers' findings in the summary.

### Q5 — Scope: roadmap, not this PR

**Decision:** Not in scope for the upgrade-flow PR. Capture here, pick up
later.

## Implementation sketch

### File layout

```
apps/mise/                    # add meta-package-manager to mise globals
  tasks/install.yaml          # ← add: mise use -g uv:meta-package-manager

bin/import-pkg-state          # the importer script (Python recommended)
  # Detects managers, enumerates explicit packages, writes bulk topics.

apps/<manager>-explicit/      # one per detected pkg manager with packages
  topic.yml                   # topic_name: <manager>-explicit
                              # topic_provides: []
                              # topic_requires: [<manager>]
                              # topic_os: [Darwin|Debian|both]
                              # topic_tier: app
  tasks/install.yaml          # one task per package
  tasks/remove.yaml           # mirror
  tasks/upgrade.yaml          # no-op (refreshed by the pkg-manager's upgrade)
  tasks/bootstrap.yaml        # no-op
  tasks/prerequisites.yaml    # no-op
  tasks/main.yaml             # lifecycle router (copy from template_dir)
```

Topic naming convention: `<manager>-explicit` so it's obvious these are the
explicit-import topics vs. hand-authored named topics like `apps/firefox/`.

Examples expected to be generated on a typical macOS dev box:
- `apps/homebrew-formulae-explicit/`
- `apps/homebrew-casks-explicit/`
- `apps/mas-explicit/`
- `apps/mise-tools-explicit/`
- `apps/uv-tools-explicit/`

On a Debian box:
- `apps/apt-explicit/`
- `apps/flatpak-explicit/`
- `apps/snap-explicit/` (if installed)

### Importer skeleton (pseudocode)

```python
#!/usr/bin/env python3
"""bin/import-pkg-state — discover explicit packages, scaffold bulk topics."""
import argparse, json, subprocess, pathlib, sys
from dataclasses import dataclass

@dataclass
class Manager:
    name: str            # "brew-formulae"
    probe: list[str]     # ["command", "-v", "brew"]
    enumerate: list[str] # ["brew", "leaves"]
    os: list[str]        # ["Darwin"]
    requires: str        # "homebrew"

MANAGERS = [
    Manager("homebrew-formulae", ["command","-v","brew"], ["brew","leaves"], ["Darwin"], "homebrew"),
    Manager("homebrew-casks",    ["command","-v","brew"], ["brew","list","--cask"], ["Darwin"], "homebrew"),
    Manager("apt",               ["command","-v","apt-mark"], ["apt-mark","showmanual"], ["Debian"], "apt"),
    Manager("flatpak",           ["command","-v","flatpak"], ["flatpak","list","--app","--columns=application"], ["Debian"], "flatpak"),
    Manager("mas",               ["command","-v","mas"], ["mas","list"], ["Darwin"], "homebrew"),
    Manager("mise-tools",        ["command","-v","mise"], ["mise","ls","--installed","--global","--json"], ["Darwin","Debian"], "mise"),
    # ... etc
]

def probe(m: Manager) -> bool:
    return subprocess.run(m.probe, capture_output=True).returncode == 0

def enumerate_pkgs(m: Manager) -> list[str]:
    r = subprocess.run(m.enumerate, capture_output=True, text=True, check=True)
    return parse(m.name, r.stdout)  # per-manager parser

def report(detected: dict[Manager, list[str]]) -> None:
    print("Detected package managers and explicit packages:")
    for m, pkgs in detected.items():
        print(f"  {m.name}: {len(pkgs)} explicit")
        for p in pkgs[:5]:
            print(f"    - {p}")
        if len(pkgs) > 5:
            print(f"    ... ({len(pkgs)-5} more)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    detected = {m: enumerate_pkgs(m) for m in MANAGERS if probe(m)}
    report(detected)

    if not args.batch:
        if input("\nProceed with import? [y/N] ").strip().lower() != "y":
            sys.exit(0)

    for m, pkgs in detected.items():
        write_topic(m, pkgs, dry_run=args.dry_run)

    if args.batch:
        write_suggestions_md(detected)

if __name__ == "__main__":
    main()
```

### Topic generation template

For each manager, generate `tasks/install.yaml` along these lines (homebrew
formulae example):

```yaml
---
# apps/homebrew-formulae-explicit/tasks/install.yaml
# Auto-generated by bin/import-pkg-state on {{ date }}.
# Edit manually — re-running the importer offers diff/merge.

- name: "Install homebrew formulae (explicit)"
  community.general.homebrew:
    name:
      - bat
      - ripgrep
      - fd
      # ... full list
    state: present
  when: ansible_facts['os_family'] == 'Darwin'
```

### Re-running the importer

If `apps/<manager>-explicit/` already exists, the importer should:

1. Read the current list of packages from `tasks/install.yaml`.
2. Diff against current explicit set.
3. Show additions + removals.
4. Prompt to merge (or `--batch` auto-merges).

This makes the importer the canonical way to refresh state, not just a
one-time tool.

## Open questions for future session

1. **Should `--batch` write directly to topic files, or to a staging dir?**
   Risk of clobbering hand-edits. Probably safer to stage and let the user
   diff/merge.

2. **What happens to manually-curated named topics when the bulk topic also
   wants the same package?** E.g., `apps/firefox/tasks/install.yaml` installs
   `firefox` via cask, and `brew list --cask` returns `firefox`. The importer
   should detect overlap and exclude from the bulk topic so we don't install
   it twice. Suggestion: read every `apps/*/tasks/install.yaml` for explicit
   package names, build an exclusion set, skip those in bulk topics.

3. **Versioned vs. unversioned imports.** `brew leaves` gives just names;
   `mise ls --json` gives versions. Should the bulk topics pin versions?
   Defaults: brew/apt/etc. unversioned (latest); mise versioned (because
   mise *is* version management).

4. **CRUD invariant for bulk topics.** Each bulk topic's `remove.yaml`
   should `state: absent` the same list. Auto-generate symmetrically.

5. **Where does the importer get re-run from?** A `--tags import` block in
   the parent playbook? A standalone script invoked by a dedicated command?
   The user's preference (Q3 answer suggests script with interactive default)
   leans toward standalone CLI in `bin/`.

6. **Output for managers mpm doesn't know about.** If a user has `nix`
   installed but mpm doesn't support it, our direct probe layer catches it.
   Document in the report that this manager was detected outside mpm so the
   user knows the coverage came from our own enumeration.

## Pointers to relevant code

- Topic conventions: [docs/CONVENTIONS.md](CONVENTIONS.md)
- Template a new topic: `template_dir/` (copy with `init-config.sh <name>`)
- Topic metadata: `apps/<topic>/topic.yml`
- Parent playbook discovery: `playbook.yaml` lines 41–95
- Sanity check resolution: `playbook.yaml` lines 110–170
- Existing pkg-manager topics for reference: `apps/homebrew/`, `apps/apt/`, `apps/docker/`
- Existing runtime-manager topic for reference: `apps/mise/`
