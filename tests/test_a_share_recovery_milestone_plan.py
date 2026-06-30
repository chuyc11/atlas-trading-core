from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_milestone_plan_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    plan = recovery_data(paths, "recovery_milestone_plan.json")
    assert len(plan["milestones"]) >= 5
    assert all(item["status"] == "planned" for item in plan["milestones"])
