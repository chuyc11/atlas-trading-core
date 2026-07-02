from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_research_quality_scorecard_and_main_result(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)

    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    scorecard = v13_json(paths, "v13_research_quality_scorecard")

    assert result["overall_passed"] is True
    assert result["research_quality_scorecard_generated"] is True
    assert result["data_leakage_guard_passed"] is True
    assert result["lookahead_bias_check_passed"] is True
    assert result["point_in_time_check_status"] == "passed"
    assert scorecard["overall_quality_score"] == 72
    assert scorecard["survivorship_bias_warning_recorded"] is True
    assert result["blocking_reasons"] == []
