from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.dashboard_builder import build_a_share_owner_dashboard
from trading_core.equity_owner_dashboard.dashboard_config import dashboard_artifact_paths


def test_dashboard_report_is_written(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    build_a_share_owner_dashboard(as_of_date=AS_OF_DATE, paths=paths)
    artifacts = dashboard_artifact_paths(paths, AS_OF_DATE)
    assert artifacts["owner_dashboard_report"].exists()
    assert "no broker" in artifacts["owner_dashboard_report"].read_text(encoding="utf-8")
