from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v32_runtime_profile_does_not_fabricate_performance_claims(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")

    assert result["runtime_profile_result_generated"] is True
    assert result["runtime_profile_fabricated"] is False
    assert result["performance_claim_fabricated"] is False
    assert result["performance_pass_means_live_trading_ready"] is False
