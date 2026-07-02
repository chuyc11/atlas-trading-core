from __future__ import annotations

import json
from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_daily_dir, v11_json
from trading_core.equity_v11_owner_ops_platform.audit import audit_a_share_v11_owner_ops_platform
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_artifact_integrity_and_safety_boundary_sweep(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    integrity = v11_json(paths, "v11_artifact_integrity_sweep")
    safety = v11_json(paths, "v11_safety_boundary_sweep")

    assert result["artifact_integrity_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert integrity["protected_path_sweep_passed"] is True
    assert safety["forbidden_wording_hits"] == []


def test_v11_audit_passes_and_catches_boundary_failure(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    assert audit_a_share_v11_owner_ops_platform(paths=paths)["overall_passed"] is True
    path = v11_daily_dir(paths) / "v11_owner_ops_platform_result.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["broker_connected"] = True
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    audit = audit_a_share_v11_owner_ops_platform(paths=paths)

    assert audit["overall_passed"] is False
    assert "forbidden_boundary_true:broker_connected" in audit["blocking_reasons"]
