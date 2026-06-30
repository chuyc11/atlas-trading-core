from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core.equity_build_output_ops_refresh.module_status_refresh import build_module_status_matrix_refresh


def test_build_output_module_status_matrix_refresh_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    matrix = build_module_status_matrix_refresh(paths=paths, as_of_date=AS_OF_DATE)
    assert matrix["module_status_matrix_refresh_performed"] is True
    assert any(row["module_id"] == "build_output_dashboard" for row in matrix["rows"])

