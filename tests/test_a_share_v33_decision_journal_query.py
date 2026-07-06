from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v33_decision_journal_query_cannot_generate_trade_instruction(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v33")

    assert result["decision_journal_query_generated"] is True
    assert result["decision_journal_query_generates_trade_instruction"] is False
    assert result["not_investment_advice"] is True
