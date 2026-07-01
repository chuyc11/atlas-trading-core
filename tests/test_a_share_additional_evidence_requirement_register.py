from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_additional_evidence_requirements_are_concrete_and_non_executing(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    register = final_json(paths, "additional_evidence_requirement_register")

    assert register["overall_requirement_status"] == "additional_evidence_required"
    assert register["requirement_count"] >= 3
    assert register["blocking_requirement_count"] >= 1
    assert register["minimum_future_research_days_required"] == 3
    assert register["future_research_days_required"] == 3
    assert any(item["category"] == "additional_research_output_days" for item in register["requirements"])
