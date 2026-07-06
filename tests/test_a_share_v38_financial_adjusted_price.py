from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v38_financial_and_adjusted_price_edges_preserve_fail_closed_rules(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v38")

    assert result["adjusted_price_corporate_action_edge_result_generated"] is True
    assert result["financial_pit_edge_case_result_generated"] is True
    assert result["financial_pit_edge_fabricated"] is False
    assert result["raw_adjusted_price_fallback_blocked_by_default"] is True
