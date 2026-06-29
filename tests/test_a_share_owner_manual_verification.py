from trading_core.equity_owner_remediation.manual_verification import build_manual_verification_checklist


def test_manual_verification_checklist_generated():
    availability = {
        "blocking_reasons": [],
        "input_artifacts": [
            {"artifact_id": "data_refresh_audit", "exists": True},
            {"artifact_id": "current_day_run_audit", "exists": True},
            {"artifact_id": "owner_dashboard_audit", "exists": True},
            {"artifact_id": "owner_monitoring_audit", "exists": True},
        ],
    }
    checklist = build_manual_verification_checklist(as_of_date="2026-06-26", availability=availability, boundary={"overall_passed": True})
    assert checklist["overall_passed"] is True
    assert len(checklist["checks"]) >= 13
