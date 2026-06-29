from tests.a_share_ops_center_test_utils import build_ops_artifacts
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_ops_history.input_availability import load_json, ops_history_input_paths
from trading_core.equity_ops_history.run_record import build_ops_run_record


def test_ops_run_record_extracts_health_and_boundary(tmp_path):
    paths = make_paths(tmp_path)
    build_ops_artifacts(paths)
    input_paths = ops_history_input_paths(paths, AS_OF_DATE)
    payloads = {key: load_json(path) for key, path in input_paths.items()}
    record = build_ops_run_record(paths=paths, as_of_date=AS_OF_DATE, payloads=payloads, input_paths=input_paths)
    assert isinstance(record["ops_health_score"], int)
    assert record["ops_health_grade"] in {"A", "B", "C", "D", "F"}
    assert record["boundary_clean"] is True
    assert record["commands_executed"] == []
