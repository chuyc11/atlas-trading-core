from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.dashboard_audit import audit_a_share_owner_dashboard
from trading_core.equity_owner_dashboard.dashboard_builder import build_a_share_owner_dashboard


def seed_monitoring_inputs(paths, as_of_date: str = AS_OF_DATE) -> None:
    seed_owner_dashboard_inputs(paths, as_of_date)
    build_a_share_owner_dashboard(as_of_date=as_of_date, paths=paths)
    audit_a_share_owner_dashboard(as_of_date=as_of_date, paths=paths)
