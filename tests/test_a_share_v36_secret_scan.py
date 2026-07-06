from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v36_secret_scan_blocks_high_confidence_secret(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v36")
    secret = component_json(paths, "v36", "v36_secret_scan_result")

    assert result["v35_baseline_verified"] is True
    assert result["secret_scan_result_generated"] is True
    assert result["high_confidence_secret_detected"] is False
    assert result["broker_credential_detected"] is False
    assert secret["artifact_generated"] is True
