from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, phase_b, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import build_a_share_research_evidence_accumulation_and_prep


def test_not_ready_reason_register_generated_for_no_go(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    register = phase_b(paths, "not_ready_reason_register")

    assert register["not_ready"] is True
    assert register["reason_count"] >= 1
    assert register["owner_readiness_state_preserved"] == "blocked"
    assert register["owner_operationally_acceptable"] is False
