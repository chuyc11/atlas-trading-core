"""Portfolio concentration diagnostics."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows, concentration_payload, symbol_set


def build_portfolio_concentration_diagnostics(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    return {
        "diagnostics_id": "A-SHARE-PORTFOLIO-CONCENTRATION-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        **concentration_payload(
            rows,
            risk_downgraded_symbols=symbol_set(inputs.candidates.get("risk_downgraded_candidates", [])),
            excluded_symbols=symbol_set(inputs.candidates.get("excluded_universe", [])),
        ),
        **ATTRIBUTION_FLAGS,
    }
