"""Score-bucket contribution aggregation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows, score_bucket_payload


def build_score_bucket_contribution_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    return {
        "snapshot_id": "A-SHARE-SCORE-BUCKET-CONTRIBUTION-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        **score_bucket_payload(rows),
        **ATTRIBUTION_FLAGS,
    }
