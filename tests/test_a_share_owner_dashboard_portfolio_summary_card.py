from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.portfolio_summary_card import build_portfolio_summary_card


def test_portfolio_summary_card_reads_tracking_snapshots(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_portfolio_summary_card(paths=paths, as_of_date=AS_OF_DATE)
    assert card["status"] == "available"
    assert card["portfolio_count"] == 1
