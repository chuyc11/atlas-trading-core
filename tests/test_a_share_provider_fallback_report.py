from __future__ import annotations

from trading_core.equity_data_refresh.provider_fallback_report import build_provider_fallback_report


def test_provider_fallback_report_records_fallbacks() -> None:
    report = build_provider_fallback_report(as_of_date="2026-06-26", provider_execution_log={"records": [{"dataset_id": "daily_price", "fallback_used": True, "fallback_provider_id": "cached_panel_provider"}]})
    assert report["fallback_used"] is True
    assert report["fallback_count"] == 1
