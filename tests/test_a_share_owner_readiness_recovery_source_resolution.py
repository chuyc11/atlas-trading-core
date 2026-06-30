from tests.a_share_owner_readiness_recovery_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_recovery_inputs
from trading_core.equity_owner_readiness_recovery.input_availability import build_input_availability
from trading_core.equity_owner_readiness_recovery.source_resolution import build_source_resolution


def test_owner_readiness_recovery_source_resolution_prefers_v0814_quality_exceptions(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["preferred_source"] == "v0.8.14_owner_quality_exception_workflow"
    assert result["no_real_account_inputs"] is True
