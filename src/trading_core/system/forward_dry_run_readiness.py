"""Forward dry-run readiness audit.

This module checks whether the project is ready to prepare a future
30 trading-day virtual forward dry-run. It does not start that run.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from trading_core.reports.research_common import PROTECTED_PATHS, snapshot_protected
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, protected_diff, relative, timestamp_id, write_json_markdown


RELEASE_CANDIDATE = "v0.5.3-forward-dry-run-readiness-audited"
REQUIRED_DOCS = [
    "docs/FORWARD_DRY_RUN_RUNBOOK.md",
    "docs/SAFETY_BOUNDARY.md",
    "docs/RUNBOOK.md",
    "docs/CLI_REFERENCE.md",
    "docs/ARTIFACT_MAP.md",
]
RUNBOOK_REQUIRED_PHRASES = [
    "30 day forward dry-run remains incomplete",
    "Do not replace forward dry-run with historical replay",
]
READABLE_FILES = [
    "VERSION",
    "RELEASE_NOTES.md",
    "README.md",
    "docs/FORWARD_DRY_RUN_RUNBOOK.md",
    "docs/RUNBOOK.md",
    "docs/SAFETY_BOUNDARY.md",
    "docs/ARCHITECTURE.md",
    "docs/CLI_REFERENCE.md",
    "docs/ARTIFACT_MAP.md",
    "docs/COMMAND_COOKBOOK.md",
]
READABLE_ARTIFACTS = [
    "data/system/system_integrity_audit.json",
    "data/system/boundary_regression_audit.json",
    "data/system/usability_audit.json",
    "data/system/final_handoff_review_summary.json",
    "data/system/quick_status.json",
    "data/system/artifact_inventory.json",
    "data/system/cli_inventory.json",
]
POSITIVE_FORBIDDEN_WORDING = [
    "live trading ready",
    "broker connected",
    "automatic promotion enabled",
    "forward dry-run validated",
    "forward 30d dry-run validated",
    "strategy effectiveness proven",
]


def run_forward_dry_run_readiness(
    start_date: str | None = None,
    trading_days: int = 30,
    calendar: str | Path | None = None,
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    before = snapshot_protected(paths)
    audit_id, created_at = timestamp_id("FWD-READINESS")
    warnings: list[str] = []
    calendar_dates = _load_calendar_dates(calendar, paths, warnings)

    day0_path = paths.outputs_dir / "system" / "FORWARD_DRY_RUN_DAY0_CHECKLIST.md"
    plan_path = paths.outputs_dir / "system" / "FORWARD_DRY_RUN_30D_PLAN.md"
    day0_markdown = build_day0_checklist_markdown()
    plan_markdown = build_forward_30d_plan_markdown(
        start_date=start_date,
        trading_days=trading_days,
        calendar_dates=calendar_dates,
    )
    _write_text(day0_path, day0_markdown)
    _write_text(plan_path, plan_markdown)

    sections = {
        "version_baseline": _audit_version_baseline(paths),
        "required_docs": _audit_required_docs(paths, strict),
        "day0_checklist": _audit_generated_file(day0_path, ["Forward Dry-Run Day-0 Checklist", "No broker", "No experiment promotion"]),
        "forward_30d_plan": _audit_generated_file(plan_path, ["Forward Dry-Run 30 Trading-Day Plan", "does not start or validate the dry-run", "not live trading"]),
        "protected_path_snapshot": {"passed": True, "issues": [], "modified_paths": [], "checked_paths": list(PROTECTED_PATHS)},
        "run_daily_isolation": _audit_run_daily_isolation(paths),
        "future_data_leakage_readiness": _audit_future_data_leakage(paths),
        "artifact_separation": _audit_artifact_separation(paths),
        "wording": _audit_wording(paths),
    }
    if calendar_dates is None:
        if strict:
            sections["forward_30d_plan"]["passed"] = False
            sections["forward_30d_plan"]["issues"].append("trading calendar missing in strict mode")
        warnings.append("Trading calendar not found. Plan uses placeholders and requires manual calendar confirmation.")

    protected_changes = protected_diff(paths, before)
    sections["protected_path_snapshot"] = {
        "passed": not protected_changes,
        "issues": ["protected path changed", *protected_changes] if protected_changes else [],
        "modified_paths": [relative(Path(item), paths.project_root) for item in protected_changes],
        "checked_paths": list(PROTECTED_PATHS),
    }
    blocking = [f"{name}: {section.get('issues', [])}" for name, section in sections.items() if not section["passed"]]
    payload = {
        "audit_id": audit_id,
        "created_at": created_at,
        "release_candidate": RELEASE_CANDIDATE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "planned_start_date": start_date,
        "planned_trading_days": trading_days,
        "sections": sections,
        "boundary": {
            "readiness_only": True,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "broker_connected": False,
            "write_main_ledger": False,
            "run_daily_called": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "strategy_state_changed": False,
            "promotion_triggered": False,
            "rl_enabled": False,
            "llm_trading_decision": False,
        },
    }
    json_path = paths.data_dir / "system" / "forward_dry_run_readiness.json"
    report_path = paths.outputs_dir / "audit" / "FORWARD_DRY_RUN_READINESS_AUDIT.md"
    write_json_markdown(json_path, payload, report_path, build_readiness_audit_markdown(payload))
    return {
        **payload,
        "json_path": str(json_path),
        "report_path": str(report_path),
        "day0_checklist_path": str(day0_path),
        "plan_path": str(plan_path),
    }


def build_day0_checklist_markdown() -> str:
    return "\n".join(
        [
            "# Forward Dry-Run Day-0 Checklist",
            "",
            "## 1. Baseline",
            "- Current git commit recorded",
            "- Current tag recorded",
            "- python -m pytest passed",
            "- boundary-regression-audit passed",
            "- system-integrity-audit passed",
            "- usability-audit passed",
            "",
            "## 2. Universe Freeze",
            "- ETF universe frozen",
            "- Benchmark set frozen",
            "- Strategy configuration frozen",
            "- Risk configuration frozen",
            "",
            "## 3. Data Readiness",
            "- Price source path confirmed",
            "- Macro signal source confirmed",
            "- No future data available to run-daily",
            "- Calendar source confirmed",
            "",
            "## 4. Boundary Confirmation",
            "- No broker",
            "- No live trading",
            "- No real orders",
            "- No ML shadow in run-daily",
            "- No labels in run-daily",
            "- No experiment promotion",
            "",
            "## 5. Output Paths",
            "- Forward dry-run output path confirmed",
            "- Historical replay output path separated",
            "- ML shadow output path separated",
            "- Experiment output path separated",
            "",
            "## 6. Daily Procedure",
            "- run-daily command documented",
            "- health command documented",
            "- export-summary command documented",
            "- check-consistency command documented",
            "",
            "## 7. Stop Conditions",
            "- data missing",
            "- consistency failure",
            "- unexpected main ledger mutation",
            "- run-daily imports labels / ML / experiments",
            "- strategy state modified unexpectedly",
            "",
        ]
    )


def build_forward_30d_plan_markdown(
    start_date: str | None,
    trading_days: int,
    calendar_dates: list[str] | None,
) -> str:
    lines = [
        "# Forward Dry-Run 30 Trading-Day Plan",
        "",
        "## 1. Scope",
        "This plan prepares a 30 trading-day virtual forward dry-run.",
        "It does not start or validate the dry-run.",
        "",
        "## 2. Daily Commands",
        "",
        "For each trading day:",
        "",
        "```bash",
        "python -m trading_core.cli run-daily --date YYYY-MM-DD",
        "python -m trading_core.cli health --date YYYY-MM-DD",
        "python -m trading_core.cli export-summary --date YYYY-MM-DD",
        "python -m trading_core.cli check-consistency --date YYYY-MM-DD",
        "```",
        "",
        "## 3. Weekly Commands",
        "",
        "```bash",
        "python -m trading_core.cli summarize-health --start-date START --end-date END",
        "python -m trading_core.cli audit-dry-run --start-date START --end-date END",
        "python -m trading_core.cli dry-run-validation-report --start-date START --end-date END",
        "python -m trading_core.cli weekly-research-report --start-date START --end-date END --include-experiments --include-ml-shadow --include-mistakes",
        "```",
        "",
        "## 4. End-of-Run Commands",
        "",
        "```bash",
        "python -m trading_core.cli dry-run-validation-report --start-date START --end-date END",
        "python -m trading_core.cli monthly-research-report --start-date START --end-date END --include-weekly --include-experiments --include-ml-shadow",
        "python -m trading_core.cli final-handoff-review",
        "```",
        "",
        "## 5. What This Is Not",
        "",
        "* not live trading",
        "* not broker execution",
        "* not strategy effectiveness proof",
        "* not historical replay",
        "* not global-briefing full replay",
        "",
        "## 6. Planned Dates",
        "",
    ]
    selected_dates = _select_plan_dates(start_date, trading_days, calendar_dates)
    if selected_dates:
        lines.extend(f"- {item}" for item in selected_dates)
    else:
        lines.append("Trading calendar not found. Plan uses placeholders and requires manual calendar confirmation.")
    lines.append("")
    return "\n".join(lines)


def build_readiness_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Forward Dry-Run Readiness Audit",
        "",
        "## 1. Scope",
        "",
        "This audit checks readiness to begin a 30 trading-day virtual forward dry-run.",
        "It does not start the dry-run.",
        "It does not validate the dry-run.",
        "It does not certify live trading readiness.",
        "",
        "## 2. Overall Verdict",
        "",
        f"- overall_passed={str(payload['overall_passed']).lower()}",
        f"- blocking_reasons={payload['blocking_reasons']}",
        f"- warnings={payload['warnings']}",
        "",
        "## 3. Readiness Sections",
        "",
    ]
    for name, section in payload["sections"].items():
        issues = section.get("issues", [])
        lines.append(f"- {name}: passed={str(section['passed']).lower()} issues={issues}")
    lines.extend(
        [
            "",
            "## 4. Generated Outputs",
            "",
            "- outputs/system/FORWARD_DRY_RUN_DAY0_CHECKLIST.md",
            "- outputs/system/FORWARD_DRY_RUN_30D_PLAN.md",
            "",
            "## 5. Start Conditions",
            "",
            "- Confirm current git commit and release tag.",
            "- Confirm python -m pytest has passed.",
            "- Confirm boundary, system integrity, and usability audits have passed.",
            "- Freeze universe, benchmarks, strategy configuration, and risk configuration.",
            "- Confirm calendar, price source, and macro signal source.",
            "- Confirm labels, ML shadow, experiments, and promotion simulations are excluded from run-daily.",
            "",
            "## 6. Stop Conditions",
            "",
            "- data missing",
            "- consistency failure",
            "- unexpected main ledger mutation",
            "- run-daily imports labels / ML / experiments",
            "- strategy state modified unexpectedly",
            "",
            "## 7. Safety Boundary",
            "",
            "- This audit is readiness-only.",
            "- This audit does not start forward dry-run.",
            "- This audit does not validate forward dry-run.",
            "- This system is not live trading ready.",
            "- No broker is connected.",
            "- No real orders are supported.",
            "- No strategy state was changed.",
            "- No promotion was triggered.",
            "- No orders were written.",
            "- No trades were written.",
            "- No portfolio was written.",
            "- No accounts were written.",
            "- ML shadow outputs are not trading instructions.",
            "- Labels must not be used in run-daily.",
            "- Historical replay is not forward dry-run.",
            "",
            "## 8. Release Recommendation",
            "",
        ]
    )
    if payload["overall_passed"]:
        lines.extend(["Recommended release tag:", RELEASE_CANDIDATE])
    else:
        lines.append("Release tag is not recommended until blocking reasons are resolved.")
    lines.append("")
    return "\n".join(lines)


def _audit_version_baseline(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    version = _read_text(paths.project_root / "VERSION").strip()
    if not version:
        issues.append("VERSION missing")
    if version and "v0.5.2" not in version and "v0.5.3" not in version:
        issues.append(f"current VERSION is not v0.5.2/v0.5.3 readiness line: {version}")
    for name in ["README.md", "RELEASE_NOTES.md"]:
        text = _read_text(paths.project_root / name)
        if _has_positive_forbidden_wording(text):
            issues.append(f"{name} contains live-ready or promotion-ready wording")
    return {"passed": not issues, "current_version": version or None, "issues": issues}


def _audit_required_docs(paths: ProjectPaths, strict: bool) -> dict[str, Any]:
    issues = []
    for doc in REQUIRED_DOCS:
        if not (paths.project_root / doc).exists():
            issues.append(f"missing {doc}")
    runbook = _read_text(paths.project_root / "docs" / "FORWARD_DRY_RUN_RUNBOOK.md")
    for phrase in RUNBOOK_REQUIRED_PHRASES:
        if phrase not in runbook:
            issues.append(f"FORWARD_DRY_RUN_RUNBOOK.md missing phrase: {phrase}")
    if strict:
        for config_name in ["config/universe_china_etf.yaml", "config/benchmarks.yaml", "config/risk_rules.yaml"]:
            if not (paths.project_root / config_name).exists():
                issues.append(f"missing strict config evidence: {config_name}")
    return {"passed": not issues, "issues": issues}


def _audit_generated_file(path: Path, phrases: list[str]) -> dict[str, Any]:
    issues = []
    text = _read_text(path)
    if not text:
        issues.append(f"missing generated file: {path.name}")
    for phrase in phrases:
        if phrase not in text:
            issues.append(f"{path.name} missing phrase: {phrase}")
    return {"passed": not issues, "issues": issues}


def _audit_run_daily_isolation(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    source = paths.project_root / "src" / "trading_core"
    run_daily = _read_text(source / "daily_run.py")
    signal_generator = _read_text(source / "signals" / "signal_generator.py")
    broker_text = _read_tree_text(source / "broker")
    if _contains_import(run_daily, "trading_core.labels") or "label_store" in run_daily:
        issues.append("run-daily imports labels")
    if _contains_import(run_daily, "trading_core.ml") or "ml_shadow" in run_daily:
        issues.append("run-daily imports ML shadow modules")
    if _contains_import(run_daily, "trading_core.experiments"):
        issues.append("run-daily imports experiment modules")
    if "promotion_simulation" in run_daily:
        issues.append("run-daily imports promotion simulation")
    if "mistake_pattern_library" in run_daily:
        issues.append("run-daily imports mistake pattern library")
    for module in ["artifact_browser", "report_index", "quick_status", "latest_artifact", "usability_audit"]:
        if module in run_daily:
            issues.append(f"run-daily imports usability module: {module}")
    if "label_store" in signal_generator or _contains_import(signal_generator, "trading_core.labels"):
        issues.append("label_store used in signal generator")
    if re.search(r"ml_shadow|shadow_predictions|ml_predictions", run_daily + "\n" + broker_text, re.IGNORECASE):
        issues.append("ML shadow predictions used in order generation")
    return {"passed": not issues, "issues": issues}


def _audit_future_data_leakage(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    source = paths.project_root / "src" / "trading_core"
    run_daily = _read_text(source / "daily_run.py")
    docs = _combined_text(paths, ["docs/SAFETY_BOUNDARY.md", "docs/FORWARD_DRY_RUN_RUNBOOK.md"])
    if _contains_import(run_daily, "trading_core.labels") or "label_store" in run_daily:
        issues.append("label store enters run-daily")
    if _contains_import(run_daily, "trading_core.features") or "feature_store" in run_daily:
        issues.append("feature store enters run-daily decision path")
    if _contains_import(run_daily, "trading_core.ml") or "ml_shadow" in run_daily:
        issues.append("ML shadow predictions enter run-daily")
    if _contains_import(run_daily, "trading_core.experiments") or "promotion_simulation" in run_daily:
        issues.append("experiment comparison or promotion simulation enters run-daily")
    if "replay-dry-run" in run_daily or "historical_dry_run_replay" in run_daily:
        issues.append("historical replay output enters run-daily")
    if "historical replay is not forward" not in docs.lower() and "not forward 30d dry-run" not in docs.lower():
        issues.append("docs do not clearly state historical replay is not forward dry-run")
    return {"passed": not issues, "issues": issues}


def _audit_artifact_separation(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    artifact_map = _read_text(paths.project_root / "docs" / "ARTIFACT_MAP.md").lower()
    required_terms = ["backtests", "replays", "shadow", "experiments", "reports", "system"]
    for term in required_terms:
        if term not in artifact_map:
            issues.append(f"artifact map missing {term} artifacts")
    for phrase in ["not broker instructions", "not permission to trade", "no"]:
        if phrase not in artifact_map:
            issues.append(f"artifact map missing boundary phrase: {phrase}")
    return {"passed": not issues, "issues": issues}


def _audit_wording(paths: ProjectPaths) -> dict[str, Any]:
    issues = []
    text = _combined_text(paths, [*READABLE_FILES, *READABLE_ARTIFACTS])
    if _has_positive_forbidden_wording(text):
        issues.append("positive live trading, broker, promotion, or strategy-proof wording found")
    return {"passed": not issues, "issues": issues}


def _load_calendar_dates(calendar: str | Path | None, paths: ProjectPaths, warnings: list[str]) -> list[str] | None:
    if calendar is None:
        return None
    path = Path(calendar)
    if not path.is_absolute():
        path = paths.project_root / path
    if not path.exists():
        warnings.append(f"trading calendar missing: {relative(path, paths.project_root)}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"trading calendar malformed: {exc.msg}")
        return None
    if isinstance(payload, list):
        raw_dates = payload
    elif isinstance(payload, dict):
        raw_dates = payload.get("trading_days") or payload.get("dates") or payload.get("calendar") or []
    else:
        raw_dates = []
    dates = [str(item) for item in raw_dates if isinstance(item, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", item)]
    if not dates:
        warnings.append("trading calendar contains no ISO trading dates")
        return None
    return sorted(dates)


def _select_plan_dates(start_date: str | None, trading_days: int, calendar_dates: list[str] | None) -> list[str]:
    if not calendar_dates:
        return []
    selected = [item for item in calendar_dates if start_date is None or item >= start_date]
    return selected[: max(0, trading_days)]


def _contains_import(text: str, module: str) -> bool:
    return f"from {module}" in text or f"import {module}" in text


def _has_positive_forbidden_wording(text: str) -> bool:
    for line in text.lower().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("- not ") or stripped.startswith("* not "):
            continue
        if "not " in stripped or "no " in stripped or "does not " in stripped:
            continue
        if any(phrase in stripped for phrase in POSITIVE_FORBIDDEN_WORDING):
            return True
    return False


def _combined_text(paths: ProjectPaths, files: list[str]) -> str:
    texts = []
    for item in files:
        path = paths.project_root / item
        if path.exists() and path.is_file():
            texts.append(path.read_text(encoding="utf-8"))
    return "\n".join(texts)


def _read_tree_text(root: Path) -> str:
    if not root.exists():
        return ""
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(root.rglob("*.py")) if path.is_file())


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
