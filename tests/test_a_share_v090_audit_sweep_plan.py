from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v090_audit_sweep_plan_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    plan = closeout_data(paths, "v090_audit_sweep_plan.json")
    assert plan["audit_count"] == 9
    assert all(item["blocks_v090_rc_if_failed"] is True for item in plan["audits"])
