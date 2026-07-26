from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.attribution.attribution_engine import build_attribution
from trading_core.backtest.event_backtester import run_event_backtest
from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.daily_run import run_daily
from trading_core.evolution.experiment_queue import update_experiment_queue
from trading_core.evolution.rule_memory import update_rule_memory
from trading_core.evolution.shadow_runner import run_shadow
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json, write_jsonl


def _global_data(root: Path) -> Path:
    path = root / "work" / "global-briefing" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _macro(date: str, side: str = "LONG", symbol: str = "510300.SH") -> dict[str, object]:
    return {
        "macro_signal_id": f"MACRO-{date}-{side}-{symbol}",
        "date": date,
        "region": "CHINA",
        "theme": "acceptance",
        "scenario": f"{side} {symbol}",
        "confidence": "medium",
        "affected_assets": [symbol],
        "side": side,
        "risk_flags": [],
        "status": "open",
    }


def _snapshot(date: str, items: list[dict[str, object]], root: Path) -> None:
    write_json(_global_data(root) / f"china-market-snapshot-{date}.json", {"provider": "test", "items": items})


def _fresh_item(symbol: str = "510300.SH", price: float = 4.0, previous_close: float = 4.0) -> dict[str, object]:
    return {
        "symbol": symbol,
        "market": "A_SHARE",
        "price": price,
        "previous_close": previous_close,
        "provider": "test",
        "data_status": "ok",
    }


def test_same_day_rerun_is_idempotent_and_archives_changed_report(sample_workspace: Path) -> None:
    first = run_daily("2026-06-23", sample_workspace)
    second = run_daily("2026-06-23", sample_workspace)
    paths = project_paths(sample_workspace)

    trades = read_jsonl(paths.dated_jsonl("trades", "trades", "2026-06-23"))
    trade_ids = [trade["trade_id"] for trade in trades]
    assert len(trades) == 1
    assert len(trade_ids) == len(set(trade_ids))
    assert first["portfolio"] == second["portfolio"]

    report = paths.daily_report("2026-06-23")
    report.write_text("critical historical report\n", encoding="utf-8")
    run_daily("2026-06-23", sample_workspace)
    archives = list((report.parent / "archive").glob("virtual-trading-report-2026-06-23-*.md"))
    assert any("critical historical report" in path.read_text(encoding="utf-8") for path in archives)


def test_account_state_continues_across_three_days(sample_workspace: Path) -> None:
    day_23 = run_daily("2026-06-23", sample_workspace)["portfolio"]
    day_24 = run_daily("2026-06-24", sample_workspace)["portfolio"]
    day_25 = run_daily("2026-06-25", sample_workspace)["portfolio"]

    assert day_23["positions"][0]["quantity"] == 1200
    assert day_23["positions"][0]["available_quantity"] == 0
    assert day_24["positions"][0]["quantity"] == 1200
    assert day_24["positions"][0]["available_quantity"] == 1200
    assert day_25["positions"][0]["quantity"] == 1200
    assert day_25["positions"][0]["available_quantity"] == 1200
    assert day_24["cash"] == day_23["cash"]
    assert day_25["cash"] == day_24["cash"]


def test_t_plus_one_rejects_same_day_sell_then_allows_next_day(tmp_path: Path) -> None:
    data = _global_data(tmp_path)
    write_jsonl(data / "macro_signals-2026-06-23.jsonl", [_macro("2026-06-23", "LONG"), _macro("2026-06-23", "SELL")])
    write_jsonl(data / "macro_signals-2026-06-24.jsonl", [_macro("2026-06-24", "SELL")])
    _snapshot("2026-06-23", [_fresh_item(price=4.0), _fresh_item("000300.SH", 5000, 5000)], tmp_path)
    _snapshot("2026-06-24", [_fresh_item(price=4.1, previous_close=4.0), _fresh_item("000300.SH", 5050, 5000)], tmp_path)

    day_23 = run_daily("2026-06-23", tmp_path)
    sell_order_23 = [order for order in day_23["orders"] if order["side"] == "SELL"][0]
    assert sell_order_23["status"] == "rejected"
    assert "available position" in sell_order_23["risk_reason"]
    assert day_23["portfolio"]["positions"][0]["quantity"] == 1200
    assert day_23["portfolio"]["positions"][0]["available_quantity"] == 0
    assert day_23["portfolio"]["positions"][0]["last_buy_date"] == "2026-06-23"

    day_24 = run_daily("2026-06-24", tmp_path)
    sell_trades = [trade for trade in day_24["trades"] if trade["side"] == "SELL"]
    assert sell_trades
    assert sell_trades[0]["date"] == "2026-06-24"
    assert sell_trades[0]["filled_quantity"] == 1200


