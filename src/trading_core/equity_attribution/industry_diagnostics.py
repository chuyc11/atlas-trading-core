"""Industry diagnostics for virtual portfolio holdings."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import aggregate_groups, build_holding_rows


def build_industry_diagnostics_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    grouped = aggregate_groups(rows, field="industry_level_1", label_field="industry_level_1")
    portfolios = {}
    for portfolio_id, records in grouped.items():
        unclassified = sum(float(row["weight"]) for row in records if str(row["industry_level_1"]).lower() == "unclassified")
        max_weight = max([float(row["weight"]) for row in records], default=0.0)
        portfolios[portfolio_id] = {
            "industry_count": len(records),
            "max_industry_weight": max_weight,
            "unclassified_industry_exposure": unclassified,
            "diagnostic_flags": {
                "concentrated_industry": max_weight > 0.35,
                "unclassified_industry_high": unclassified > 0.50,
            },
            "industries": records,
        }
    return {
        "diagnostics_id": "A-SHARE-INDUSTRY-DIAGNOSTICS-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "portfolios": portfolios,
        **ATTRIBUTION_FLAGS,
    }
