from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs


def test_owner_daily_pack_history_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    out = paths.outputs_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE
    assert "Owner Daily Pack History" in (out / "A_SHARE_OWNER_DAILY_PACK_HISTORY.md").read_text(encoding="utf-8")
    assert "Owner Readiness Trends" in (out / "A_SHARE_OWNER_READINESS_TRENDS.md").read_text(encoding="utf-8")
    assert (out / "A_SHARE_DAILY_PACK_HISTORY_SOURCE_TRACE.md").exists()
