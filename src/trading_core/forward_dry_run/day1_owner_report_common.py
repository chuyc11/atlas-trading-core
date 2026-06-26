"""Shared helpers for v0.6.3.2 day1 owner report pack."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from trading_core.forward_dry_run.day1_common import audit_report, system_json, system_report, write_artifact
from trading_core.forward_dry_run.day1_continuation_common import (
    CONTINUATION_ARTIFACTS,
    DAY1_CORE_ARTIFACTS,
    artifact_record,
    day1_core_status,
    day2_executed,
    day3_executed,
    paths_or_default,
    project_path,
    sha256_path,
    standard_boundary,
)
from trading_core.execution.common import read_dict
from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.6.3.2-forward-dry-run-day1-owner-report-pack"
BASELINE_FROM = "v0.6.3.1-forward-dry-run-day1-continuation-artifacts"
RECOMMENDED_NEXT_VERSION = "v0.6.3.3-forward-dry-run-data-horizon-extension"
DAY1_AS_OF_DATE = "2026-06-25"
LATEST_COMMON_LOCAL_DATA_DATE = "2026-06-25"

V064_EVIDENCE_ARTIFACTS: dict[str, str] = {
    "v064_day2_continuation_preflight": "data/system/forward_dry_run_day2_continuation_preflight_v064.json",
    "v064_day2_continuation_preflight_report": "outputs/audit/FORWARD_DRY_RUN_DAY2_CONTINUATION_PREFLIGHT_V064.md",
    "v064_day2_input_readiness_audit": "data/system/forward_dry_run_day2_input_readiness_audit.json",
    "v064_day2_input_readiness_audit_report": "outputs/audit/FORWARD_DRY_RUN_DAY2_INPUT_READINESS_AUDIT.md",
}

REQUIRED_SYSTEM_ARTIFACTS: dict[str, str] = {
    "forward_dry_run_status": "data/system/forward_dry_run_status.json",
    "day1_blocker_reclassification_v063": "data/system/day1_blocker_reclassification_v063.json",
    "day1_continuation_reclassification_v0631": "data/system/day1_continuation_reclassification_v0631.json",
}

REPORT_ARTIFACTS: dict[str, str] = {
    "owner_summary": "data/forward_dry_run/day_001/reports/day1_owner_summary_report.json",
    "strategy_signal_explanation": "data/forward_dry_run/day_001/reports/day1_strategy_signal_explanation.json",
    "virtual_order_fill_report": "data/forward_dry_run/day_001/reports/day1_virtual_order_fill_report.json",
    "isolated_ledger_report": "data/forward_dry_run/day_001/reports/day1_isolated_ledger_report.json",
    "data_reproducibility_appendix": "data/forward_dry_run/day_001/reports/day1_data_reproducibility_appendix.json",
    "continuation_blocker_note": "data/forward_dry_run/day_001/reports/day1_continuation_blocker_note.json",
    "owner_report_pack_summary": "data/forward_dry_run/day_001/reports/day1_owner_report_pack_summary.json",
}


def report_data_path(paths: ProjectPaths, filename: str) -> Path:
    return paths.data_dir / "forward_dry_run" / "day_001" / "reports" / filename


def report_output_path(paths: ProjectPaths, filename: str) -> Path:
    return paths.outputs_dir / "forward_dry_run" / "day_001" / "reports" / filename


def read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return read_dict(path)


def load_day1_owner_report_context(paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    artifacts = {
        **DAY1_CORE_ARTIFACTS,
        **CONTINUATION_ARTIFACTS,
        **REQUIRED_SYSTEM_ARTIFACTS,
    }
    records = [
        artifact_record(paths, name, relative, required=True, source_role="day1_owner_report_input", blocking_if_missing=True)
        for name, relative in artifacts.items()
    ]
    v064_records = [
        artifact_record(paths, name, relative, required=False, source_role="v064_fail_closed_evidence", blocking_if_missing=False)
        for name, relative in V064_EVIDENCE_ARTIFACTS.items()
    ]
    missing_required = [record["path"] for record in records if not record["exists"]]
    missing_v064 = [record["path"] for record in v064_records if not record["exists"]]
    payloads = {name: read_optional_json(project_path(paths, relative)) for name, relative in artifacts.items() if relative.endswith(".json")}
    v064_payloads = {name: read_optional_json(project_path(paths, relative)) for name, relative in V064_EVIDENCE_ARTIFACTS.items() if relative.endswith(".json")}
    return {
        "paths": paths,
        "records": records,
        "v064_records": v064_records,
        "missing_required": missing_required,
        "missing_v064_evidence": missing_v064,
        "day2_input_readiness_evidence_found": not missing_v064,
        "payloads": payloads,
        "v064_payloads": v064_payloads,
        "core": day1_core_status(paths),
        "day2_executed": day2_executed(paths),
        "day3_executed": day3_executed(paths),
    }


def report_boundary(scope_key: str) -> dict[str, Any]:
    boundary = standard_boundary(scope_key)
    boundary.update(
        {
            "report_generation_only": True,
            "external_api_called": False,
            "real_time_market_data_downloaded": False,
            "main_orders_written": False,
            "main_trades_written": False,
            "main_portfolio_written": False,
            "main_accounts_written": False,
            "real_trading": False,
            "broker_execution": False,
            "ml_trading_approved": False,
            "llm_trading_approved": False,
            "rl_trading_approved": False,
        }
    )
    return boundary


def owner_non_claim_lines() -> list[str]:
    return [
        "- Report generation only.",
        "- Day 2 was not executed.",
        "- Day 3 was not executed.",
        "- run-daily was not called.",
        "- No external market API was called.",
        "- No real-time market data was downloaded.",
        "- Main orders, trades, portfolio, and accounts ledgers were not written.",
        "- No broker is connected.",
        "- No real orders were placed.",
        "- ML, LLM, and RL were not used for trading authorization.",
        "- No promotion was triggered.",
        "- This is not strategy effectiveness proof.",
        "- This is not full forward dry-run validation.",
        "- This is not live trading readiness.",
    ]


def key_numbers(context: dict[str, Any]) -> dict[str, Any]:
    payloads = context["payloads"]
    signals = payloads.get("day1_strategy_signals", {})
    execution = payloads.get("day1_virtual_execution_result", {})
    preview = payloads.get("day1_virtual_order_preview", {})
    status = payloads.get("forward_dry_run_status", {})
    return {
        "strategies_total": signals.get("strategies_total", 0),
        "strategies_generated": signals.get("strategies_generated", 0),
        "virtual_orders_total": len(preview.get("orders", [])),
        "virtual_fills": len(execution.get("fills", [])),
        "virtual_rejects": len(execution.get("rejects", [])),
        "forward_dry_run_days_completed": status.get("forward_dry_run_days_completed", 0),
        "next_day_index": status.get("next_day_index", 0),
    }


def order_side_summary(orders: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(order.get("side", "UNKNOWN")) for order in orders))


def symbol_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol", "UNKNOWN"))
        item = summary.setdefault(symbol, {"orders_or_fills": 0, "quantity": 0, "gross_amount": 0.0, "net_amount": 0.0})
        item["orders_or_fills"] += 1
        item["quantity"] += int(row.get("quantity", 0) or 0)
        item["gross_amount"] = round(float(item["gross_amount"]) + float(row.get("gross_amount", 0.0) or 0.0), 6)
        item["net_amount"] = round(float(item["net_amount"]) + float(row.get("net_amount", row.get("estimated_cost", 0.0)) or 0.0), 6)
    return summary


def main_ledger_written(context: dict[str, Any]) -> bool:
    execution = context["payloads"].get("day1_virtual_execution_result", {})
    writes = execution.get("ledger_writes", {})
    return any(writes.get(key) is True for key in ["main_orders_written", "main_trades_written", "main_portfolio_written", "main_accounts_written"])


def write_report_artifact(paths: ProjectPaths, json_name: str, payload: dict[str, Any], md_name: str, markdown: str) -> dict[str, Any]:
    return write_artifact(report_data_path(paths, json_name), payload, report_output_path(paths, md_name), markdown)


def source_and_artifact_hashes(context: dict[str, Any]) -> dict[str, Any]:
    payloads = context["payloads"]
    manifest = payloads.get("day1_reproducibility_manifest", {})
    return {
        "source_hashes": manifest.get("source_hashes", {}),
        "source_artifact_hashes": manifest.get("source_artifact_hashes", {}),
        "artifact_hashes": manifest.get("artifact_hashes", {}),
        "ledger_hash": manifest.get("ledger_hash") or sha256_path(context["paths"].data_dir / "forward_dry_run" / "ledger" / "day1_ledger.json"),
    }


def build_simple_markdown(title: str, lines: list[str], payload: dict[str, Any]) -> str:
    output = [f"# {title}", "", *lines, "", "## Boundary", *owner_non_claim_lines(), ""]
    if payload.get("warnings"):
        output.extend(["## Warnings", *[f"- {warning}" for warning in payload["warnings"]], ""])
    return "\n".join(output)


def scope_plan_system_paths(paths: ProjectPaths) -> tuple[Path, Path]:
    return (
        system_json(paths, "forward_dry_run_day1_owner_report_scope_plan.json"),
        system_report(paths, "FORWARD_DRY_RUN_DAY1_OWNER_REPORT_SCOPE_PLAN.md"),
    )


def audit_paths(paths: ProjectPaths) -> tuple[Path, Path]:
    return (
        system_json(paths, "forward_dry_run_day1_owner_report_audit.json"),
        audit_report(paths, "FORWARD_DRY_RUN_DAY1_OWNER_REPORT_AUDIT.md"),
    )
