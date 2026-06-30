from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_exception_severity_matrix_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    matrix = exception_data(paths, "exception_severity_matrix.json")
    assert "blocking" in matrix["severity_levels"]
    assert matrix["trade_related_severity_allowed"] is False
