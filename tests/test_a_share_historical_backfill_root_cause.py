from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import fake_price_provider_result, make_history_paths
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.historical_backfill_root_cause import diagnose_a_share_historical_backfill_coverage


def test_root_cause_diagnostic_detects_low_symbol_sample_failure(tmp_path: Path) -> None:
    paths = make_history_paths(tmp_path)
    backfill_a_share_daily_price_history(
        start_date="2023-01-01",
        end_date="2026-06-26",
        paths=paths,
        provider_result=fake_price_provider_result(symbols=["600000.SH"], periods=260),
    )

    result = diagnose_a_share_historical_backfill_coverage(paths=paths)

    assert result["diagnostic_id"] == "A-SHARE-HISTORICAL-BACKFILL-ROOT-CAUSE"
    assert result["historical_price_symbols"] == 1
    assert result["symbol_limit_detected"] is True
    assert any("sample" in cause.lower() for cause in result["confirmed_root_causes"])
