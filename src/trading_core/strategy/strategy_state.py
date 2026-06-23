"""Strategy state machine constants."""

from __future__ import annotations


VALID_STATES = ("candidate", "shadow", "active_small", "active_normal", "paused", "retired")


def is_valid_state(state: str) -> bool:
    return state in VALID_STATES
