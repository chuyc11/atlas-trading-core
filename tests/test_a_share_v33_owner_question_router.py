from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v33_owner_question_router_refuses_trading_advice(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v33")
    question = component_json(paths, "v33", "v33_owner_question_router_result")

    assert result["owner_question_router_generated"] is True
    assert result["question_router_generates_trading_advice"] is False
    assert result["question_router_generates_buy_sell_signal"] is False
    assert question["unsupported_question_handling"] == "safety_refusal_for_trading_advice"
