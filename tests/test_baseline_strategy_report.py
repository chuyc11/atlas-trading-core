from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_strategy_report import EXPLICIT_NON_CLAIMS, build_baseline_strategy_report
from trading_core.strategies.common import STRATEGY_IDS


def test_baseline_strategy_reports_include_non_claims(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    result = build_baseline_strategy_report(strategy="all", start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert result["all_reports_generated"] is True
    for strategy_id in STRATEGY_IDS:
        report_path = Path(result["paths"][strategy_id]["report_path"])
        text = report_path.read_text(encoding="utf-8")
        for claim in EXPLICIT_NON_CLAIMS:
            assert claim in text
        assert "PIT Constraints" in text
        assert "Benchmark Comparison" in text
        assert "Execution Summary" in text
        assert "promotion approved" not in text.lower()
        assert "strategy effectiveness proven" not in text.lower()
        assert "live trading ready" not in text.lower()
    assert_no_protected_paths(paths)


def test_baseline_strategy_report_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["baseline-strategy-report", "--strategy", "all", "--start-date", TEST_START, "--end-date", TEST_END]) == 0

