from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_evidence_quality_assessment_marks_insufficient(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    assessment = execution_data(paths, "recovery_evidence_quality_assessment.json")
    assert assessment["evidence_quality_grade"] == "insufficient"
    assert assessment["evidence_sufficient_for_gate_reevaluation"] is False
    assert assessment["does_not_fabricate_evidence"] is True
