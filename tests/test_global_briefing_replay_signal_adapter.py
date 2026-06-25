from __future__ import annotations

from pathlib import Path

from global_briefing_test_utils import assert_no_protected_paths, make_paths
from trading_core.global_briefing.replay_signal_adapter import adapt_bundle_row_to_replay_signals


def _row(signals: dict) -> dict:
    return {
        "replay_date": "2024-01-02",
        "selected_signal_as_of_date": "2024-01-02",
        "selected_signal_generated_at": "2024-01-02T06:00:00Z",
        "signals": signals,
    }


def test_valid_macro_signal_generates_target_weights() -> None:
    signals, warnings = adapt_bundle_row_to_replay_signals(_row({"risk_on": 0.2, "policy_support": 0.4}), replay_id="R1")

    assert signals
    assert warnings == []
    assert any(signal.symbol == "510300.SH" and signal.target_weight > 0 for signal in signals)


def test_negative_risk_on_does_not_create_negative_weight() -> None:
    signals, _warnings = adapt_bundle_row_to_replay_signals(_row({"risk_on": -1, "policy_support": 0}), replay_id="R1")

    assert all(signal.target_weight >= 0 for signal in signals)


def test_total_weight_capped() -> None:
    signals, _warnings = adapt_bundle_row_to_replay_signals(
        _row({"risk_on": 1, "liquidity": 1, "policy_support": 1}),
        replay_id="R1",
        max_total_weight=0.20,
    )

    assert sum(signal.target_weight for signal in signals) <= 0.200001


def test_symbol_weight_capped() -> None:
    signals, _warnings = adapt_bundle_row_to_replay_signals(_row({"risk_on": 1, "policy_support": 1}), replay_id="R1", max_symbol_weight=0.05)

    assert all(signal.target_weight <= 0.050001 for signal in signals)


def test_missing_signals_generates_cash_only() -> None:
    signals, warnings = adapt_bundle_row_to_replay_signals(_row({}), replay_id="R1")

    assert signals == []
    assert any("cash-only" in item for item in warnings)


def test_unknown_signal_fields_warn() -> None:
    _signals, warnings = adapt_bundle_row_to_replay_signals(_row({"risk_on": 0.2, "mystery": 1}), replay_id="R1")

    assert any("unknown signal fields" in item for item in warnings)


def test_signal_adapter_boundaries_do_not_use_labels_ml_or_future_returns() -> None:
    signals, _warnings = adapt_bundle_row_to_replay_signals(_row({"risk_on": 0.2}), replay_id="R1")
    payload = [signal.to_dict() for signal in signals]

    text = str(payload).lower()
    assert "label" not in text
    assert "ml_shadow" not in text
    assert "future_return" not in text


def test_signal_adapter_does_not_write_main_ledger(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    adapt_bundle_row_to_replay_signals(_row({"risk_on": 0.2}), replay_id="R1")

    assert_no_protected_paths(paths)
