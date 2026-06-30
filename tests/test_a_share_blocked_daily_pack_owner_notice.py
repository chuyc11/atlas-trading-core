from tests.a_share_owner_quality_exception_test_utils import AS_OF_DATE, exception_data, make_paths, seed_owner_quality_exception_outputs


def test_blocked_daily_pack_owner_notice_explains_blocked_state(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    notice = exception_data(paths, "blocked_daily_pack_owner_notice.json")
    text = (paths.outputs_dir / "equity_owner_quality_exceptions" / "daily" / AS_OF_DATE / "A_SHARE_BLOCKED_DAILY_PACK_OWNER_NOTICE.md").read_text(encoding="utf-8")
    assert notice["daily_pack_owner_operationally_acceptable"] is False
    assert "audit passed" in text
    assert "不代表 gate 放行" in text
