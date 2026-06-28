"""Liquidity diagnostics for virtual portfolio holdings."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows, liquidity_bucket_payload


def build_liquidity_diagnostics_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    payload = liquidity_bucket_payload(rows)
    return {
        "diagnostics_id": "A-SHARE-LIQUIDITY-DIAGNOSTICS-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "portfolios": payload["liquidity_diagnostics"],
        **ATTRIBUTION_FLAGS,
    }
