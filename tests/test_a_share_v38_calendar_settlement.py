from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v38_calendar_and_settlement_edges_are_verified(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v38")

    assert result["v37_baseline_verified"] is True
    assert result["calendar_edge_case_result_generated"] is True
    assert result["tplusone_settlement_edge_case_result_generated"] is True
    assert result["calendar_edge_fabricated"] is False
    assert result["settlement_edge_fabricated"] is False
    assert result["formal_calendar_fail_closed_verified"] is True
