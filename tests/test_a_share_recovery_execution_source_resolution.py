from tests.a_share_recovery_execution_test_utils import AS_OF_DATE, make_paths, seed_recovery_execution_inputs
from trading_core.equity_owner_readiness_recovery_execution.input_availability import build_input_availability
from trading_core.equity_owner_readiness_recovery_execution.source_resolution import build_source_resolution


def test_recovery_execution_source_resolution_prefers_v0815_recovery(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["preferred_source"] == "v0.8.15_owner_readiness_recovery_artifacts"
    assert result["no_real_account_inputs"] is True
