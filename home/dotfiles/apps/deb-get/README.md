# deb-get

[deb-get](https://github.com/wimpysworld/deb-get) topic: installs and refreshes the
`deb-get` package manager on Debian-family systems.

`DEBGET_TOKEN` (a GitHub PAT) is required or `deb-get update` hits the GitHub
API rate limit. The topic resolves it from Bitwarden by default and fails with a
clear message if it cannot.

Signing keys for the third-party apt repos deb-get adds (GitHub CLI, HashiCorp,
...) are **not** repaired here any more: that moved to the apt topic
(`apps/apt`, `apt_keyrings`), which runs before any cache refresh. From this
app-tier topic the repair always ran too late.

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

# Tear down (the deb-get package only)
./run-role.sh deb-get remove
```

## Required GitHub token

Create a GitHub Personal Access Token at https://github.com/settings/tokens. No
scopes are required; the token is only used for public repository metadata so
deb-get can list available packages.

The topic resolves `DEBGET_TOKEN` in this order:

1. Explicit `-e debget_token=...` override.
2. **Bitwarden** (default on personal machines): `bw get password DEBGET_TOKEN`.  
   Requires `bw` on PATH. If `BW_SESSION` is not already exported, the topic
   will prompt for your master password at provision time.
3. **1Password** (work machines): pass `-e debget_secrets_manager=1password`.  
   Requires `op` on PATH. If a signed-in session or `OP_SERVICE_ACCOUNT_TOKEN`
   is not available, the topic will prompt for your master password.
4. **`~/.localrc`**: `export DEBGET_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx`.
5. **Environment variable**: `export DEBGET_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx`.

The topic never writes the token to disk itself.

## After pulling on a new Mac

```bash
chezmoi update
cd "$(chezmoi source-path)"
./run-role.sh bitwarden   # or mise, which installs the bw binary
./run-role.sh deb-get
```

If `BW_SESSION` is not already set, the run will pause and ask for your
Bitwarden master password. The session token is kept in memory only.

## Configuration


| Variable | Default | Meaning |
|---|---|---|
| `debget_secrets_manager` | `bitwarden` | `bitwarden`, `1password`, `localrc`, or `env` |
| `debget_bitwarden_item` | `DEBGET_TOKEN` | Bitwarden item name (password field) |
| `debget_onepassword_uri` | `op://Personal/DEBGET_TOKEN/password` | 1Password secret reference |

## What this topic owns

| Artefact | Path |
|---|---|
| package | `deb-get` via the official installer |
| helper packages | `curl`, `jq`, `lsb-release`, `wget` |

Teardown removes only the `deb-get` package. Sources deb-get added are left in
place: their packages outlive deb-get, and the apt topic keeps their keys valid.

## Tests

Unit tests live in `apps/deb-get/tests/` and do not mutate the system:

```bash
mise exec -- ansible-playbook apps/deb-get/tests/topic-metadata.yaml
mise exec -- ansible-playbook apps/deb-get/tests/token-resolution.yaml
```
