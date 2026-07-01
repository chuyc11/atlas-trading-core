from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_owner_not_ready_summary_is_chinese_owner_facing_and_safe(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    summary = final_json(paths, "owner_not_ready_summary")

    assert summary["headline"] == "Owner-readiness remains blocked."
    assert "当前研究系统可以继续用于 research-only / virtual-only 分析" in summary["plain_language_summary"]
    assert summary["not_live_trading_ready"] is True
    assert summary["not_investment_advice"] is True
    assert summary["not_order_instruction"] is True
    assert any("不能把候选股当作买入建议" in item for item in summary["what_owner_must_not_do"])
