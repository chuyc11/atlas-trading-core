from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v33_evidence_router_does_not_fabricate_or_route_to_trading(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v33")
    router = component_json(paths, "v33", "v33_evidence_router_result")

    assert result["evidence_router_generated"] is True
    assert result["evidence_links_fabricated"] is False
    assert router["evidence_confidence_is_trading_confidence"] is False
    assert result["not_buy_sell_signal"] is True
