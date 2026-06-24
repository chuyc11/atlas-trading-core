from __future__ import annotations

from pathlib import Path

from trading_core.backtest.event_backtester import date_range
from trading_core.evaluation.dry_run_validation_report import build_dry_run_validation_report
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl


def _seed_global_inputs(root: Path, day: str) -> None:
    data_dir = root / "work" / "global-briefing" / "data"
    write_jsonl(
        data_dir / f"macro_signals-{day}.jsonl",
        [
            {
                "macro_signal_id": f"MACRO-{day}",
                "date": day,
                "region": "CHINA",
                "confidence": "medium",
                "affected_assets": ["510300.SH"],
                "risk_flags": [],
                "status": "open",
            }
        ],
    )
    write_json(
        data_dir / f"china-market-snapshot-{day}.json",
        {
            "provider": "test",
            "items": [
                {"symbol": "510300.SH", "market": "A_SHARE", "price": 4.0, "previous_close": 3.99, "data_status": "ok"},
                {"symbol": "000300.SH", "market": "A_SHARE_INDEX", "price": 5000.0, "previous_close": 4990.0, "data_status": "ok"},
            ],
        },
    )


def _seed_run_day(root: Path, day: str, *, duplicate_id: str | None = None, shadow_mutation: bool = False) -> None:
    paths = project_paths(root)
    order_id = duplicate_id or f"ORD-{day}-001"
    trade_id = duplicate_id or f"TRD-{day}-001"
    write_json(
        paths.dated_json("runtime", "health", day),
        {
            "date": day,
            "errors": [],
            "input_files_found": [],
            "input_files_missing": [],
            "trading_signals_count": 1,
            "orders_count": 1,
            "trades_count": 1,
            "rejected_orders_count": 0,
            "fallback_prices_count": 0,
            "stale_prices_count": 0,
            "missing_prices_count": 0,
            "portfolio_total_asset": 100000.0,
        },
    )
    write_json(
        paths.dated_json("portfolios", "portfolio", day),
        {
            "date": day,
            "cash": 100000.0,
            "market_value": 0.0,
            "total_asset": 100000.0,
            "positions": [],
        },
    )
    write_jsonl(paths.dated_jsonl("signals", "trading_signals", day), [{"signal_id": f"SIG-{day}", "date": day}])
    write_jsonl(
        paths.dated_jsonl("orders", "orders", day),
        [{"order_id": order_id, "date": day, "status": "submitted", "side": "BUY", "symbol": "510300.SH"}],
    )
    write_jsonl(
        paths.dated_jsonl("trades", "trades", day),
        [{"trade_id": trade_id, "order_id": order_id, "date": day, "side": "BUY", "symbol": "510300.SH", "filled_price": 4.0, "filled_quantity": 100}],
    )
    write_json(paths.dated_json("snapshots", "data_quality", day), {"limitations": []})
    write_json(paths.data_dir / "evolution" / f"evolution-summary-{day}.json", {"rule_memory": {"rules": []}})
    if shadow_mutation:
        write_jsonl(paths.data_dir / "experiments" / f"shadow_signals-{day}.jsonl", [{"signal_id": "SHADOW", "cash": 1.0}])


def _seed_clean_days(root: Path, days: list[str]) -> None:
    for day in days:
        _seed_global_inputs(root, day)
        _seed_run_day(root, day)


def test_dry_run_validation_report_passes_clean_30_day_run(tmp_path: Path) -> None:
    days = date_range("2026-01-01", "2026-02-20")[:30]
    _seed_clean_days(tmp_path, days)

    result = build_dry_run_validation_report(days[0], days[-1], project_paths(tmp_path), execute_missing_runs=False)

    assert result["dry_run_30d_passed"] is True
    assert result["actual_run_days"] == 30
    assert result["release_blocking_reasons"] == []
    assert Path(result["report_path"]).exists()
    assert Path(result["json_path"]).exists()
    assert read_json(Path(result["json_path"]))["dry_run_30d_passed"] is True


def test_dry_run_validation_report_blocks_when_coverage_is_below_30_days(tmp_path: Path) -> None:
    days = date_range("2026-06-23", "2026-06-24")
    _seed_clean_days(tmp_path, days)

    result = build_dry_run_validation_report("2026-06-23", "2026-06-24", project_paths(tmp_path), execute_missing_runs=False)

    assert result["dry_run_30d_passed"] is False
    assert "actual_run_days_below_30" in result["release_blocking_reasons"]


def test_dry_run_validation_report_blocks_missing_real_inputs(tmp_path: Path) -> None:
    day = "2026-06-23"
    _seed_run_day(tmp_path, day)

    result = build_dry_run_validation_report(day, day, project_paths(tmp_path), execute_missing_runs=False)

    assert result["dry_run_30d_passed"] is False
    assert result["missing_input_days"] == [day]
    assert "missing_real_global_briefing_inputs" in result["release_blocking_reasons"]
    assert any("missing input file" in warning for warning in result["warnings"])


def test_dry_run_validation_report_blocks_audit_critical_errors(tmp_path: Path) -> None:
    days = date_range("2026-06-23", "2026-06-24")
    for day in days:
        _seed_global_inputs(tmp_path, day)
    _seed_run_day(tmp_path, "2026-06-23", duplicate_id="DUPLICATE")
    _seed_run_day(tmp_path, "2026-06-24", duplicate_id="DUPLICATE", shadow_mutation=True)

    result = build_dry_run_validation_report("2026-06-23", "2026-06-24", project_paths(tmp_path), execute_missing_runs=False)

    assert result["dry_run_30d_passed"] is False
    assert "audit_critical_errors" in result["release_blocking_reasons"]
    assert "duplicate_order_or_trade" in result["release_blocking_reasons"]
    assert "shadow_contamination" in result["release_blocking_reasons"]
