from pathlib import Path

import pytest

from baseline_strategy_test_utils import make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_strategy_contract import build_baseline_strategy_contract


def test_baseline_strategy_contract(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = build_baseline_strategy_contract(paths=paths)
    assert set(result["strategies"]) == {"equal_weight_etf_rotation", "momentum_risk_adjusted_rotation", "defensive_cash_rotation"}
    for contract in result["strategies"].values():
        assert contract["uses_ml_shadow"] is False
        assert contract["uses_llm"] is False
        assert contract["uses_rl"] is False
        assert contract["uses_promotion_outputs"] is False
        assert contract["signal_timing"] == "after_t_close"
        assert contract["execution_timing"] == "t_plus_1"
        assert "live trading ready" in contract["forbidden_claims"]
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_baseline_strategy_contract_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["baseline-strategy-contract"]) == 0

