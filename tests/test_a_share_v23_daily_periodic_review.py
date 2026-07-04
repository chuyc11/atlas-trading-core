from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal


def test_v23_daily_review_is_chinese_blocked_and_not_signal(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    daily = v23_json(paths, "v23_daily_research_review_result")

    assert result["daily_research_review_generated"] is True
    assert daily["language"] == "zh-CN"
    assert daily["owner_readiness_blocked_displayed"] is True
    assert daily["live_trading_ready"] is False
    assert daily["owner_reports_generate_buy_sell_signal"] is False
    assert daily["owner_reports_generate_real_allocation"] is False


def test_v23_periodic_review_warns_when_history_is_unavailable(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    periodic = v23_json(paths, "v23_periodic_research_review_result")

    assert periodic["weekly_review_framework_generated"] is True
    assert periodic["monthly_review_framework_generated"] is True
    assert periodic["rolling_5_run_summary"] == "not_available"
    assert periodic["rolling_20_run_summary"] == "not_available"
    assert periodic["missing_history_warning"] is True
    assert periodic["history_fabricated"] is False
