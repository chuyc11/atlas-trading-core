"""Holding-level contribution snapshot."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows


def build_holding_contribution_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    return {
        "snapshot_id": "A-SHARE-HOLDING-CONTRIBUTION-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "limited_history": True,
        "realized_performance_attribution_available": False,
        "records": rows,
        "portfolio_weight_sums": _weight_sums(rows),
        **ATTRIBUTION_FLAGS,
    }


def _weight_sums(rows: list[dict[str, Any]]) -> dict[str, float]:
    sums: dict[str, float] = {}
    for row in rows:
        sums[row["portfolio_id"]] = sums.get(row["portfolio_id"], 0.0) + float(row.get("actual_weight") or 0.0)
    return sums
