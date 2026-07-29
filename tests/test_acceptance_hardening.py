from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.attribution.attribution_engine import build_attribution
from trading_core.backtest.event_backtester import run_event_backtest
from trading_core.benchmarks.benchmark_engine import build_benchmark
from trading_core.daily_run import run_daily
from trading_core.evolution.experiment_queue import update_experiment_queue
from trading_core.evolution.mistake_classifier import classify_mistakes
from trading_core.evolution.rule_memory import update_rule_memory
from trading_core.evolution.shadow_runner import run_shadow
from trading_core.evolution.signal_scorecard import score_signals
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json, write_jsonl


DATES = ["2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25", "2026-06-26"]


def _global_data(root: Path) -> Path:
    path = root / "work" / "global-briefing" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _macro(
    date: str,
    symbol: str,
    *,
    side: str = "LONG",
    confidence: str = "medium",
    target_weight: float = 0.05,
) -> dict[str, object]:
    return {
        "macro_signal_id": f"MACRO-{date}-{side}-{symbol}",
        "date": date,
        "region": "CHINA",
        "theme": "hardening",
        "scenario": f"{side} {symbol}",
        "confidence": confidence,
        "affected_assets": [symbol],
        "side": side,
        "target_weight": target_weight,
        "risk_flags": [],
        "status": "open",
    }


def _price_item(
    symbol: str,
    price: float,
    previous_close: float,
    *,
    status: str = "ok",
    market: str = "A_SHARE",
) -> dict[str, object]:
    return {
        "symbol": symbol,
        "market": market,
        "price": price,
        "previous_close": previous_close,
        "provider": "hardening-test",
        "data_status": status,
    }


def _snapshot(root: Path, date: str, items: list[dict[str, object]]) -> None:
    write_json(_global_data(root) / f"china-market-snapshot-{date}.json", {"provider": "hardening-test", "items": items})


def _write_five_day_dataset(root: Path, *, include_sell_cycle: bool = False) -> None:
    data = _global_data(root)
    day1_signals = [
        _macro(DATES[0], "510300.SH"),
        _macro(DATES[0], "999999.SH"),
    ]
    if include_sell_cycle:
        day1_signals.append(_macro(DATES[0], "510300.SH", side="SELL"))
    write_jsonl(data / f"macro_signals-{DATES[0]}.jsonl", day1_signals)

    day2_signals = [_macro(DATES[1], "510300.SH", side="SELL", target_weight=0.025)] if include_sell_cycle else []
    write_jsonl(data / f"macro_signals-{DATES[1]}.jsonl", day2_signals)
    write_jsonl(data / f"macro_signals-{DATES[2]}.jsonl", [_macro(DATES[2], "510300.SH")])
    write_jsonl(data / f"macro_signals-{DATES[3]}.jsonl", [_macro(DATES[3], "510300.SH")])
    write_jsonl(data / f"macro_signals-{DATES[4]}.jsonl", [_macro(DATES[4], "510300.SH")])

    _snapshot(
        root,
        DATES[0],
        [
            _price_item("510300.SH", 4.00, 3.96),
            _price_item("159915.SZ", 2.00, 1.98),
            _price_item("000300.SH", 5000.00, 4950.00, market="A_SHARE_INDEX"),
        ],
    )
    _snapshot(
        root,
        DATES[1],
        [
            _price_item("510300.SH", 4.04, 4.00),
            _price_item("159915.SZ", 2.02, 2.00),
            _price_item("000300.SH", 5050.00, 5000.00, market="A_SHARE_INDEX"),
        ],
    )
    _snapshot(
        root,
        DATES[2],
        [
            _price_item("159915.SZ", 2.04, 2.02),
            _price_item("000300.SH", 5075.00, 5050.00, market="A_SHARE_INDEX"),
        ],
    )
    _snapshot(
        root,
        DATES[3],
        [
            _price_item("510300.SH", 4.08, 4.04, status="fallback"),
            _price_item("159915.SZ", 2.05, 2.04),
            _price_item("000300.SH", 5100.00, 5075.00, market="A_SHARE_INDEX"),
        ],
    )
    _snapshot(
        root,
        DATES[4],
        [
            _price_item("510300.SH", 4.10, 4.08, status="stale"),
            _price_item("159915.SZ", 2.06, 2.05),
            _price_item("000300.SH", 5125.00, 5100.00, market="A_SHARE_INDEX"),
        ],
    )


@pytest.fixture
def hardening_workspace(workspace_with_calendar: Path) -> Path:
    _write_five_day_dataset(workspace_with_calendar)
    return workspace_with_calendar


