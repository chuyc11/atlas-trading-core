"""Historical A-share backfill plan and shared helpers."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import HISTORICAL_BASELINE_VERSION, HISTORICAL_BOUNDARY, HISTORICAL_TARGET_VERSION, RECOMMENDED_NEXT_VERSION, data_quality_dir, markdown_boundary, write_report
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


DEFAULT_TARGET_START_DATE = "2021-01-01"
DEFAULT_MINIMUM_START_DATE = "2023-01-01"
DEFAULT_END_DATE = "2026-06-26"


def build_a_share_historical_backfill_plan(
    *,
    target_start_date: str = DEFAULT_TARGET_START_DATE,
    minimum_start_date: str = DEFAULT_MINIMUM_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    payload = {
        "plan_id": "A-SHARE-HISTORICAL-BACKFILL-PLAN",
        "target_version": HISTORICAL_TARGET_VERSION,
        "baseline_version": HISTORICAL_BASELINE_VERSION,
        "target_start_date": target_start_date,
        "minimum_start_date": minimum_start_date,
        "end_date": end_date,
        "target_price_history_years": 5,
        "minimum_price_history_years": 3,
        "target_financial_quarters": 20,
        "minimum_financial_quarters": 12,
        "data_backfill_only": True,
        "scores_generated": False,
        "candidates_generated": False,
        "virtual_portfolio_generated": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "model_profit_guaranteed": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "boundary": dict(HISTORICAL_BOUNDARY),
    }
    json_path = data_quality_dir(paths) / "a_share_historical_backfill_plan.json"
    report_path = paths.outputs_dir / "equity_data_quality" / "A_SHARE_HISTORICAL_BACKFILL_PLAN.md"
    lines = [
        "# A-Share Historical Backfill Plan",
        "",
        f"- target_version: {HISTORICAL_TARGET_VERSION}",
        f"- baseline_version: {HISTORICAL_BASELINE_VERSION}",
        f"- target_start_date: {target_start_date}",
        f"- minimum_start_date: {minimum_start_date}",
        f"- end_date: {end_date}",
        "- data_backfill_only: true",
        "- scores_generated: false",
        "- candidates_generated: false",
        "- virtual_portfolio_generated: false",
        "",
        "## Boundary",
        *markdown_boundary(),
        "- Live trading ready: false.",
        "",
    ]
    return write_report(json_path, payload, report_path, "\n".join(lines))


def history_dirs(paths: ProjectPaths) -> dict[str, Any]:
    return {
        "market_history": paths.data_dir / "equity_market" / "history",
        "fundamental_history": paths.data_dir / "equity_fundamental" / "history",
        "market_history_outputs": paths.outputs_dir / "equity_market" / "history",
        "fundamental_history_outputs": paths.outputs_dir / "equity_fundamental" / "history",
    }
