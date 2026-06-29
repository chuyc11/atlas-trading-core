from tests.a_share_current_day_test_utils import AS_OF_DATE
from trading_core.equity_current_day.current_day_report import render_summary


def test_current_day_report_rendered_without_positive_forbidden_wording():
    payload = {
        "current_day_summary": {
            "overall_passed": True,
            "as_of_date": AS_OF_DATE,
            "resolved_as_of_date": AS_OF_DATE,
            "mode": "run_research_from_existing_refresh",
            "workflow_mode": "validate_existing_artifacts",
            "data_refresh_audit_passed": True,
            "workflow_audit_passed": True,
            "key_artifacts": {},
            "warning_summary": {"warning_count": 0, "known_warnings_carried_forward": []},
            "blocking_reasons": [],
        },
        "current_day_stage_manifest": {"stages": []},
    }
    text = render_summary(payload)
    assert "总体结论" in text
    assert "推荐买入" not in text
    assert "保证盈利" not in text

