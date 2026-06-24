"""Human-readable report index."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.system.common import relative, timestamp_id, write_json_markdown


TRUST_LEVELS = {"engineering_audit", "research_review", "system_status", "diagnostic", "unknown"}


def build_report_index(
    include_audit: bool = False,
    include_experiments: bool = False,
    include_system: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    index_id, created_at = timestamp_id("REPORT-INDEX")
    selected_dirs = [("reports", paths.outputs_dir / "reports")]
    if include_system:
        selected_dirs.append(("system", paths.outputs_dir / "system"))
    if include_experiments:
        selected_dirs.append(("experiments", paths.outputs_dir / "experiments"))
    if include_audit:
        selected_dirs.append(("audit", paths.outputs_dir / "audit"))
    reports: list[dict[str, Any]] = []
    warnings: list[str] = []
    for category, directory in selected_dirs:
        if not directory.exists():
            warnings.append(f"missing report directory: {relative(directory, paths.project_root)}")
            continue
        for path in sorted(directory.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
            reports.append(_report_record(path, category, paths))
    counts = {category: sum(1 for report in reports if report["category"] == category) for category, _ in selected_dirs}
    payload = {
        "index_id": index_id,
        "created_at": created_at,
        "reports": reports,
        "counts": counts,
        "warnings": warnings,
        "boundary": {
            "index_only": True,
            "write_main_ledger": False,
            "run_daily_called": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "report_index.json"
    report_path = paths.outputs_dir / "system" / "REPORT_INDEX.md"
    write_json_markdown(json_path, payload, report_path, build_report_index_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_report_index_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Report Index", ""]
    sections = [
        ("## 1. System Reports", "system"),
        ("## 2. Research Reports", "reports"),
        ("## 3. Experiment Reports", "experiments"),
        ("## 4. Audit Reports", "audit"),
    ]
    for title, category in sections:
        lines.extend([title, ""])
        items = [report for report in payload["reports"] if report["category"] == category]
        if items:
            lines.extend(f"- {Path(item['path']).name} ({item['trust_level']})" for item in items)
        else:
            lines.append("- none found")
        lines.append("")
    lines.extend(
        [
            "## 5. Safety Boundary",
            "- report index only",
            "- no run-daily",
            "- no orders/trades/portfolio/accounts written",
            "- This system is not live-ready.",
            "- Forward 30d dry-run is not completed.",
            "",
        ]
    )
    return "\n".join(lines)


def _report_record(path: Path, category: str, paths: ProjectPaths) -> dict[str, Any]:
    modified = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat().replace("+00:00", "Z")
    return {
        "title": _title(path),
        "category": category,
        "path": relative(path, paths.project_root),
        "exists": True,
        "modified_at": modified,
        "description": _description(path),
        "trust_level": _trust_level(path, category),
    }


def _title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").title()


def _description(path: Path) -> str:
    name = path.name
    descriptions = {
        "FINAL_HANDOFF_REVIEW_REPORT.md": "Human handoff and acceptance report",
        "SYSTEM_INTEGRITY_AUDIT.md": "System integrity release audit",
        "BOUNDARY_REGRESSION_AUDIT.md": "Boundary regression audit",
        "REPORTING_SYSTEM_AUDIT.md": "Reporting system audit",
        "EXPERIMENT_SYSTEM_AUDIT.md": "Experiment system audit",
        "REPORT_INDEX.md": "Report index",
    }
    return descriptions.get(name, "Markdown report artifact")


def _trust_level(path: Path, category: str) -> str:
    name = path.name
    if category == "audit" or "AUDIT" in name or name == "FINAL_HANDOFF_REVIEW_REPORT.md":
        return "engineering_audit"
    if category == "system":
        return "system_status"
    if category == "experiments":
        return "diagnostic" if "MISTAKE" in name else "research_review"
    if category == "reports":
        return "research_review"
    return "unknown"
