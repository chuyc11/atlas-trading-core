from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_owner_monitoring.monitoring_audit import audit_a_share_owner_monitoring
from trading_core.equity_owner_monitoring.monitoring_builder import build_a_share_owner_monitoring


def test_owner_monitoring_audit_passes_generated_artifacts(tmp_path):
    paths = make_paths(tmp_path)
    seed_monitoring_inputs(paths)
    build_a_share_owner_monitoring(as_of_date=AS_OF_DATE, paths=paths)
    audit = audit_a_share_owner_monitoring(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
