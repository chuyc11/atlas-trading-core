from __future__ import annotations

from pathlib import Path

from a_share_release_chain_test_utils import build_release, make_release_paths


def test_v29_v3_readiness_prepares_without_releasing_v3(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v29")
    spec, result, audit = build_release(paths, "v29")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert result["v28_baseline_verified"] is True
    assert result["docs_operator_guide_generated"] is True
    assert result["migration_upgrade_plan_generated"] is True
    assert result["owner_v3_readiness_dashboard_generated"] is True
    assert result["v3_released"] is False
    assert result["full_pytest_run"] is False
    assert result["known_limitations_hidden"] is False
    assert len(spec["json_names"]) == 13
