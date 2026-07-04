from __future__ import annotations

from pathlib import Path

from a_share_v24_test_utils import build_v24, make_v24_paths, v24_json


def test_v24_cleanup_plan_is_dry_run_and_does_not_claim_fake_savings(tmp_path: Path) -> None:
    paths = make_v24_paths(tmp_path)
    build_v24(paths)
    cleanup = v24_json(paths, "v24_artifact_cleanup_plan_result")

    assert cleanup["artifact_cleanup_plan_result_generated"] is True
    assert cleanup["cleanup_plan_dry_run_only"] is True
    assert cleanup["cleanup_actions"] == []
    assert cleanup["estimated_space_savings_bytes"] == 0
    assert cleanup["space_savings_fabricated"] is False
    assert cleanup["historical_evidence_deleted"] is False
    assert cleanup["audit_evidence_deleted"] is False
    assert cleanup["release_evidence_deleted"] is False
    assert cleanup["required_artifacts_deleted"] is False
