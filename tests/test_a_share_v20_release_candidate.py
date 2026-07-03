from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import RELEASE_DECISION, run_a_share_v20_platform_closeout


def test_v20_release_candidate_and_health_report(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    candidate = v20_json(paths, "v20_release_candidate_result")
    health = v20_json(paths, "v20_release_health_report")
    limitations = v20_json(paths, "v20_plan_gap_known_limitations_result")

    assert result["release_decision"] == RELEASE_DECISION
    assert candidate["release_candidate_result_generated"] is True
    assert candidate["full_pytest_run"] is True
    assert candidate["full_pytest_passed"] is True
    assert health["release_health_report_generated"] is True
    assert limitations["recommended_next_version"] == result["recommended_next_version"]
