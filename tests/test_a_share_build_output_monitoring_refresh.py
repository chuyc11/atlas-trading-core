from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core.equity_build_output_ops_refresh.monitoring_refresh import build_alert_summary_refresh, build_monitoring_refresh


def test_build_output_monitoring_and_alert_refresh(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    monitoring = build_monitoring_refresh(paths=paths, as_of_date=AS_OF_DATE)
    alert = build_alert_summary_refresh(paths=paths, as_of_date=AS_OF_DATE, monitoring_refresh=monitoring)
    assert monitoring["monitoring_refresh_performed"] is True
    assert alert["alert_summary_refresh_performed"] is True
    assert alert["external_notifications_sent"] is False

