"""v0.5.7.1 historical data gap closure workflow."""

from __future__ import annotations

from typing import Any

from trading_core.global_briefing.full_historical_proxy_workflow import run_full_historical_proxy_replay
from trading_core.global_briefing.historical_data_acquisition_audit import audit_historical_data_acquisition
from trading_core.global_briefing.historical_data_acquisition_report import build_historical_data_acquisition_report
from trading_core.global_briefing.historical_data_downloaders import repair_historical_data_gap_packages
from trading_core.global_briefing.historical_data_packages import TRADING_AUTHORIZATION_NOTICE, latest_end_date
from trading_core.global_briefing.historical_data_quality_audit import audit_historical_data_quality
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages
from trading_core.global_briefing.historical_warning_inventory import build_historical_warning_inventory
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


BASELINE = {
    "available_packages": 6,
    "quality_warnings": 20,
    "proxy_replay_warnings": 665,
    "proxy_coverage_ratio": 0.9490196078431372,
    "epu_status": "failed",
    "oecd_status": "failed",
}


def close_historical_data_gaps(
    *,
    start_date: str = "2018-01-01",
    end_date: str = "latest",
    replay_start_date: str = "2024-01-02",
    replay_end_date: str = "2024-12-31",
    min_coverage: float = 0.80,
    continue_on_error: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    resolved_end_date = latest_end_date(end_date)
    workflow_id, created_at = timestamp_id("HIST-DATA-GAP-CLOSURE")
    repaired_manifest = repair_historical_data_gap_packages(start_date=start_date, end_date=resolved_end_date, continue_on_error=True, paths=paths)
    normalization = normalize_historical_data_packages(start_date=start_date, end_date=resolved_end_date, paths=paths)
    quality = audit_historical_data_quality(paths=paths)
    replay = run_full_historical_proxy_replay(start_date=replay_start_date, end_date=replay_end_date, min_coverage=min_coverage, execution_mode="isolated", paths=paths)
    acquisition_report = build_historical_data_acquisition_report(paths=paths)
    acquisition_audit = audit_historical_data_acquisition(paths=paths)
    warning_inventory = build_historical_warning_inventory(paths=paths)
    packages = {item.get("package_id"): item for item in repaired_manifest.get("packages", [])}
    available_packages = sum(1 for item in packages.values() if item.get("status") in {"downloaded", "partial_downloaded", "loaded_from_local"})
    blocking = []
    if quality.get("overall_passed") is not True:
        blocking.append("quality audit failed")
    if replay.get("overall_status") != "research_review_ready":
        blocking.append("proxy replay workflow not ready")
    if acquisition_audit.get("overall_passed") is not True:
        blocking.append("acquisition audit failed")
    if warning_inventory.get("unknown_warning_count", 1) != 0:
        blocking.append("unknown warning count is non-zero")
    if available_packages < 8:
        blocking.append("available packages below 8/9")
    status = "passed" if not blocking else ("passed_with_warnings" if continue_on_error and acquisition_audit.get("overall_passed") else "needs_attention")
    payload: dict[str, Any] = {
        "workflow_id": workflow_id,
        "created_at": created_at,
        "overall_status": status,
        "blocking_reasons": [] if status == "passed_with_warnings" else blocking,
        "warnings": blocking if status == "passed_with_warnings" else [],
        "baseline": BASELINE,
        "current": {
            "available_packages": available_packages,
            "quality_warnings": len(quality.get("warnings", [])),
            "proxy_replay_raw_warnings": replay.get("raw_warning_count", len(replay.get("warnings", []))),
            "proxy_replay_grouped_warnings": replay.get("grouped_warning_count"),
            "proxy_coverage_ratio": replay.get("coverage_ratio"),
            "epu_status": packages.get("HIST-POLICY-UNCERTAINTY-EPU-V1", {}).get("status"),
            "oecd_status": packages.get("HIST-OECD-CLI-MACRO-CYCLE-V1", {}).get("status"),
        },
        "artifacts": {
            "download_manifest": repaired_manifest["json_path"],
            "normalization": normalization["json_path"],
            "quality_audit": quality["json_path"],
            "proxy_replay": replay["json_path"],
            "warning_inventory": warning_inventory["json_path"],
            "acquisition_report": acquisition_report["json_path"],
            "acquisition_audit": acquisition_audit["json_path"],
        },
        "boundary": {
            "historical_data_gap_closure_only": True,
            "trading_authorization": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "strategy_effectiveness_proven": False,
            "live_trading_ready": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_data_gap_closure_workflow.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_DATA_GAP_CLOSURE_WORKFLOW.md"
    write_json_markdown(json_path, payload, md_path, build_gap_closure_workflow_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_gap_closure_workflow_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Data Gap Closure Workflow",
            "",
            "## Scope",
            TRADING_AUTHORIZATION_NOTICE,
            "This workflow closes historical research data gaps and reduces replay warning noise.",
            "",
            "## Overall Status",
            f"- overall_status={payload['overall_status']}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Baseline To Current",
            *[f"- {key}: {payload['baseline'].get(key)} -> {payload['current'].get(key)}" for key in payload["current"]],
            "",
            "## Artifacts",
            *[f"- {key}: {value}" for key, value in payload["artifacts"].items()],
            "",
            "## Boundary",
            "- historical data gap closure only",
            "- no main ledger write",
            "- no run-daily call",
            "- not forward dry-run validation",
            "- not live trading readiness",
            "- not strategy effectiveness proof",
            "",
        ]
    )
