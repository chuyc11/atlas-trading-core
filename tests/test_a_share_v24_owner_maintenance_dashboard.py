from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json


def test_v24_owner_maintenance_dashboard_does_not_change_owner_readiness(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    dashboard = v24_json(paths, "v24_owner_maintenance_dashboard_result")
    scorecard = v24_json(paths, "v24_maintenance_quality_scorecard")

    assert dashboard["owner_maintenance_dashboard_generated"] is True
    assert dashboard["owner_readiness_state"] == "blocked"
    assert dashboard["owner_operationally_acceptable"] is False
    assert dashboard["source_readiness_score"] == 54
    assert dashboard["minimum_owner_readiness_score"] == 75
    assert dashboard["score_gap"] == 21
    assert scorecard["maintenance_quality_score_is_owner_readiness_score"] is False
    assert scorecard["maintenance_quality_pass_means_live_trading_ready"] is False
