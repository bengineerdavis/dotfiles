"""The decision itself, as pure functions.

Kept free of I/O so the precedence order can be tested exhaustively without a
network, a filesystem, or a config file. `cli.py` does the gathering; this module
only judges.
"""

from __future__ import annotations

import dataclasses
import enum


class Verdict(enum.Enum):
    PERMITTED = 0
    DENIED = 1


# SPDX identifiers, by what they mean for putting someone else's code on a
# machine and possibly redistributing it inside a shared skill library.
PERMISSIVE = frozenset(
    {
        "MIT",
        "MIT-0",
        "Apache-2.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "ISC",
        "0BSD",
        "Unlicense",
        "CC0-1.0",
        "BSL-1.0",  # Boost, not Business
    }
)

# Open, but redistribution carries obligations. Vendoring a skill into a library
# every agent loads IS redistribution, so these need a deliberate opt-in rather
# than arriving silently under "it's open source".
COPYLEFT = frozenset(
    {
        "GPL-2.0",
        "GPL-3.0",
        "GPL-2.0-only",
        "GPL-3.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-or-later",
        "AGPL-3.0",
        "AGPL-3.0-only",
        "AGPL-3.0-or-later",
        "LGPL-2.1",
        "LGPL-3.0",
        "LGPL-2.1-or-later",
        "LGPL-3.0-or-later",
        "MPL-2.0",
        "EPL-2.0",
        "CC-BY-SA-4.0",
    }
)

# Source-available and NOT open, however much they read like it. This is the
# tier most often mistaken for permissive — the source is right there and the
# licence has a friendly name. Sentry ships some of its own products this way.
SOURCE_AVAILABLE = frozenset(
    {
        "BUSL-1.1",
        "BSL-1.1",
        "SSPL-1.0",
        "Elastic-2.0",
        "FSL-1.1",
        "FSL-1.1-MIT",
        "FSL-1.1-ALv2",
        "Commons-Clause",
        "RSAL",
    }
)

# Not an SPDX tier — these are what a skill writes when it is declaring that it
# is nobody else's to copy. Matched case-insensitively because this field is
# prose written by hand, not a generated identifier. Kept separate from UNKNOWN
# so the report can say "it told us it is proprietary" rather than "we found
# nothing": the two look identical in a verdict and could not be less alike when
# someone is deciding what to do next.
PROPRIETARY = frozenset(
    {
        "proprietary",
        "all-rights-reserved",
        "all rights reserved",
        "unlicensed",
    }
)


class Tier(enum.Enum):
    PERMISSIVE = "permissive"
    COPYLEFT = "copyleft"
    SOURCE_AVAILABLE = "source-available"
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"


def licence_tier(spdx: str | None) -> Tier:
    """Classify an SPDX id.

    Absent is not permissive. No licence, or GitHub's `NOASSERTION`, means all
    rights reserved — the most restrictive position there is, not the least. A
    checker that read a missing licence as "nothing forbids this" would approve
    precisely the material it exists to catch.
    """
    if not spdx or spdx.strip().upper() in {"NOASSERTION", "NONE", "UNKNOWN", ""}:
        return Tier.UNKNOWN
    key = spdx.strip()
    if key.lower() in PROPRIETARY:
        return Tier.PROPRIETARY
    if key in PERMISSIVE:
        return Tier.PERMISSIVE
    if key in COPYLEFT:
        return Tier.COPYLEFT
    if key in SOURCE_AVAILABLE:
        return Tier.SOURCE_AVAILABLE
    return Tier.UNKNOWN


@dataclasses.dataclass(frozen=True)
class Decision:
    verdict: Verdict
    rule: str  # which level decided, for the audit trail
    reason: str  # what to tell a human

    @property
    def permitted(self) -> bool:
        return self.verdict is Verdict.PERMITTED


def source_matches(pattern: str, source: str) -> bool:
    """`owner/repo` matches that repo; a bare `owner` matches the whole org."""
    pattern, source = pattern.strip().lower(), source.strip().lower()
    if "/" in pattern:
        return pattern == source
    return source.split("/", 1)[0] == pattern


def decide(
    source: str,
    skill: str | None,
    config: dict,
    spdx: str | None = None,
) -> Decision:
    """Apply the trust levels in precedence order, failing closed at the bottom.

    The order is deliberate and the first level is the reason for it: a ban is a
    judgement about a publisher, and it has to outrank the paperwork. A denied
    source carrying an impeccable MIT licence is still denied, because the
    licence was never what the ban was about.
    """
    for pattern in config.get("deny_sources") or []:
        if source_matches(pattern, source):
            return Decision(
                Verdict.DENIED,
                "deny_sources",
                f'"{source}" matches the banned source "{pattern}". A ban '
                "outranks approval and licence both; nothing from here installs.",
            )

    excludes = config.get("exclude") or {}
    if skill:
        for pattern, names in excludes.items():
            if source_matches(pattern, source) and skill in (names or []):
                return Decision(
                    Verdict.DENIED,
                    "exclude",
                    f'"{skill}" is vetoed from the otherwise approved source '
                    f'"{source}".',
                )

    for pattern in config.get("approved_sources") or []:
        if source_matches(pattern, source):
            return Decision(
                Verdict.PERMITTED,
                "approved_sources",
                f'"{source}" matches the approved source "{pattern}".',
            )

    tier = licence_tier(spdx)
    if tier is Tier.PERMISSIVE:
        return Decision(
            Verdict.PERMITTED,
            "licence",
            f'"{source}" is not named, but its licence {spdx} is permissive.',
        )
    if tier is Tier.COPYLEFT:
        if (config.get("licences") or {}).get("allow_copyleft"):
            return Decision(
                Verdict.PERMITTED,
                "licence",
                f'"{source}" is {spdx}; copyleft is allowed by config.',
            )
        return Decision(
            Verdict.DENIED,
            "licence",
            f'"{source}" is {spdx}. Copyleft is open, but vendoring into a '
            "shared library is redistribution and carries obligations, so it "
            "needs licences.allow_copyleft or an explicit approval.",
        )
    if tier is Tier.SOURCE_AVAILABLE:
        return Decision(
            Verdict.DENIED,
            "licence",
            f'"{source}" is {spdx} — source-available, not open source, '
            "however much it reads like it.",
        )
    if tier is Tier.PROPRIETARY:
        return Decision(
            Verdict.DENIED,
            "licence",
            f'"{source}" declares itself {spdx}. It is not unlicensed by '
            "oversight — it is someone else's, deliberately. Nothing here can "
            "approve it; the owner can.",
        )
    return Decision(
        Verdict.DENIED,
        "default",
        f'"{source}" is not approved and has no licence this tool recognises '
        f"({spdx or 'none found'}). Absent is not permissive: unlicensed means "
        "all rights reserved. Approve the source explicitly if you have another "
        "basis for trusting it.",
    )
