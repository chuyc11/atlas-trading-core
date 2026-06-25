"""Execution timeline contract artifact."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import HARDENING_NOTICE, paths_or_default, standard_boundary
from trading_core.execution.t_plus_1_semantics import validate_execution_timeline
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import timestamp_id, write_json_markdown


def build_execution_timeline_contract(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    contract_id, created_at = timestamp_id("EXECUTION-TIMELINE-CONTRACT")
    examples = {
        "valid_t_plus_1": validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T15:30:00", execution_date="2024-01-03", execution_market="SSE", price_date="2024-01-03"),
        "same_day_rejected": validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T15:30:00", execution_date="2024-01-02", execution_market="SSE", price_date="2024-01-02"),
        "future_price_rejected": validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T15:30:00", execution_date="2024-01-03", execution_market="SSE", price_date="2024-01-04"),
        "early_generated_warning": validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T14:59:00", execution_date="2024-01-03", execution_market="SSE", price_date="2024-01-03"),
        "hkex_independent_calendar": validate_execution_timeline(signal_date="2024-06-28", generated_at="2024-06-28T16:30:00", execution_date="2024-07-02", execution_market="HKEX", price_date="2024-07-02"),
    }
    payload: dict[str, Any] = {
        "contract_id": contract_id,
        "created_at": created_at,
        "rules": {
            "same_day_execution_for_close_signal_allowed": False,
            "execution_date_min_rule": "next_trading_day",
            "future_price_allowed": False,
            "generated_at_must_be_after_market_close": True,
            "market_calendar_independent": True,
        },
        "examples": examples,
        "same_day_close_signal_execution_rejected": examples["same_day_rejected"]["accepted"] is False,
        "future_price_rejected": examples["future_price_rejected"]["accepted"] is False,
        "boundary": standard_boundary("timeline_contract_only"),
    }
    json_path = paths.data_dir / "system" / "execution_timeline_contract.json"
    md_path = paths.outputs_dir / "system" / "EXECUTION_TIMELINE_CONTRACT.md"
    write_json_markdown(json_path, payload, md_path, build_execution_timeline_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_execution_timeline_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Execution Timeline Contract", "", "## Scope", "This contract defines T-day close signal and T+1 execution semantics.", HARDENING_NOTICE, "", "## Rules"]
    lines.extend(f"- {key}: {value}" for key, value in payload["rules"].items())
    lines.extend(["", "## Boundary", "- timeline contract only", "- run-daily not called", "- forward dry-run not started", "- main ledger not written", ""])
    return "\n".join(lines)

