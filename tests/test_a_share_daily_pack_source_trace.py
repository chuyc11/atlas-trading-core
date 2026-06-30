from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs
from trading_core.equity_owner_daily_pack.daily_pack_audit import audit_a_share_owner_daily_pack
from trading_core.equity_owner_daily_pack.input_availability import load_json


def test_daily_pack_source_trace_complete_and_hashes_match(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)

    trace = load_json(paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "daily_pack_source_trace.json")
    audit = audit_a_share_owner_daily_pack(as_of_date=AS_OF_DATE, paths=paths)

    assert trace["source_trace_complete"] is True
    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
