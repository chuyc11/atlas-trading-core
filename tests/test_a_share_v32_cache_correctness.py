from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v32_cache_correctness_blocks_unsafe_reuse(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")

    assert result["cache_correctness_audit_result_generated"] is True
    assert result["cache_bypassed_protected_path_sweep"] is False
    assert result["cache_bypassed_artifact_integrity_sweep"] is False
    assert result["cache_result_fabricated"] is False
