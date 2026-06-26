from __future__ import annotations

from pathlib import Path

import pytest

from forward_dry_run_day1_owner_report_test_utils import make_day1_owner_report_paths
from trading_core.forward_dry_run.day1_strategy_signal_explanation import build_day1_strategy_signal_explanation


def test_day1_strategy_signal_explanation_covers_baseline_strategies(tmp_path: Path) -> None:
    paths = make_day1_owner_report_paths(tmp_path)
    result = build_day1_strategy_signal_explanation(paths=paths)
    assert result["strategies_total"] == 3
    assert result["strategies_explained"] == 3
    ids = {item["strategy_id"] for item in result["strategy_explanations"]}
    assert ids == {"equal_weight_etf_rotation", "momentum_risk_adjusted_rotation", "defensive_cash_rotation"}
    assert all(item["uses_ml"] is False for item in result["strategy_explanations"])
    assert result["boundary"]["promotion_triggered"] is False


def test_day1_strategy_signal_explanation_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_owner_report_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["forward-dry-run-day1-strategy-signal-explanation"]) == 0
