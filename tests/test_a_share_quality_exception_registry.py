from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_quality_exception_registry_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    registry = exception_data(paths, "quality_exception_registry.json")
    assert registry["exception_count"] >= 1
    assert registry["blocked_gate_decision_preserved"] is True
