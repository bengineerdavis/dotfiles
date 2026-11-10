"""What a client CLI actually said, in the order that names the cause.

A client wiring step records its result with `failed_when: false` and
then fails in a separate task, so the message has to come from the
result dict. Reading `stderr` alone loses the cause in the commonest
case.

`ansible.builtin.command` reports a missing binary as rc 2 with an EMPTY
stderr and the reason in `msg` ("Error executing command."), so a
stderr-only message prints "nothing on stderr" for the one failure that
matters most. That is how a Debian box with no `claude` reported the
failure (measured 2026-11-09).

Order: a real stderr line if the client wrote one, else stdout (some
clients explain a refusal on stdout, e.g. `plugin install` printing
"Aborted."), else `msg` (the module's own explanation, which is all a
missing binary provides).

`nothing` is supplied by the caller so each failure names its own
recovery command rather than a generic one.
"""


def client_said(result, nothing="no output on stdout or stderr"):
    """Return the most useful explanation a failed client call has."""
    if not isinstance(result, dict):
        return str(result) if result else nothing
    for field in ("stderr", "stdout", "msg"):
        value = result.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return nothing


class FilterModule:
    def filters(self):
        return {"client_said": client_said}
