# bitwarden — changelog

## Unreleased

### major_changes

- Added `apps/bitwarden` as an `app`-tier dependency-provider topic for the
  Bitwarden CLI (`bw`) on Debian-family systems. The binary itself is managed
  by the mise topic; this topic verifies it and fails loudly if it is missing.

### minor_changes

- Marked topic as supported on Darwin as well as Debian.
