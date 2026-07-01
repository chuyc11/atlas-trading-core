from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_unresolved_blockers_are_not_fabricated_as_closed(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    summary = final_json(paths, "unresolved_blocker_closeout_summary")

    assert summary["source_blocker_count"] == 6
    assert summary["blockers_closed_by_v096"] == 0
    assert summary["blockers_remaining_open"] == 6
    assert summary["overall_blocker_status"] == "open"
    assert all(blocker["closed_by_v096"] is False for blocker in summary["blockers"])
