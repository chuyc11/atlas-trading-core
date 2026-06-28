"""Boundary check for data refresh."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import REFRESH_BOUNDARY, TARGET_VERSION


def build_data_refresh_boundary_check(*, as_of_date: str, warnings: list[str] | None = None, blocking_reasons: list[str] | None = None) -> dict[str, Any]:
    blocking = blocking_reasons or []
    return {
        "boundary_id": "A-SHARE-DAILY-DATA-REFRESH-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **REFRESH_BOUNDARY,
        "forbidden_artifacts_present": [],
        "forbidden_wording_positive_hits": [],
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings or [],
    }
