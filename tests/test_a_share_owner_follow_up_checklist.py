from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_owner_follow_up_checklist_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    checklist = exception_data(paths, "owner_follow_up_checklist.json")
    assert checklist["owner_follow_up_count"] >= 1
    assert checklist["not_order_instruction"] is True
