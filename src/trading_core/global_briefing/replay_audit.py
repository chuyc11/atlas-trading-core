"""Full global-briefing historical replay harness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.4-global-briefing-historical-replay-harness-audited"
FORBIDDEN_PHRASES = [
    "live trading ready",
    "strategy effectiveness proven",
    "forward dry-run validated",
    "promotion approved",
    "broker connected",
    "real orders supported",
]


def audit_global_briefing_replay(
    *,
    validation_path: str | None = None,
    bundle_path: str | None = None,
    replay_path: str | None = None,
    evaluation_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("GB-REPLAY-AUDIT")

    contract_json = paths.data_dir / "system" / "global_briefing_signal_contract.json"
    contract_md = paths.outputs_dir / "system" / "GLOBAL_BRIEFING_SIGNAL_CONTRACT.md"
    validation_json = _resolve_or_default(validation_path, paths.data_dir / "system" / "global_briefing_signal_validation.json", paths)
    bundle_json = _resolve_or_latest(bundle_path, paths.data_dir / "replays" / "global_briefing", "replay_bundle-*.json", paths)
    replay_json = _resolve_or_latest(replay_path, paths.data_dir / "replays" / "global_briefing", "global_briefing_replay-*.json", paths)
    evaluation_json = _resolve_or_latest(
        evaluation_path,
        paths.data_dir / "replays" / "global_briefing",
        "global_briefing_replay_evaluation-*.json",
        paths,
    )

    sections = {
        "contract": _audit_contract(contract_json, contract_md),
        "signal_validation": _audit_validation(validation_json),
        "replay_bundle": _audit_bundle(bundle_json),
        "historical_replay": _audit_replay(replay_json),
        "evaluation": _audit_evaluation(evaluation_json),
        "protected_path_snapshot": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _audit_wording([contract_md, _md_pair(validation_json), _md_pair(bundle_json), _md_pair(replay_json), _md_pair(evaluation_json)]),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_path_snapshot"] = {
        "passed": not protected_changes,
        "issues": ["protected path changed", *protected_changes] if protected_changes else [],
        "modified_paths": [relative(Path(item), paths.project_root) for item in protected_changes],
        "checked_paths": list(PROTECTED_PATHS),
    }
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "inputs": {
            "contract": str(contract_json),
            "validation": str(validation_json) if validation_json else None,
            "bundle": str(bundle_json) if bundle_json else None,
            "replay": str(replay_json) if replay_json else None,
            "evaluation": str(evaluation_json) if evaluation_json else None,
        },
        "sections": sections,
        "boundary": {
            "historical_replay_harness_only": True,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "broker_connected": False,
            "main_ledger_written": False,
            "run_daily_called": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "system" / "global_briefing_replay_audit.json"
    report_path = paths.outputs_dir / "audit" / "GLOBAL_BRIEFING_REPLAY_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _resolve_or_default(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    if path.is_absolute():
        return path
    return paths.project_root / path


def _resolve_or_latest(path_text: str | None, directory: Path, pattern: str, paths: ProjectPaths) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else paths.project_root / path
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(pattern), key=lambda item: (item.stat().st_mtime_ns, item.name))
    return candidates[-1] if candidates else None


def _audit_contract(json_path: Path, md_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    payload = read_json(json_path, default=None)
    if payload is None:
        issues.append("contract JSON missing")
        payload = {}
    if not md_path.exists():
        issues.append("contract Markdown missing")
    if not payload.get("point_in_time_rules"):
        issues.append("point-in-time rules missing")
    return {"passed": not issues, "issues": issues}


def _audit_validation(path: Path) -> dict[str, Any]:
    issues: list[str] = []
    payload = read_json(path, default=None)
    if payload is None:
        issues.append("validation JSON missing")
        payload = {}
    if payload.get("overall_passed") is not True:
        issues.append("validation overall_passed is not true")
    if payload.get("point_in_time", {}).get("future_signal_rows", 1) != 0:
        issues.append("future signal leakage detected")
    if payload.get("point_in_time", {}).get("passed") is not True:
        issues.append("point-in-time validation did not pass")
    return {"passed": not issues, "issues": issues}


def _audit_bundle(path: Path | None) -> dict[str, Any]:
    issues: list[str] = []
    payload = read_json(path, default=None) if path else None
    if payload is None:
        issues.append("bundle JSON missing")
        payload = {}
    if payload.get("point_in_time", {}).get("future_signal_used") is not False:
        issues.append("future_signal_used is not false")
    if "missing_signal_days" not in payload.get("coverage", {}):
        issues.append("missing signal days are not recorded")
    if payload.get("boundary", {}).get("trading_signal") is not False:
        issues.append("bundle boundary trading_signal is not false")
    return {"passed": not issues, "issues": issues}


def _audit_replay(path: Path | None) -> dict[str, Any]:
    issues: list[str] = []
    payload = read_json(path, default=None) if path else None
    if payload is None:
        issues.append("replay JSON missing")
        payload = {}
    boundary = payload.get("boundary", {}) if isinstance(payload.get("boundary"), dict) else {}
    if payload.get("isolated") is not True:
        issues.append("replay isolated is not true")
    for key in ["main_ledger_written", "run_daily_called", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered"]:
        if boundary.get(key) is not False:
            issues.append(f"{key} is not false")
    return {"passed": not issues, "issues": issues}


def _audit_evaluation(path: Path | None) -> dict[str, Any]:
    issues: list[str] = []
    payload = read_json(path, default=None) if path else None
    if payload is None:
        issues.append("evaluation JSON missing")
        payload = {}
    boundary = payload.get("boundary", {}) if isinstance(payload.get("boundary"), dict) else {}
    for key in ["strategy_effectiveness_proven", "forward_dry_run_validated", "live_trading_ready"]:
        if boundary.get(key) is not False:
            issues.append(f"evaluation {key} is not false")
    if payload.get("overall_status") != "research_review_ready":
        issues.append("evaluation is not research_review_ready")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: list[Path | None]) -> dict[str, Any]:
    issues: list[str] = []
    for path in paths:
        if path is None or not path.exists() or not path.is_file():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lowered = line.strip().lower()
            if not lowered:
                continue
            if "not " in lowered or "no " in lowered or "does not " in lowered or "=false" in lowered or ": false" in lowered:
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in lowered:
                    issues.append(f"{path.name}:{line_number} contains forbidden positive wording: {phrase}")
    return {"passed": not issues, "issues": issues}


def _md_pair(path: Path | None) -> Path | None:
    if path is None:
        return None
    name = path.name
    project_root = _project_root_from_data_path(path)
    if project_root is None:
        return None
    mapping = {
        "global_briefing_signal_validation.json": ("system", "GLOBAL_BRIEFING_SIGNAL_VALIDATION.md"),
        "global_briefing_replay_audit.json": ("audit", "GLOBAL_BRIEFING_REPLAY_AUDIT.md"),
    }
    if name in mapping:
        directory, report = mapping[name]
        return project_root / "outputs" / directory / report
    if name.startswith("replay_bundle-"):
        suffix = name.removeprefix("replay_bundle-").removesuffix(".json")
        return project_root / "outputs" / "replays" / "global_briefing" / f"GLOBAL_BRIEFING_REPLAY_BUNDLE-{suffix}.md"
    if name.startswith("global_briefing_replay_evaluation-"):
        suffix = name.removeprefix("global_briefing_replay_evaluation-").removesuffix(".json")
        return project_root / "outputs" / "replays" / "global_briefing" / f"GLOBAL_BRIEFING_REPLAY_EVALUATION-{suffix}.md"
    if name.startswith("global_briefing_replay-"):
        suffix = name.removeprefix("global_briefing_replay-").removesuffix(".json")
        return project_root / "outputs" / "replays" / "global_briefing" / f"GLOBAL_BRIEFING_HISTORICAL_REPLAY-{suffix}.md"
    return None


def _project_root_from_data_path(path: Path) -> Path | None:
    parts = list(path.parts)
    for index, part in enumerate(parts):
        if part.lower() == "data":
            return Path(*parts[:index])
    return None


def build_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Global Briefing Replay Audit",
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        "",
        "## Section Results",
    ]
    for name, section in payload["sections"].items():
        lines.append(f"- {name}: passed={str(section['passed']).lower()} issues={section.get('issues', [])}")
    lines.extend(
        [
            "",
            "## Protected Path Snapshot",
            f"- modified_paths={payload['sections']['protected_path_snapshot']['modified_paths']}",
            f"- checked_paths={payload['sections']['protected_path_snapshot']['checked_paths']}",
            "",
            "## Boundary",
            "- This is a historical replay harness audit.",
            "- This is not forward dry-run validation.",
            "- This is not live trading readiness.",
            "- This does not prove strategy effectiveness.",
            "- No broker is connected.",
            "- No real orders are supported.",
            "- Main ledger was not written.",
            "- run-daily CLI was not called.",
            "- ML shadow outputs were not used.",
            "- Labels were not used.",
            "- Promotion was not triggered.",
            "",
            "## Release Recommendation",
        ]
    )
    if payload["overall_passed"]:
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
    lines.append("")
    return "\n".join(lines)
