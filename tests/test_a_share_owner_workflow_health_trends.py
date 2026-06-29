from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_owner_monitoring.workflow_health_trends import build_workflow_health_trend_snapshot


def test_workflow_health_trend_reads_workflow_card(tmp_path):
    paths = make_paths(tmp_path)
    seed_monitoring_inputs(paths)
    snapshot = build_workflow_health_trend_snapshot(paths=paths, as_of_date=AS_OF_DATE, run_history_snapshot={"run_history_observation_count": 1, "records": []}, minimum_history_observations=3)
    assert snapshot["current_status"] == "passed"
    assert snapshot["trend_status"] == "insufficient_history"
