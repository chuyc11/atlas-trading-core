"""Global-briefing historical replay evaluation report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.global_briefing.signal_schema import compact_date, resolve_project_path
from trading_core.storage.file_paths import ProjectPaths
from trading_core.storage.jsonl_store import read_json, read_jsonl
from trading_core.system.common import default_paths, write_json_markdown


def build_global_briefing_replay_report(
    replay_path: str,
    *,
    bundle_path: str | None = None,
    validation_path: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    blocking: list[str] = []
    warnings: list[str] = []
    replay_file = resolve_project_path(replay_path, paths)
    replay = read_json(replay_file, default=None)
    if replay is None:
        blocking.append(f"missing replay artifact: {replay_file}")
        replay = {}
    if not isinstance(replay, dict):
        blocking.append("replay artifact is not a JSON object")
        replay = {}

    bundle = _optional_json(bundle_path, paths, warnings)
    validation = _optional_json(validation_path, paths, warnings)
    integrity = _integrity_from_replay(replay)
    execution = _execution_from_replay(replay, paths, blocking, warnings)
    for key in ["main_ledger_written", "run_daily_called", "labels_used", "ml_shadow_used", "experiments_used"]:
        if integrity[key]:
            blocking.append(f"integrity failure: {key}=true")
    if replay and replay.get("isolated") is not True:
        blocking.append("integrity failure: isolated replay is not true")

    start_date = str(replay.get("start_date") or "unknown")
    end_date = str(replay.get("end_date") or "unknown")
    evaluation_id = f"GB-REPLAY-EVAL-{compact_date(start_date) if start_date != 'unknown' else 'UNKNOWN'}-{compact_date(end_date) if end_date != 'unknown' else 'UNKNOWN'}"
    replay_days = int(replay.get("summary", {}).get("replay_days", 0) or 0)
    days_processed = int(replay.get("summary", {}).get("days_processed", 0) or 0)
    signal_ratio = _signal_coverage_ratio(bundle, replay)
    price_ratio = (days_processed / replay_days) if replay_days else None
    if validation and validation.get("overall_passed") is False:
        blocking.append("validation artifact did not pass")

    payload: dict[str, Any] = {
        "evaluation_id": evaluation_id,
        "overall_status": "research_review_ready" if not blocking else "blocked",
        "blocking_reasons": blocking,
        "warnings": warnings + list(replay.get("warnings", [])),
        "inputs": {
            "replay": str(replay_file),
            "bundle": str(resolve_project_path(bundle_path, paths)) if bundle_path else None,
            "validation": str(resolve_project_path(validation_path, paths)) if validation_path else None,
        },
        "coverage": {
            "replay_days": replay_days,
            "days_processed": days_processed,
            "signal_coverage_ratio": signal_ratio,
            "price_coverage_ratio": price_ratio,
            "missing_signal_days": replay.get("data_quality", {}).get("missing_signal_days", []),
            "missing_price_days": replay.get("data_quality", {}).get("missing_price_days", []),
        },
        "execution": execution,
        "integrity": integrity,
        "isolated_output_paths": replay.get("isolated_outputs") or replay.get("isolated_output_paths", {}),
        "boundary": {
            "research_review_only": True,
            "strategy_effectiveness_proven": False,
            "forward_dry_run_validated": False,
            "live_trading_ready": False,
            "admission_gate": False,
        },
    }
    suffix = f"{start_date}-{end_date}" if start_date != "unknown" and end_date != "unknown" else "unknown"
    json_path = paths.data_dir / "replays" / "global_briefing" / f"global_briefing_replay_evaluation-{suffix}.json"
    report_path = paths.outputs_dir / "replays" / "global_briefing" / f"GLOBAL_BRIEFING_REPLAY_EVALUATION-{suffix}.md"
    write_json_markdown(json_path, payload, report_path, build_evaluation_markdown(payload))
    return {**payload, "json_path": str(json_path), "report_path": str(report_path)}


def _optional_json(path_text: str | None, paths: ProjectPaths, warnings: list[str]) -> dict[str, Any] | None:
    if not path_text:
        return None
    path = resolve_project_path(path_text, paths)
    payload = read_json(path, default=None)
    if payload is None:
        warnings.append(f"optional artifact missing: {path}")
        return None
    if not isinstance(payload, dict):
        warnings.append(f"optional artifact is not an object: {path}")
        return None
    return payload


def _integrity_from_replay(replay: dict[str, Any]) -> dict[str, Any]:
    boundary = replay.get("boundary", {}) if isinstance(replay.get("boundary"), dict) else {}
    execution = replay.get("execution", {}) if isinstance(replay.get("execution"), dict) else {}
    outputs = replay.get("isolated_outputs") or replay.get("isolated_output_paths") or {}
    valuations = _read_jsonl_safely(outputs.get("valuations")) if isinstance(outputs, dict) else []
    account = read_json(Path(outputs.get("account")), default={}) if isinstance(outputs, dict) and outputs.get("account") else {}
    processed_days = int(replay.get("summary", {}).get("days_processed", 0) or 0)
    positions_negative = _positions_negative(valuations) or _positions_negative([account] if isinstance(account, dict) else [])
    cash_negative = any(float(row.get("cash", 0.0)) < -0.000001 for row in valuations if isinstance(row, dict))
    if isinstance(account, dict) and float(account.get("cash", 0.0)) < -0.000001:
        cash_negative = True
    valuation_days_match = bool(processed_days == len(valuations)) if processed_days else False
    isolated_outputs_present = isinstance(outputs, dict) and all(Path(str(outputs.get(key, ""))).exists() for key in ["account", "orders", "trades", "portfolio", "valuations", "signals"])
    return {
        "isolated_ledger_complete": isolated_outputs_present,
        "valuation_days_match_processed_days": valuation_days_match,
        "cash_negative": cash_negative,
        "positions_negative": positions_negative,
        "main_ledger_written": bool(boundary.get("main_ledger_written")),
        "isolated_replay": replay.get("isolated") is True,
        "run_daily_called": bool(boundary.get("run_daily_called")),
        "labels_used": bool(boundary.get("labels_used")),
        "ml_shadow_used": bool(boundary.get("ml_shadow_used")),
        "experiments_used": bool(boundary.get("experiments_used")),
    }


def _execution_from_replay(
    replay: dict[str, Any],
    paths: ProjectPaths,
    blocking: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    execution = replay.get("execution", {}) if isinstance(replay.get("execution"), dict) else {}
    outputs = replay.get("isolated_outputs") or replay.get("isolated_output_paths") or {}
    summary = replay.get("summary", {}) if isinstance(replay.get("summary"), dict) else {}
    mode = execution.get("mode")
    no_trade_fallback = bool(execution.get("no_trade_fallback"))
    if no_trade_fallback:
        warnings.append("no_trade_fallback=true; isolated execution adapter did not replace fallback")
    if mode != "isolated":
        warnings.append(f"execution mode is {mode!r}, not isolated")
    isolated_outputs_present = isinstance(outputs, dict) and all(Path(str(outputs.get(key, ""))).exists() for key in ["account", "orders", "trades", "portfolio", "valuations", "signals"])
    if not isolated_outputs_present:
        blocking.append("isolated outputs are missing or incomplete")
    valuations = _read_jsonl_safely(outputs.get("valuations")) if isinstance(outputs, dict) else []
    processed_days = int(summary.get("days_processed", 0) or 0)
    if processed_days and len(valuations) != processed_days:
        blocking.append("valuation days do not match processed days")
    if _cash_negative(outputs):
        blocking.append("negative cash detected in isolated ledger")
    if _positions_negative(valuations):
        blocking.append("negative positions detected in isolated ledger")
    return {
        "mode": mode,
        "no_trade_fallback": no_trade_fallback,
        "orders": int(summary.get("orders", 0) or 0),
        "trades": int(summary.get("trades", 0) or 0),
        "valuations": int(summary.get("valuations", 0) or 0),
        "isolated_outputs_present": isolated_outputs_present,
    }


def _signal_coverage_ratio(bundle: dict[str, Any] | None, replay: dict[str, Any]) -> float | None:
    if bundle and isinstance(bundle.get("coverage"), dict):
        replay_days = bundle["coverage"].get("replay_days")
        days_with_signal = bundle["coverage"].get("days_with_signal")
        if replay_days:
            return float(days_with_signal) / float(replay_days)
    summary = replay.get("summary", {}) if isinstance(replay.get("summary"), dict) else {}
    replay_days = summary.get("replay_days")
    missing_signal_days = replay.get("data_quality", {}).get("missing_signal_days", [])
    if replay_days:
        return (float(replay_days) - float(len(missing_signal_days))) / float(replay_days)
    return None


def _read_jsonl_safely(path_text: str | None) -> list[dict[str, Any]]:
    if not path_text:
        return []
    path = Path(path_text)
    if not path.exists():
        return []
    try:
        return read_jsonl(path)
    except ValueError:
        return []


def _cash_negative(outputs: dict[str, Any]) -> bool:
    if not isinstance(outputs, dict):
        return False
    rows = _read_jsonl_safely(outputs.get("valuations"))
    account = read_json(Path(outputs.get("account")), default={}) if outputs.get("account") else {}
    values = [float(row.get("cash", 0.0)) for row in rows if isinstance(row, dict)]
    if isinstance(account, dict):
        values.append(float(account.get("cash", 0.0)))
    return any(value < -0.000001 for value in values)


def _positions_negative(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        for position in row.get("positions", []) if isinstance(row, dict) else []:
            try:
                if int(position.get("quantity", 0)) < 0:
                    return True
            except (TypeError, ValueError):
                return True
    return False


def build_evaluation_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Global Briefing Replay Evaluation",
            "",
            "## Verdict",
            f"- overall_status={payload['overall_status']}",
            f"- blocking_reasons={payload['blocking_reasons']}",
            "",
            "## Coverage",
            f"- replay_days={payload['coverage']['replay_days']}",
            f"- days_processed={payload['coverage']['days_processed']}",
            f"- signal_coverage_ratio={payload['coverage']['signal_coverage_ratio']}",
            f"- price_coverage_ratio={payload['coverage']['price_coverage_ratio']}",
            "",
            "## Replay Integrity",
            *[f"- {key}={str(value).lower()}" for key, value in payload["integrity"].items()],
            "",
            "## Isolated Execution Review",
            f"- execution mode={payload['execution']['mode']}",
            f"- no_trade_fallback={str(payload['execution']['no_trade_fallback']).lower()}",
            f"- isolated outputs={str(payload['execution']['isolated_outputs_present']).lower()}",
            f"- valuation coverage={str(payload['integrity']['valuation_days_match_processed_days']).lower()}",
            "",
            "## Boundary",
            "- research review only",
            "- main ledger not written",
            "- run-daily not called",
            "- labels not used",
            "- ML shadow not used",
            "- experiments not used",
            "",
            "## Limitations",
            "- This isolated replay does not prove strategy effectiveness.",
            "- This isolated replay is not forward dry-run validation.",
            "- This isolated replay is not live trading readiness.",
            "- This evaluation is not an admission gate.",
            "",
        ]
    )
