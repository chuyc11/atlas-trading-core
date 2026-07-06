from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v37_observability_is_local_internal_only(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v37")
    telemetry = component_json(paths, "v37", "v37_run_telemetry_result")

    assert result["v36_baseline_verified"] is True
    assert result["run_telemetry_result_generated"] is True
    assert telemetry["telemetry_scope"] == "local_internal_only"
    assert result["telemetry_external_notification_enabled"] is False
