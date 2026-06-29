from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.candidate_summary_card import build_candidate_summary_card


def test_candidate_summary_card_counts_candidate_lists(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_candidate_summary_card(paths=paths, as_of_date=AS_OF_DATE)
    assert card["long_candidate_count"] == 2
    assert card["top10_symbols"]["long"] == ["000001.SZ", "000002.SZ"]
