from pathlib import Path

import pytest

from baseline_strategy_test_utils import make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_strategy_registry import build_baseline_strategy_registry


def test_baseline_strategy_registry(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = build_baseline_strategy_registry(paths=paths)
    assert set(result["parameter_versions"]) == {"equal_weight_etf_rotation", "momentum_risk_adjusted_rotation", "defensive_cash_rotation"}
    for item in result["strategies"].values():
        params = item["parameters"]
        assert item["parameter_version"]
        assert params.get("max_weight", 0.2) <= 0.30
        assert 0 <= params["cash_buffer_pct"] < 1
        assert item["uses_ml"] is False
        assert item["uses_llm"] is False
        assert item["uses_rl"] is False
    momentum = result["strategies"]["momentum_risk_adjusted_rotation"]["parameters"]
    defensive = result["strategies"]["defensive_cash_rotation"]["parameters"]
    assert momentum["lookback_days"] >= momentum["min_history_days"]
    assert defensive["risk_off_threshold"] > defensive["risk_on_threshold"]
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_baseline_strategy_registry_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["baseline-strategy-registry"]) == 0

