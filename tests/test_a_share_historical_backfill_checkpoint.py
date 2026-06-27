from __future__ import annotations

from pathlib import Path

from a_share_historical_test_utils import fake_financial_provider_result, fake_price_provider_result, make_history_paths
from trading_core.equity_data import historical_backfill_scheduler as scheduler
from trading_core.equity_data.historical_backfill_checkpoint import write_backfill_checkpoint
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history


def test_checkpoint_resume_does_not_skip_unprocessed_symbols(tmp_path: Path, monkeypatch) -> None:
    paths = make_history_paths(tmp_path)
    calls: list[list[str]] = []
    write_backfill_checkpoint(
        paths,
        target_version="test",
        symbols_total=3,
        symbols_completed=["600000.SH"],
        symbols_failed=[],
        current_batch=1,
        complete=False,
    )

    def fake_fetch(symbols, **kwargs):
        calls.append(list(symbols))
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
                "failure_reason": "",
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
            provider_result=fake_financial_provider_result(symbols=["600000.SH"]),
        ),
    )

    scheduler.backfill_a_share_historical_panels_full_market(
        target_start_date="2023-01-01",
        minimum_start_date="2023-01-01",
        end_date="2026-06-26",
        batch_size=10,
        sample_size=3,
        resume=True,
        paths=paths,
    )

    assert calls
    assert "600000.SH" not in calls[0]
    assert calls[0]
