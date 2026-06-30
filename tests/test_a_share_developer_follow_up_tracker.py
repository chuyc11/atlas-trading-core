from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_developer_follow_up_tracker_generated_and_commands_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    tracker = exception_data(paths, "developer_follow_up_tracker.json")
    assert tracker["follow_up_count"] >= 1
    assert tracker["no_forbidden_follow_up_commands"] is True
