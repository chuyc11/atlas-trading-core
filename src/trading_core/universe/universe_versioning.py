"""Universe version helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def stable_universe_id(universe: dict[str, Any]) -> str:
    if universe.get("universe_id"):
        return str(universe["universe_id"])
    symbols = sorted(item["symbol"] for item in universe.get("symbols", []))
    # This digest is a reproducible label, not a security or integrity check.
    digest = hashlib.sha1(json.dumps(symbols).encode("utf-8"), usedforsecurity=False).hexdigest()[:8]
    return f"universe_{digest}"


def stamp_record_with_universe(record: dict[str, Any], universe: dict[str, Any]) -> dict[str, Any]:
    stamped = dict(record)
    stamped["universe_id"] = stable_universe_id(universe)
    stamped["universe_effective_date"] = universe.get("effective_date")
    return stamped
