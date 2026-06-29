"""Portfolio summary card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_portfolio_summary_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    base = paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date
    nav = load_json(base / "portfolio_nav_snapshot.json")
    exposure = load_json(base / "portfolio_exposure_snapshot.json")
    portfolios = nav.get("portfolios", {})
    risk_downgraded = exposure.get("risk_downgraded_symbols_included", [])
    excluded = exposure.get("excluded_universe_symbols_included", [])
    blocking = []
    if risk_downgraded:
        blocking.append("risk_downgraded_symbols_included_non_empty")
    if excluded:
        blocking.append("excluded_universe_symbols_included_non_empty")
    return {
        "card_id": "PORTFOLIO_SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "status": "available" if portfolios else "missing_optional",
        "portfolio_count": len(portfolios) if isinstance(portfolios, dict) else 0,
        "performance_observed": not any(record.get("performance_not_yet_observed") for record in portfolios.values() if isinstance(record, dict)),
        "portfolios": {
            key: {
                "nav": _num(record.get("portfolio_nav")),
                "holdings_count": record.get("holdings_count", record.get("holding_count")),
                "cash_balance": _num(record.get("cash_balance")),
                "gross_exposure": _num(record.get("gross_exposure")),
            }
            for key, record in portfolios.items()
            if isinstance(record, dict)
        },
        "largest_holding_weight": exposure.get("largest_holding_weight"),
        "largest_industry_weight": exposure.get("largest_industry_weight"),
        "risk_downgraded_symbols_included": risk_downgraded or [],
        "excluded_universe_symbols_included": excluded or [],
        "blocking_reasons": blocking,
        "warnings": [] if portfolios else ["portfolio_tracking_missing_optional"],
    }


def _num(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
