"""Return OpenCode's plugin response as a dictionary."""

import json


def json_or_empty(value):
    """Return {} unless the CLI returns a JSON object."""
    try:
        parsed = json.loads(value)
    # The pipx Ansible controller may predate PEP 758.
    except (json.JSONDecodeError, TypeError):  # fmt: skip
        return {}
    return parsed if isinstance(parsed, dict) else {}


class FilterModule:
    def filters(self):
        return {"json_or_empty": json_or_empty}
