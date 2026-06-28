"""Weighted factor exposure diagnostics."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows, factor_exposure_payload


def build_factor_exposure_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    return {
        "snapshot_id": "A-SHARE-FACTOR-EXPOSURE-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        **factor_exposure_payload(rows),
        **ATTRIBUTION_FLAGS,
    }
