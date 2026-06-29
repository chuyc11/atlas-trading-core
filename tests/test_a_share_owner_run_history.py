from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_monitoring_test_utils import seed_monitoring_inputs
from trading_core.equity_owner_monitoring.run_history import update_run_history


def test_run_history_is_append_only_and_deduplicates(tmp_path):
    paths = make_paths(tmp_path)
    seed_monitoring_inputs(paths)
    update_run_history(paths=paths, as_of_date=AS_OF_DATE, history_window_days=30, minimum_history_observations=3, allow_rebuild_history=False)
    _, snapshot = update_run_history(paths=paths, as_of_date=AS_OF_DATE, history_window_days=30, minimum_history_observations=3, allow_rebuild_history=False)
    assert snapshot["run_history_observation_count"] == 1
    assert snapshot["trend_analysis_available"] is False
