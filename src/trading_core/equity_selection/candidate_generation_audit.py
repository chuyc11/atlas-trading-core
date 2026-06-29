"""Audit v0.7.5 A-share candidate generation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, write_report
from trading_core.equity_selection.candidate_config import CANDIDATE_BOUNDARY, CANDIDATE_FILES, CANDIDATE_REPORTS, DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, REMEDIATION_VERSION, TARGET_VERSION
from trading_core.equity_selection.filter_inputs import selection_data_dir, selection_output_dir
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


FORBIDDEN_POSITIVE_WORDING = [
    '"virtual_portfolio_generated": true',
    '"buy_sell_signals_generated": true',
    '"order_preview_generated": true',
    '"day2_executed": true',
    '"run_daily_called": true',
    '"broker_connected": true',
    '"real_orders_placed": true',
    '"model_profit_guaranteed": true',
    '"live_trading_ready": true',
    '"candidate_not_investment_advice": false',
    '"not_buy_signal": false',
    '"not_sell_signal": false',
    '"not_order_instruction": false',
    '"not_profit_guarantee": false',
    "guaranteed profit",
    "model can make money",
    "live trading ready: true",
    "strong buy",
    "must buy",
    "portfolio weight",
    "rebalance action",
    "order instruction: true",
    "保证盈利",
    "实盘就绪",
    "强烈买入",
    "必买",
]

FORBIDDEN_ARTIFACTS = {
    "virtual_portfolio_artifacts_present": [
        "data/equity_portfolios",
        "outputs/equity_portfolios",
        "outputs/equity_selection/daily/{date}/PORTFOLIO_ACTIONS.md",
    ],
    "buy_sell_signal_artifacts_present": [
        "outputs/equity_selection/daily/{date}/BUY_LIST.md",
        "outputs/equity_selection/daily/{date}/SELL_LIST.md",
    ],
    "order_preview_artifacts_present": [
        "outputs/equity_selection/daily/{date}/ORDER_PREVIEW.md",
        "data/equity_selection/daily/{date}/order_preview.json",
        "data/equity_selection/daily/{date}/orders.json",
    ],
}

DISALLOWED_COLUMNS = {
    "buy_signal",
    "sell_signal",
    "order_preview",
    "portfolio_weight",
    "position_size",
    "rebalance_action",
    "trade_instruction",
    "order_instruction",
}


def audit_a_share_candidates(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    minimum_strict_count: int = 500,
    allow_latest_score_date: bool = False,
    allow_existing_downstream_artifacts: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    effective_as_of_date, data_dir = _resolve_candidate_dir(paths, as_of_date, allow_latest_score_date)
    output_dir = selection_output_dir(paths, effective_as_of_date)
    artifacts = _artifact_paths(paths, data_dir, output_dir, effective_as_of_date)
    config = _load_any(artifacts["candidate_generation_config"], {})
    manifest = _load_any(artifacts["candidate_manifest"], {})
    summary = _load_any(artifacts["candidate_generation_summary"], {})
    strict_rows = _load_any(paths.data_dir / "equity_selection" / "daily" / effective_as_of_date / "strict_tradable_universe.json", [])
    score_manifest = _load_any(paths.data_dir / "equity_scores" / "daily" / effective_as_of_date / "score_manifest.json", {})
    frames = {
        "long_candidates": read_frame(artifacts["long_candidates_parquet"]),
        "mid_candidates": read_frame(artifacts["mid_candidates_parquet"]),
        "short_candidates": read_frame(artifacts["short_candidates_parquet"]),
        "extended_watch_pool": read_frame(artifacts["extended_watch_pool_parquet"]),
    }
    json_rows = {
        "multi_horizon_candidates": _load_any(artifacts["multi_horizon_candidates"], []),
        "risk_downgraded_candidates": _load_any(artifacts["risk_downgraded_candidates"], []),
    }
    score_symbols = _score_symbols(paths, effective_as_of_date)
    counts = _counts(frames, json_rows, strict_rows, score_symbols)
    forbidden_artifacts = _forbidden_artifacts(paths, effective_as_of_date)
    forbidden_wording_hits = _forbidden_wording_hits(artifacts)
    checks = _checks(
        artifacts=artifacts,
        config=config,
        manifest=manifest,
        summary=summary,
        strict_rows=strict_rows,
        score_manifest=score_manifest,
        frames=frames,
        json_rows=json_rows,
        score_symbols=score_symbols,
        counts=counts,
        minimum_strict_count=minimum_strict_count,
        allow_existing_downstream_artifacts=allow_existing_downstream_artifacts,
        forbidden_artifacts=forbidden_artifacts,
        forbidden_wording_hits=forbidden_wording_hits,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    payload = {
        "audit_id": "A-SHARE-CANDIDATE-GENERATION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": effective_as_of_date,
        "requested_as_of_date": as_of_date,
        "allow_existing_downstream_artifacts": allow_existing_downstream_artifacts,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": list(summary.get("warnings", [])) if isinstance(summary, dict) else [],
        "checks": checks,
        "counts": counts,
        "forbidden_artifacts": forbidden_artifacts,
        "forbidden_wording_hits": forbidden_wording_hits,
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "boundary": dict(CANDIDATE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_candidate_generation_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_CANDIDATE_GENERATION_AUDIT.md"
    return write_report(json_path, json_safe(payload), report_path, _markdown(payload))


def _artifact_paths(paths: ProjectPaths, data_dir: Path, output_dir: Path, as_of_date: str) -> dict[str, Path]:
    artifacts = {key: data_dir / filename for key, filename in CANDIDATE_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in CANDIDATE_REPORTS.items()})
    return artifacts


def _counts(frames: dict[str, pd.DataFrame], json_rows: dict[str, list[dict[str, Any]]], strict_rows: list[dict[str, Any]], score_symbols: set[str]) -> dict[str, int]:
    return {
        "strict_tradable_count": len(strict_rows),
        "scored_symbols": len(score_symbols),
        "long_candidates": len(frames["long_candidates"]),
        "mid_candidates": len(frames["mid_candidates"]),
        "short_candidates": len(frames["short_candidates"]),
        "extended_watch_pool": len(frames["extended_watch_pool"]),
        "multi_horizon_candidates": len(json_rows["multi_horizon_candidates"]),
        "risk_downgraded_candidates": len(json_rows["risk_downgraded_candidates"]),
    }


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    config = kwargs["config"]
    manifest = kwargs["manifest"]
    summary = kwargs["summary"]
    frames: dict[str, pd.DataFrame] = kwargs["frames"]
    json_rows: dict[str, list[dict[str, Any]]] = kwargs["json_rows"]
    strict_symbols = {str(row.get("symbol")) for row in kwargs["strict_rows"] if row.get("symbol")}
    score_symbols = kwargs["score_symbols"]
    candidate_symbols = _all_candidate_symbols(frames, json_rows)
    counts = kwargs["counts"]
    checks = {
        "candidate_config_exists": artifacts["candidate_generation_config"].exists(),
        "candidate_manifest_exists": artifacts["candidate_manifest"].exists(),
        "long_candidate_files_exist": artifacts["long_candidates_json"].exists() and artifacts["long_candidates_parquet"].exists(),
        "mid_candidate_files_exist": artifacts["mid_candidates_json"].exists() and artifacts["mid_candidates_parquet"].exists(),
        "short_candidate_files_exist": artifacts["short_candidates_json"].exists() and artifacts["short_candidates_parquet"].exists(),
        "extended_watch_pool_exists": artifacts["extended_watch_pool_json"].exists() and artifacts["extended_watch_pool_parquet"].exists(),
        "multi_horizon_candidates_exists": artifacts["multi_horizon_candidates"].exists(),
        "risk_downgraded_candidates_exists": artifacts["risk_downgraded_candidates"].exists(),
        "reason_breakdown_exists": artifacts["candidate_reason_breakdown"].exists(),
        "candidate_reports_exist": all(artifacts[key].exists() for key in CANDIDATE_REPORTS),
        "input_score_manifest_exists": bool(kwargs["score_manifest"]),
        "strict_tradable_count_minimum": counts["strict_tradable_count"] >= kwargs["minimum_strict_count"],
        "all_candidates_subset_of_strict_tradable_universe": candidate_symbols.issubset(strict_symbols),
        "all_candidates_exist_in_score_tables": candidate_symbols.issubset(score_symbols),
        "long_candidate_count_matches_config": counts["long_candidates"] == int(config.get("long_count", -1)),
        "mid_candidate_count_matches_config": counts["mid_candidates"] == int(config.get("mid_count", -1)),
        "short_candidate_count_matches_config": counts["short_candidates"] == int(config.get("short_count", -1)),
        "extended_watch_pool_meets_config": counts["extended_watch_pool"] >= int(config.get("extended_count", 0)),
        "manifest_counts_match_files": manifest.get("candidate_counts") == {key: counts[key] for key in ["long_candidates", "mid_candidates", "short_candidates", "extended_watch_pool", "multi_horizon_candidates", "risk_downgraded_candidates"]},
        "long_candidates_sorted": _sorted_by(frames["long_candidates"], "LongRank"),
        "mid_candidates_sorted": _sorted_by(frames["mid_candidates"], "MidRank"),
        "short_candidates_sorted": _sorted_by(frames["short_candidates"], "ShortRank"),
        "candidate_records_contain_explanations": _records_have_fields(frames, ["primary_inclusion_reasons", "component_highlights", "confidence_notes"]),
        "candidate_records_contain_risk_notes": _records_have_fields(frames, ["main_risk_reasons"]),
        "candidate_records_contain_not_investment_advice_flags": _disclaimer_flags_valid(frames, json_rows),
        "no_virtual_portfolio_artifacts_generated": kwargs["allow_existing_downstream_artifacts"] or not kwargs["forbidden_artifacts"]["virtual_portfolio_artifacts_present"],
        "no_buy_sell_signal_artifacts_generated": not kwargs["forbidden_artifacts"]["buy_sell_signal_artifacts_present"],
        "no_order_preview_generated": not kwargs["forbidden_artifacts"]["order_preview_artifacts_present"],
        "no_buy_sell_or_order_columns": not _disallowed_columns(frames),
        "no_profit_guarantee_wording": not kwargs["forbidden_wording_hits"],
        "target_version_matches": manifest.get("target_version") == TARGET_VERSION and summary.get("target_version") == TARGET_VERSION and config.get("target_version") == TARGET_VERSION,
    }
    for key, expected in CANDIDATE_BOUNDARY.items():
        checks[f"boundary_{key}_{str(expected).lower()}"] = _boundary(manifest, config, summary, key) is expected
    return checks


def _all_candidate_symbols(frames: dict[str, pd.DataFrame], json_rows: dict[str, list[dict[str, Any]]]) -> set[str]:
    symbols: set[str] = set()
    for frame in frames.values():
        if not frame.empty and "symbol" in frame.columns:
            symbols.update(frame["symbol"].dropna().astype(str))
    for rows in json_rows.values():
        symbols.update(str(row.get("symbol")) for row in rows if row.get("symbol"))
    return symbols


def _sorted_by(frame: pd.DataFrame, column: str) -> bool:
    if frame.empty or column not in frame.columns:
        return False
    values = pd.to_numeric(frame[column], errors="coerce").dropna().tolist()
    return values == sorted(values)


def _records_have_fields(frames: dict[str, pd.DataFrame], fields: list[str]) -> bool:
    for frame in [frames["long_candidates"], frames["mid_candidates"], frames["short_candidates"], frames["extended_watch_pool"]]:
        if frame.empty:
            return False
        for field in fields:
            if field not in frame.columns or frame[field].isna().any() or (frame[field].astype(str).str.len() == 0).any():
                return False
    return True


def _disclaimer_flags_valid(frames: dict[str, pd.DataFrame], json_rows: dict[str, list[dict[str, Any]]]) -> bool:
    flags = ["candidate_not_investment_advice", "not_buy_signal", "not_sell_signal", "not_order_instruction", "not_profit_guarantee"]
    for frame in frames.values():
        if frame.empty:
            return False
        for flag in flags:
            if flag not in frame.columns or not frame[flag].fillna(False).astype(bool).all():
                return False
    for rows in json_rows.values():
        for row in rows:
            if not all(row.get(flag) is True for flag in flags):
                return False
    return True


def _disallowed_columns(frames: dict[str, pd.DataFrame]) -> list[str]:
    hits = []
    for frame in frames.values():
        for column in frame.columns:
            if column in DISALLOWED_COLUMNS:
                hits.append(column)
    return sorted(set(hits))


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, list[str]]:
    result = {}
    for key, templates in FORBIDDEN_ARTIFACTS.items():
        present = []
        for template in templates:
            path = paths.project_root / template.format(date=as_of_date)
            if path.exists():
                present.append(str(path))
        result[key] = present
    return result


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for key, path in artifacts.items():
        if key.startswith("audit_") or not path.exists() or path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase.lower() in text:
                hits.append(f"{path.name}:{phrase}")
    return hits


def _boundary(manifest: dict[str, Any], config: dict[str, Any], summary: dict[str, Any], key: str) -> Any:
    values = []
    for payload in [manifest, config, summary]:
        boundary = payload.get("boundary") if isinstance(payload, dict) else {}
        if boundary:
            values.append(boundary.get(key))
    if not values:
        return None
    first = values[0]
    if any(value is not first for value in values):
        return "__boundary_mismatch__"
    return first


def _score_symbols(paths: ProjectPaths, as_of_date: str) -> set[str]:
    frame = read_frame(paths.data_dir / "equity_scores" / "daily" / as_of_date / "composite_scores.parquet")
    if frame.empty or "symbol" not in frame.columns:
        return set()
    return set(frame["symbol"].dropna().astype(str))


def _resolve_candidate_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_selection" / "daily"
    exact = base / as_of_date
    if (exact / CANDIDATE_FILES["candidate_manifest"]).exists():
        return as_of_date, exact
    if not allow_latest:
        return as_of_date, exact
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / CANDIDATE_FILES["candidate_manifest"]).exists())
    if not candidates:
        return as_of_date, exact
    selected = candidates[-1]
    return selected.name, selected


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Candidate Generation Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            f"- counts: {payload['counts']}",
            f"- forbidden_artifacts: {payload['forbidden_artifacts']}",
            "",
            "## Boundary",
            "- Candidate generation only.",
            "- Candidates generated: true.",
            "- Watch pools generated: true.",
            "- No virtual portfolios generated.",
            "- No buy/sell signals generated.",
            "- No order preview generated.",
            "- Official forward dry-run status unchanged.",
            "- Day2 was not executed.",
            "- run-daily was not called.",
            "- No broker is connected.",
            "- No real orders were placed.",
            "- This is not a model profit guarantee.",
            "- Live trading ready: false.",
            "- Candidates are not investment advice or trade instructions.",
            "",
            f"Recommended next version: {payload['recommended_next_version']}",
            "",
        ]
    )
