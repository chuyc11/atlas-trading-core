from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_text
from trading_core.equity_owner_monitoring.monitoring_boundary import build_monitoring_boundary_check


def test_monitoring_boundary_fails_on_date_order_artifact(tmp_path):
    paths = make_paths(tmp_path)
    write_text(paths.data_dir / "orders" / f"orders-{AS_OF_DATE}.jsonl", "{}")
    boundary = build_monitoring_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is False
    assert boundary["forbidden_artifacts_present"]
