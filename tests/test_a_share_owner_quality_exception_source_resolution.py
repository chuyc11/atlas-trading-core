from tests.a_share_owner_quality_exception_test_utils import AS_OF_DATE, make_paths, seed_owner_quality_exception_inputs
from trading_core.equity_owner_quality_exceptions.input_availability import build_input_availability
from trading_core.equity_owner_quality_exceptions.source_resolution import build_source_resolution


def test_quality_exception_source_resolution_prefers_v0813_gate(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["preferred_source"] == "v0.8.13_owner_readiness_gate"
    assert result["no_broker_inputs"] is True
