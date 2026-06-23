"""Point-in-time metadata normalization."""

from __future__ import annotations

from datetime import datetime
from typing import Any


PIT_FIELDS = ("event_time", "publish_time", "available_time", "as_of_time")


def normalize_pit_record(record: dict[str, Any], default_time: str | None = None) -> dict[str, Any]:
    normalized = dict(record)
    missing = [field for field in PIT_FIELDS if not normalized.get(field)]
    if missing:
        fallback = default_time or normalized.get("date") or normalized.get("fetched_at")
        for field in missing:
            normalized[field] = fallback
        normalized["pit_quality"] = "weak"
        normalized["pit_missing_fields"] = missing
    else:
        normalized["pit_quality"] = "strong"
        normalized["pit_missing_fields"] = []
    return normalized


def _parse_time(value: str) -> datetime:
    text = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return datetime.strptime(text[:10], "%Y-%m-%d")


def is_available(record: dict[str, Any], decision_time: str) -> bool:
    normalized = normalize_pit_record(record)
    available = normalized.get("available_time")
    if not available:
        return False
    return _parse_time(str(available)) <= _parse_time(decision_time)