def test_issue_26_dataset_contains_required_hardening_cases(hardening_workspace: Path) -> None:
    data = _global_data(hardening_workspace)
    for date in DATES:
        assert (data / f"china-market-snapshot-{date}.json").exists()
        assert (data / f"macro_signals-{date}.jsonl").exists()

    day1_macros = read_jsonl(data / f"macro_signals-{DATES[0]}.jsonl")
    assert any("510300.SH" in row["affected_assets"] for row in day1_macros)
    assert any("999999.SH" in row["affected_assets"] for row in day1_macros)

    day3_items = read_json(data / f"china-market-snapshot-{DATES[2]}.json")["items"]
    day4_items = read_json(data / f"china-market-snapshot-{DATES[3]}.json")["items"]
    day5_items = read_json(data / f"china-market-snapshot-{DATES[4]}.json")["items"]
    assert "510300.SH" not in {item["symbol"] for item in day3_items}
    assert any(item["symbol"] == "510300.SH" and item["data_status"] == "fallback" for item in day4_items)
    assert any(item["symbol"] == "510300.SH" and item["data_status"] == "stale" for item in day5_items)


def test_issue_26_rerun_same_day_is_idempotent(hardening_workspace: Path) -> None:
    first = run_daily(DATES[0], hardening_workspace)
    second = run_daily(DATES[0], hardening_workspace)
    paths = project_paths(hardening_workspace)

    trades = read_jsonl(paths.dated_jsonl("trades", "trades", DATES[0]))
    orders = read_jsonl(paths.dated_jsonl("orders", "orders", DATES[0]))
    order_ids = [order["order_id"] for order in orders]
    trade_ids = [trade["trade_id"] for trade in trades]

    assert first["portfolio"]["cash"] == second["portfolio"]["cash"]
    assert first["portfolio"]["positions"] == second["portfolio"]["positions"]
    assert len(trades) == 1
    assert len(order_ids) == len(set(order_ids))
    assert len(trade_ids) == len(set(trade_ids))


def test_issue_26_account_continues_across_days_without_reinitializing(hardening_workspace: Path) -> None:
    day1 = run_daily(DATES[0], hardening_workspace)["portfolio"]
    day2 = run_daily(DATES[1], hardening_workspace)["portfolio"]
    day3 = run_daily(DATES[2], hardening_workspace)["portfolio"]

    assert day1["cash"] < 100000
    assert day2["cash"] == day1["cash"]
    assert day3["cash"] == day2["cash"]
    assert day2["positions"][0]["quantity"] == day1["positions"][0]["quantity"]
    assert day3["positions"][0]["quantity"] == day2["positions"][0]["quantity"]
    assert day2["positions"][0]["available_quantity"] == day1["positions"][0]["quantity"]


def test_issue_26_a_share_t_plus_one_blocks_same_day_sell_and_allows_next_day(
    workspace_with_calendar: Path,
) -> None:
    _write_five_day_dataset(workspace_with_calendar, include_sell_cycle=True)

    day1 = run_daily(DATES[0], workspace_with_calendar)
    buy_trades = [trade for trade in day1["trades"] if trade["side"] == "BUY"]
    same_day_sell_orders = [order for order in day1["orders"] if order["side"] == "SELL"]
    assert buy_trades[0]["filled_quantity"] == 1200
    assert day1["portfolio"]["positions"][0]["available_quantity"] == 0
    assert day1["portfolio"]["positions"][0]["last_buy_date"] == DATES[0]
    assert same_day_sell_orders[0]["status"] == "rejected"

    day2 = run_daily(DATES[1], workspace_with_calendar)
    sell_trades = [trade for trade in day2["trades"] if trade["side"] == "SELL"]
    assert day2["portfolio"]["positions"][0]["available_quantity"] > 0
    assert sell_trades
    assert sell_trades[0]["date"] == DATES[1]
    assert day2["portfolio"]["positions"][0]["last_sell_date"] == DATES[1]


def test_issue_26_data_quality_controls_and_report_limitations(hardening_workspace: Path) -> None:
    fresh = run_daily(DATES[0], hardening_workspace)
    missing = run_daily(DATES[2], hardening_workspace)
    fallback = run_daily(DATES[3], hardening_workspace)
    stale = run_daily(DATES[4], hardening_workspace)

    assert any(order["status"] == "submitted" and order["side"] == "BUY" for order in fresh["orders"])
    assert missing["orders"][0]["status"] == "rejected"
    assert "missing_price: 510300.SH" in missing["report_markdown"]
    assert fallback["orders"][0]["status"] == "rejected"
    assert "fallback_price_blocks_buy: 510300.SH" in fallback["report_markdown"]
    assert stale["orders"][0]["status"] == "rejected"
    assert "stale_price_blocks_buy: 510300.SH" in stale["report_markdown"]


def test_issue_26_benchmark_uses_manual_previous_current_price_math(hardening_workspace: Path) -> None:
    benchmark = build_benchmark(
        DATES[1],
        {"account_id": "CHINA_PAPER", "daily_return": 0.015},
        {
            "510300.SH": {"price": 4.04, "previous_close": 4.00},
            "159915.SZ": {"price": 2.02, "previous_close": 2.00},
            "000300.SH": {"price": 5050.00, "previous_close": 5000.00},
        },
        paths=project_paths(hardening_workspace),
    )

    assert benchmark["benchmarks"]["CSI300"]["return"] == pytest.approx(0.01)
    assert benchmark["benchmarks"]["EQUAL_ETF"]["return"] == pytest.approx(0.01)
    assert benchmark["benchmarks"]["CASH"]["return"] == 0
    assert benchmark["excess_return"]["EQUAL_ETF"] == pytest.approx(0.005)


