from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v19_ml_validation_model_risk.audit import audit_a_share_v19_ml_validation_model_risk
from trading_core.equity_v19_ml_validation_model_risk.builder import JSON_NAMES, MARKDOWN_NAMES, run_a_share_v19_ml_validation_model_risk


def test_v19_safety_boundary_artifacts_and_audit_pass(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    audit = audit_a_share_v19_ml_validation_model_risk(paths=paths)

    assert audit["overall_passed"] is True
    assert audit["artifact_checks"]["json_count"] == len(JSON_NAMES)
    assert audit["artifact_checks"]["markdown_count"] == len(MARKDOWN_NAMES)
    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False
    assert result["broker_connected"] is False
    assert result["real_account_data_read"] is False
    assert result["real_orders_placed"] is False
    assert result["real_order_preview_generated"] is False
    assert result["buy_sell_signals_generated"] is False
    assert result["new_gate_score_generated"] is False
    assert result["new_gate_decision_generated"] is False
    assert result["model_status_real_trading_active_present"] is False
