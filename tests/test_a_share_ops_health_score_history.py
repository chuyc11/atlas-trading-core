from trading_core.equity_ops_history.health_score_history import build_ops_health_score_history


def test_ops_health_score_history_uses_run_records():
    history = build_ops_health_score_history(as_of_date="2026-06-26", records=[{"as_of_date": "2026-06-26", "ops_health_score": 65, "ops_health_grade": "C"}])
    assert history["records"][0]["score"] == 65
    assert history["records"][0]["grade"] == "C"

