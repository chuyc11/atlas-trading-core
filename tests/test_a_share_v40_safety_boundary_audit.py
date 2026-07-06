from a_share_v3x_release_test_utils import assert_common_boundary, build_through, make_v3x_paths


def test_v40_final_safety_boundary_and_no_fabrication(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v40")

    assert result["fabricated_test_result"] is False
    assert result["fabricated_security_evidence"] is False
    assert result["fabricated_incident_evidence"] is False
    assert result["fabricated_docs_evidence"] is False
    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert_common_boundary(result)
