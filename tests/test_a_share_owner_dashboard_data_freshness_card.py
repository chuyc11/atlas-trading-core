from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.data_freshness_card import build_data_freshness_card


def test_data_freshness_card_uses_refresh_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_data_freshness_card(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    assert card["data_refresh_audit_passed"] is True
    assert card["freshness_status"] == "passed"
