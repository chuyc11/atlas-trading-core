"""Release audit for the v0.6.0 baseline strategy pack."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import protected_diff, write_json_markdown

from .common import (
    DEFAULT_END_DATE,
    DEFAULT_START_DATE,
    NEXT_VERSION,
    RELEASE_CANDIDATE,
    RESEARCH_NOTICE,
    STRATEGY_IDS,
    benchmark_path,
    paths_or_default,
    preview_path,
    read_dict,
    read_rows,
    replay_summary_path,
    report_path,
    research_boundary,
    signal_path,
)


FORBIDDEN_POSITIVE_PHRASES = [
    "strategy effectiveness proven",
    "forward dry-run validated",
    "live trading ready",
    "broker connected",
    "real orders supported",
    "promotion approved",
    "ml approved for trading",
    "llm approved for trading",
    "rl approved for trading",
]


def audit_baseline_strategy_pack(
    *,
    start_date: str = DEFAULT_START_DATE,
    end_date: str = DEFAULT_END_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths_or_default(paths)
    before = snapshot_protected(paths)
    artifacts = _load_artifacts(paths, start_date, end_date)
    sections = {
        "scope_plan": _exists(artifacts["scope_plan"], "scope plan missing"),
        "contract": _contract_section(artifacts["contract"]),
        "registry": _registry_section(artifacts["registry"]),
        "signals": _signals_section(artifacts["signals"]),
        "order_preview": _preview_section(artifacts["previews"]),
        "replay": _replay_section(artifacts["replays"], paths),
        "benchmark_comparison": _exists(artifacts["benchmark"], "benchmark comparison missing"),
        "reports": _reports_section(artifacts["reports"]),
        "pack_summary": _summary_section(artifacts["summary"]),
        "boundary": _boundary_section(artifacts),
        "protected_paths": {"passed": True, "issues": [], "checked_paths": list(PROTECTED_PATHS)},
        "wording": _wording_section(paths),
    }
    protected_changes = protected_diff(paths, before)
    sections["protected_paths"] = {"passed": not protected_changes, "issues": protected_changes, "checked_paths": list(PROTECTED_PATHS)}
    blocking = [f"{name}: {section['issues']}" for name, section in sections.items() if not section["passed"]]
    registry_count = len(artifacts["registry"].get("strategies", {})) if artifacts["registry"] else 0
    summary = artifacts["summary"] or {}
    payload: dict[str, Any] = {
        "audit_id": f"BASELINE-STRATEGY-PACK-AUDIT-{start_date}-{end_date}",
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "summary": {
            "strategy_count": registry_count,
            "strategies_complete": int(summary.get("strategies_complete", 0) or 0),
            "all_strategies_complete": summary.get("all_strategies_complete") is True,
            "recommended_next_version": NEXT_VERSION,
        },
        "sections": sections,
        "boundary": research_boundary("baseline_strategy_pack_only"),
    }
    json_path = paths.data_dir / "system" / "baseline_strategy_pack_audit.json"
    md_path = paths.outputs_dir / "audit" / "BASELINE_STRATEGY_PACK_AUDIT.md"
    write_json_markdown(json_path, payload, md_path, build_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def _load_artifacts(paths: ProjectPaths, start_date: str, end_date: str) -> dict[str, Any]:
    return {
        "scope_plan": read_dict(paths.data_dir / "system" / "baseline_strategy_scope_plan.json"),
        "contract": read_dict(paths.data_dir / "strategies" / "baseline_strategy_contract.json"),
        "registry": read_dict(paths.data_dir / "strategies" / "baseline_strategy_registry.json"),
        "signals": {strategy_id: read_rows(signal_path(paths, strategy_id, start_date, end_date)) for strategy_id in STRATEGY_IDS},
        "previews": {strategy_id: read_rows(preview_path(paths, strategy_id, start_date, end_date)) for strategy_id in STRATEGY_IDS},
        "replays": {strategy_id: read_dict(replay_summary_path(paths, strategy_id, start_date, end_date)) for strategy_id in STRATEGY_IDS},
        "benchmark": read_dict(benchmark_path(paths, start_date, end_date)),
        "reports": {strategy_id: read_dict(report_path(paths, strategy_id, start_date, end_date)) for strategy_id in STRATEGY_IDS},
        "summary": read_dict(paths.data_dir / "strategies" / "baseline_strategy_pack_summary.json"),
    }


def _exists(data: Any, issue: str) -> dict[str, Any]:
    passed = bool(data)
    return {"passed": passed, "issues": [] if passed else [issue]}


def _contract_section(contract: dict[str, Any]) -> dict[str, Any]:
    issues = []
    strategies = contract.get("strategies", {}) if contract else {}
    if not contract:
        issues.append("contract missing")
    for strategy_id in STRATEGY_IDS:
        item = strategies.get(strategy_id)
        if not item:
            issues.append(f"{strategy_id} contract missing")
            continue
        for key in ["uses_ml_shadow", "uses_llm", "uses_rl", "uses_promotion_outputs", "starts_forward_dry_run"]:
            if item.get(key) is not False:
                issues.append(f"{strategy_id} {key} is not false")
    return {"passed": not issues, "issues": issues}


def _registry_section(registry: dict[str, Any]) -> dict[str, Any]:
    issues = []
    strategies = registry.get("strategies", {}) if registry else {}
    if not registry:
        issues.append("strategy registry missing")
    if len(strategies) < 3:
        issues.append("less than 3 strategies registered")
    for strategy_id in STRATEGY_IDS:
        item = strategies.get(strategy_id)
        if not item:
            issues.append(f"{strategy_id} registry missing")
            continue
        if not item.get("parameter_version"):
            issues.append(f"{strategy_id} parameter_version missing")
    return {"passed": not issues, "issues": issues}


def _signals_section(signals: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    issues = []
    for strategy_id, rows in signals.items():
        if not rows:
            issues.append(f"{strategy_id} signals missing")
            continue
        if not all(row.get("pit_constraints_passed") is True for row in rows):
            issues.append(f"{strategy_id} signal PIT constraints failed")
    return {"passed": not issues, "issues": issues}


def _preview_section(previews: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    issues = []
    for strategy_id, rows in previews.items():
        if not rows:
            issues.append(f"{strategy_id} order preview missing")
            continue
        if not all(row.get("preview_only") is True for row in rows):
            issues.append(f"{strategy_id} preview_only not true")
        if any(row.get("executed") is True for row in rows):
            issues.append(f"{strategy_id} preview row executed")
    return {"passed": not issues, "issues": issues}


def _replay_section(replays: dict[str, dict[str, Any]], paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    allowed_root = paths.data_dir / "replays" / "strategies"
    for strategy_id, replay in replays.items():
        if not replay:
            issues.append(f"{strategy_id} replay missing")
            continue
        if replay.get("execution_mode") != "isolated":
            issues.append(f"{strategy_id} replay not isolated")
        for key in ["orders_path", "trades_path", "portfolio_path", "valuations_path"]:
            raw = replay.get(key)
            path = paths.project_root / raw if isinstance(raw, str) else Path("")
            if not str(path).startswith(str(allowed_root)):
                issues.append(f"{strategy_id} {key} outside strategy replay root")
    return {"passed": not issues, "issues": issues}


def _reports_section(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    issues = []
    for strategy_id, report in reports.items():
        if not report:
            issues.append(f"{strategy_id} report missing")
            continue
        if not report.get("explicit_non_claims"):
            issues.append(f"{strategy_id} explicit non-claims missing")
        if report.get("promotion_triggered") is not False:
            issues.append(f"{strategy_id} report promotion boundary failed")
    return {"passed": not issues, "issues": issues}


def _summary_section(summary: dict[str, Any]) -> dict[str, Any]:
    issues = []
    if not summary:
        issues.append("pack summary missing")
    if summary and summary.get("all_strategies_complete") is not True:
        issues.append("all_strategies_complete is not true")
    if summary and summary.get("promotion_triggered") is not False:
        issues.append("promotion_triggered is not false")
    if summary and summary.get("run_daily_called") is not False:
        issues.append("run_daily_called is not false")
    if summary and summary.get("forward_dry_run_started") is not False:
        issues.append("forward_dry_run_started is not false")
    if summary and summary.get("main_ledger_written") is not False:
        issues.append("main_ledger_written is not false")
    return {"passed": not issues, "issues": issues}


def _boundary_section(artifacts: dict[str, Any]) -> dict[str, Any]:
    issues = []
    forbidden = [
        "run_daily_called",
        "forward_dry_run_started",
        "forward_dry_run_validated",
        "main_ledger_written",
        "labels_used_as_authorization",
        "ml_shadow_used_as_authorization",
        "experiments_used_as_authorization",
        "llm_trading_decision",
        "rl_used",
        "promotion_triggered",
        "strategy_effectiveness_proven",
        "live_trading_ready",
        "broker_connected",
        "ml_trading_approved",
        "llm_trading_approved",
        "rl_trading_approved",
    ]
    for artifact_name, artifact in artifacts.items():
        candidates = artifact.values() if isinstance(artifact, dict) and artifact_name in {"reports", "replays"} else [artifact]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            boundary = item.get("boundary", {})
            for key in forbidden:
                if item.get(key) is True or boundary.get(key) is True:
                    issues.append(f"{artifact_name} {key} is true")
    return {"passed": not issues, "issues": issues}


def _wording_section(paths: ProjectPaths) -> dict[str, Any]:
    roots = [
        paths.outputs_dir / "strategies",
        paths.outputs_dir / "replays" / "strategies",
        paths.outputs_dir / "audit",
        paths.project_root / "docs",
    ]
    issues = []
    for root in roots:
        if not root.exists():
            continue
        for file in root.rglob("*.md"):
            _scan_file(file, issues)
    return {"passed": not issues, "issues": issues}


def _scan_file(file: Path, issues: list[str]) -> None:
    for line_number, line in enumerate(file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        lowered = line.lower()
        if not lowered or any(token in lowered for token in ["not ", "no ", "false", "does not", "is not", "not used"]):
            continue
        for phrase in FORBIDDEN_POSITIVE_PHRASES:
            if phrase in lowered:
                issues.append(f"{file.name}:{line_number} forbidden positive wording: {phrase}")


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Baseline Strategy Pack Audit",
        "",
        RESEARCH_NOTICE,
        "",
        "## Overall Verdict",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        "",
        "## Strategy Pack Coverage",
        f"- strategy_count: {payload['summary']['strategy_count']}",
        f"- strategies_complete: {payload['summary']['strategies_complete']}",
        f"- all_strategies_complete: {str(payload['summary']['all_strategies_complete']).lower()}",
        "",
        "## Strategy Reports",
        f"- reports section passed: {str(payload['sections']['reports']['passed']).lower()}",
        "",
        "## Benchmark Comparison",
        f"- comparison section passed: {str(payload['sections']['benchmark_comparison']['passed']).lower()}",
        "",
        "## Recommended Next Version",
        f"- {payload['summary']['recommended_next_version']}",
        "",
        "## Boundary",
        "- baseline strategy pack only",
        "- run-daily not called",
        "- forward dry-run not started",
        "- main ledger not written",
        "- not strategy effectiveness proof",
        "- not live trading readiness",
        "- no broker connected",
        "- ML shadow not used as authorization",
        "- LLM not used for trading decision",
        "- RL not used",
        "- promotion not triggered",
        "",
        "## Release Recommendation",
    ]
    lines.append(f"Recommended release tag: {RELEASE_CANDIDATE}" if payload["overall_passed"] else "Release tag is not recommended until blockers are resolved.")
    lines.append("")
    return "\n".join(lines)

