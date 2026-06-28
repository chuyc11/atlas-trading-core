"""Risk diagnostics for virtual portfolio holdings."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import ATTRIBUTION_FLAGS, TARGET_VERSION
from trading_core.equity_attribution.attribution_core import build_holding_rows, concentration_payload, symbol_set


def build_risk_diagnostics_snapshot(config: Any, inputs: Any) -> dict[str, Any]:
    rows = build_holding_rows(inputs)
    risk_symbols = symbol_set(inputs.candidates.get("risk_downgraded_candidates", []))
    excluded_symbols = symbol_set(inputs.candidates.get("excluded_universe", []))
    concentration = concentration_payload(rows, risk_downgraded_symbols=risk_symbols, excluded_symbols=excluded_symbols)["portfolios"]
    return {
        "diagnostics_id": "A-SHARE-RISK-DIAGNOSTICS-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": config.as_of_date,
        "mode": config.mode,
        "portfolios": {
            portfolio_id: {
                "weighted_average_risk_score": row["weighted_average_risk_score"],
                "high_risk_exposure": row["high_risk_exposure"],
                "risk_downgraded_exposure": row["risk_downgraded_exposure"],
                "excluded_universe_exposure": row["excluded_universe_exposure"],
                "diagnostic_flags": {
                    "contains_risk_downgraded": row["diagnostic_flags"]["contains_risk_downgraded"],
                    "contains_excluded_universe": row["diagnostic_flags"]["contains_excluded_universe"],
                    "high_risk_cluster": row["high_risk_exposure"] > 0.5,
                },
            }
            for portfolio_id, row in concentration.items()
        },
        "risk_downgraded_symbols_in_portfolio": sorted({str(row.get("symbol")) for row in rows if str(row.get("symbol")) in risk_symbols}),
        **ATTRIBUTION_FLAGS,
    }
