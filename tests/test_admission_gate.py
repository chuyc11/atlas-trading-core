from __future__ import annotations

from trading_core.evolution.admission_gate import evaluate_admission


BASE_METRICS = {
    "backtest_days": 80,
    "trades": 15,
    "excess_return": 0.05,
    "max_drawdown": 0.02,
    "mistake_rate": 0.10,
    "cost_ratio": 0.05,
    "benchmark_comparison": True,
    "future_data_flag": False,
}


def _decision(**overrides):
    metrics = {**BASE_METRICS, **overrides}
    return evaluate_admission("macro_etf_strategy_v1", "2026-06-23", metrics)


def test_admission_rejects_insufficient_days() -> None:
    assert "min_backtest_days" in _decision(backtest_days=10)["failed_rules"]


def test_admission_rejects_insufficient_trades() -> None:
    assert "min_trades" in _decision(trades=2)["failed_rules"]


def test_admission_rejects_non_positive_excess_return() -> None:
    assert "require_positive_excess_return" in _decision(excess_return=0)["failed_rules"]


def test_admission_rejects_drawdown_and_cost() -> None:
    decision = _decision(max_drawdown=0.10, cost_ratio=0.25)
    assert "max_drawdown" in decision["failed_rules"]
    assert "max_cost_ratio" in decision["failed_rules"]


def test_admission_allows_shadow_only_when_rules_pass() -> None:
    decision = _decision()
    assert decision["passed"]
    assert decision["status"] == "shadow_allowed"
    assert decision["auto_applied"] is False
