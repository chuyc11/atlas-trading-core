from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v34_strategy_model_ensemble_contribution_is_not_signal(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v34")

    assert result["strategy_model_ensemble_contribution_generated"] is True
    assert result["strategy_model_ensemble_contribution_fabricated"] is False
    assert result["attribution_generates_buy_sell_signal"] is False
