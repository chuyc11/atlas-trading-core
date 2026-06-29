from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_owner_monitoring.monitoring_builder import build_a_share_owner_monitoring
from trading_core.equity_owner_monitoring.monitoring_config import monitoring_artifact_paths


def test_owner_monitoring_reports_are_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_monitoring_inputs(paths)
    build_a_share_owner_monitoring(as_of_date=AS_OF_DATE, paths=paths)
    artifacts = monitoring_artifact_paths(paths, AS_OF_DATE)
    assert artifacts["owner_monitoring_summary_report"].exists()
    assert "今日监控总览" in artifacts["owner_monitoring_summary_report"].read_text(encoding="utf-8")
