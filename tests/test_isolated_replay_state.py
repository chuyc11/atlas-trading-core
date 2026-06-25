from __future__ import annotations

import json
from pathlib import Path

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.isolated_replay_state import (
    ReplayAccount,
    ReplayDayResult,
    ReplayOrder,
    ReplayPosition,
    ReplaySignal,
    ReplayState,
    ReplayTrade,
)


def test_replay_account_serializable() -> None:
    account = ReplayAccount(replay_id="R1", cash=100.0, equity=100.0)

    assert json.loads(json.dumps(account.to_dict()))["replay_id"] == "R1"


def test_replay_position_serializable() -> None:
    position = ReplayPosition(replay_id="R1", symbol="510300.SH")

    assert json.loads(json.dumps(position.to_dict()))["isolated"] is True


def test_replay_signal_serializable() -> None:
    signal = ReplaySignal("R1", "2024-01-02", "510300.SH", 0.1, "macro_signal_adapter", "2024-01-02", "2024-01-02T06:00:00Z")

    assert json.loads(json.dumps(signal.to_dict()))["target_weight"] == 0.1


def test_replay_order_serializable() -> None:
    order = ReplayOrder("O1", "R1", "2024-01-02", "510300.SH", "BUY", 100, 4.0, "FILLED")

    assert json.loads(json.dumps(order.to_dict()))["order_id"] == "O1"


def test_replay_trade_serializable() -> None:
    trade = ReplayTrade("T1", "O1", "R1", "2024-01-02", "510300.SH", "BUY", 100, 4.0, 400.0, 0.2)

    assert json.loads(json.dumps(trade.to_dict()))["fee"] == 0.2


def test_replay_state_initializes_correctly() -> None:
    state = ReplayState.initialize("R1", 1_000_000.0)

    assert state.replay_id == "R1"
    assert state.account.cash == 1_000_000.0
    assert state.isolated is True


def test_replay_state_supports_empty_positions() -> None:
    state = ReplayState.initialize("R1", 100.0)

    assert state.to_dict()["positions"] == []


def test_replay_state_supports_no_trade_day() -> None:
    state = ReplayState.initialize("R1", 100.0)
    state.record_day(ReplayDayResult("R1", "2024-01-02", 0, 0, 0, 100.0, 100.0, ["no trade"]))

    assert state.to_dict()["day_results"][0]["trades"] == 0


def test_all_state_outputs_include_replay_id() -> None:
    state = ReplayState.initialize("R1", 100.0)
    state.get_position("510300.SH")
    payload = state.to_dict()

    assert payload["replay_id"] == "R1"
    assert payload["account"]["replay_id"] == "R1"
    assert payload["positions"][0]["replay_id"] == "R1"


def test_state_model_does_not_write_main_ledger(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    ReplayState.initialize("R1", 100.0)

    assert_no_protected_paths(paths)