def test_issue_26_attribution_reconciles_to_portfolio_pnl(hardening_workspace: Path) -> None:
    previous = {
        "total_asset": 100000.0,
        "positions": [{"symbol": "510300.SH", "quantity": 1200, "current_price": 4.00, "strategy_id": "macro"}],
    }
    portfolio = {
        "account_id": "CHINA_PAPER",
        "total_asset": 100048.0,
        "daily_return": 0.00048,
        "positions": [{"symbol": "510300.SH", "quantity": 1200, "current_price": 4.04, "strategy_id": "macro"}],
    }
    attribution = build_attribution(DATES[1], portfolio, [], {"excess_return": {}}, previous, project_paths(hardening_workspace))

    assert attribution["total_pnl"] == pytest.approx(48.0)
    assert attribution["holding_pnl"] == pytest.approx(48.0)
    assert attribution["holding_pnl"] + attribution["cash_and_flow_impact"] + attribution["cost_impact"] == pytest.approx(
        attribution["total_pnl"]
    )
    assert attribution["residual_pnl"] == pytest.approx(0.0)


def test_issue_26_evolution_has_logic_and_deduplicates_queue(hardening_workspace: Path) -> None:
    paths = project_paths(hardening_workspace)
    signal = {
        "signal_id": "SIG-HARDENING-001",
        "date": DATES[1],
        "strategy_id": "macro_etf_strategy_v1",
        "symbol": "510300.SH",
        "side": "LONG",
        "confidence": 0.65,
        "risk_flags": [],
    }
    scorecard = score_signals(
        DATES[1],
        [signal],
        [{"signal_id": "SIG-HARDENING-001"}],
        {"daily_return": 0.0},
        {"benchmarks": {"EQUAL_ETF": {"return": 0.01}}},
        paths=paths,
    )
    assert scorecard["items"][0]["status"] == "wrong"

    mistakes = classify_mistakes(DATES[1], scorecard, paths=paths)
    assert mistakes[0]["mistake_type"] == "benchmark_underperformance"

    for index in range(4):
        dated_mistakes = [{**mistakes[0], "date": DATES[index], "signal_id": f"SIG-HARDENING-{index:03d}"}]
        memory = update_rule_memory(DATES[index], dated_mistakes, paths=paths, min_evidence_count=5)
        assert memory["rules"] == []
    final_mistakes = [{**mistakes[0], "date": DATES[4], "signal_id": "SIG-HARDENING-004"}]
    memory = update_rule_memory(DATES[4], final_mistakes, paths=paths, min_evidence_count=5)
    assert len(memory["rules"]) == 1
    assert memory["rules"][0]["status"] == "proposed"

    first_queue = update_experiment_queue(DATES[4], memory, paths=paths)
    second_queue = update_experiment_queue(DATES[4], memory, paths=paths)
    assert first_queue == second_queue
    assert len(first_queue) == 1


def test_issue_26_shadow_does_not_modify_main_account_or_outputs(hardening_workspace: Path) -> None:
    run_daily(DATES[0], hardening_workspace)
    paths = project_paths(hardening_workspace)
    portfolio_before = read_json(paths.dated_json("portfolios", "portfolio", DATES[0]))
    valuation_before = read_jsonl(paths.dated_jsonl("valuations", "valuations", DATES[0]))

    shadow_rows = run_shadow(
        DATES[0],
        "CHINA_PAPER",
        {
            "510300.SH": {"price": 4.0, "change_pct": 1.0, "raw": {"market": "A_SHARE"}},
            "159915.SZ": {"price": 2.0, "change_pct": 0.5, "raw": {"market": "A_SHARE"}},
        },
        paths=paths,
    )

    assert shadow_rows
    assert all(row["status"] == "shadow" for row in shadow_rows)
    assert read_json(paths.dated_json("portfolios", "portfolio", DATES[0])) == portfolio_before
    assert read_jsonl(paths.dated_jsonl("valuations", "valuations", DATES[0])) == valuation_before


def test_issue_26_backtest_executes_t_plus_one_without_same_day_fill(hardening_workspace: Path) -> None:
    summary = run_event_backtest(DATES[0], DATES[1], hardening_workspace)

    assert summary["daily"][0]["generated_signal_count"] == 1
    assert summary["daily"][0]["trade_count"] == 0
    assert summary["daily"][0]["executed_signal_date"] is None
    assert summary["daily"][1]["executed_signal_date"] == DATES[0]
    assert summary["daily"][1]["trade_count"] == 1
    assert summary["execution_model"] == "T day generates signals; next trading day executes pending signals."
