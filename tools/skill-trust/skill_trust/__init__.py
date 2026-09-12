"""Decide whether an agent skill may be installed on this machine."""

from .decide import Decision, Verdict, decide, licence_tier

__all__ = ["Decision", "Verdict", "decide", "licence_tier"]
