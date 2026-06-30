from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, make_paths, seed_controlled_gate_reevaluation_inputs
from trading_core.equity_owner_controlled_gate_reevaluation.input_availability import build_input_availability


def test_controlled_gate_reevaluation_input_availability_prefers_recovery_execution(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_inputs(paths)
    availability = build_input_availability(as_of_date=AS_OF_DATE, paths=paths)
    assert availability["overall_passed"] is True
    assert availability["preferred_source"] == "v0.8.16_owner_readiness_recovery_execution_artifacts"
    assert availability["source_gate_decision"] == "blocked"
    assert availability["source_ready_for_future_gate_reevaluation"] is False

