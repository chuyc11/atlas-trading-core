from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_non_actionable_recovery_items_include_history_wait(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    items = recovery_data(paths, "non_actionable_recovery_items.json")
    assert items["item_count"] == 1
    assert items["items"][0]["status"] == "waiting_for_more_history"
