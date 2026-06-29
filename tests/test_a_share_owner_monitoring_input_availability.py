from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_owner_monitoring.input_availability import build_monitoring_input_availability


def test_monitoring_input_availability_passes_seeded_dashboard(tmp_path):
    paths = make_paths(tmp_path)
    seed_monitoring_inputs(paths)
    availability = build_monitoring_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert availability["overall_passed"] is True
    assert availability["input_audit_checks"]["owner_dashboard_audit_passed"] is True
