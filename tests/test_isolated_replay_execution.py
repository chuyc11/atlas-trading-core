from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.isolated_replay_execution import ReplayCostModel, process_isolated_replay_day
from trading_core.global_briefing.isolated_replay_state import ReplaySignal, ReplayState


def _signal(weight: float) -> ReplaySignal:
    return ReplaySignal("R1", "2024-01-02", "510300.SH", weight, "macro_signal_adapter", "2024-01-02", "2024-01-02T06:00:00Z")


def _prices(price: float = 4.0) -> dict:
    return {"510300": {"symbol": "510300", "close": price}}


def _dated_prices(day: str, price: float = 4.0) -> dict:
    return {"510300": {"date": day, "symbol": "510300", "close": price, "source": "fixture"}}


def test_target_weight_generates_buy_order() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)

    orders, trades, _valuation, _day = process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _prices())

    assert orders[0].side == "BUY"
    assert trades[0].quantity > 0


def test_target_weight_decrease_generates_sell_order() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _prices())

    orders, trades, _valuation, _day = process_isolated_replay_day(state, "2024-01-03", [_signal(0.02)], _prices())

    assert orders[0].side == "SELL"
    assert trades[0].side == "SELL"


def test_missing_price_does_not_order() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)

    orders, trades, _valuation, day = process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], {})

    assert orders == []
    assert trades == []
    assert any("missing price" in item for item in day.warnings)


def test_market_constraints_block_isolated_replay_fill() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    prices = {"510300": {"symbol": "510300", "close": 4.0, "volume": 0}}

    orders, trades, _valuation, day = process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], prices)

    assert orders == []
    assert trades == []
    assert any("zero_volume_suspension" in item for item in day.warnings)


def test_insufficient_cash_shrinks_quantity() -> None:
    state = ReplayState.initialize("R1", 1_000.0)

    orders, trades, _valuation, _day = process_isolated_replay_day(state, "2024-01-02", [_signal(2.0)], _prices())

    assert trades[0].notional + trades[0].fee <= 1_000.0
    assert state.account.cash >= 0


def test_short_is_not_allowed() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)

    orders, trades, _valuation, _day = process_isolated_replay_day(state, "2024-01-02", [_signal(0.0)], _prices())

    assert orders == []
    assert trades == []
    assert state.get_position("510300.SH").quantity == 0


def test_cash_never_negative() -> None:
    state = ReplayState.initialize("R1", 1_000.0)
    process_isolated_replay_day(state, "2024-01-02", [_signal(1.0)], _prices())

    assert state.account.cash >= 0


def test_no_leverage() -> None:
    state = ReplayState.initialize("R1", 1_000.0)
    process_isolated_replay_day(state, "2024-01-02", [_signal(10.0)], _prices())

    assert state.account.equity >= 0
    assert state.account.cash >= 0


def test_quantity_is_integer() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    _orders, trades, _valuation, _day = process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _prices())

    assert isinstance(trades[0].quantity, int)


def test_fee_recorded() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    _orders, trades, _valuation, _day = process_isolated_replay_day(
        state,
        "2024-01-02",
        [_signal(0.10)],
        _prices(),
        cost_model=ReplayCostModel(commission_rate=0.001),
    )

    assert trades[0].fee > 0


def test_slippage_changes_buy_and_sell_fills_and_is_auditable() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    cost_model = ReplayCostModel(commission_rate=0.0, slippage_bps=10.0)

    buy_orders, buy_trades, _valuation, _day = process_isolated_replay_day(
        state,
        "2024-01-02",
        [_signal(0.10)],
        _dated_prices("2024-01-02"),
        cost_model=cost_model,
    )
    sell_orders, sell_trades, _valuation, _day = process_isolated_replay_day(
        state,
        "2024-01-03",
        [_signal(0.0)],
        _dated_prices("2024-01-03"),
        cost_model=cost_model,
    )

    assert buy_orders[0].price == pytest.approx(4.004)
    assert buy_trades[0].reference_price == pytest.approx(4.0)
    assert buy_trades[0].slippage_bps == pytest.approx(10.0)
    assert buy_trades[0].slippage_cost == pytest.approx(buy_trades[0].quantity * 0.004)
    assert buy_trades[0].to_dict()["costs"]["slippage"] == pytest.approx(buy_trades[0].slippage_cost)
    assert sell_orders[0].price == pytest.approx(3.996)
    assert sell_trades[0].price == pytest.approx(3.996)
    assert sell_trades[0].slippage_cost == pytest.approx(sell_trades[0].quantity * 0.004)


def test_open_position_uses_dated_bounded_carry_instead_of_zero_value() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    process_isolated_replay_day(state, "2024-01-05", [_signal(0.10)], _dated_prices("2024-01-05"))

    _orders, _trades, valuation, day = process_isolated_replay_day(
        state,
        "2024-01-08",
        [],
        {},
        max_price_staleness_days=3,
    )

    assert valuation.valuation_valid is True
    assert valuation.market_value > 0
    assert valuation.positions[0]["market_value"] > 0
    assert valuation.price_observations == [
        {
            "symbol": "510300.SH",
            "requirement": "holding",
            "status": "carry_forward",
            "price": 4.0,
            "source_date": "2024-01-05",
            "age_days": 3,
            "source": "fixture",
        }
    ]
    assert day.valuation_valid is True


def test_open_position_stale_beyond_limit_fails_closed_without_zero_value() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)
    process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _dated_prices("2024-01-02"))

    orders, trades, valuation, day = process_isolated_replay_day(
        state,
        "2024-01-08",
        [_signal(0.20)],
        {},
        max_price_staleness_days=3,
    )

    assert orders == []
    assert trades == []
    assert valuation.valuation_valid is False
    assert valuation.market_value is None
    assert valuation.equity is None
    assert valuation.positions[0]["market_value"] > 0
    assert valuation.price_observations[0]["status"] == "stale"
    assert valuation.price_observations[0]["source_date"] == "2024-01-02"
    assert valuation.price_observations[0]["age_days"] == 6
    assert day.valuation_valid is False
    assert any("stale valuation price" in item for item in day.warnings)


def test_no_trade_day_still_generates_valuation() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)

    _orders, _trades, valuation, day = process_isolated_replay_day(state, "2024-01-02", [], _prices())

    assert valuation.equity == 1_000_000.0
    assert day.trades == 0


def test_orders_and_trades_isolated() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)

    orders, trades, _valuation, _day = process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _prices())

    assert orders[0].isolated is True
    assert trades[0].isolated is True


def test_execution_does_not_write_main_ledger(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    state = ReplayState.initialize("R1", 1_000_000.0)

    process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _prices())

    assert_no_protected_paths(paths)


def test_execution_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    state = ReplayState.initialize("R1", 1_000_000.0)

    process_isolated_replay_day(state, "2024-01-02", [_signal(0.10)], _prices())
