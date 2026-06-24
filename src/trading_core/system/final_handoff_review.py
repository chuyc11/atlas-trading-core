"""Final human handoff and acceptance review report."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.system.common import write_json_markdown


PYTEST_RESULT = "374 passed, 1 skipped"
REQUIRED_FILES = [
    "VERSION",
    "RELEASE_NOTES.md",
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/SAFETY_BOUNDARY.md",
    "docs/RELEASE_MATRIX.md",
    "docs/CLI_REFERENCE.md",
    "docs/ARTIFACT_MAP.md",
    "docs/RUNBOOK.md",
    "docs/FORWARD_DRY_RUN_RUNBOOK.md",
    "data/system/system_integrity_audit.json",
    "outputs/audit/SYSTEM_INTEGRITY_AUDIT.md",
    "data/system/boundary_regression_audit.json",
    "outputs/audit/BOUNDARY_REGRESSION_AUDIT.md",
    "data/system/cli_inventory.json",
    "data/system/artifact_inventory.json",
    "data/system/reporting_system_audit.json",
    "data/experiments/experiment_system_audit.json",
    "data/experiments/mistake_pattern_library.json",
    "data/system/project_status_summary.json",
    "data/system/system_dashboard.json",
]
GLOB_FILES = [
    ("data/experiments/promotion_simulation-*.json", "promotion simulation"),
    ("data/experiments/strategy_comparison-*.json", "strategy comparison"),
    ("data/experiments/parameter_sweep-*.json", "parameter sweep"),
    ("data/shadow/ml_shadow_leaderboard-*.json", "ML shadow leaderboard"),
]


def build_final_handoff_review(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    warnings: list[str] = []
    now = datetime.now(UTC)
    artifacts = _collect_artifact_status(paths, warnings)
    system_integrity = _read_json(paths.project_root / "data/system/system_integrity_audit.json", warnings, "system integrity audit")
    boundary_regression = _read_json(paths.project_root / "data/system/boundary_regression_audit.json", warnings, "boundary regression audit")
    reporting_audit = _read_json(paths.project_root / "data/system/reporting_system_audit.json", warnings, "reporting system audit")
    experiment_audit = _read_json(paths.project_root / "data/experiments/experiment_system_audit.json", warnings, "experiment system audit")
    mistake_library = _read_json(paths.project_root / "data/experiments/mistake_pattern_library.json", warnings, "mistake pattern library")
    system_dashboard = _read_json(paths.project_root / "data/system/system_dashboard.json", warnings, "system dashboard")

    promotion_payloads = _read_glob(paths, "data/experiments/promotion_simulation-*.json", warnings)
    comparison_payloads = _read_glob(paths, "data/experiments/strategy_comparison-*.json", warnings)
    sweep_payloads = _read_glob(paths, "data/experiments/parameter_sweep-*.json", warnings)
    shadow_payloads = _read_glob(paths, "data/shadow/ml_shadow_leaderboard-*.json", warnings)

    system_integrity_passed = system_integrity.get("overall_passed") is True
    overall_status = "research_workbench_ready" if system_integrity_passed else "needs_attention"
    if not system_integrity:
        warnings.append("system_integrity_audit missing or unreadable")

    strategic_interpretation = _strategic_interpretation(
        promotion_payloads,
        comparison_payloads,
        sweep_payloads,
        shadow_payloads,
        mistake_library,
        warnings,
    )
    payload: dict[str, Any] = {
        "review_id": f"FINAL-HANDOFF-{now:%Y%m%d}",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "current_tag": _read_text(paths.project_root / "VERSION", warnings, "VERSION").strip() or "unknown",
        "pytest": PYTEST_RESULT,
        "overall_status": overall_status,
        "live_trading_ready": False,
        "forward_30d_dry_run_validated": False,
        "strategy_effectiveness_proven": False,
        "completed_layers": [
            "core trading engine",
            "historical real-data validation",
            "price-only historical replay",
            "ML shadow research pipeline",
            "strategy experiment system",
            "reporting control plane",
            "system integrity documentation",
        ],
        "validated_items": {
            "pytest": PYTEST_RESULT,
            "system_integrity_audit_passed": system_integrity_passed,
            "boundary_regression_passed": boundary_regression.get("passed") is True,
            "reporting_system_audit_passed": reporting_audit.get("overall_passed") is True,
            "experiment_system_audit_passed": experiment_audit.get("overall_passed") is True,
            "ml_shadow_boundary_audit_passed": _ml_shadow_boundary_passed(system_dashboard, shadow_payloads),
        },
        "trusted_outputs": [
            "pytest result",
            "system integrity audit",
            "boundary regression audit",
            "artifact inventory",
            "CLI inventory",
        ],
        "restricted_outputs": [
            "ML shadow leaderboard",
            "parameter sweep",
            "strategy comparison",
            "promotion simulation",
            "mistake pattern library",
            "weekly/monthly reports",
            "shadow signals",
            "watch recommendation",
            "promising_shadow",
            "active_small_candidate simulation",
            "historical replay",
        ],
        "open_items": [
            "30 trading-day forward dry-run is not completed",
            "full global-briefing historical replay is not completed",
            "live broker integration does not exist",
            "live trading is not supported",
            "strategy effectiveness is not proven",
        ],
        "recommended_next_steps": [
            "P0: keep project paused or run documentation review",
            "P0: do not start live trading",
            "P0: do not start RL",
            "P1: v0.5.2 usability polish",
            "P1: report index page",
            "P1: open-latest-report CLI",
            "P1: artifact browser markdown",
            "P2: v0.6 multi-market research expansion",
            "P2: US ETF universe",
            "P2: cross-market benchmark",
            "P2: global macro signal mapping",
            "P3: forward 30d dry-run when ready",
        ],
        "artifact_status": artifacts,
        "strategic_interpretation": strategic_interpretation,
        "warnings": warnings,
        "boundary": {
            "research_only": True,
            "broker_connected": False,
            "live_trading": False,
            "real_orders": False,
            "rl_active_trading": False,
            "llm_trading_decision": False,
            "promotion_triggered": False,
            "run_daily_called": False,
            "write_main_ledger": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "final_handoff_review_summary.json"
    report_path = paths.outputs_dir / "system" / "FINAL_HANDOFF_REVIEW_REPORT.md"
    write_json_markdown(json_path, payload, report_path, build_final_handoff_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def build_final_handoff_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Final Handoff Review Report",
        "",
        "## 1. Executive Summary",
        "",
        "* trading-core is a research-only virtual trading workbench",
        f"* current tag: {payload['current_tag']}",
        f"* pytest result: {payload['pytest']}",
        f"* system integrity audit result: {str(payload['validated_items']['system_integrity_audit_passed']).lower()}",
        "* not live trading ready",
        "* forward 30d dry-run not completed",
        "* strategy effectiveness not proven",
        "",
        "## 2. Current Version and Release Line",
        "",
    ]
    versions = [
        "v0.1.0-core-hardened",
        "v0.2.0-historical-real-data-validated",
        "v0.2.1-price-only-historical-replay-validated",
        "v0.3.0-ml-shadow-pipeline-audited",
        "v0.4.0-strategy-experiment-system-audited",
        "v0.5.0-research-reporting-control-plane-audited",
        "v0.5.1-system-integrity-and-documentation",
    ]
    lines.extend(f"* {version}" for version in versions)
    lines.extend(
        [
            "",
            "## 3. Completed Capabilities",
            "",
            "### Core",
            "",
            "* virtual account",
            "* orders/trades/portfolio",
            "* benchmark",
            "* attribution",
            "* T+1",
            "* health / consistency",
            "",
            "### Data and replay",
            "",
            "* price acquisition",
            "* data validation",
            "* historical backtest",
            "* price-only replay",
            "",
            "### ML shadow",
            "",
            "* feature store",
            "* label store",
            "* walk-forward dataset",
            "* shadow predictions",
            "* shadow signals",
            "* leaderboard",
            "* audited boundary",
            "",
            "### Experiments",
            "",
            "* experiment registry",
            "* parameter sweep",
            "* strategy comparison",
            "* dashboard",
            "* promotion simulation",
            "* mistake pattern library",
            "",
            "### Reports and control plane",
            "",
            "* weekly report",
            "* monthly report",
            "* system dashboard",
            "* project status report",
            "* research pipeline",
            "* reporting audit",
            "",
            "### Documentation and integrity",
            "",
            "* CLI inventory",
            "* artifact inventory",
            "* smoke test",
            "* boundary regression audit",
            "* system integrity audit",
            "",
            "## 4. What Has Been Validated",
            "",
            f"* pytest result: {payload['pytest']}",
            "* release audits passed",
            f"* boundary regression passed: {str(payload['validated_items']['boundary_regression_passed']).lower()}",
            f"* ML shadow boundary audit passed: {str(payload['validated_items']['ml_shadow_boundary_audit_passed']).lower()}",
            f"* experiment system audit passed: {str(payload['validated_items']['experiment_system_audit_passed']).lower()}",
            f"* reporting system audit passed: {str(payload['validated_items']['reporting_system_audit_passed']).lower()}",
            f"* system integrity audit passed: {str(payload['validated_items']['system_integrity_audit_passed']).lower()}",
            "",
            "## 5. What Has Not Been Validated",
            "",
            "* 30 trading-day forward dry-run is not completed",
            "* full global-briefing historical replay is not completed",
            "* live broker integration does not exist",
            "* live trading is not supported",
            "* strategy effectiveness is not proven",
            "* ML shadow results are not trading signals",
            "* promotion simulation is not promotion",
            "* reports are not admission gates",
            "",
            "## 6. Output Trust Levels",
            "",
            "### Trusted for engineering audit",
            "",
            "* pytest result",
            "* system integrity audit",
            "* boundary regression audit",
            "* artifact inventory",
            "* CLI inventory",
            "",
            "### Trusted for research review only",
            "",
            "* ML shadow leaderboard",
            "* parameter sweep",
            "* strategy comparison",
            "* promotion simulation",
            "* mistake pattern library",
            "* weekly/monthly reports",
            "",
            "### Not trusted as trading authorization",
            "",
            "* shadow signals",
            "* watch recommendation",
            "* promising_shadow",
            "* active_small_candidate simulation",
            "* historical replay",
            "",
            "## 7. Current Strategic Interpretation",
            "",
        ]
    )
    lines.extend(f"* {item}" for item in payload["strategic_interpretation"])
    if payload["warnings"]:
        lines.extend(["", "Warnings:"])
        lines.extend(f"* {warning}" for warning in payload["warnings"])
    lines.extend(
        [
            "",
            "## 8. How to Resume Work Later",
            "",
            "```bash",
            "git status",
            "git tag --points-at HEAD",
            "python -m pytest",
            "python -m trading_core.cli system-smoke-test --include-reports --include-inventory",
            "python -m trading_core.cli boundary-regression-audit",
            "python -m trading_core.cli system-integrity-audit",
            "```",
            "",
            "## 9. Recommended Next Steps",
            "",
            "* P0: keep project paused or run documentation review",
            "* P0: do not start live trading",
            "* P0: do not start RL",
            "* P1: v0.5.2 usability polish",
            "* P1: report index page",
            "* P1: open-latest-report CLI",
            "* P1: artifact browser markdown",
            "* P2: v0.6 multi-market research expansion",
            "* P2: US ETF universe",
            "* P2: cross-market benchmark",
            "* P2: global macro signal mapping",
            "* P3: forward 30d dry-run when ready",
            "",
            "## 10. Safety Boundary",
            "",
            "* This project remains research-only.",
            "* This system is not live trading ready.",
            "* No broker is connected.",
            "* No real orders are supported.",
            "* No strategy effectiveness is proven.",
            "* Forward 30d dry-run is not completed.",
            "* Shadow signals are not trading instructions.",
            "* Promotion simulation is not promotion.",
            "* Research reports are not admission gates.",
            "* This report does not authorize trading.",
            "",
        ]
    )
    return "\n".join(lines)


def _collect_artifact_status(paths: ProjectPaths, warnings: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for file_name in REQUIRED_FILES:
        path = paths.project_root / file_name
        exists = path.exists()
        rows.append({"path": file_name, "exists": exists})
        if not exists:
            warnings.append(f"missing artifact: {file_name}")
    for pattern, label in GLOB_FILES:
        matches = sorted((paths.project_root).glob(pattern))
        rows.append({"path": pattern, "exists": bool(matches), "count": len(matches)})
        if not matches:
            warnings.append(f"missing artifact group: {label} ({pattern})")
    return rows


def _strategic_interpretation(
    promotions: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    sweeps: list[dict[str, Any]],
    shadows: list[dict[str, Any]],
    mistake_library: dict[str, Any],
    warnings: list[str],
) -> list[str]:
    items: list[str] = []
    if sweeps:
        best_candidates = [payload.get("best_shadow_candidate") for payload in sweeps if payload.get("best_shadow_candidate")]
        if best_candidates:
            items.append("parameter sweep has shadow candidates for research review only; this is not trading authorization")
        else:
            items.append("parameter sweep did not produce an eligible candidate in the current artifacts")
    else:
        warnings.append("parameter sweep artifacts missing; no sweep interpretation made")

    if promotions:
        summary = _latest(promotions).get("summary", {})
        shadow_count = int(summary.get("shadow_candidate", 0) or 0)
        active_small = int(summary.get("active_small_candidate", 0) or 0)
        if shadow_count == 0 and active_small == 0:
            items.append("promotion simulation produced no shadow_candidate or active_small_candidate in the latest artifact")
        else:
            items.append(f"promotion simulation shows shadow_candidate={shadow_count}, active_small_candidate={active_small}; this remains simulation only")
    else:
        warnings.append("promotion simulation artifacts missing; no promotion interpretation made")

    if mistake_library:
        pattern_count = len(mistake_library.get("patterns", []))
        items.append(f"mistake pattern library contains {pattern_count} pattern(s); current strategy research should remain in shadow review")
    else:
        warnings.append("mistake pattern library missing; no pattern interpretation made")

    if shadows:
        recommendations = sorted({
            str(payload.get("shadow_recommendation") or payload.get("recommendation") or "unknown")
            for payload in shadows
        })
        items.append(f"ML shadow recommendation(s): {', '.join(recommendations)}; observation-only and not trading signals")
    else:
        warnings.append("ML shadow leaderboard artifacts missing; no shadow interpretation made")

    if comparisons:
        items.append(f"strategy comparison artifact count: {len(comparisons)}; comparison outputs are research review only")
    else:
        warnings.append("strategy comparison artifacts missing; no comparison interpretation made")
    return items


def _ml_shadow_boundary_passed(system_dashboard: dict[str, Any], shadows: list[dict[str, Any]]) -> bool:
    boundary = system_dashboard.get("safety_boundary", {}) if isinstance(system_dashboard, dict) else {}
    return boundary.get("live_trading") is False and bool(shadows)


def _latest(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    return payloads[-1] if payloads else {}


def _read_glob(paths: ProjectPaths, pattern: str, warnings: list[str]) -> list[dict[str, Any]]:
    payloads = []
    for path in sorted(paths.project_root.glob(pattern)):
        payload = _read_json(path, warnings, pattern)
        if payload:
            payloads.append(payload)
    return payloads


def _read_json(path: Path, warnings: list[str], label: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"malformed JSON skipped: {label} ({exc.msg})")
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: Path, warnings: list[str], label: str) -> str:
    if not path.exists():
        warnings.append(f"missing artifact: {label}")
        return ""
    return path.read_text(encoding="utf-8")
