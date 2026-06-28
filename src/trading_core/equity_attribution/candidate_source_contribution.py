"""Candidate-source contribution aggregation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import aggregate_groups, build_holding_rows


def build_candidate_source_contribution_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    return {
        "snapshot_id": "A-SHARE-CANDIDATE-SOURCE-CONTRIBUTION-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "portfolios": aggregate_groups(rows, field="candidate_source", label_field="candidate_source"),
        **ATTRIBUTION_FLAGS,
    }
