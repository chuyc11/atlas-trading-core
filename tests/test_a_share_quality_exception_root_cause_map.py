from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_quality_exception_root_cause_map_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    root_map = recovery_data(paths, "quality_exception_root_cause_map.json")
    assert root_map["mapped_count"] == 3
    assert any(item["requires_developer_follow_up"] for item in root_map["items"])
    assert all(item["evidence"] and item["confidence"] for item in root_map["items"])
