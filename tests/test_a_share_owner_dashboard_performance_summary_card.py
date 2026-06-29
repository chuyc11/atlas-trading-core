from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.performance_summary_card import build_performance_summary_card


def test_performance_summary_card_marks_limited_history(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_performance_summary_card(paths=paths, as_of_date=AS_OF_DATE)
    assert card["status"] == "limited_history"
    assert card["sufficient_history"] is False
