"""v0.5.7.1 historical data gap closure report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_gap_closure_workflow import BASELINE
from trading_core.global_briefing.historical_data_packages import TRADING_AUTHORIZATION_NOTICE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


def build_historical_data_gap_closure_report(*, workflow_path: str | None = None, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    report_id, created_at = timestamp_id("HIST-DATA-GAP-CLOSURE-REPORT")
    workflow_file = _resolve(workflow_path, paths.data_dir / "system" / "historical_data_gap_closure_workflow.json", paths)
    workflow = _read(workflow_file)
    download = _read(paths.data_dir / "system" / "historical_data_download_manifest.json")
    quality = _read(paths.data_dir / "system" / "historical_data_quality_audit.json")
    inventory = _read(paths.data_dir / "system" / "historical_warning_inventory.json")
    replay_file = Path(workflow.get("artifacts", {}).get("proxy_replay", paths.data_dir / "replays" / "global_briefing" / "missing.json"))
    replay = _read(replay_file)
    packages = {item.get("package_id"): item for item in download.get("packages", [])}
    payload: dict[str, Any] = {
        "report_id": report_id,
        "created_at": created_at,
        "workflow": str(workflow_file),
        "overall_status": workflow.get("overall_status", "missing"),
        "baseline": BASELINE,
        "epu": _status_change(packages, "HIST-POLICY-UNCERTAINTY-EPU-V1", BASELINE["epu_status"]),
        "oecd": _status_change(packages, "HIST-OECD-CLI-MACRO-CYCLE-V1", BASELINE["oecd_status"]),
        "available_packages": {"previous": BASELINE["available_packages"], "current": workflow.get("current", {}).get("available_packages")},
        "quality_warnings": {"previous": BASELINE["quality_warnings"], "current": len(quality.get("warnings", []))},
        "proxy_replay_warnings": {"previous": BASELINE["proxy_replay_warnings"], "current_raw": replay.get("raw_warning_count"), "current_grouped": replay.get("grouped_warning_count")},
        "proxy_coverage_ratio": {"previous": BASELINE["proxy_coverage_ratio"], "current": replay.get("coverage_ratio")},
        "grouped_warning_output_enabled": bool(replay.get("grouped_warnings")),
        "unknown_warning_count": inventory.get("unknown_warning_count"),
        "unresolved_data_gaps": _unresolved(packages),
        "accepted_limitations": [
            "Authorized global-briefing historical signal package remains separately configured and is not required for proxy gap closure.",
            "EPU may be policy-uncertainty proxy when official EPU sources are unavailable.",
            "OECD CLI may be authorized macro-cycle proxy and is not official OECD CLI when marked as such.",
        ],
        "boundary": {
            "report_only": True,
            "trading_authorization": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "strategy_effectiveness_proven": False,
            "live_trading_ready": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_gap_closure_report.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_DATA_GAP_CLOSURE_REPORT.md"
    write_json_markdown(json_path, payload, md_path, build_gap_closure_report_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _status_change(packages: dict[str, Any], package_id: str, previous: str) -> dict[str, Any]:
    item = packages.get(package_id, {})
    return {"previous_status": previous, "current_status": item.get("status"), "path": item.get("path"), "source": item.get("source"), "warnings": item.get("warnings", [])}


def _unresolved(packages: dict[str, Any]) -> list[str]:
    gaps = []
    for package_id, item in packages.items():
        if item.get("status") in {"failed", "failed_soft"}:
            gaps.append(f"{package_id}: {item.get('status')}")
    return gaps


def _resolve(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _read(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def build_gap_closure_report_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Data Gap Closure Report",
            "",
            "## Overall Status",
            f"- overall_status={payload['overall_status']}",
            "",
            "## EPU Repair",
            f"- {payload['epu']['previous_status']} -> {payload['epu']['current_status']}",
            "",
            "## OECD / Macro Cycle Repair",
            f"- {payload['oecd']['previous_status']} -> {payload['oecd']['current_status']}",
            "",
            "## Warning Reduction",
            f"- quality warnings: {payload['quality_warnings']['previous']} -> {payload['quality_warnings']['current']}",
            f"- proxy replay warnings: {payload['proxy_replay_warnings']['previous']} -> raw {payload['proxy_replay_warnings']['current_raw']} / grouped {payload['proxy_replay_warnings']['current_grouped']}",
            "",
            "## Remaining Gaps",
            *([f"- {item}" for item in payload["unresolved_data_gaps"]] if payload["unresolved_data_gaps"] else ["- none"]),
            "",
            "## Boundary",
            f"- {TRADING_AUTHORIZATION_NOTICE}",
            "- not forward dry-run validation",
            "- not live trading readiness",
            "- not strategy effectiveness proof",
            "- main ledger not written",
            "- run-daily not called",
            "",
        ]
    )
