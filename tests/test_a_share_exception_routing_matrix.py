from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_exception_routing_matrix_has_no_forbidden_routes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    routing = exception_data(paths, "exception_routing_matrix.json")
    assert routing["no_forbidden_routes"] is True
