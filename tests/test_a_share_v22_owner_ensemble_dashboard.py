from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_owner_ensemble_dashboard_shows_blocked_not_live_ready(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    dashboard = v22_json(paths, "v22_owner_ensemble_dashboard_result")
    report = paths.outputs_dir / "equity_v22_ensemble_meta_strategy" / "daily" / "2026-07-01" / "A_SHARE_V22_OWNER_ENSEMBLE_DASHBOARD.md"

    assert result["owner_ensemble_dashboard_generated"] is True
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["not_live_trading_ready_displayed"] is True
    assert dashboard["copy_to_real_account_blocked"] is True
    assert dashboard["real_portfolio_recommendation_output"] is False
    assert "OWNER-READINESS: BLOCKED" in report.read_text(encoding="utf-8")
