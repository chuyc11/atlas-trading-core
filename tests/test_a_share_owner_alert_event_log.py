from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_owner_monitoring.alert_event_log import write_alert_event_log_and_history


def test_alert_event_log_never_sends_external_notifications(tmp_path):
    paths = make_paths(tmp_path)
    log, history = write_alert_event_log_and_history(paths=paths, as_of_date=AS_OF_DATE, alert_evaluation_result={"events": [{"alert_id": "a", "status": "not_triggered"}]})
    assert log["external_notifications_sent"] is False
    assert history["event_count"] == 1
