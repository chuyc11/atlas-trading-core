from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_quality_exception_classification_covers_score_and_insufficient_history(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    rows = exception_data(paths, "quality_exception_classification.json")["classifications"]
    categories = {row["category"] for row in rows}
    assert "readiness_score_below_threshold" in categories
    assert "insufficient_history" in categories
    assert all(row["trade_related"] is False and row["broker_related"] is False and row["order_related"] is False for row in rows)
