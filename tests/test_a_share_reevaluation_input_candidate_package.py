from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_reevaluation_input_candidate_package_is_not_gate_execution(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    package = phase_b(paths, "reevaluation_input_candidate_package")

    assert package["not_gate_execution"] is True
    assert package["owner_readiness_gate_executed"] is False
    assert package["new_gate_score_generated"] is False
    assert package["new_gate_decision_generated"] is False
    assert package["package_status"] == "not_ready"
    assert "minimum_evidence_days_for_future_controlled_reevaluation" in package["missing_required_sections"]
