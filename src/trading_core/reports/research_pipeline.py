"""One-command research-only reporting pipeline."""

from __future__ import annotations

from typing import Any

from trading_core.reports.monthly_research_report import build_monthly_research_report
from trading_core.reports.project_status_report import build_project_status_report
from trading_core.reports.research_common import default_paths, write_json_and_markdown
from trading_core.reports.system_dashboard import build_system_dashboard
from trading_core.reports.weekly_research_report import build_weekly_research_report
from trading_core.storage.file_paths import ProjectPaths


def run_research_pipeline(
    start_date: str,
    end_date: str,
    skip_weekly: bool = False,
    skip_monthly: bool = False,
    skip_dashboard: bool = False,
    skip_project_status: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    steps: list[dict[str, Any]] = []
    warnings: list[str] = []

    def run_step(name: str, fn):
        try:
            result = fn()
            steps.append({"step": name, "status": "success", "output": result.get("report_path"), "json_output": result.get("json_path")})
        except Exception as exc:  # report pipeline records failure instead of crashing
            warnings.append(f"{name} failed: {exc}")
            steps.append({"step": name, "status": "failed", "output": None, "error": str(exc)})

    if not skip_weekly:
        run_step("weekly_research_report", lambda: build_weekly_research_report(start_date, end_date, True, True, True, paths))
    else:
        steps.append({"step": "weekly_research_report", "status": "skipped", "output": None})
    if not skip_monthly:
        run_step("monthly_research_report", lambda: build_monthly_research_report(start_date, end_date, None, True, True, True, paths))
    else:
        steps.append({"step": "monthly_research_report", "status": "skipped", "output": None})
    if not skip_dashboard:
        run_step("system_dashboard", lambda: build_system_dashboard(True, True, paths))
    else:
        steps.append({"step": "system_dashboard", "status": "skipped", "output": None})
    if not skip_project_status:
        run_step("project_status_report", lambda: build_project_status_report(True, True, paths))
    else:
        steps.append({"step": "project_status_report", "status": "skipped", "output": None})

    overall = "success" if all(step["status"] in {"success", "skipped"} for step in steps) else "failed"
    payload = {
        "pipeline_id": f"RESEARCH-PIPELINE-{start_date.replace('-', '')}-{end_date.replace('-', '')}",
        "start_date": start_date,
        "end_date": end_date,
        "steps": steps,
        "overall_status": overall,
        "status": overall,
        "warnings": warnings,
        "failures": [step for step in steps if step["status"] == "failed"],
        "boundary": {
            "research_only": True,
            "write_main_ledger": False,
            "orders_written": False,
            "trades_written": False,
            "portfolio_written": False,
            "accounts_written": False,
            "strategy_state_changed": False,
            "promotion_triggered": False,
            "run_daily_called": False,
        },
    }
    json_path = paths.data_dir / "system" / f"research_pipeline_summary-{start_date}-{end_date}.json"
    md_path = paths.outputs_dir / "system" / f"RESEARCH_PIPELINE_REPORT-{start_date}-{end_date}.md"
    write_json_and_markdown(json_path, payload, md_path, build_pipeline_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_pipeline_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Research Pipeline Report",
        "",
        "## 1. Scope",
        f"- start_date: {payload['start_date']}",
        f"- end_date: {payload['end_date']}",
        "",
        "## 2. Steps",
    ]
    lines.extend(f"- {step['step']}: {step['status']}" for step in payload["steps"])
    lines.extend(["", "## 3. Outputs"])
    lines.extend(f"- {step['step']}: {step.get('output')}" for step in payload["steps"])
    lines.extend(["", "## 4. Warnings"])
    lines.extend([f"- {warning}" for warning in payload["warnings"]] or ["- none"])
    lines.extend(
        [
            "",
            "## 5. Safety Boundary",
            "- research only",
            "- no run-daily",
            "- no orders/trades/portfolio/accounts",
            "- no strategy state changed",
            "- no promotion triggered",
            "",
        ]
    )
    return "\n".join(lines)
