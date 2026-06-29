"""Date alignment checks for the daily ops center."""

from __future__ import annotations

from typing import Any

from trading_core.equity_ops_center.ops_config import TARGET_VERSION


def build_ops_date_alignment(*, as_of_date: str, payloads: dict[str, Any], allow_date_mismatch: bool = False) -> dict[str, Any]:
    records = []
    for key, payload in payloads.items():
        if not isinstance(payload, dict):
            continue
        if key.endswith("_audit") or "config" in key or "manifest" in key or "summary" in key or "readiness" in key:
            records.append(
                {
                    "artifact_id": key,
                    "as_of_date": payload.get("as_of_date"),
                    "resolved_as_of_date": payload.get("resolved_as_of_date", payload.get("as_of_date")),
                    "aligned": _aligned(payload, as_of_date),
                }
            )
    mismatches = [row["artifact_id"] for row in records if not row["aligned"]]
    return {
        "alignment_id": "A-SHARE-DAILY-OPS-CENTER-DATE-ALIGNMENT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allow_date_mismatch": allow_date_mismatch,
        "date_records": records,
        "all_dates_aligned": not mismatches,
        "blocking_reasons": [] if (not mismatches or allow_date_mismatch) else [f"date_mismatch:{item}" for item in mismatches],
    }


def _aligned(payload: dict[str, Any], as_of_date: str) -> bool:
    actual = payload.get("as_of_date")
    resolved = payload.get("resolved_as_of_date", actual)
    return (actual in {None, as_of_date}) and (resolved in {None, as_of_date})
