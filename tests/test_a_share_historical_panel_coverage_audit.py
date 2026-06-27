from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import fake_financial_provider_result, fake_price_provider_result, make_history_paths
from trading_core.equity_data.historical_adjusted_price import backfill_a_share_adjusted_price_history
from trading_core.equity_data.historical_daily_basic import backfill_a_share_daily_basic_history
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.historical_coverage_audit import audit_a_share_historical_panel_coverage
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history


def _build_history(paths) -> None:
    backfill_a_share_daily_price_history(start_date="2023-01-01", end_date="2026-06-26", paths=paths, provider_result=fake_price_provider_result())
    backfill_a_share_adjusted_price_history(start_date="2023-01-01", end_date="2026-06-26", paths=paths)
    backfill_a_share_daily_basic_history(start_date="2023-01-01", end_date="2026-06-26", paths=paths)
    backfill_a_share_financial_history(start_date="2021-01-01", end_date="2026-06-26", paths=paths, provider_result=fake_financial_provider_result())


def test_a_share_historical_panel_coverage_audit_passes_with_test_thresholds(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    _build_history(paths)
    result = audit_a_share_historical_panel_coverage(paths=paths, minimum_price_symbols=3, minimum_trading_days=200, minimum_120d_symbols=3, minimum_250d_symbols=3)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["coverage"]["symbols_with_250d_history"] == 3


def test_a_share_historical_panel_coverage_audit_fails_when_minimum_not_met(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    _build_history(paths)
    result = audit_a_share_historical_panel_coverage(paths=paths)
    assert result["overall_passed"] is False
    assert "price_history_symbols_minimum=false" in result["blocking_reasons"]
