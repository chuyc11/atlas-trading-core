from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v15_market_regime_lab.audit import audit_a_share_v15_market_regime_lab
from trading_core.equity_v15_market_regime_lab.builder import JSON_NAMES, MARKDOWN_NAMES, run_a_share_v15_market_regime_lab


def test_v15_safety_boundary_and_audit(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    audit = audit_a_share_v15_market_regime_lab(paths=paths)
    alerts = v15_json(paths, "v15_regime_monitoring_alerts")

    assert audit["overall_passed"] is True
    assert audit["artifact_checks"]["json_count"] == len(JSON_NAMES)
    assert audit["artifact_checks"]["markdown_count"] == len(MARKDOWN_NAMES)
    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert all(alert["local_internal_only"] for alert in alerts["alerts"])
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False
    assert result["market_regime_fabricated"] is False
    assert result["volatility_fabricated"] is False
    assert result["breadth_fabricated"] is False
    assert result["liquidity_fabricated"] is False
