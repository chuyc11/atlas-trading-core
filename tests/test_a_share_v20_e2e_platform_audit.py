from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_e2e_platform_audit_matrix(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    audit = v20_json(paths, "v20_e2e_platform_audit_result")

    assert result["e2e_platform_audit_generated"] is True
    assert audit["e2e_platform_audit_generated"] is True
    assert audit["blocker_register"] == []
    assert len(audit["pass_warning_fail_matrix"]) >= 19
    assert "model_risk" in {row["layer"] for row in audit["pass_warning_fail_matrix"]}
