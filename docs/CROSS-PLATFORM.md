# Cross-platform traps

What has actually bitten when running on both macOS and Debian. The rules that
bind are in `AGENTS.md` § Cross-platform; this is the evidence behind them.

## Per-user services

**A per-user launchd agent maps to a systemd *user* timer, not a system one.**
Same ownership, no root. It only fires while the user has a session, so report
the `loginctl enable-linger` fix rather than silently changing login behaviour.

## Network tools

**`nc -U` needs `netcat-openbsd`.** Debian ships two providers and
`netcat-traditional` has no `-U`; probe the `nc` on `PATH`, because alternatives
can point at the wrong build.

## Command flags

**BSD and GNU flags differ** for `script`, `stat`, `sed -i` and `mktemp`. Prefer
Python over a portability shim, or try both forms.

## Python floors

A deployed script runs on the interpreter the host provides, not the one you
prefer. `/usr/bin/python3` is 3.10.12 on this Debian 12 host and the apt topic
invokes it by absolute path under `become`, where a mise python on `PATH` is not
the system one. `tests/test_python_floors.py` enforces the floor per file.
