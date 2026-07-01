from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_next_cycle_plan_requires_additional_days_without_scheduling(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    plan = final_json(paths, "next_cycle_evidence_plan")

    assert plan["plan_status"] == "required"
    assert plan["minimum_additional_research_days"] == 3
    assert plan["target_total_evidence_days"] == 5
    assert plan["current_eligible_days"] == 2
    assert "broker_connection" in plan["forbidden_tasks"]
    assert "owner_readiness_gate_rerun_without_evidence" in plan["forbidden_tasks"]
    assert "Plan is non-executing and does not schedule automation." in plan["notes"]
