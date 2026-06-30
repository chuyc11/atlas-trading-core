from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, make_paths, seed_controlled_gate_reevaluation_inputs
from trading_core.equity_owner_controlled_gate_reevaluation.input_availability import build_input_availability
from trading_core.equity_owner_controlled_gate_reevaluation.source_resolution import build_source_resolution


def test_controlled_gate_reevaluation_source_resolution(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_inputs(paths)
    availability = build_input_availability(as_of_date=AS_OF_DATE, paths=paths)
    resolution = build_source_resolution(as_of_date=AS_OF_DATE, paths=paths, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["preferred_source"] == "v0.8.16_owner_readiness_recovery_execution_artifacts"
    assert resolution["no_broker_inputs"] is True

