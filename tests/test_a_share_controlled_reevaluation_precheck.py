from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_controlled_precheck_does_not_execute_gate(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    precheck = phase_b(paths, "controlled_reevaluation_precheck")

    assert precheck["controlled_reevaluation_executed"] is False
    assert precheck["owner_readiness_gate_rerun"] is False
    assert precheck["new_gate_score_generated"] is False
    assert precheck["new_gate_decision_generated"] is False
    assert precheck["precheck_status"] == "not_ready"
    assert any(not item["passed"] for item in precheck["criteria"])
