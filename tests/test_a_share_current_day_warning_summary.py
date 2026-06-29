from tests.a_share_current_day_test_utils import AS_OF_DATE
from trading_core.equity_current_day.current_day_warning_summary import build_current_day_warning_summary


def test_current_day_warning_summary_classifies_known_warnings():
    summary = build_current_day_warning_summary(
        as_of_date=AS_OF_DATE,
        resolved_as_of_date=AS_OF_DATE,
        data_refresh_warnings=["daily_basic:required_field_all_null"],
        workflow_warnings=["workflow warning"],
    )
    assert summary["warning_count"] == 2
    assert summary["warnings"][0]["classification"] == "known_non_blocking"
    assert summary["overall_passed"] is True

