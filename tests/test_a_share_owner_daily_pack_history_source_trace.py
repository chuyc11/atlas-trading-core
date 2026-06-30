from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.daily_pack_history_audit import audit_a_share_owner_daily_pack_history
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_history_source_trace_complete_and_hashes_match(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    trace = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_history_source_trace.json")
    audit = audit_a_share_owner_daily_pack_history(as_of_date=AS_OF_DATE, paths=paths)
    assert trace["source_trace_complete"] is True
    assert audit["overall_passed"] is True
