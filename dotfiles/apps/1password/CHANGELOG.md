# 1password — changelog

## Unreleased

### major_changes

- Added `apps/1password` as an `app`-tier dependency-provider topic for the
  1Password CLI (`op`) on Debian-family work machines. The binary itself is
  managed by the mise topic; this topic verifies it and fails loudly if it is
  missing.