def test_missing_price_blocks_order_and_records_data_quality(tmp_path: Path) -> None:
    data = _global_data(tmp_path)
    write_jsonl(data / "macro_signals-2026-06-23.jsonl", [_macro("2026-06-23")])
    _snapshot("2026-06-23", [_fresh_item("000300.SH", 5000, 5000)], tmp_path)

    result = run_daily("2026-06-23", tmp_path)
    assert result["signals"][0]["symbol"] == "510300.SH"
    assert result["orders"][0]["status"] == "rejected"
    assert result["trades"] == []
    assert result["portfolio"]["total_asset"] == 100000
    assert "missing_price: 510300.SH" in result["limitations"]
    assert result["data_quality"]["counts"]["missing"] == 1


@pytest.mark.parametrize(
    ("status", "expected_order_status", "expected_trades"),
    [
        ("ok", "submitted", 1),
        ("fallback", "rejected", 0),
        ("stale", "rejected", 0),
    ],
)
def test_fallback_and_stale_block_buy(tmp_path: Path, status: str, expected_order_status: str, expected_trades: int) -> None:
    data = _global_data(tmp_path)
    write_jsonl(data / "macro_signals-2026-06-23.jsonl", [_macro("2026-06-23")])
    item = _fresh_item()
    item["data_status"] = status
    _snapshot("2026-06-23", [item, _fresh_item("000300.SH", 5000, 5000)], tmp_path)

    result = run_daily("2026-06-23", tmp_path)
    assert result["orders"][0]["status"] == expected_order_status
    assert len(result["trades"]) == expected_trades


def test_benchmark_uses_real_previous_and_current_prices(sample_workspace: Path) -> None:
    paths = project_paths(sample_workspace)
    benchmark = build_benchmark(
        "2026-06-23",
        {"account_id": "CHINA_PAPER", "daily_return": 0.02},
        {"510300.SH": {"price": 4.04, "previous_close": 4.00}},
        paths=paths,
    )
    assert benchmark["benchmarks"]["EQUAL_ETF"]["return"] == pytest.approx(0.01)
    assert benchmark["benchmarks"]["CASH"]["return"] == 0
    assert benchmark["excess_return"]["EQUAL_ETF"] == pytest.approx(0.01)


def test_attribution_reconciles_to_total_pnl(sample_workspace: Path) -> None:
    previous = {
        "total_asset": 100000.0,
        "positions": [{"symbol": "510300.SH", "quantity": 1200, "current_price": 4.0, "strategy_id": "macro"}],
    }
    portfolio = {
        "account_id": "CHINA_PAPER",
        "total_asset": 100120.0,
        "daily_return": 0.0012,
        "positions": [{"symbol": "510300.SH", "quantity": 1200, "current_price": 4.1, "strategy_id": "macro"}],
    }
    attribution = build_attribution("2026-06-24", portfolio, [], {"excess_return": {}}, previous, project_paths(sample_workspace))
    assert attribution["total_pnl"] == pytest.approx(120.0)
    assert attribution["holding_pnl"] == pytest.approx(120.0)
    assert attribution["holding_pnl"] + attribution["cash_and_flow_impact"] + attribution["cost_impact"] == pytest.approx(
        attribution["total_pnl"]
    )
    assert attribution["residual_pnl"] == pytest.approx(0.0)


def test_evolution_waits_for_repeated_evidence_and_deduplicates_experiments(sample_workspace: Path) -> None:
    paths = project_paths(sample_workspace)
    mistake = {"strategy_id": "macro", "mistake_type": "benchmark_underperformance", "signal_id": "S1"}
    for day in range(1, 5):
        memory = update_rule_memory(f"2026-06-2{day}", [mistake], paths=paths, min_evidence_count=5)
        assert memory["rules"] == []

    memory = update_rule_memory("2026-06-25", [mistake], paths=paths, min_evidence_count=5)
    assert len(memory["rules"]) == 1
    first_queue = update_experiment_queue("2026-06-25", memory, paths=paths)
    second_queue = update_experiment_queue("2026-06-26", memory, paths=paths)
    assert len(first_queue) == 1
    assert first_queue == second_queue


def test_shadow_runner_does_not_modify_main_portfolio(sample_workspace: Path) -> None:
    run_daily("2026-06-23", sample_workspace)
    paths = project_paths(sample_workspace)
    before = read_json(paths.dated_json("portfolios", "portfolio", "2026-06-23"))
    run_shadow("2026-06-23", "CHINA_PAPER", {"510300.SH": {"price": 4.0, "change_pct": 1.0}}, paths=paths)
    after = read_json(paths.dated_json("portfolios", "portfolio", "2026-06-23"))
    assert before == after


def test_backtest_executes_prior_day_signal_on_next_day(sample_workspace: Path) -> None:
    summary = run_event_backtest("2026-06-23", "2026-06-24", sample_workspace)
    assert summary["daily"][0]["trade_count"] == 0
    assert summary["daily"][1]["trade_count"] == 1
    assert summary["daily"][1]["executed_signal_date"] == "2026-06-23"
    assert summary["execution_model"] == "T day generates signals; next trading day executes pending signals."
