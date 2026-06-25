"""Audit the isolated global-briefing replay execution adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.5-isolated-replay-execution-adapter-audited"
FORBIDDEN_PHRASES = [
    "live trading ready",
    "strategy effectiveness proven",
    "forward dry-run validated",
]


def audit_isolated_replay_adapter(
    *,
    replay_path: str | None = None,
    evaluation_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("ISOLATED-REPLAY-ADAPTER-AUDIT")
    replay_json = _resolve_or_latest(replay_path, paths.data_dir / "replays" / "global_briefing", "global_briefing_replay-*.json", paths)
    evaluation_json = _resolve_or_latest(
        evaluation_path,
        paths.data_dir / "replays" / "global_briefing",
        "global_briefing_replay_evaluation-*.json",
        paths,
    )
    replay = read_json(replay_json, default=None) if replay_json else None
    evaluation = read_json(evaluation_json, default=None) if evaluation_json else None
    sections = {
        "replay_execution": _audit_replay_execution(replay),
        "isolated_outputs": _audit_isolated_outputs(replay, paths),
        "protected_paths": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "boundary": _audit_boundary(replay),
        "evaluation": _audit_evaluation(evaluation),
        "wording": _audit_wording([_report_pair(replay_json), _report_pair(evaluation_json)]),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {
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
            "replay": str(replay_json) if replay_json else None,
            "evaluation": str(evaluation_json) if evaluation_json else None,
        },
        "sections": sections,
        "boundary": {
            "isolated_replay_adapter_only": True,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "broker_connected": False,
            "strategy_effectiveness_proven": False,
            "promotion_triggered": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
        },
    }
    json_path = paths.data_dir / "system" / "isolated_replay_adapter_audit.json"
    report_path = paths.outputs_dir / "audit" / "ISOLATED_REPLAY_ADAPTER_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_adapter_audit_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _resolve_or_latest(path_text: str | None, directory: Path, pattern: str, paths: ProjectPaths) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else paths.project_root / path
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(pattern), key=lambda item: (item.stat().st_mtime_ns, item.name))
    return candidates[-1] if candidates else None


def _audit_replay_execution(replay: dict[str, Any] | None) -> dict[str, Any]:
    issues: list[str] = []
    if replay is None:
        return {"passed": False, "issues": ["replay result missing"]}
    execution = replay.get("execution", {}) if isinstance(replay.get("execution"), dict) else {}
    if execution.get("mode") != "isolated":
        issues.append("execution.mode is not isolated")
    if execution.get("no_trade_fallback") is not False:
        issues.append("no_trade_fallback is not false")
    if replay.get("boundary", {}).get("isolated_replay_ledger_written") is not True:
        issues.append("isolated_replay_ledger_written is not true")
    return {"passed": not issues, "issues": issues}


def _audit_isolated_outputs(replay: dict[str, Any] | None, paths: ProjectPaths) -> dict[str, Any]:
    issues: list[str] = []
    if replay is None:
        return {"passed": False, "issues": ["replay result missing"]}
    outputs = replay.get("isolated_outputs") or replay.get("isolated_output_paths") or {}
    allowed_root = (paths.data_dir / "replays" / "global_briefing").resolve()
    for key in ["account", "orders", "trades", "portfolio", "valuations", "signals"]:
        raw = outputs.get(key) if isinstance(outputs, dict) else None
        if not raw:
            issues.append(f"missing {key} output")
            continue
        output_path = Path(str(raw))
        if not output_path.exists():
            issues.append(f"{key} output does not exist: {output_path}")
            continue
        try:
            output_path.resolve().relative_to(allowed_root)
        except ValueError:
            issues.append(f"{key} output outside data/replays/global_briefing: {output_path}")
    return {"passed": not issues, "issues": issues}


def _audit_boundary(replay: dict[str, Any] | None) -> dict[str, Any]:
    issues: list[str] = []
    if replay is None:
        return {"passed": False, "issues": ["replay result missing"]}
    boundary = replay.get("boundary", {}) if isinstance(replay.get("boundary"), dict) else {}
    expected_false = [
        "main_ledger_written",
        "run_daily_called",
        "labels_used",
        "ml_shadow_used",
        "experiments_used",
        "promotion_triggered",
        "forward_dry_run",
        "live_trading",
        "broker_connected",
    ]
    for key in expected_false:
        if boundary.get(key) is not False:
            issues.append(f"{key} is not false")
    return {"passed": not issues, "issues": issues}


def _audit_evaluation(evaluation: dict[str, Any] | None) -> dict[str, Any]:
    issues: list[str] = []
    if evaluation is None:
        return {"passed": False, "issues": ["evaluation missing"]}
    if evaluation.get("overall_status") != "research_review_ready":
        issues.append("evaluation is not research_review_ready")
    integrity = evaluation.get("integrity", {}) if isinstance(evaluation.get("integrity"), dict) else {}
    if integrity.get("isolated_ledger_complete") is not True:
        issues.append("evaluation isolated_ledger_complete is not true")
    if integrity.get("valuation_days_match_processed_days") is not True:
        issues.append("evaluation valuation coverage did not pass")
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


def _report_pair(path: Path | None) -> Path | None:
    if path is None:
        return None
    project_root = _project_root_from_data_path(path)
    if project_root is None:
        return None
    name = path.name
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


def build_adapter_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Isolated Replay Adapter Audit",
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        "",
        "## Isolated Execution",
        f"- replay_execution={payload['sections']['replay_execution']}",
        "",
        "## Isolated Outputs",
        f"- isolated_outputs={payload['sections']['isolated_outputs']}",
        "",
        "## Protected Path Snapshot",
        f"- modified_paths={payload['sections']['protected_paths']['modified_paths']}",
        f"- checked_paths={payload['sections']['protected_paths']['checked_paths']}",
        "",
        "## Boundary",
        "- This audit checks isolated replay execution only.",
        "- This is not forward dry-run validation.",
        "- This is not live trading readiness.",
        "- This does not prove strategy effectiveness.",
        "- Main ledger was not written.",
        "- run-daily CLI was not called.",
        "- Labels were not used.",
        "- ML shadow outputs were not used.",
        "- Experiment or promotion outputs were not used.",
        "- Promotion was not triggered.",
        "",
        "## Release Recommendation",
    ]
    if payload["overall_passed"]:
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
    lines.append("")
    return "\n".join(lines)
