from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths
from a_share_feature_test_utils import AS_OF_DATE


def test_validate_existing_artifacts_does_not_regenerate_upstream_artifacts(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    score_manifest = paths.data_dir / "equity_scores" / "daily" / AS_OF_DATE / "score_manifest.json"
    before = score_manifest.read_bytes()

    result = build_workflow_package(paths, mode="validate_existing_artifacts")

    assert result["workflow_run_manifest"]["overall_passed"] is True
    assert score_manifest.read_bytes() == before
    commands = [stage["command"] for stage in result["workflow_run_manifest"]["stages"]]
    assert not any("build-and-audit-a-share" in command for command in commands[2:9])
