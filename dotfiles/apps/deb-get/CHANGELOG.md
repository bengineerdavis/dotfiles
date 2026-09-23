# deb-get — changelog

## Unreleased

### major_changes

- Re-created `apps/deb-get` as an `app`-tier topic for Debian-family systems.
  Installs/upgrades `deb-get` and resolves `DEBGET_TOKEN` from Bitwarden by
  default, with loud failures if the token or apt signing keys cannot be
  verified.

### minor_changes

- `DEBGET_TOKEN` resolution order: Bitwarden (default), 1Password (work via
  `debget_secrets_manager=1password`), `~/.localrc`, then environment
  variable. The topic never writes the token to disk.
- Added `apps/deb-get/tests/token-resolution.yaml` to validate the token chain.

### removed_features

- 2026-09-23: apt signing-key repair (`tasks/apt-auth.yaml`,
  `debget_known_keyrings`, `debget_auto_fix_apt_auth`,
  `debget_remove_managed_repos`) moved to the apt topic as `apt_keyrings`. As an
  app-tier topic this ran after the pkg-manager-tier `apt` update it was meant
  to protect, so it could never prevent the failure. Its tests went with it.

### bugfixes

- 2026-09-23: the removed repair wrote whatever the keyring URL returned and
  reported success. On 2026-09-16 it left a 0-byte HashiCorp keyring and a
  577 KB HTML page as the GitHub CLI keyring, at the right paths but with no
  key in them, so apt kept failing with NO_PUBKEY. The apt topic's replacement
  validates with gpg before writing.

### known_issues

- The makedeb prebuilt-mPR repository (`proget.makedeb.org`) occasionally
  returns HTTP 530. This is an upstream outage; the topic reports it but cannot
  repair the key.
