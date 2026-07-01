from tests.a_share_recovery_evidence_test_utils import AS_OF_DATE, make_paths, seed_recovery_evidence_inputs
from trading_core.equity_owner_recovery_evidence.input_availability import build_input_availability
from trading_core.equity_owner_recovery_evidence.source_resolution import build_source_resolution


def test_recovery_evidence_source_resolution_prefers_v017(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_inputs(paths)
    availability = build_input_availability(as_of_date=AS_OF_DATE, paths=paths)
    resolution = build_source_resolution(as_of_date=AS_OF_DATE, paths=paths, input_availability=availability)
    assert resolution["overall_passed"] is True
    assert resolution["preferred_source"] == "v0.8.17_controlled_gate_reevaluation_artifacts"
    assert resolution["no_broker_inputs"] is True

