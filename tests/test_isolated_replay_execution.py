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
