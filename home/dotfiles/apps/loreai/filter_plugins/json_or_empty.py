"""Return OpenCode's plugin list, or an empty list for invalid input."""

import json


def json_or_empty(value):
    """Return an empty response when the CLI output is not JSON."""
    try:
        return json.loads(value)
    except json.JSONDecodeError, TypeError:
        return {}


class FilterModule:
    def filters(self):
        return {"json_or_empty": json_or_empty}
