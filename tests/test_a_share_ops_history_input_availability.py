from tests.a_share_ops_center_test_utils import build_ops_artifacts
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_ops_history.input_availability import build_ops_history_input_availability


def test_ops_history_input_availability_requires_passed_ops_center(tmp_path):
    paths = make_paths(tmp_path)
    build_ops_artifacts(paths)
    result = build_ops_history_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["input_audit_checks"]["ops_center_audit_passed"] is True

