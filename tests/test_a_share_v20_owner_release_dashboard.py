from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_owner_release_dashboard_shows_blocked_not_ready(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    dashboard = v20_json(paths, "v20_owner_dashboard_closeout")
    report = paths.outputs_dir / "equity_v20_platform_closeout" / "daily" / "2026-07-01" / "A_SHARE_V20_OWNER_RELEASE_DASHBOARD.md"

    assert result["owner_release_dashboard_generated"] is True
    assert dashboard["dashboard_language"] == "zh-CN"
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["owner_operationally_acceptable"] is False
    assert dashboard["live_trading_ready"] is False
    assert dashboard["source_readiness_score"] == 54
    assert "OWNER-READINESS: BLOCKED" in report.read_text(encoding="utf-8")
