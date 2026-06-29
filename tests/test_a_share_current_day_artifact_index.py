from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths, seed_data_refresh
from trading_core.equity_current_day.current_day_artifact_index import build_current_day_artifact_index


def test_current_day_artifact_index_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_data_refresh(paths)
    index = build_current_day_artifact_index(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    assert index["artifact_count"] > 0
    assert any(row["stage"] == "data_refresh" for row in index["artifacts"])

