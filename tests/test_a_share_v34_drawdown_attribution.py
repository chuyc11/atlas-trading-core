from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v34_drawdown_attribution_is_not_real_allocation(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v34")

    assert result["drawdown_attribution_generated"] is True
    assert result["drawdown_attribution_fabricated"] is False
    assert result["attribution_generates_real_allocation"] is False
