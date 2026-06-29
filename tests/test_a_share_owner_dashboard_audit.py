from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.dashboard_audit import audit_a_share_owner_dashboard
from trading_core.equity_owner_dashboard.dashboard_builder import build_a_share_owner_dashboard


def test_owner_dashboard_audit_passes_generated_dashboard(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    build_a_share_owner_dashboard(as_of_date=AS_OF_DATE, paths=paths)
    audit = audit_a_share_owner_dashboard(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
