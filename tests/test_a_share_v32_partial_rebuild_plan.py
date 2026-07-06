from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v32_partial_rebuild_plan_is_dry_run_only(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")
    plan = component_json(paths, "v32", "v32_partial_rebuild_plan_result")

    assert result["partial_rebuild_plan_result_generated"] is True
    assert plan["dry_run_partial_rebuild_mode"] is True
    assert result["cache_bypassed_safety_audit"] is False
