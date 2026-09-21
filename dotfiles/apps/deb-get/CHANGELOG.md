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

### known_issues

- The makedeb prebuilt-mPR repository (`proget.makedeb.org`) occasionally
  returns HTTP 530. This is an upstream outage; the topic reports it but cannot
  repair the key.
