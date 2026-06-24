"""Real-data validation report assembly for v0.2 release candidates."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths, project_paths
from trading_core.storage.jsonl_store import read_json, write_json


def build_real_data_validation_report(
    artifact_dir: Path | str,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    artifact_path = _resolve_artifact_dir(artifact_dir, paths)
    batch_config = _read_json(artifact_path / "batch_config.json")
    data_validation = _read_json(artifact_path / "data_validation.json")
    strategy_results = _read_json(artifact_path / "strategy_results.json")
    benchmark_results = _read_json(artifact_path / "benchmark_results.json")
    admission_results = _read_json(artifact_path / "admission_results.json")
    leaderboard = _read_json(artifact_path / "leaderboard.json")
    start_date = str(batch_config.get("start_date") or _first_strategy_value(strategy_results, "start_date") or "")
    end_date = str(batch_config.get("end_date") or _first_strategy_value(strategy_results, "end_date") or "")
    manifest = _load_price_manifest(data_validation, batch_config, paths)
    consistency = _load_backtest_consistency(start_date, end_date, paths)
    git = _git_context(paths.project_root)

    warnings: list[str] = []
    limitations: list[str] = [
        "no live trading",
        "no broker connection",
        "no ML/RL/LLM decisioning",
    ]
    symbols_failed = list(manifest.get("symbols_failed", [])) if isinstance(manifest, dict) else []
    source_by_symbol = manifest.get("source_by_symbol", {}) if isinstance(manifest, dict) else {}
    fallback_source = manifest.get("fallback_source", {}) if isinstance(manifest, dict) else {}
    if _only_fallback_source(source_by_symbol):
        warnings.append("all downloaded historical prices came from yfinance fallback; research-only validation")
        limitations.append("yfinance fallback research-only")
    if source_by_symbol and not any(source == "akshare" for source in source_by_symbol.values()):
        limitations.append("no primary AKShare success")
    if data_validation.get("suspicious_return_count", 0):
        limitations.append(f"suspicious returns recorded: {data_validation.get('suspicious_return_count')}")
    if data_validation.get("warnings"):
        warnings.extend(str(item) for item in data_validation.get("warnings", []))
    if manifest.get("warnings"):
        warnings.extend(str(item) for item in manifest.get("warnings", []))

    blocking_reasons = _blocking_reasons(data_validation, consistency, symbols_failed)
    strategy_rows = _strategy_rows(strategy_results, admission_results)
    summary = {
        "artifact_dir": str(artifact_path),
        "git_commit": git["commit"],
        "git_tags": git["tags"],
        "price_source": {
            "source_by_symbol": source_by_symbol,
            "fallback_source": fallback_source,
            "symbols_success": list(manifest.get("symbols_success", [])) if isinstance(manifest, dict) else [],
            "symbols_failed": symbols_failed,
        },
        "data_quality": {
            "passed": data_validation.get("passed"),
            "rows": data_validation.get("total_rows", 0),
            "symbols": data_validation.get("symbols_count", 0),
            "date_range": data_validation.get("date_range", {}),
            "ohlc_anomalies": data_validation.get("ohlc_anomaly_count", 0),
            "suspicious_returns": data_validation.get("suspicious_return_count", 0),
            "discarded_rows": _discarded_rows(manifest),
        },
        "backtest": {
            "start_date": start_date,
            "end_date": end_date,
            "strategies": list(strategy_results.keys()) if isinstance(strategy_results, dict) else [],
            "benchmarks": _benchmark_ids(benchmark_results),
        },
        "strategy_results": strategy_rows,
        "consistency": {
            "passed": consistency.get("passed"),
            "warnings": consistency.get("warnings", []),
            "critical_errors": consistency.get("critical_errors", []),
            "report_path": consistency.get("report_path"),
        },
        "leaderboard": leaderboard,
        "admission_all_rejected": _admission_all_rejected(admission_results),
        "warnings": sorted(set(warnings)),
        "limitations": sorted(set(limitations)),
        "release_candidate_passed": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
    }

    output_dir = paths.outputs_dir / "validation"
    report_path = output_dir / "REAL_DATA_VALIDATION_REPORT.md"
    json_path = output_dir / "real_data_validation_summary.json"
    write_json(json_path, summary)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_markdown_report(summary), encoding="utf-8")
    summary["json_path"] = str(json_path)
    summary["report_path"] = str(report_path)
    write_json(json_path, summary)
    return summary


def _resolve_artifact_dir(artifact_dir: Path | str, paths: ProjectPaths) -> Path:
    path = Path(artifact_dir)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return (paths.project_root / path).resolve() if not path.exists() else path.resolve()


def _read_json(path: Path) -> dict[str, Any]:
    payload = read_json(path, default={})
    return payload if isinstance(payload, dict) else {}


def _first_strategy_value(strategy_results: dict[str, Any], key: str) -> Any:
    if not isinstance(strategy_results, dict):
        return None
    for row in strategy_results.values():
        if isinstance(row, dict) and row.get(key) is not None:
            return row[key]
    return None


def _load_price_manifest(
    data_validation: dict[str, Any],
    batch_config: dict[str, Any],
    paths: ProjectPaths,
) -> dict[str, Any]:
    candidates = []
    for raw in [data_validation.get("input_path"), batch_config.get("data")]:
        if raw:
            input_path = _resolve_input_path(str(raw), paths)
            candidates.extend([input_path / "manifest.json", input_path / "merge_manifest.json"])
    for candidate in candidates:
        payload = read_json(candidate, default=None)
        if isinstance(payload, dict):
            return payload
    return {}


def _resolve_input_path(raw: str, paths: ProjectPaths) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return paths.project_root / path


def _load_backtest_consistency(start_date: str, end_date: str, paths: ProjectPaths) -> dict[str, Any]:
    if not start_date or not end_date:
        return {"passed": False, "critical_errors": ["missing backtest date range"], "warnings": []}
    path = paths.data_dir / "evaluation" / f"backtest_consistency-{start_date}-{end_date}.json"
    payload = read_json(path, default={})
    if isinstance(payload, dict) and payload:
        return payload
    return {"passed": False, "critical_errors": [f"missing backtest consistency output: {path}"], "warnings": []}


def _git_context(project_root: Path) -> dict[str, Any]:
    return {
        "commit": _git(project_root, ["rev-parse", "HEAD"]) or "unknown",
        "tags": (_git(project_root, ["tag", "--points-at", "HEAD"]) or "").splitlines(),
    }


def _git(project_root: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _only_fallback_source(source_by_symbol: dict[str, Any]) -> bool:
    values = {str(value) for value in source_by_symbol.values()}
    return bool(values) and values == {"yfinance"}


def _discarded_rows(manifest: dict[str, Any]) -> int:
    if manifest.get("discarded_records_count") is not None:
        return int(manifest.get("discarded_records_count", 0))
    warnings = manifest.get("warnings", [])
    return sum(1 for warning in warnings if "dropped invalid" in str(warning))


def _blocking_reasons(
    data_validation: dict[str, Any],
    consistency: dict[str, Any],
    symbols_failed: list[str],
) -> list[str]:
    reasons = []
    if data_validation.get("passed") is not True:
        reasons.append("data_validation_failed")
    if consistency.get("passed") is not True:
        reasons.append("backtest_consistency_failed")
    if symbols_failed:
        reasons.append("symbols_failed")
    return reasons


def _strategy_rows(strategy_results: dict[str, Any], admission_results: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    if not isinstance(strategy_results, dict):
        return rows
    for strategy_id, result in strategy_results.items():
        if not isinstance(result, dict):
            continue
        admission = admission_results.get(strategy_id, {}) if isinstance(admission_results, dict) else {}
        rows.append(
            {
                "strategy_id": strategy_id,
                "cumulative_return": result.get("cumulative_return"),
                "max_drawdown": result.get("max_drawdown"),
                "trade_count": result.get("trade_count", result.get("trades_count")),
                "cost": result.get("cost_total"),
                "excess_vs_equal_etf": result.get("excess_return_equal_etf"),
                "admission_decision": admission.get("status") if isinstance(admission, dict) else None,
            }
        )
    return rows


def _benchmark_ids(benchmark_results: dict[str, Any]) -> list[str]:
    if not isinstance(benchmark_results, dict):
        return []
    ids: set[str] = set()
    for row in benchmark_results.values():
        if isinstance(row, dict):
            ids.update(str(key) for key in row.keys())
    return sorted(ids)


def _admission_all_rejected(admission_results: dict[str, Any]) -> bool:
    if not isinstance(admission_results, dict) or not admission_results:
        return False
    return all(isinstance(row, dict) and row.get("status") == "rejected" for row in admission_results.values())


def _markdown_report(summary: dict[str, Any]) -> str:
    data_quality = summary["data_quality"]
    price_source = summary["price_source"]
    consistency = summary["consistency"]
    lines = [
        "# Real Data Validation Report",
        "",
        f"- Git commit: {summary['git_commit']}",
        f"- Current tags: {summary['git_tags']}",
        f"- Release candidate passed: {summary['release_candidate_passed']}",
        f"- Blocking reasons: {summary['blocking_reasons']}",
        "",
        "## Data Source",
        f"- source_by_symbol: {price_source['source_by_symbol']}",
        f"- fallback_source: {price_source['fallback_source']}",
        f"- symbols_success: {price_source['symbols_success']}",
        f"- symbols_failed: {price_source['symbols_failed']}",
        "",
        "## Data Quality",
        f"- rows: {data_quality['rows']}",
        f"- symbols: {data_quality['symbols']}",
        f"- date range: {data_quality['date_range']}",
        f"- OHLC anomalies: {data_quality['ohlc_anomalies']}",
        f"- suspicious returns: {data_quality['suspicious_returns']}",
        f"- discarded rows: {data_quality['discarded_rows']}",
        "",
        "## Backtest Range",
        f"- start_date: {summary['backtest']['start_date']}",
        f"- end_date: {summary['backtest']['end_date']}",
        f"- strategies: {summary['backtest']['strategies']}",
        f"- benchmarks: {summary['backtest']['benchmarks']}",
        "",
        "## Strategy Results",
        "| Strategy | Cumulative return | Max drawdown | Trades | Cost | Excess vs EQUAL_ETF | Admission |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary["strategy_results"]:
        lines.append(
            "| {strategy_id} | {cumulative_return} | {max_drawdown} | {trade_count} | {cost} | {excess_vs_equal_etf} | {admission_decision} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Consistency Audit",
            f"- passed: {consistency['passed']}",
            f"- warnings: {len(consistency.get('warnings', []))}",
            f"- critical errors: {len(consistency.get('critical_errors', []))}",
            "",
            "## Limitations",
        ]
    )
    lines.extend(f"- {item}" for item in summary["limitations"]) if summary["limitations"] else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in summary["warnings"]) if summary["warnings"] else lines.append("- none")
    return "\n".join(lines) + "\n"
