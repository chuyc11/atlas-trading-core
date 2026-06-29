from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths, seed_data_refresh
from trading_core.equity_current_day.current_day_readiness import build_current_day_readiness


def test_current_day_readiness_passes_when_data_refresh_passed(tmp_path):
    paths = make_paths(tmp_path)
    seed_data_refresh(paths)
    readiness = build_current_day_readiness(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE, workflow_mode="validate_existing_artifacts")
    assert readiness["overall_passed"] is True
    assert readiness["data_refresh_audit_passed"] is True
    assert "daily_basic:required_field_all_null" in readiness["known_warnings"]


def test_current_day_readiness_fails_when_data_refresh_failed(tmp_path):
    paths = make_paths(tmp_path)
    seed_data_refresh(paths, passed=False)
    readiness = build_current_day_readiness(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE, workflow_mode="validate_existing_artifacts")
    assert readiness["overall_passed"] is False
    assert "data_refresh_audit_passed=false" in readiness["blocking_reasons"]

