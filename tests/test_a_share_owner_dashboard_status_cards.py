from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.status_cards import build_provider_health_card


def test_provider_health_card_summarizes_disabled_network_providers(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_provider_health_card(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    assert card["provider_count"] == 3
    assert card["network_providers_disabled"] is True
