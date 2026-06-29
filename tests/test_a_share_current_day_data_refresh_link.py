from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths, seed_data_refresh
from trading_core.equity_current_day.data_refresh_link import build_data_refresh_link


def test_current_day_data_refresh_link_carries_warnings_and_hash(tmp_path):
    paths = make_paths(tmp_path)
    seed_data_refresh(paths)
    link = build_data_refresh_link(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    assert link["data_refresh_audit_passed"] is True
    assert link["data_refresh_audit_hash"]
    assert "trading_calendar:exchange_level_calendar_collapsed_to_trade_date" in link["data_refresh_warnings"]

