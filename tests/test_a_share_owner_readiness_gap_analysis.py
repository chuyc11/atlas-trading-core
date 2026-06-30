from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_owner_readiness_gap_analysis_calculates_gap(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    gap = exception_data(paths, "owner_readiness_gap_analysis.json")
    assert gap["score_gap"] == gap["minimum_owner_readiness_score"] - gap["actual_owner_readiness_score"]
    assert gap["not_trading_signal"] is True
