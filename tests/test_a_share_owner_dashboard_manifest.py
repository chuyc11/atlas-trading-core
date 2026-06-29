from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE
from trading_core.equity_owner_dashboard.dashboard_manifest import build_dashboard_manifest


def test_manifest_carries_recommended_next_version():
    manifest = build_dashboard_manifest(as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE, generated_at="now", mode="build_dashboard_from_existing_run", executive_status_card={"overall_status": "passed"}, required_cards_present=True, optional_cards_present=True, warning_and_blocker_card={"blocking_count": 0, "warning_count": 1}, output_artifacts={}, source_artifacts={}, boundary={"overall_passed": True})
    assert manifest["required_cards_present"] is True
    assert manifest["recommended_next_version"].startswith("v0.8.3")
