from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_owner_quality_dashboard_keeps_owner_blocked(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    dashboard = v13_json(paths, "v13_owner_research_quality_dashboard_result")

    assert result["owner_research_quality_dashboard_generated"] is True
    assert dashboard["owner_readiness_state"] == "blocked"
    assert dashboard["owner_operationally_acceptable"] is False
    assert dashboard["readiness_score"] == 54
    assert dashboard["score_gap"] == 21
