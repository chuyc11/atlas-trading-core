"""Run isolated replay on the authorized full historical proxy package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.global_briefing.historical_data_packages import PROXY_PACKAGE_ID, latest_end_date, write_jsonl
from trading_core.global_briefing.historical_warning_inventory import group_warning_messages
from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.real_package_coverage_audit import audit_global_briefing_package_coverage
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle
from trading_core.global_briefing.replay_evaluation_report import build_global_briefing_replay_report
from trading_core.global_briefing.signal_schema import compact_date
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def run_full_historical_proxy_replay(
    *,
    signals_path: str | None = None,
    prices_path: str | None = None,
    start_date: str = "2018-01-01",
    end_date: str = "latest",
    min_coverage: float = 0.80,
    execution_mode: str = "isolated",
    strict: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    resolved_end_date = latest_end_date(end_date)
    signals = signals_path or str(paths.data_dir / "global_briefing" / "normalized" / f"{PROXY_PACKAGE_ID}.normalized.jsonl")
    prices = prices_path or str(paths.data_dir / "market" / "historical" / "authorized" / "HIST-ETF-OHLCV-CN-HK-V1.csv")
    workflow_id = f"FULL-HISTORICAL-PROXY-WORKFLOW-{compact_date(start_date)}-{compact_date(resolved_end_date)}"
    warnings: list[str] = []
    blocking: list[str] = []
    outputs: dict[str, Any] = {"workflow_id": workflow_id, "signals": signals, "prices": prices}
    signal_file = _resolve_input_path(signals, paths)
    if signal_file is None:
        blocking.append("proxy signal package missing")
        return _write_workflow(outputs, start_date, resolved_end_date, warnings, blocking, paths)
    windowed_signals, windowed_count = _write_windowed_signals(signal_file, start_date, resolved_end_date, paths)
    outputs["windowed_signals"] = windowed_signals
    outputs["windowed_signal_rows"] = windowed_count
    if windowed_count == 0:
        blocking.append("proxy signal package has no rows in requested replay window")
        return _write_workflow(outputs, start_date, resolved_end_date, warnings, blocking, paths)

    validation = validate_global_briefing_signals(windowed_signals, start_date=start_date, end_date=resolved_end_date, paths=paths)
    outputs["validation"] = validation["json_path"]
    warnings.extend(validation["warnings"])
    if not validation["overall_passed"]:
        blocking.extend(validation["blocking_reasons"])
        return _write_workflow(outputs, start_date, resolved_end_date, warnings, blocking, paths)
    coverage = audit_global_briefing_package_coverage(
        windowed_signals,
        prices_path=prices,
        start_date=start_date,
        end_date=resolved_end_date,
        min_coverage=min_coverage,
        strict=strict,
        paths=paths,
    )
    outputs["coverage_audit"] = coverage["json_path"]
    outputs["coverage_ratio"] = coverage["coverage"]["coverage_ratio"]
    warnings.extend(coverage["warnings"])
    if not coverage["overall_passed"]:
        blocking.extend(coverage["blocking_reasons"])
        return _write_workflow(outputs, start_date, resolved_end_date, warnings, blocking, paths)
    try:
        bundle = build_global_briefing_replay_bundle(windowed_signals, prices, start_date=start_date, end_date=resolved_end_date, allow_carry_forward=True, paths=paths)
        outputs["bundle"] = bundle["json_path"]
        replay = replay_global_briefing_history(bundle["json_path"], prices, start_date=start_date, end_date=resolved_end_date, execution_mode=execution_mode, paths=paths)
        outputs["replay"] = replay["json_path"]
        outputs["execution"] = replay["execution"]
        warnings.extend(replay["warnings"])
        evaluation = build_global_briefing_replay_report(replay["json_path"], bundle_path=bundle["json_path"], validation_path=validation["json_path"], paths=paths)
        outputs["evaluation"] = evaluation["json_path"]
        warnings.extend(evaluation["warnings"])
        if evaluation["overall_status"] != "research_review_ready":
            blocking.extend(evaluation["blocking_reasons"])
    except ValueError as exc:
        blocking.append(str(exc))
    return _write_workflow(outputs, start_date, resolved_end_date, warnings, blocking, paths)


def _resolve_input_path(raw_path: str, paths: ProjectPaths) -> Path | None:
    path = Path(raw_path)
    candidates = [path] if path.is_absolute() else [paths.project_root / path, path]
    return next((candidate for candidate in candidates if candidate.exists()), None)


def _write_windowed_signals(signal_file: Path, start_date: str, end_date: str, paths: ProjectPaths) -> tuple[str, int]:
    rows = []
    for line in signal_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        as_of = str(row.get("as_of_date") or "")
        if start_date <= as_of <= end_date:
            rows.append(row)
    output = paths.data_dir / "replays" / "global_briefing" / f"full_historical_proxy_signals-{start_date}-{end_date}.jsonl"
    write_jsonl(output, rows)
    return str(output), len(rows)


def _write_workflow(outputs: dict[str, Any], start_date: str, end_date: str, warnings: list[str], blocking: list[str], paths: ProjectPaths) -> dict[str, Any]:
    grouped_warnings = group_warning_messages(warnings)
    warning_summaries = [f"{item['category']}: {item['message_pattern']} ({item['raw_count']})" for item in grouped_warnings]
    payload = {
        **outputs,
        "start_date": start_date,
        "end_date": end_date,
        "overall_status": "research_review_ready" if not blocking else "needs_attention",
        "blocking_reasons": blocking,
        "warnings": warning_summaries,
        "raw_warnings_sample": warnings[:25],
        "raw_warning_count": len(warnings),
        "grouped_warning_count": len(grouped_warnings),
        "grouped_warnings": grouped_warnings,
        "boundary": {
            "full_historical_proxy_workflow_only": True,
            "proxy_signals_not_internal_global_briefing": True,
            "historical_replay_only": True,
            "forward_dry_run_started": False,
            "forward_dry_run_validated": False,
            "strategy_effectiveness_proven": False,
            "live_trading_ready": False,
            "main_ledger_written": False,
            "isolated_replay_ledger_written": "replay" in outputs,
            "run_daily_called": False,
            "labels_used": False,
            "ml_shadow_used": False,
            "experiments_used": False,
            "promotion_triggered": False,
        },
    }
    json_path = paths.data_dir / "replays" / "global_briefing" / f"full_historical_proxy_workflow-{start_date}-{end_date}.json"
    md_path = paths.outputs_dir / "replays" / "global_briefing" / f"FULL_HISTORICAL_PROXY_WORKFLOW-{start_date}-{end_date}.md"
    write_json_markdown(json_path, payload, md_path, build_proxy_workflow_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(md_path)}


def build_proxy_workflow_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Full Historical Proxy Workflow",
            "",
            "## Scope",
            "Proxy signals are not internal global-briefing signals.",
            "Historical data authorization is not trading authorization.",
            "This workflow is historical replay only.",
            "",
            "## Overall Status",
            f"- overall_status={payload['overall_status']}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            f"- raw_warning_count={payload.get('raw_warning_count')}",
            f"- grouped_warning_count={payload.get('grouped_warning_count')}",
            "",
            "## Outputs",
            *[f"- {key}: {value}" for key, value in payload.items() if key in {"windowed_signals", "validation", "coverage_audit", "bundle", "replay", "evaluation"}],
            "",
            "## Grouped Warnings",
            *([f"- {item['category']} severity={item['severity']} raw_count={item['raw_count']} pattern={item['message_pattern']}" for item in payload.get("grouped_warnings", [])] if payload.get("grouped_warnings") else ["- none"]),
            "",
            "## Boundary",
            "- historical replay only",
            "- proxy signals are not internal global-briefing signals",
            "- not forward dry-run validation",
            "- not strategy effectiveness proof",
            "- not live trading readiness",
            "- main ledger not written",
            "- run-daily not called",
            "",
        ]
    )
