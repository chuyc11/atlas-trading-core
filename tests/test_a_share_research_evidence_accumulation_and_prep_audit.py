from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, seed_research_evidence_inputs
from trading_core.equity_research_evidence_accumulation import (
    audit_a_share_research_evidence_accumulation_and_prep,
    build_a_share_research_evidence_accumulation_and_prep,
)


def test_combined_audit_passes_generated_package_and_policy(tmp_path):
    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    audit = audit_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["phase_a_checks"]["evidence_accumulation_result_generated"] is True
    assert audit["phase_b_checks"]["go_no_go_decision_generated"] is True
    assert audit["gate_safety"]["owner_readiness_state"] == "blocked"
    assert audit["trading_boundary"]["broker_connected"] is False
    assert audit["test_policy"]["full_pytest_run"] is False
