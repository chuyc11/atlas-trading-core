from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.attribution_summary_card import build_attribution_summary_card


def test_attribution_summary_card_marks_structural_diagnostics(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_attribution_summary_card(paths=paths, as_of_date=AS_OF_DATE)
    assert card["status"] == "structural_diagnostics_available"
    assert card["realized_performance_attribution_available"] is False
