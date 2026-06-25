"""Inventory and group historical data and replay warnings."""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import TRADING_AUTHORIZATION_NOTICE
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json
from trading_core.system.common import default_paths, timestamp_id, write_json_markdown


CATEGORIES = {
    "missing_optional_package",
    "missing_critical_package",
    "source_download_failed",
    "coverage_gap",
    "data_quality",
    "pit_ambiguity",
    "future_leakage",
    "stale_monthly_carry_forward",
    "missing_signal_component",
    "missing_price",
    "skipped_trade",
    "lot_size_constraint",
    "cash_constraint",
    "adapter_limitation",
    "documentation_only",
    "unknown",
}


def build_historical_warning_inventory(
    *,
    quality_audit_path: str | None = None,
    workflow_path: str | None = None,
    download_manifest_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    inventory_id, created_at = timestamp_id("HIST-WARNING-INVENTORY")
    quality_file = _resolve(quality_audit_path, paths.data_dir / "system" / "historical_data_quality_audit.json", paths)
    workflow_file = _resolve_latest(workflow_path, paths.data_dir / "replays" / "global_briefing", "full_historical_proxy_workflow-*.json", paths)
    manifest_file = _resolve(download_manifest_path, paths.data_dir / "system" / "historical_data_download_manifest.json", paths)
    quality = _read(quality_file)
    workflow = _read(workflow_file) if workflow_file else {}
    manifest = _read(manifest_file)
    quality_warnings = list(quality.get("warnings", []))
    has_grouped_workflow_warnings = isinstance(workflow.get("grouped_warnings"), list)
    workflow_warnings = [] if has_grouped_workflow_warnings else list(workflow.get("raw_warnings") or workflow.get("warnings", []))
    warning_items = [{"source": "quality_audit", "message": item} for item in quality_warnings]
    warning_items.extend({"source": "proxy_replay_workflow", "message": item} for item in workflow_warnings)
    groups = group_warning_messages([item["message"] for item in warning_items], manifest=manifest)
    if has_grouped_workflow_warnings:
        groups.extend(_from_existing_groups(workflow["grouped_warnings"]))
    raw_warning_count = len(quality_warnings) + int(workflow.get("raw_warning_count", len(workflow_warnings)))
    by_category = Counter(group["category"] for group in groups)
    by_severity = Counter(group["severity"] for group in groups)
    unknown_warning_count = by_category.get("unknown", 0)
    payload: dict[str, Any] = {
        "inventory_id": inventory_id,
        "created_at": created_at,
        "quality_audit": str(quality_file),
        "workflow": str(workflow_file) if workflow_file else None,
        "download_manifest": str(manifest_file),
        "raw_warning_count": raw_warning_count,
        "grouped_warning_count": len(groups),
        "unknown_warning_count": unknown_warning_count,
        "by_category": {category: by_category.get(category, 0) for category in sorted(CATEGORIES)},
        "by_severity": {severity: by_severity.get(severity, 0) for severity in ["low", "medium", "high"]},
        "top_groups": groups[:20],
        "fixable_now": [group for group in groups if group["fix_status"] == "fixable_now"],
        "requires_external_source": [group for group in groups if group["fix_status"] == "requires_external_source"],
        "accepted_limitations": [group for group in groups if group["fix_status"] == "accepted_limitation"],
        "production_blockers": [group for group in groups if group["severity"] == "high" and group["category"] in {"future_leakage", "missing_critical_package"}],
        "boundary": {
            "inventory_only": True,
            "main_ledger_written": False,
            "run_daily_called": False,
            "forward_dry_run_started": False,
            "trading_authorization": False,
        },
    }
    json_path = paths.data_dir / "system" / "historical_warning_inventory.json"
    md_path = paths.outputs_dir / "system" / "HISTORICAL_WARNING_INVENTORY.md"
    write_json_markdown(json_path, payload, md_path, build_warning_inventory_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def group_warning_messages(messages: list[str], *, manifest: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for raw in messages:
        expanded = _expand_warning(raw)
        for message, count in expanded:
            category, severity, pattern, fix_status, affected_package, action = _classify(message, manifest or {})
            key = (category, pattern, affected_package or "")
            group = grouped.setdefault(
                key,
                {
                    "category": category,
                    "severity": severity,
                    "raw_count": 0,
                    "message_pattern": pattern,
                    "affected_package": affected_package,
                    "first_seen_date": None,
                    "last_seen_date": None,
                    "affected_symbols": [],
                    "affected_components": [],
                    "recommended_action": action,
                    "fix_status": fix_status,
                },
            )
            group["raw_count"] += count
            day = _extract_date(message)
            if day:
                group["first_seen_date"] = min(filter(None, [group["first_seen_date"], day]), default=day)
                group["last_seen_date"] = max(filter(None, [group["last_seen_date"], day]), default=day)
            symbol = _extract_symbol(message)
            if symbol and symbol not in group["affected_symbols"]:
                group["affected_symbols"].append(symbol)
            component = _extract_component(message)
            if component and component not in group["affected_components"]:
                group["affected_components"].append(component)
    return sorted(grouped.values(), key=lambda item: (-int(item["raw_count"]), item["category"], item["message_pattern"]))


def _from_existing_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for group in groups:
        if not isinstance(group, dict):
            continue
        category = str(group.get("category") or "unknown")
        if category not in CATEGORIES:
            category = "unknown"
        output.append(
            {
                "category": category,
                "severity": group.get("severity") or "medium",
                "raw_count": int(group.get("raw_count") or 0),
                "message_pattern": group.get("message_pattern") or category,
                "affected_package": group.get("affected_package"),
                "first_seen_date": group.get("first_seen_date"),
                "last_seen_date": group.get("last_seen_date"),
                "affected_symbols": group.get("affected_symbols") or [],
                "affected_components": group.get("affected_components") or [],
                "recommended_action": group.get("recommended_action") or "review grouped replay warning",
                "fix_status": group.get("fix_status") or "accepted_limitation",
            }
        )
    return output


def _expand_warning(message: str) -> list[tuple[str, int]]:
    if "missing signal dates:" in message:
        try:
            raw_list = message.split("missing signal dates:", 1)[1].strip()
            dates = ast.literal_eval(raw_list)
            if isinstance(dates, list):
                return [("missing signal dates", len(dates))]
        except (SyntaxError, ValueError):
            return [(message, 1)]
    return [(message, 1)]


def _classify(message: str, manifest: dict[str, Any]) -> tuple[str, str, str, str, str | None, str]:
    lowered = message.lower()
    if lowered.startswith("coverage_gap:") or "coverage gap" in lowered:
        return "coverage_gap", "medium", "coverage gap in replay calendar or price-aligned dates", "accepted_limitation", None, "review calendar and expected trading-day basis"
    if lowered.startswith("missing_price:") or "missing replay price" in lowered or "missing price" in lowered or "missing valuation price" in lowered:
        return "missing_price", "high", "missing replay price for symbol", "fixable_now", None, "fill historical price gap or reduce replay universe"
    if lowered.startswith("lot_size_constraint:") or "target delta below lot size" in lowered:
        return "lot_size_constraint", "medium", "target delta below lot size", "accepted_limitation", None, "review lot size and target-weight settings"
    if "no future" in lowered or "future_signal_used" in lowered:
        return "documentation_only", "low", "future-data boundary statement", "accepted_limitation", None, "no data action required"
    if "future leakage" in lowered or ("future" in lowered and "warning" in lowered):
        return "future_leakage", "high", "future leakage or future data warning", "fixable_now", None, "block release and fix point-in-time handling"
    if "critical" in lowered and "unavailable" in lowered:
        return "missing_critical_package", "high", "critical package unavailable", "fixable_now", _package_from_text(message), "restore critical package before release"
    if "policy_uncertainty" in lowered or "epu" in lowered:
        return "missing_signal_component", "medium", "policy uncertainty / EPU component unavailable or proxied", "accepted_limitation", "HIST-POLICY-UNCERTAINTY-EPU-V1", "review EPU source configuration or accept proxy limitation"
    if "oecd" in lowered or "macro_cycle" in lowered:
        return "missing_signal_component", "medium", "OECD CLI / macro-cycle component unavailable or proxied", "accepted_limitation", "HIST-OECD-CLI-MACRO-CYCLE-V1", "review OECD source configuration or accept macro-cycle proxy"
    if "download failed" in lowered or "unavailable" in lowered or "no fred rows" in lowered:
        return "source_download_failed", "medium", _source_pattern(message), "requires_external_source", _package_from_text(message), "use configured authorized/local source or documented fallback"
    if "missing signal dates" in lowered or "coverage ratio" in lowered:
        return "coverage_gap", "medium", "coverage gap in replay calendar or price-aligned dates", "accepted_limitation", None, "review calendar and expected trading-day basis"
    if "unknown signal fields ignored" in lowered:
        return "adapter_limitation", "low", "adapter ignored non-trading macro fields", "fixable_now", None, "add known macro fields or keep grouped as adapter limitation"
    if "cash-only replay target" in lowered or "no order generated" in lowered:
        return "skipped_trade", "low", "trade skipped by replay constraints", "accepted_limitation", None, "review replay constraints only if unexpected"
    if "cash" in lowered and "constraint" in lowered:
        return "cash_constraint", "medium", "cash constraint warning", "accepted_limitation", None, "review cash and sizing settings"
    if "fixture source used for tests" in lowered:
        return "documentation_only", "low", "fixture source used for tests", "accepted_limitation", _package_from_text(message), "no production data action required"
    if "package status explained" in lowered or "not configured" in lowered:
        return "missing_optional_package", "medium", "optional package status explained", "accepted_limitation", _package_from_text(message), "configure optional source if production validation is required"
    if "documentation" in lowered:
        return "documentation_only", "low", "documentation-only warning", "accepted_limitation", None, "no data action required"
    return "unknown", "medium", _normalize_pattern(message), "fixable_now", _package_from_text(message), "triage unknown warning pattern"


def _source_pattern(message: str) -> str:
    if "fred" in message.lower():
        return "FRED source unavailable or timed out"
    return _normalize_pattern(message)


def _package_from_text(message: str) -> str | None:
    match = re.search(r"(HIST-[A-Z0-9-]+-V1)", message)
    return match.group(1) if match else None


def _extract_date(message: str) -> str | None:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", message)
    return match.group(1) if match else None


def _extract_symbol(message: str) -> str | None:
    match = re.search(r"for ([0-9A-Z.]+)", message)
    return match.group(1) if match else None


def _extract_component(message: str) -> str | None:
    lowered = message.lower()
    for component in ["policy_uncertainty", "macro_cycle_pressure", "epu", "oecd", "vix", "fx"]:
        if component in lowered:
            return component
    return None


def _normalize_pattern(message: str) -> str:
    return re.sub(r"20\d{2}-\d{2}-\d{2}", "DATE", message)[:180]


def _resolve(path_text: str | None, default: Path, paths: ProjectPaths) -> Path:
    if not path_text:
        return default
    path = Path(path_text)
    return path if path.is_absolute() else paths.project_root / path


def _resolve_latest(path_text: str | None, directory: Path, pattern: str, paths: ProjectPaths) -> Path | None:
    if path_text:
        path = Path(path_text)
        return path if path.is_absolute() else paths.project_root / path
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(pattern), key=lambda item: (item.stat().st_mtime_ns, item.name))
    return candidates[-1] if candidates else None


def _read(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def build_warning_inventory_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Historical Warning Inventory",
            "",
            "## Scope",
            "This report groups warnings from v0.5.7 historical data quality and proxy replay artifacts.",
            TRADING_AUTHORIZATION_NOTICE,
            "",
            "## Raw Warning Count",
            f"- {payload['raw_warning_count']}",
            "",
            "## Grouped Warning Count",
            f"- {payload['grouped_warning_count']}",
            "",
            "## Categories",
            *[f"- {key}: {value}" for key, value in payload["by_category"].items() if value],
            "",
            "## Top Warning Groups",
            *[f"- {item['category']} severity={item['severity']} raw_count={item['raw_count']} pattern={item['message_pattern']}" for item in payload["top_groups"]],
            "",
            "## Fix Plan",
            *[f"- {item['category']}: {item['recommended_action']}" for item in payload["top_groups"]],
            "",
            "## Boundary",
            "- inventory only",
            "- no run-daily call",
            "- no main ledger write",
            "- not forward dry-run",
            "- not strategy effectiveness proof",
            "",
        ]
    )
