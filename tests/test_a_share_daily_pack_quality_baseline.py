from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.input_availability import load_json
from trading_core.equity_owner_daily_pack_history.quality_baseline import build_quality_baseline


def test_daily_pack_quality_baseline_insufficient_history(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    quality = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_quality_baseline.json")
    assert quality["baseline_status"] == "insufficient_history"
    assert quality["no_fabricated_trends"] is True


def test_daily_pack_quality_baseline_enough_history(tmp_path):
    quality = build_quality_baseline(
        as_of_date=AS_OF_DATE,
        artifacts={},
        records=[{}] * 5,
        sufficiency={"trend_analysis_available": True},
        source_trace={"source_trace_complete": True},
        boundary={"overall_passed": True, "forbidden_wording_positive_hits": []},
        summary={"not_investment_decision_pack": True},
    )
    assert quality["baseline_status"] == "available"
