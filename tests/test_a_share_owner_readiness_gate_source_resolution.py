from tests.a_share_owner_readiness_gate_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_gate_inputs
from trading_core.equity_owner_readiness_gate.input_availability import build_input_availability
from trading_core.equity_owner_readiness_gate.source_resolution import build_source_resolution


def test_owner_readiness_gate_source_resolution_prefers_history(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_inputs(paths)
    availability = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    result = build_source_resolution(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability)
    assert result["preferred_source"] == "v0.8.12_owner_daily_pack_history"
    assert result["no_real_account_inputs"] is True
