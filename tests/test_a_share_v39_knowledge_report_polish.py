from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v39_knowledge_base_and_report_polish_are_evidence_safe(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v39")

    assert result["knowledge_base_polish_generated"] is True
    assert result["report_readability_consistency_generated"] is True
    assert result["knowledge_base_links_fabricated"] is False
    assert result["question_router_generates_trading_advice"] is False
    assert result["forbidden_wording_detected"] is False
