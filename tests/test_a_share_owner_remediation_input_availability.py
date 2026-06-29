from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_remediation_test_utils import seed_remediation_inputs
from trading_core.equity_owner_remediation.input_availability import build_remediation_input_availability


def test_remediation_input_availability_passes_seeded_inputs(tmp_path):
    paths = make_paths(tmp_path)
    seed_remediation_inputs(paths)
    result = build_remediation_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["input_audit_checks"]["owner_monitoring_audit_passed"] is True


def test_remediation_input_availability_fails_missing_inputs(tmp_path):
    paths = make_paths(tmp_path)
    result = build_remediation_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
    assert result["blocking_reasons"]
