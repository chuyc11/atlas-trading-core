from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_readiness_gap_summary_calculates_gap(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    gap = recovery_data(paths, "readiness_gap_summary.json")
    assert gap["source_gate_decision"] == "blocked"
    assert gap["readiness_score_gap"] == gap["minimum_owner_readiness_score"] - gap["actual_owner_readiness_score"]
    assert gap["not_trade_instruction"] is True
