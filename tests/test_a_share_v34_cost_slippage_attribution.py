from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v34_cost_slippage_attribution_does_not_generate_rebalance_advice(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v34")

    assert result["turnover_cost_slippage_attribution_generated"] is True
    assert result["cost_slippage_attribution_fabricated"] is False
    assert result["attribution_generates_rebalance_advice"] is False
