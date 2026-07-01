from tests.a_share_v0820_test_utils import AS_OF_DATE, make_paths, seed_v0820_inputs
from trading_core.equity_owner_v0820_gate_outcome.input_availability import build_input_availability


def test_v0820_input_availability_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_inputs(paths)
    passed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert passed["overall_passed"] is True
    assert passed["evidence_backed_prep_audit_passed"] is True
    assert passed["v0819_eligibility_decision"] == "not_eligible"
    (paths.data_dir / "equity_data_quality" / "a_share_owner_evidence_backed_reevaluation_prep_audit.json").unlink()
    failed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False
    assert "required_inputs_missing" in failed["blocking_reasons"]

