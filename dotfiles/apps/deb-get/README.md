# deb-get

[deb-get](https://github.com/wimpysworld/deb-get) topic: installs and refreshes the
`deb-get` package manager on Debian-family systems, and loudly handles the two
auth problems that otherwise break `apt update` / `apt dist-upgrade`:

1. **GitHub PAT** — `DEBGET_TOKEN` is required or `deb-get update` will hit the
   GitHub API rate limit. The topic resolves the token from Bitwarden by default
   and fails with a clear message if it cannot be resolved.
2. **Missing apt signing keys** — `deb-get` installs third-party apt repos
   (GitHub CLI, HashiCorp, etc.). The topic repairs the keyrings it knows about
   and fails loudly if any repository is still unsigned.

## Installation

From a Debian or Ubuntu machine, with a `DEBGET_TOKEN` available (see below):

```bash
./run-role.sh deb-get
```

A clean provision run with the parent playbook also works:

```bash
ansible-playbook playbook.yaml --tags provision
```

## Usage

```bash
# Just the topic (bootstrap + prerequisites + upgrade + install)
./run-role.sh deb-get

# Only refresh deb-get repos and keys (no bootstrap confirmation prompt)
./run-role.sh deb-get upgrade

# Tear down (package only, by default)
./run-role.sh deb-get remove

# Tear down including managed apt sources/keyrings
ansible-playbook apps/deb-get/playbook.yaml --tags remove -e debget_remove_managed_repos=true
```

## Required GitHub token

Create a GitHub Personal Access Token at https://github.com/settings/tokens. No
scopes are required; the token is only used for public repository metadata so
deb-get can list available packages.

The topic resolves `DEBGET_TOKEN` in this order:

1. Explicit `-e debget_token=...` override.
2. **Bitwarden** (default on personal machines): `bw get password DEBGET_TOKEN`.  
   Requires `bw` on PATH and an unlocked vault. The easiest way is to add  
   `export BW_SESSION=...` to `~/.localrc` after running `bw unlock --raw`.
3. **1Password** (work machines): pass `-e debget_secrets_manager=1password`.  
   Requires `op` on PATH and a signed-in session or `OP_SERVICE_ACCOUNT_TOKEN`.
4. **`~/.localrc`**: `export DEBGET_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx`.
5. **Environment variable**: `export DEBGET_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx`.

The topic never writes the token to disk itself.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `debget_secrets_manager` | `bitwarden` | `bitwarden`, `1password`, `localrc`, or `env` |
| `debget_bitwarden_item` | `DEBGET_TOKEN` | Bitwarden item name (password field) |
| `debget_onepassword_uri` | `op://Personal/DEBGET_TOKEN/password` | 1Password secret reference |

## Known keyrings

The topic knows the official signing keys for these commonly configured repos:

| Repository | Keyring URL |
|---|--|
| GitHub CLI | `https://cli.github.com/packages/githubcli-archive-keyring.gpg` |
| HashiCorp | `https://apt.releases.hashicorp.com/gpg` |

It finds the correct destination path by reading the `signed-by=` option in
existing `.list` files or the `Signed-By:` field in `.sources` files, so it works
whether the source uses the legacy `/usr/share/keyrings/` layout or the modern
`/etc/apt/keyrings/` layout.

To add more repos, edit `apps/deb-get/vars/main.yaml` and extend
`debget_known_keyrings`.

## What this topic owns

| Artefact | Path |
|---|---|
| package | `deb-get` via the official installer |
| helper packages | `curl`, `jq`, `lsb-release`, `wget` |
| keyring files | paths discovered from `/etc/apt/sources.list.d/*.{list,sources}` |

Teardown removes only the `deb-get` package by default. Managed apt sources and
keyrings are left in place unless you set `debget_remove_managed_repos=true`.

## Tests

Unit tests live in `apps/deb-get/tests/` and do not mutate the system:

```bash
mise exec -- ansible-playbook apps/deb-get/tests/topic-metadata.yaml
mise exec -- ansible-playbook apps/deb-get/tests/no-pubkey-parsing.yaml
mise exec -- ansible-playbook apps/deb-get/tests/keyring-path-detection.yaml
mise exec -- ansible-playbook apps/deb-get/tests/token-resolution.yaml
```
