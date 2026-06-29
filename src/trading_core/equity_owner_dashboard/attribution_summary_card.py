"""Attribution summary card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_attribution_summary_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    summary = load_json(paths.data_dir / "equity_attribution" / "daily" / as_of_date / "attribution_summary.json")
    status = "missing_optional"
    if summary:
        status = "structural_diagnostics_available" if summary.get("structural_diagnostics_available") else "limited_history"
    return {
        "card_id": "ATTRIBUTION_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "status": status,
        "limited_history": summary.get("limited_history"),
        "structural_diagnostics_available": summary.get("structural_diagnostics_available"),
        "realized_performance_attribution_available": summary.get("realized_performance_attribution_available"),
        "risk_downgraded_symbols_in_portfolio": summary.get("risk_downgraded_symbols_in_portfolio", []),
        "excluded_universe_exposure": summary.get("diagnostic_flags", {}).get("excluded_universe_exposure", 0),
        "weight_reconciliation_status": "available" if summary.get("portfolio_weight_sums") else "unavailable",
        "concentration_diagnostics": summary.get("diagnostic_flags", {}),
        "liquidity_diagnostics": summary.get("liquidity_portfolios", {}),
        "industry_diagnostics": summary.get("industry_portfolios", {}),
        "structural_diagnostics_are_not_trade_signals": True,
        "warnings": list(summary.get("warnings", [])) if summary else ["attribution_missing_optional"],
    }

