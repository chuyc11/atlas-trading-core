"""Risk-bucket contribution aggregation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows, risk_bucket_payload, symbol_set


def build_risk_bucket_contribution_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    risk_symbols = symbol_set(inputs.candidates.get("risk_downgraded_candidates", []))
    return {
        "snapshot_id": "A-SHARE-RISK-BUCKET-CONTRIBUTION-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        **risk_bucket_payload(rows, risk_symbols),
        **ATTRIBUTION_FLAGS,
    }
