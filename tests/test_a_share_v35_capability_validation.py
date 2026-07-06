from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v35_capability_validation_does_not_fabricate_claims(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v35")

    assert result["v3x_capability_validation_generated"] is True
    assert result["fabricated_capability_claim"] is False
    assert result["historical_evidence_deleted"] is False
