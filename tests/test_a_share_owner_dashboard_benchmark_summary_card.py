from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.benchmark_summary_card import build_benchmark_summary_card


def test_benchmark_summary_card_reads_first_day_state(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_benchmark_summary_card(paths=paths, as_of_date=AS_OF_DATE)
    assert card["status"] == "available"
    assert card["first_day_initialization"] is True
