from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v14_portfolio_risk_lab.audit import audit_a_share_v14_portfolio_risk_lab
from trading_core.equity_v14_portfolio_risk_lab.builder import JSON_NAMES, MARKDOWN_NAMES, run_a_share_v14_portfolio_risk_lab


def test_v14_safety_boundary_and_audit(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    audit = audit_a_share_v14_portfolio_risk_lab(paths=paths)
    safety = v14_json(paths, "v14_safety_boundary_sweep")
    alerts = v14_json(paths, "v14_portfolio_risk_monitoring_alerts")

    assert audit["overall_passed"] is True
    assert audit["artifact_checks"]["json_count"] == len(JSON_NAMES)
    assert audit["artifact_checks"]["markdown_count"] == len(MARKDOWN_NAMES)
    assert safety["safety_boundary_sweep_passed"] is True
    assert alerts["portfolio_risk_monitoring_alerts_generated"] is True
    assert all(alert["local_internal_only"] for alert in alerts["alerts"])
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False
    assert result["real_portfolio_advice_generated"] is False
    assert result["real_allocation_instruction_generated"] is False
    assert result["real_rebalance_instruction_generated"] is False
    assert result["real_trade_instruction_generated"] is False
    assert result["strategy_real_trading_active_state_present"] is False
