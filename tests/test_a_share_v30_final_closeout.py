from __future__ import annotations

from pathlib import Path

from a_share_release_chain_test_utils import build_release, make_release_paths


def test_v30_final_closeout_is_research_only_release_not_live_trading(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v30")
    spec, result, audit = build_release(paths, "v30")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert result["v29_baseline_verified"] is True
    assert result["release_decision"] == "released_as_research_only_simulation_platform"
    assert result["full_regression_evidence_generated"] is True
    assert result["full_pytest_run"] is True
    assert result["full_pytest_passed"] is True
    assert result["fabricated_release_evidence"] is False
    assert result["fabricated_capability_claim"] is False
    assert result["live_trading_ready"] is False
    assert result["owner_operationally_acceptable"] is False
    assert len(spec["json_names"]) == 14
