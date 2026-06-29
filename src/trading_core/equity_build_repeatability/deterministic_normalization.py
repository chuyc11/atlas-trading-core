"""Normalize generated fields before repeatability comparisons."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from trading_core.equity_build_repeatability.repeatability_config import TARGET_VERSION


NORMALIZED_FIELD_NAMES = {
    "generated_at",
    "started_at",
    "finished_at",
    "duration_seconds",
    "modified_at",
    "latest_modified_at",
    "sha256",
    "sha256_tree_hash",
    "records_before",
    "records_after",
}


def build_deterministic_field_normalization(*, as_of_date: str) -> dict:
    return {
        "normalization_id": "A-SHARE-DETERMINISTIC-FIELD-NORMALIZATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "normalized_fields": sorted(NORMALIZED_FIELD_NAMES),
        "timestamp_fields": ["generated_at", "started_at", "finished_at", "modified_at", "latest_modified_at"],
        "hash_fields": ["sha256", "sha256_tree_hash"],
        "normalization_applied": True,
    }


def normalized_json_hash(text: str) -> str | None:
    try:
        payload = json.loads(text)
    except Exception:
        return None
    normalized = normalize_value(payload)
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize_value(val)
            for key, val in sorted(value.items())
            if key not in NORMALIZED_FIELD_NAMES and not key.endswith("_at")
        }
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    return value

