from __future__ import annotations

from pathlib import Path

from a_share_daily_workflow_test_utils import build_workflow_package, make_workflow_paths, workflow_output_dir


def test_daily_workflow_owner_summary_generated_without_forbidden_positive_wording(tmp_path: Path) -> None:
    paths = make_workflow_paths(tmp_path)
    build_workflow_package(paths)
    text = (workflow_output_dir(paths) / "A_SHARE_DAILY_WORKFLOW_SUMMARY.md").read_text(encoding="utf-8")

    assert "A 股每日研究工作流汇总" in text
    assert "阶段状态" in text
    assert "候选池与组合" in text
    for phrase in ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]:
        assert phrase not in text
