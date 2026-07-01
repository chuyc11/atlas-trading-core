from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_evidence_quality_scorecard_is_not_gate_score(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    scorecard = phase_b(paths, "evidence_quality_scorecard")

    assert scorecard["not_owner_readiness_score"] is True
    assert scorecard["not_gate_score"] is True
    assert scorecard["strong_evidence_count"] >= 1
    assert scorecard["moderate_evidence_count"] >= 1
    assert scorecard["evidence_quality_overall_status"] in {"partial", "insufficient"}
