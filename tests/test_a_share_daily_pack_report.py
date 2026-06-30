from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs


def test_daily_pack_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)
    out = paths.outputs_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE

    decision = (out / "A_SHARE_OWNER_DAILY_DECISION_PACK.md").read_text(encoding="utf-8")
    runbook = (out / "A_SHARE_OWNER_DAILY_RUNBOOK.md").read_text(encoding="utf-8")

    assert "今日 Owner Operations Decision Pack 总览" in decision
    assert "这是 owner operations decision pack，不是投资决策包。" in decision
    assert "Daily Review Sequence" in runbook
    assert (out / "A_SHARE_OWNER_DAILY_STATUS_BRIEF.md").exists()
    assert (out / "A_SHARE_RESEARCH_OUTPUT_DIGEST.md").exists()
