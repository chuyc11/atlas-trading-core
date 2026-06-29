from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.research_output_card import build_research_output_card


def test_research_output_card_finds_required_reports(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_research_output_card(paths=paths, as_of_date=AS_OF_DATE)
    assert card["briefing_status"] == "available"
    assert card["tracking_status"] == "available"
    assert card["blocking_reasons"] == []
