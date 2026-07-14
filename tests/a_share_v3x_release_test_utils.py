from __future__ import annotations

import hashlib
import json
from pathlib import Path

from trading_core.equity_release_chain import audit_release_artifacts, run_release_artifacts, spec_by_key
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE
from trading_core.storage.file_paths import ProjectPaths

AS_OF_DATE = "2026-07-01"
V31_VERSION = "v3.1.0-a-share-post-v3-verification-reproducibility-and-external-audit-readiness-hardening"


def make_v3x_paths(tmp_path: Path) -> ProjectPaths:
    workspace_root = tmp_path / "workspace"
    paths = ProjectPaths(workspace_root)
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.outputs_dir.mkdir(parents=True, exist_ok=True)
    paths.project_root.mkdir(parents=True, exist_ok=True)
    (paths.project_root / "VERSION").write_text(V31_VERSION, encoding="utf-8")
    _write_json(
        paths.data_dir / "equity_v31_post_v3_verification" / "daily" / AS_OF_DATE / "v31_post_v3_verification_result.json",
        {
            "target_version": V31_VERSION,
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            **{key: False for key in BOUNDARY_FALSE},
        },
    )
    _write_json(
        paths.data_dir / "equity_data_quality" / "a_share_v31_post_v3_verification_audit.json",
        {"target_version": V31_VERSION, "overall_passed": True, "blocking_reasons": [], "warnings": []},
    )
    _write_security_evidence(paths)
    return paths


def build_through(paths: ProjectPaths, key: str) -> dict:
    order = ["v32", "v33", "v34", "v35", "v36", "v37", "v38", "v39", "v40"]
    result = {}
    for item in order[: order.index(key) + 1]:
        spec = spec_by_key(item)
        (paths.project_root / "VERSION").write_text(spec["source_version"], encoding="utf-8")
        result = run_release_artifacts(spec, as_of_date=AS_OF_DATE, simulation_only=True, paths=paths)
        assert result["overall_passed"] is True
        audit = audit_release_artifacts(spec=spec, as_of_date=AS_OF_DATE, paths=paths)
        assert audit["overall_passed"] is True
        (paths.project_root / "VERSION").write_text(spec["target_version"], encoding="utf-8")
    return result


def result_json(paths: ProjectPaths, key: str) -> dict:
    spec = spec_by_key(key)
    path = paths.data_dir / spec["package_dir"] / "daily" / AS_OF_DATE / f"{spec['result_name']}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def component_json(paths: ProjectPaths, key: str, name: str) -> dict:
    spec = spec_by_key(key)
    path = paths.data_dir / spec["package_dir"] / "daily" / AS_OF_DATE / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_common_boundary(result: dict) -> None:
    assert result["research_only"] is True
    assert result["simulation_only"] is True
    assert result["virtual_only"] is True
    assert result["not_real_order"] is True
    assert result["not_order_preview"] is True
    assert result["not_buy_sell_signal"] is True
    assert result["not_investment_advice"] is True
    assert result["not_live_trading_ready"] is True
    assert result["owner_readiness_gate_rerun"] is False
    assert result["controlled_gate_reevaluation_run"] is False
    assert result["new_gate_score_generated"] is False
    assert result["new_gate_decision_generated"] is False
    assert result["broker_connected"] is False
    assert result["real_account_data_read"] is False
    assert result["real_orders_placed"] is False
    assert result["real_order_preview_generated"] is False
    assert result["buy_sell_signals_generated"] is False
    assert result["old_run_daily_called"] is False
    assert result["day2_executed"] is False
    assert result["live_trading_ready"] is False


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_security_evidence(paths: ProjectPaths) -> None:
    evidence_root = paths.project_root / "data" / "security_evidence" / "raw"
    scans = {}
    for name, tool in {
        "secret_scan": "gitleaks",
        "config_governance": "atlas-config-policy",
        "dependency_scan": "pip-audit",
        "filesystem_path_scan": "atlas-path-policy",
        "network_boundary_scan": "atlas-network-policy",
    }.items():
        raw_path = evidence_root / f"{name}.json"
        _write_json(raw_path, {"scan": name, "status": "passed", "findings": []})
        relative = raw_path.relative_to(paths.project_root).as_posix()
        scan = {
            "status": "passed",
            "tool": tool,
            "tool_version": "test-fixture-1",
            "evidence_path": relative,
            "evidence_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        }
        if name == "dependency_scan":
            scan.update(
                {
                    "vulnerability_db_status": "available",
                    "vulnerability_db_updated_at": "2026-07-01T00:00:00Z",
                }
            )
        scans[name] = scan
    _write_json(
        paths.project_root / "data" / "security_evidence" / "v36_security_assessment.json",
        {
            "schema_version": 1,
            "generated_at": "2026-07-01T00:00:00Z",
            "scope_commit": "a" * 40,
            "scans": scans,
        },
    )
