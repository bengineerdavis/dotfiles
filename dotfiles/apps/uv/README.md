# uv

Owns the machine-level [uv](https://docs.astral.sh/uv/) binary and — on work
machines — the capture of the private package index into `~/.localrc`.

| What | Owner | Where |
|---|---|---|
| The `uv` binary | this topic | `~/.local/bin/uv` (astral install; never mise or brew, so `mise upgrade` never churns the uvx that builds pipx: backends) |
| The private-index env block | this topic | `~/.localrc`, marker-delimited, written from the vault |
| The uv user config | chezmoi | `dot_config/uv/uv.toml.tmpl` → `~/.config/uv/uv.toml` |

First install on a fresh machine belongs to `dotfiles/bootstrap/bootstrap.sh`
(ordering: uv → mise → mise sync → ansible); this topic maintains it from then
on.

## Usage

```bash
./run-role.sh uv              # provision (install + version check + capture)
./run-role.sh uv upgrade      # uv self update
./run-role.sh uv remove       # drop the ~/.localrc block; binary is opt-in
./run-role.sh uv remove -e uv_remove_binary=true   # also uninstall the binary
```

## Work machines: the private index

1. Flag the host in `.chezmoidata/uv.yaml` (`hosts: <hostname>: work: true`).
   Hostnames only — nothing employer-identifying enters the repo.
2. Store three values in the vault under `uv-private-index` (url, username,
   password; item references are in `defaults/main.yaml`).
3. Sign in to 1Password, then `./run-role.sh uv install`. The topic resolves
   the values (`no_log` — never echoed) and writes a marker block into
   `~/.localrc`:
   ```sh
   export UV_PRIVATE_INDEX_URL="…"
   export UV_INDEX_PRIVATE_USERNAME="…"
   export UV_INDEX_PRIVATE_PASSWORD="…"
   ```
4. `chezmoi apply`. The `dot_config/uv/uv.toml.tmpl` template renders the
   private index with `default = true` (names resolve here first; public PyPI
   stays the non-default fallback — the dependency-confusion guard). On
   personal machines the same template renders public PyPI only.

A work host applying **without** the captured env fails the template loudly
instead of silently rendering public-only — a silent public-only render on a
work machine is fail-open dependency confusion.

`~/.config/uv/uv.toml` also pins `required-version` to the same floor as
`pyproject.toml`, so an old astral install is refused everywhere with the fix
named, not just inside project runs.

## Security notes

- The URL and credentials never enter git. The repo carries only the
  hostname flags and the (non-secret) vault item references.
- Every task whose output carries a captured value sets `no_log`.
- `tests/uv/test_lock_sources.py` fails the suite if any committed lock file
  references an index other than public PyPI — a work machine must never
  commit a re-lock performed against its mirror (spec.md § Data; the
  2026-09-24 skill-trust re-lock incident is the precedent).

## Verification

```bash
mise exec -- ansible-playbook -i localhost, apps/uv/tests/topic-metadata.yaml
mise exec -- ansible-playbook --syntax-check apps/uv/playbook.yaml
uv run --frozen pytest tests/uv -q
```

Debian renders and is syntax-checked, but has not been applied on a live
Debian machine (AGENTS.md § Cross-platform: say what was not run).
