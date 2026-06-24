"""Human-oriented artifact browser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.system.common import relative, timestamp_id, write_json_markdown


def build_artifact_browser(
    include_missing: bool = False,
    group_by: str = "category",
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    browser_id, created_at = timestamp_id("ARTBROWSER")
    warnings: list[str] = []
    artifacts = _load_inventory(paths, warnings)
    reports = _load_report_index(paths, warnings)
    if not artifacts:
        artifacts = _scan(paths)
    if not include_missing:
        artifacts = [item for item in artifacts if item.get("exists", True)]
    start_here = [
        _entry("Final handoff review", "outputs/system/FINAL_HANDOFF_REVIEW_REPORT.md", "engineering_audit"),
        _entry("System dashboard", "outputs/system/SYSTEM_DASHBOARD.md", "system_status"),
        _entry("Project status report", "outputs/system/PROJECT_STATUS_REPORT.md", "system_status"),
        _entry("System integrity audit", "outputs/audit/SYSTEM_INTEGRITY_AUDIT.md", "engineering_audit"),
        _entry("Report index", "outputs/system/REPORT_INDEX.md", "system_status"),
    ]
    payload = {
        "browser_id": browser_id,
        "created_at": created_at,
        "group_by": group_by,
        "start_here": start_here,
        "engineering_audit_artifacts": [item for item in reports if item.get("trust_level") == "engineering_audit"],
        "research_review_artifacts": [item for item in reports if item.get("trust_level") == "research_review"],
        "machine_readable_data": artifacts,
        "not_trading_authorization": [
            "shadow signals",
            "watch recommendation",
            "promising_shadow",
            "promotion simulation",
        ],
        "warnings": warnings,
        "boundary": {
            "browser_only": True,
            "write_main_ledger": False,
            "run_daily_called": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "artifact_browser.json"
    report_path = paths.outputs_dir / "system" / "ARTIFACT_BROWSER.md"
    write_json_markdown(json_path, payload, report_path, build_artifact_browser_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_artifact_browser_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact Browser",
        "",
        "## 1. Start Here",
    ]
    lines.extend(f"- {item['title']}: {item['path']}" for item in payload["start_here"])
    lines.extend(["", "## 2. Engineering Audit Artifacts"])
    lines.extend([f"- {item.get('title', item.get('artifact', 'artifact'))}: {item.get('path')}" for item in payload["engineering_audit_artifacts"]] or ["- none found"])
    lines.extend(["", "## 3. Research Review Artifacts"])
    lines.extend([f"- {item.get('title', item.get('artifact', 'artifact'))}: {item.get('path')}" for item in payload["research_review_artifacts"]] or ["- none found"])
    lines.extend(["", "## 4. Machine-readable Data"])
    lines.extend([f"- {item.get('artifact', Path(item.get('path', '')).name)}: {item.get('path')}" for item in payload["machine_readable_data"][:40]] or ["- none found"])
    lines.extend(["", "## 5. Not Trading Authorization"])
    lines.extend(f"- {item}" for item in payload["not_trading_authorization"])
    lines.extend(
        [
            "",
            "## Safety Boundary",
            "- artifact browser only",
            "- no run-daily",
            "- no orders/trades/portfolio/accounts written",
            "- This system is not live-ready.",
            "- Forward 30d dry-run is not completed.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_inventory(paths: ProjectPaths, warnings: list[str]) -> list[dict[str, Any]]:
    path = paths.data_dir / "system" / "artifact_inventory.json"
    payload = _read_json(path)
    if not payload:
        warnings.append("artifact_inventory.json missing; scanned directories directly")
        return []
    return payload.get("artifacts", []) if isinstance(payload.get("artifacts"), list) else []


def _load_report_index(paths: ProjectPaths, warnings: list[str]) -> list[dict[str, Any]]:
    path = paths.data_dir / "system" / "report_index.json"
    payload = _read_json(path)
    if not payload:
        warnings.append("report_index.json missing; report groups may be sparse")
        return []
    return payload.get("reports", []) if isinstance(payload.get("reports"), list) else []


def _scan(paths: ProjectPaths) -> list[dict[str, Any]]:
    rows = []
    for root in [paths.data_dir, paths.outputs_dir]:
        if root.exists():
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    rows.append({"artifact": path.name, "path": relative(path, paths.project_root), "exists": True})
    return rows


def _entry(title: str, path: str, trust_level: str) -> dict[str, str]:
    return {"title": title, "path": path, "trust_level": trust_level}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
