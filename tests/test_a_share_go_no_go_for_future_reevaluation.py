from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_go_no_go_is_not_gate_decision(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    decision = phase_b(paths, "go_no_go_for_future_reevaluation")

    assert decision["decision"] == "no_go_additional_evidence_required"
    assert decision["not_owner_readiness_gate_decision"] is True
    assert decision["controlled_reevaluation_executed"] is False
    assert decision["new_gate_score_generated"] is False
    assert decision["new_gate_decision_generated"] is False
    assert decision["forbidden_next_step"] == "execute_controlled_reevaluation_now"
