from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_owner_monitoring.provider_health_trends import build_provider_health_trend_snapshot


def test_provider_health_trend_does_not_fabricate_history(tmp_path):
    paths = make_paths(tmp_path)
    seed_monitoring_inputs(paths)
    snapshot = build_provider_health_trend_snapshot(paths=paths, as_of_date=AS_OF_DATE, run_history_snapshot={"run_history_observation_count": 1, "records": []}, minimum_history_observations=3)
    assert snapshot["insufficient_history"] is True
    assert snapshot["degraded"] is False
