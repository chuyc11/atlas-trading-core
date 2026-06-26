"""Shared helpers for v0.6.3.1 day1 continuation artifacts."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from pathlib import Path
from typing import Any

from trading_core.forward_dry_run.day1_common import (
    RELEASE_CANDIDATE as BASELINE_TAG,
    audit_report,
    day_json,
    day_report,
    non_claim_lines,
    paths_or_default,
    read_json_file,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.6.3.1-forward-dry-run-day1-continuation-artifacts"
NEXT_VERSION = "v0.6.4-forward-dry-run-day2-continuation"
DAY1_CORE_ARTIFACTS: dict[str, str] = {
    "day1_pre_execution_gate": "data/forward_dry_run/day_001/day1_pre_execution_gate.json",
    "day1_input_snapshot": "data/forward_dry_run/day_001/day1_input_snapshot.json",
    "day1_strategy_signals": "data/forward_dry_run/day_001/day1_strategy_signals.json",
    "day1_virtual_order_preview": "data/forward_dry_run/day_001/day1_virtual_order_preview.json",
    "day1_virtual_execution_result": "data/forward_dry_run/day_001/day1_virtual_execution_result.json",
    "day1_forward_dry_run_ledger_snapshot": "data/forward_dry_run/day_001/day1_forward_dry_run_ledger_snapshot.json",
    "day1_risk_and_boundary_report": "data/forward_dry_run/day_001/day1_risk_and_boundary_report.json",
    "day1_operator_report": "data/forward_dry_run/day_001/day1_operator_report.json",
    "day1_post_execution_audit": "data/forward_dry_run/day_001/day1_post_execution_audit.json",
    "forward_dry_run_status": "data/system/forward_dry_run_status.json",
    "day1_blocker_reclassification_v063": "data/system/day1_blocker_reclassification_v063.json",
}
OPTIONAL_PREFLIGHT_ARTIFACTS: dict[str, str] = {
    "v064_blocking_preflight": "data/system/forward_dry_run_day2_continuation_preflight.json",
    "v064_blocking_preflight_report": "outputs/audit/FORWARD_DRY_RUN_DAY2_CONTINUATION_PREFLIGHT.md",
}
CONTINUATION_ARTIFACTS: dict[str, str] = {
    "day1_artifact_manifest": "data/forward_dry_run/day_001/day1_artifact_manifest.json",
    "day1_reproducibility_manifest": "data/forward_dry_run/day_001/day1_reproducibility_manifest.json",
    "day2_readiness_packet": "data/forward_dry_run/day_001/day2_readiness_packet.json",
    "day2_continuation_gate_preview": "data/forward_dry_run/day_001/day2_continuation_gate_preview.json",
}
FORBIDDEN_POSITIVE_PHRASES = [
    "day2 executed",
    "day3 executed",
    "run-daily executed",
    "real orders placed",
    "broker connected",
    "strategy effectiveness proven",
    "forward dry-run fully validated",
    "live trading ready",
    "production trading ready",
    "ML approved for trading",
    "LLM approved for trading",
    "RL approved for trading",
    "promotion approved",
]


def project_path(paths: ProjectPaths, relative: str) -> Path:
    return paths.project_root / relative


def sha256_path(path: Path, *, ignore_generated_at: bool = False) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    if ignore_generated_at and path.suffix.lower() == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            payload = _strip_generated_at(payload)
            return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _strip_generated_at(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_generated_at(item) for key, item in value.items() if key != "generated_at"}
    if isinstance(value, list):
        return [_strip_generated_at(item) for item in value]
    return value


def artifact_record(paths: ProjectPaths, name: str, relative: str, *, required: bool, source_role: str, blocking_if_missing: bool) -> dict[str, Any]:
    path = project_path(paths, relative)
    payload = read_json_file(path) if path.exists() and path.suffix.lower() == ".json" else {}
    return {
        "name": name,
        "path": relative,
        "exists": path.exists(),
        "required": required,
        "sha256": sha256_path(path),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "generated_at": payload.get("generated_at") if isinstance(payload, dict) else None,
        "source_role": source_role,
        "blocking_if_missing": blocking_if_missing,
    }


def artifact_records(paths: ProjectPaths, *, include_optional_preflight: bool = True) -> list[dict[str, Any]]:
    records = [
        artifact_record(paths, name, relative, required=True, source_role="day1_core_evidence", blocking_if_missing=True)
        for name, relative in DAY1_CORE_ARTIFACTS.items()
    ]
    if include_optional_preflight:
        records.extend(
            artifact_record(paths, name, relative, required=False, source_role="v064_blocking_preflight_evidence", blocking_if_missing=False)
            for name, relative in OPTIONAL_PREFLIGHT_ARTIFACTS.items()
        )
    return records


def artifact_hashes(records: list[dict[str, Any]]) -> dict[str, str]:
    return {record["name"]: record["sha256"] for record in records if record.get("sha256")}


def continuation_missing(paths: ProjectPaths) -> list[str]:
    return [relative for relative in CONTINUATION_ARTIFACTS.values() if not project_path(paths, relative).exists()]


def day2_executed(paths: ProjectPaths) -> bool:
    return (paths.data_dir / "forward_dry_run" / "day_002" / "day2_virtual_execution_result.json").exists()


def day3_executed(paths: ProjectPaths) -> bool:
    return (paths.data_dir / "forward_dry_run" / "day_003" / "day3_virtual_execution_result.json").exists()


def day1_core_status(paths: ProjectPaths) -> dict[str, Any]:
    missing = [relative for relative in DAY1_CORE_ARTIFACTS.values() if not project_path(paths, relative).exists()]
    day1_audit = read_json_file(day_json(paths, "day1_post_execution_audit.json"))
    status = read_json_file(system_json(paths, "forward_dry_run_status.json"))
    reclass = read_json_file(system_json(paths, "day1_blocker_reclassification_v063.json"))
    execution = read_json_file(day_json(paths, "day1_virtual_execution_result.json"))
    risk = read_json_file(day_json(paths, "day1_risk_and_boundary_report.json"))
    ledger_writes = execution.get("ledger_writes", {})
    boundary_summary = risk.get("boundary_summary", {})
    checks = {
        "required_day1_core_artifacts_exist": not missing,
        "day1_post_execution_audit_passed": day1_audit.get("overall_passed") is True and day1_audit.get("blocking_reasons") == [],
        "forward_dry_run_started": status.get("forward_dry_run_started") is True,
        "forward_dry_run_days_completed_is_1": status.get("forward_dry_run_days_completed") == 1,
        "next_day_index_is_2": status.get("next_day_index") == 2,
        "remaining_day1_blocker_count_0": reclass.get("remaining_day1_blocker_count") == 0,
        "day2_blocker_count_0": reclass.get("day2_blocker_count") == 0,
        "main_ledger_written_false": all(ledger_writes.get(key) is False for key in ["main_orders_written", "main_trades_written", "main_portfolio_written", "main_accounts_written"]),
        "real_execution_false": execution.get("real_execution") is False,
        "broker_execution_false": execution.get("broker_execution") is False,
        "broker_connected_false": boundary_summary.get("broker_connected") is False,
        "real_orders_placed_false": boundary_summary.get("real_orders_placed") is False,
        "strategy_effectiveness_proven_false": boundary_summary.get("strategy_effectiveness_proven") is False,
        "live_trading_ready_false": boundary_summary.get("live_trading_ready") is False,
    }
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    blocking.extend(f"missing_day1_core_artifact: {relative}" for relative in missing)
    return {
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "missing_day1_core_artifacts": missing,
        "checks": checks,
        "day1_audit": day1_audit,
        "status": status,
        "reclassification": reclass,
        "execution": execution,
        "risk": risk,
    }


def v064_preflight(paths: ProjectPaths) -> dict[str, Any]:
    return read_json_file(system_json(paths, "forward_dry_run_day2_continuation_preflight.json"))


def git_value(paths: ProjectPaths, args: list[str]) -> str:
    if not (paths.project_root / ".git").exists():
        return ""
    try:
        return subprocess.run(["git", *args], cwd=paths.project_root, check=False, capture_output=True, text=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def release_commit_info(paths: ProjectPaths) -> dict[str, str]:
    return {
        "baseline_tag": BASELINE_TAG,
        "tag_commit": git_value(paths, ["rev-parse", BASELINE_TAG]),
        "implementation_commit": git_value(paths, ["rev-parse", f"{BASELINE_TAG}~1"]),
        "release_commit": git_value(paths, ["rev-parse", BASELINE_TAG]),
        "current_head": git_value(paths, ["rev-parse", "HEAD"]),
    }


def python_runtime() -> dict[str, str]:
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }


def standard_boundary(scope_key: str) -> dict[str, Any]:
    return {
        scope_key: True,
        "day2_executed": False,
        "day3_executed": False,
        "run_daily_called": False,
        "main_ledger_written": False,
        "broker_connected": False,
        "real_orders_placed": False,
        "ml_shadow_used_as_authorization": False,
        "llm_trading_decision": False,
        "rl_used": False,
        "promotion_triggered": False,
        "strategy_effectiveness_proven": False,
        "forward_dry_run_fully_validated": False,
        "live_trading_ready": False,
    }


def markdown_boundary() -> list[str]:
    return [
        "- This stage only materializes day1 continuation artifacts.",
        "- Day 2 was not executed.",
        "- Day 3 was not executed.",
        "- run-daily was not called.",
        *non_claim_lines(),
    ]


def write_failure_artifact(paths: ProjectPaths, *, json_name: str, report_name: str, artifact_id_key: str, artifact_id: str, blocking: list[str], scope_key: str) -> dict[str, Any]:
    payload = {
        artifact_id_key: artifact_id,
        "baseline_tag": BASELINE_TAG,
        "overall_passed": False,
        "blocking_reasons": blocking,
        "boundary": standard_boundary(scope_key),
    }
    lines = [
        f"# {artifact_id.replace('-', ' ').title()}",
        "",
        "- overall_passed: false",
        f"- blocking_reasons: {blocking}",
        "",
        "## Boundary",
        *markdown_boundary(),
        "",
    ]
    return write_artifact(system_json(paths, json_name), payload, audit_report(paths, report_name), "\n".join(lines))


def forbidden_wording_issues(paths: ProjectPaths) -> list[str]:
    issues: list[str] = []
    candidates = list((paths.outputs_dir / "forward_dry_run" / "day_001").glob("*.md"))
    candidates.extend((paths.outputs_dir / "audit").glob("*DAY1_CONTINUATION*.md"))
    for path in candidates:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lower = line.lower()
            for phrase in FORBIDDEN_POSITIVE_PHRASES:
                phrase_lower = phrase.lower()
                if phrase_lower in lower and not _is_negated(lower, phrase_lower):
                    issues.append(f"forbidden positive wording: {path.name}:{number}:{phrase}")
    return issues


def _is_negated(line: str, phrase: str) -> bool:
    idx = line.find(phrase)
    prefix = line[max(0, idx - 32) : idx]
    return any(marker in prefix for marker in ["not ", "no ", "false", "without ", "did not ", "was not ", "is not "]) or any(marker in line for marker in ["=false", ": false"])

