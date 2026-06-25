from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.execution.trading_calendar_contract import default_calendar
from trading_core.storage.jsonl_store import read_jsonl
from trading_core.strategies.baseline_signal_engine import generate_baseline_strategy_signals
from trading_core.strategies.common import STRATEGY_IDS


def test_baseline_signal_engine_generates_pit_safe_signals(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = generate_baseline_strategy_signals(strategy="all", start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert result["all_signals_generated"] is True
    assert result["all_pit_constraints_passed"] is True
    calendar = default_calendar()
    first_run_payloads = {}
    for strategy_id in STRATEGY_IDS:
        signal_path = Path(result["paths"][strategy_id]["signal_path"])
        rows = read_jsonl(signal_path)
        first_run_payloads[strategy_id] = signal_path.read_text(encoding="utf-8")
        assert rows
        for row in rows:
            assert row["strategy_id"] == strategy_id
            assert row["generated_at"].endswith("16:30:00+08:00")
            assert row["execution_earliest_date"] == calendar.next_trading_day(row["signal_date"], "SSE")
            assert row["inputs"]["price_data_as_of"] <= row["signal_date"]
            risk_date = row["inputs"].get("risk_data_as_of")
            assert risk_date is None or risk_date <= row["signal_date"]
            assert sum(row["target_weights"].values()) + row["cash_weight"] <= 1.000001
            assert row["cash_weight"] >= 0
            assert all(weight >= 0 for weight in row["target_weights"].values())
            assert row["uses_ml_shadow"] is False
            assert row["uses_llm"] is False
            assert row["uses_rl"] is False
    generate_baseline_strategy_signals(strategy="all", start_date=TEST_START, end_date=TEST_END, paths=paths)
    for strategy_id in STRATEGY_IDS:
        assert Path(result["paths"][strategy_id]["signal_path"]).read_text(encoding="utf-8") == first_run_payloads[strategy_id]
    assert_no_protected_paths(paths)


def test_baseline_signal_engine_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["generate-baseline-strategy-signals", "--strategy", "all", "--start-date", TEST_START, "--end-date", TEST_END]) == 0

