from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_owner_data_dashboard_shows_blocked_and_not_live_ready(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    dashboard = v21_json(paths, "v21_owner_data_reliability_dashboard_result")
    report = paths.outputs_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / "2026-07-01" / "A_SHARE_V21_OWNER_DATA_RELIABILITY_DASHBOARD.md"

    assert result["owner_data_reliability_dashboard_generated"] is True
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["owner_operationally_acceptable"] is False
    assert dashboard["live_trading_ready"] is False
    assert dashboard["not_investment_advice_displayed"] is True
    assert "OWNER-READINESS: BLOCKED" in report.read_text(encoding="utf-8")
