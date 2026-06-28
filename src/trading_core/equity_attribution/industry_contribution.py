"""Industry-level attribution aggregation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import aggregate_groups, build_holding_rows


def build_industry_contribution_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    return {
        "snapshot_id": "A-SHARE-INDUSTRY-CONTRIBUTION-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "industry_level": "industry_level_1",
        "portfolios": aggregate_groups(rows, field="industry_level_1", label_field="industry_level_1"),
        "unclassified_industry_notes": "Missing industry_level_1 is mapped to Unclassified.",
        **ATTRIBUTION_FLAGS,
    }
