from __future__ import annotations

import json
from pathlib import Path

from a_share_feature_test_utils import AS_OF_DATE
from a_share_virtual_portfolio_tracking_test_utils import audit_tracking_package, build_tracking_package, make_tracking_paths
from trading_core.equity_briefings.briefing_audit import audit_a_share_daily_stock_selection_briefing
from trading_core.equity_workflows.workflow_config import WORKFLOW_FILES
from trading_core.equity_workflows.workflow_runner import run_a_share_daily_research_workflow
from trading_core.storage.file_paths import ProjectPaths


def make_workflow_paths(tmp_path: Path) -> ProjectPaths:
    paths = make_tracking_paths(tmp_path)
    _write_version_files(paths)
    _write_safety_doc(paths)
    _write_tradable_artifacts(paths)
    audit_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=AS_OF_DATE)
    build_tracking_package(paths)
    audit_tracking_package(paths)
    _force_upstream_audits_pass(paths)
    return paths


def build_workflow_package(paths: ProjectPaths, mode: str = "validate_existing_artifacts") -> dict:
    return run_a_share_daily_research_workflow(paths=paths, as_of_date=AS_OF_DATE, mode=mode)


def workflow_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_workflows" / "daily" / AS_OF_DATE


def workflow_output_dir(paths: ProjectPaths) -> Path:
    return paths.outputs_dir / "equity_workflows" / "daily" / AS_OF_DATE


def workflow_json(paths: ProjectPaths, key: str):
    return json.loads((workflow_data_dir(paths) / WORKFLOW_FILES[key]).read_text(encoding="utf-8"))


def write_root_version(paths: ProjectPaths, version: str) -> None:
    root_init = paths.project_root / "trading_core" / "__init__.py"
    root_init.parent.mkdir(parents=True, exist_ok=True)
    root_init.write_text(f'"""test root shim."""\n__version__ = "{version}"\n', encoding="utf-8")


def _write_version_files(paths: ProjectPaths) -> None:
    (paths.project_root / "VERSION").write_text("v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger\n", encoding="utf-8")
    src_init = paths.project_root / "src" / "trading_core" / "__init__.py"
    src_init.parent.mkdir(parents=True, exist_ok=True)
    src_init.write_text('"""Trading Core package."""\n\n__version__ = "0.7.8"\n', encoding="utf-8")
    write_root_version(paths, "0.7.8")


def _write_safety_doc(paths: ProjectPaths) -> None:
    path = paths.project_root / "docs" / "SAFETY_BOUNDARY.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Safety Boundary\n\nResearch-only workflow boundary.\n", encoding="utf-8")


def _write_tradable_artifacts(paths: ProjectPaths) -> None:
    data_dir = paths.data_dir / "equity_selection" / "daily" / AS_OF_DATE
    strict_path = data_dir / "strict_tradable_universe.json"
    rows = json.loads(strict_path.read_text(encoding="utf-8"))
    (data_dir / "tradable_universe.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    manifest = {
        "manifest_id": "A-SHARE-TRADABLE-UNIVERSE-MANIFEST",
        "target_version": "v0.7.2-a-share-tradable-universe-filter",
        "as_of_date": AS_OF_DATE,
        "overall_passed": True,
        "source_trace_complete": True,
        "boundary": {"run_daily_called": False, "broker_connected": False, "real_orders_placed": False},
    }
    (data_dir / "tradable_universe_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_tradable_universe_audit.json"
    audit_path.write_text(
        json.dumps(
            {
                "audit_id": "A-SHARE-TRADABLE-UNIVERSE-AUDIT",
                "overall_passed": True,
                "blocking_reasons": [],
                "warnings": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _force_upstream_audits_pass(paths: ProjectPaths) -> None:
    audit_ids = {
        "a_share_tradable_universe_audit.json": "A-SHARE-TRADABLE-UNIVERSE-AUDIT",
        "a_share_multi_horizon_feature_audit.json": "A-SHARE-MULTI-HORIZON-FEATURE-AUDIT",
        "a_share_scoring_audit.json": "A-SHARE-SCORING-AUDIT",
        "a_share_candidate_generation_audit.json": "A-SHARE-CANDIDATE-GENERATION-AUDIT",
        "a_share_virtual_portfolio_construction_audit.json": "A-SHARE-VIRTUAL-PORTFOLIO-CONSTRUCTION-AUDIT",
        "a_share_daily_stock_selection_briefing_audit.json": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING-AUDIT",
        "a_share_virtual_portfolio_tracking_audit.json": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-AUDIT",
    }
    audit_dir = paths.data_dir / "equity_data_quality"
    for filename, audit_id in audit_ids.items():
        path = audit_dir / filename
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"audit_id": audit_id}
        payload["audit_id"] = payload.get("audit_id") or audit_id
        payload["overall_passed"] = True
        payload["blocking_reasons"] = []
        payload.setdefault("warnings", [])
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
