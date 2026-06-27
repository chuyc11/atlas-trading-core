"""One-command A-share historical panel backfill."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data.historical_adjusted_price import backfill_a_share_adjusted_price_history
from trading_core.equity_data.historical_backfill_scheduler import backfill_a_share_historical_panels_full_market
from trading_core.equity_data.historical_daily_basic import backfill_a_share_daily_basic_history
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.feature_readiness_audit import audit_a_share_feature_readiness
from trading_core.equity_data_quality.historical_coverage_audit import audit_a_share_historical_panel_coverage
from trading_core.equity_data_quality.history_manifest import build_a_share_historical_backfill_plan
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def backfill_a_share_historical_panels(
    *,
    target_start_date: str,
    minimum_start_date: str,
    end_date: str,
    paths: ProjectPaths | None = None,
    max_symbols: int | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    plan = build_a_share_historical_backfill_plan(
        target_start_date=target_start_date,
        minimum_start_date=minimum_start_date,
        end_date=end_date,
        paths=paths,
    )
    daily_price = backfill_a_share_daily_price_history(start_date=target_start_date, end_date=end_date, paths=paths, max_symbols=max_symbols)
    adjusted = backfill_a_share_adjusted_price_history(start_date=target_start_date, end_date=end_date, paths=paths)
    daily_basic = backfill_a_share_daily_basic_history(start_date=minimum_start_date, end_date=end_date, paths=paths)
    financials = backfill_a_share_financial_history(start_date=target_start_date, end_date=end_date, paths=paths)
    coverage = audit_a_share_historical_panel_coverage(paths=paths)
    readiness = audit_a_share_feature_readiness(paths=paths)
    return {
        "backfill_id": "A-SHARE-HISTORICAL-PANELS-BACKFILL",
        "plan": plan,
        "daily_price": daily_price,
        "adjusted_price": adjusted,
        "daily_basic": daily_basic,
        "financials": financials,
        "coverage_audit": coverage,
        "feature_readiness_audit": readiness,
        "overall_passed": bool(coverage["overall_passed"] and readiness["overall_passed"]),
    }
