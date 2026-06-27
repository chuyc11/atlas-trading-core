from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import fake_financial_provider_result, fake_price_provider_result, make_history_paths
from trading_core.equity_data import historical_backfill_scheduler as scheduler
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history


def test_full_market_scheduler_sample_mode_writes_checkpoint_and_manifest(tmp_path: Path, monkeypatch) -> None:
    paths = make_history_paths(tmp_path)

    def fake_fetch(symbols, **kwargs):
        result = fake_price_provider_result(symbols=symbols, periods=260)
        result["providers_attempted"] = ["fixture_history_provider"]
        result["providers_succeeded"] = ["fixture_history_provider"]
        result["provider_breakdown"] = {"fixture_history_provider": {"attempted_symbol_count": len(symbols), "succeeded_symbol_count": len(symbols), "failed_symbol_count": 0}}
        result["symbol_results"] = [
            {
                "symbol": symbol,
                "provider": "fixture_history_provider",
                "provider_attempted": True,
                "provider_succeeded": True,
                "provider_failed": False,
                "row_count": 260,
                "first_date": "2023-01-02",
                "last_date": "2023-12-29",
                "failure_reason": "",
                "last_attempted_at": "2026-06-26T00:00:00Z",
            }
            for symbol in symbols
        ]
        return result

    monkeypatch.setattr(scheduler, "fetch_price_history_with_fallback", fake_fetch)
    monkeypatch.setattr(
        scheduler,
        "backfill_a_share_financial_history",
        lambda **kwargs: backfill_a_share_financial_history(
            paths=paths,
            start_date=kwargs["start_date"],
            end_date=kwargs["end_date"],
            provider_result=fake_financial_provider_result(symbols=["600000.SH", "688001.SH"]),
        ),
    )

    result = scheduler.backfill_a_share_historical_panels_full_market(
        target_start_date="2023-01-01",
        minimum_start_date="2023-01-01",
        end_date="2026-06-26",
        batch_size=1,
        sample_size=2,
        paths=paths,
    )

    assert result["sample_mode"] is True
    assert result["release_eligible"] is False
    assert result["checkpoint"]["symbols_completed_count"] == 2
    assert result["symbol_manifest"]["summary"]["symbols_succeeded"] == 2
    assert (paths.data_dir / "equity_data_quality" / "backfill_batches" / "batch_0001_manifest.json").exists()
