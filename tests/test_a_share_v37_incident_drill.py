from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v37_incident_drill_does_not_fabricate_or_remediate_destructively(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v37")

    assert result["incident_drill_result_generated"] is True
    assert result["incident_evidence_fabricated"] is False
    assert result["destructive_recovery_performed"] is False
    assert result["git_history_rollback_performed"] is False
