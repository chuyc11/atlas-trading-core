from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_controlled_reevaluation_plan_does_not_execute(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    plan = execution_data(paths, "controlled_reevaluation_plan.json")
    assert plan["gate_reevaluation_executed"] is False
    assert plan["rerun_owner_readiness_gate"] is False
    assert plan["rerun_build_from_existing_data"] is False
    assert plan["rerun_daily_pack"] is False
