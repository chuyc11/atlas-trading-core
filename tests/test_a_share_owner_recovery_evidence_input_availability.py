from tests.a_share_recovery_evidence_test_utils import AS_OF_DATE, make_paths, seed_recovery_evidence_inputs
from trading_core.equity_owner_recovery_evidence.input_availability import build_input_availability


def test_recovery_evidence_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_inputs(paths)
    availability = build_input_availability(as_of_date=AS_OF_DATE, paths=paths)
    assert availability["overall_passed"] is True
    assert availability["preferred_source"] == "v0.8.17_controlled_gate_reevaluation_artifacts"
    assert availability["reevaluation_skipped"] is True

