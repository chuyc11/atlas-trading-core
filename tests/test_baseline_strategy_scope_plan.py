from pathlib import Path

import pytest

from baseline_strategy_test_utils import make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_strategy_scope_plan import build_baseline_strategy_scope_plan


def test_baseline_strategy_scope_plan(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = build_baseline_strategy_scope_plan(paths=paths)
    assert result["execution_day1_blockers_closed"] is True
    assert result["forward_dry_run_day1_allowed"] is False
    assert result["strategies"] == ["equal_weight_etf_rotation", "momentum_risk_adjusted_rotation", "defensive_cash_rotation"]
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert result["boundary"]["ml_shadow_used_as_authorization"] is False
    assert result["boundary"]["llm_trading_decision"] is False
    assert result["boundary"]["rl_used"] is False
    assert result["boundary"]["promotion_triggered"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_baseline_strategy_scope_plan_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["baseline-strategy-scope-plan"]) == 0

