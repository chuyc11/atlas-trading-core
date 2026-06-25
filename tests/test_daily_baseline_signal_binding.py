from pathlib import Path

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_baseline_signal_binding import build_daily_baseline_signals
from trading_core.execution.trading_calendar_contract import default_calendar


def test_daily_baseline_signals(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_baseline_signals(as_of_date=AS_OF, strategy="all", paths=paths)
    assert result["strategies_total"] == 3
    for signal in result["signals"]:
        assert signal["signal_date"] == AS_OF
        assert signal["generated_at"].endswith("16:30:00+08:00")
        assert signal["execution_earliest_date"] == default_calendar().next_trading_day(AS_OF, "SSE")
        assert sum(signal["target_weights"].values()) + signal["cash_weight"] <= 1.000001
        assert signal["inputs"]["freeze_manifest"].endswith(f"{AS_OF}.json")
        assert signal["inputs"]["price_data_as_of"] <= AS_OF
        risk_date = signal["inputs"].get("risk_data_as_of")
        assert risk_date is None or risk_date <= AS_OF
        assert signal["uses_ml_shadow"] is False
        assert signal["uses_llm"] is False
        assert signal["uses_rl"] is False
    assert not (paths.data_dir / "strategies" / "signals" / f"daily_baseline_signals-{AS_OF}.json").exists()
    assert_no_protected_paths(paths)


def test_daily_baseline_signals_single_strategy_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    result = build_daily_baseline_signals(as_of_date=AS_OF, strategy="equal_weight_etf_rotation", paths=paths)
    assert len(result["signals"]) == 1
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["daily-baseline-signals", "--as-of-date", AS_OF, "--strategy", "all"]) == 0

