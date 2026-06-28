from __future__ import annotations

from pathlib import Path

from a_share_daily_stock_selection_briefing_test_utils import build_briefing_package, make_briefing_paths
from trading_core.equity_briefings.briefing_renderer import render_daily_stock_selection_briefing


def test_briefing_renderer_contains_required_owner_sections_and_disclaimer(tmp_path: Path) -> None:
    paths = make_briefing_paths(tmp_path)
    payload = build_briefing_package(paths)

    markdown = render_daily_stock_selection_briefing(payload)

    assert "## 今日总体结论" in markdown
    assert "## 长期研究候选 Top 10" in markdown
    assert "## 多周期共振候选" in markdown
    assert "## 不要误读" in markdown
    assert "候选股不是买入建议" in markdown
    assert "目标权重不是下单指令" in markdown
    assert "今日必买" not in markdown
    assert "保证盈利" not in markdown
