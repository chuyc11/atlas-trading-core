from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_reevaluation_prep_boundary_preserves_blocked_state(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    boundary = phase_b(paths, "reevaluation_prep_boundary_check")

    assert boundary["overall_passed"] is True
    assert boundary["known_owner_readiness_state"] == "blocked"
    assert boundary["owner_operationally_acceptable"] is False
    assert boundary["source_readiness_score"] == 54
    assert boundary["controlled_reevaluation_executed"] is False
    assert boundary["owner_readiness_gate_rerun"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
