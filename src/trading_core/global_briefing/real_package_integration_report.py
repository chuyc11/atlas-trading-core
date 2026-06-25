"""Integration report for local real global-briefing package replay."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


LIMITATIONS = [
    "This does not validate forward dry-run.",
    "This does not prove strategy effectiveness.",
    "This is not live trading readiness.",
]


def build_global_briefing_real_package_report(
    *,
    manifest_path: str | None = None,
    workflow_path: str | None = None,
    coverage_path: str | None = None,
    evaluation_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    report_id, created_at = timestamp_id("GB-REAL-PACKAGE-INTEGRATION")
    warnings: list[str] = []
    manifest_file = _resolve_or_default(manifest_path, paths.data_dir / "system" / "global_briefing_package_manifest.json", paths)
    workflow_file = _resolve_or_latest(workflow_path, paths.data_dir / "replays" / "global_briefing", "real_package_replay_workflow-*.json", paths)
    coverage_file = _resolve_or_default(coverage_path, paths.data_dir / "system" / "global_briefing_package_coverage_audit.json", paths)
    evaluation_file = _resolve_or_latest(evaluation_path, paths.data_dir / "replays" / "global_briefing", "global_briefing_replay_evaluation-*.json", paths)

    manifest = _read_optional(manifest_file, "manifest", warnings)
    workflow = _read_optional(workflow_file, "workflow", warnings)
    coverage = _read_optional(coverage_file, "coverage", warnings)
    evaluation = _read_optional(evaluation_file, "evaluation", warnings)
    normalization = _read_optional(Path(workflow.get("normalization")), "normalization", warnings) if workflow.get("normalization") else {}
    package_count = len(manifest.get("packages", [])) if manifest else 0
    selected_package = normalization.get("package_id") or workflow.get("package_id") or None
    coverage_ratio = coverage.get("coverage", {}).get("coverage_ratio") if coverage else None
    evaluation_status = evaluation.get("overall_status") if evaluation else None
    workflow_status = workflow.get("overall_status") if workflow else None
    blocking = []
    if workflow and workflow_status != "research_review_ready":
        blocking.extend(workflow.get("blocking_reasons", []))
    overall_status = "research_review_ready" if workflow_status == "research_review_ready" and not blocking else "needs_attention"
    payload: dict[str, Any] = {
        "report_id": report_id,
        "created_at": created_at,
        "overall_status": overall_status,
        "package_count": package_count,
        "selected_package": selected_package,
        "coverage_ratio": coverage_ratio,
        "replay_status": "completed" if workflow.get("replay") and workflow_status == "research_review_ready" else "not_completed",
        "evaluation_status": evaluation_status,
        "blocking_reasons": blocking,
        "warnings": warnings + workflow.get("warnings", []),
        "known_limitations": LIMITATIONS,
        "next_data_requirements": [
            "Provide broader historical local global-briefing packages before research review beyond fixture smoke.",
            "Maintain generated_at timestamps for point-in-time replay.",
        ],
        "inputs": {
            "manifest": str(manifest_file) if manifest_file else None,
            "workflow": str(workflow_file) if workflow_file else None,
            "coverage": str(coverage_file) if coverage_file else None,
            "evaluation": str(evaluation_file) if evaluation_file else None,
        },
        "boundary": {
            "report_only": True,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_validated": False,
            "strategy_effectiveness_proven": False,
            "live_trading_ready": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_real_package_integration_report.json"
    report_path = paths.outputs_dir / "replays" / "global_briefing" / "GLOBAL_BRIEFING_REAL_PACKAGE_INTEGRATION_REPORT.md"
    write_json_markdown(json_path, payload, report_path, build_integration_report_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _resolve_or_default(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _resolve_or_latest(path_text: str | None, directory: Path, pattern: str, paths: ProjectPaths) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else paths.project_root / path
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(pattern), key=lambda item: (item.stat().st_mtime_ns, item.name))
    return candidates[-1] if candidates else None


def _read_optional(path: Path | None, label: str, warnings: list[str]) -> dict[str, Any]:
    if path is None or not path.exists():
        warnings.append(f"missing {label}")
        return {}
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def build_integration_report_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Real Package Integration Report",
            "",
            "## Overall Status",
            f"- overall_status={payload['overall_status']}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Package Inventory",
            f"- package_count={payload['package_count']}",
            "",
            "## Selected Package",
            f"- {payload['selected_package']}",
            "",
            "## Coverage",
            f"- coverage_ratio={payload['coverage_ratio']}",
            "",
            "## Replay",
            f"- replay_status={payload['replay_status']}",
            "",
            "## Evaluation",
            f"- evaluation_status={payload['evaluation_status']}",
            "",
            "## Known Limitations",
            *[f"- {item}" for item in payload["known_limitations"]],
            "",
            "## Boundary",
            "- report only",
            "- main ledger not written",
            "- run-daily not called",
            "",
        ]
    )
