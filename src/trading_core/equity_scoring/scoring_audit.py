"""Audit the v0.7.4 A-share scoring artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, write_report
from trading_core.equity_scoring.component_scores import score_data_dir, score_output_dir
from trading_core.equity_scoring.normalization import score_range
from trading_core.equity_scoring.score_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, REMEDIATION_VERSION, SCORE_BOUNDARY, SCORE_COLUMNS, SCORE_FILES, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


FORBIDDEN_POSITIVE_WORDING = [
    '"candidates_generated": true',
    '"watchlists_generated": true',
    '"virtual_portfolio_generated": true',
    '"day2_executed": true',
    '"run_daily_called": true',
    '"broker_connected": true',
    '"real_orders_placed": true',
    '"model_profit_guaranteed": true',
    '"live_trading_ready": true',
    "candidates generated: true",
    "watchlists generated: true",
    "virtual portfolios generated: true",
    "broker connected: true",
    "real orders placed: true",
    "live trading ready: true",
    "guaranteed profit",
    "model can make money",
    "recommended buy",
    "buy signal: true",
    "sell signal: true",
    "保证盈利",
    "实盘就绪",
    "买入信号: true",
    "卖出信号: true",
]

FORBIDDEN_ARTIFACTS = {
    "candidate_artifacts": [
        "outputs/equity_scores/daily/{date}/LONG_CANDIDATES.md",
        "outputs/equity_scores/daily/{date}/MID_CANDIDATES.md",
        "outputs/equity_scores/daily/{date}/SHORT_CANDIDATES.md",
        "outputs/equity_scores/daily/{date}/BUY_LIST.md",
        "outputs/equity_scores/daily/{date}/SELL_LIST.md",
        "outputs/equity_scores/daily/{date}/PORTFOLIO_ACTIONS.md",
        "data/equity_selection/daily/{date}/long_candidates.json",
        "data/equity_selection/daily/{date}/mid_candidates.json",
        "data/equity_selection/daily/{date}/short_candidates.json",
    ],
    "watchlist_artifacts": [
        "outputs/equity_scores/daily/{date}/WATCHLIST.md",
        "data/equity_selection/daily/{date}/watchlist.json",
    ],
    "virtual_portfolio_artifacts": [
        "data/equity_portfolios",
    ],
}


def audit_a_share_scores(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    minimum_strict_count: int = 500,
    allow_latest_feature_date: bool = False,
    allow_existing_downstream_artifacts: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    effective_as_of_date, data_dir = _resolve_score_dir(paths, as_of_date, allow_latest_feature_date)
    output_dir = score_output_dir(paths, effective_as_of_date)
    artifacts = _artifact_paths(paths, data_dir, output_dir, effective_as_of_date)
    config = _load_any(artifacts["score_config"], {})
    manifest = _load_any(artifacts["score_manifest"], {})
    summary = _load_any(artifacts["scoring_summary"], {})
    feature_manifest = _load_any(paths.data_dir / "equity_features" / "daily" / effective_as_of_date / "feature_manifest.json", {})
    strict_rows = _load_any(paths.data_dir / "equity_selection" / "daily" / effective_as_of_date / "strict_tradable_universe.json", [])
    excluded_rows = _load_any(paths.data_dir / "equity_selection" / "daily" / effective_as_of_date / "excluded_universe.json", [])
    frames = {
        "risk_liquidity_industry_fundamental_scores": read_frame(artifacts["risk_liquidity_industry_fundamental_scores"]),
        "horizon_scores": read_frame(artifacts["horizon_scores"]),
        "composite_scores": read_frame(artifacts["composite_scores"]),
        "score_component_breakdown": read_frame(artifacts["score_component_breakdown"]),
    }
    counts = _counts(frames, strict_rows)
    score_ranges = _score_ranges(frames)
    forbidden_artifacts = _forbidden_artifacts(paths, effective_as_of_date)
    forbidden_wording_hits = _forbidden_wording_hits(artifacts)
    checks = _checks(
        artifacts=artifacts,
        config=config,
        manifest=manifest,
        summary=summary,
        feature_manifest=feature_manifest,
        strict_rows=strict_rows,
        excluded_rows=excluded_rows,
        frames=frames,
        counts=counts,
        score_ranges=score_ranges,
        forbidden_artifacts=forbidden_artifacts,
        forbidden_wording_hits=forbidden_wording_hits,
        minimum_strict_count=minimum_strict_count,
        requested_as_of_date=as_of_date,
        effective_as_of_date=effective_as_of_date,
        allow_latest_feature_date=allow_latest_feature_date,
        allow_existing_downstream_artifacts=allow_existing_downstream_artifacts,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    warnings = list(summary.get("warnings", [])) if isinstance(summary, dict) else []
    payload = {
        "audit_id": "A-SHARE-SCORING-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": effective_as_of_date,
        "requested_as_of_date": as_of_date,
        "allow_latest_feature_date": allow_latest_feature_date,
        "allow_existing_downstream_artifacts": allow_existing_downstream_artifacts,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "counts": counts,
        "score_ranges": score_ranges,
        "forbidden_artifacts": forbidden_artifacts,
        "forbidden_wording_hits": forbidden_wording_hits,
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "boundary": dict(SCORE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_scoring_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_SCORING_AUDIT.md"
    return write_report(json_path, json_safe(payload), report_path, _markdown(payload))


def _artifact_paths(paths: ProjectPaths, data_dir: Path, output_dir: Path, as_of_date: str) -> dict[str, Path]:
    artifacts = {key: data_dir / filename for key, filename in SCORE_FILES.items()}
    artifacts.update(
        {
            "scoring_summary_report": output_dir / "SCORING_SUMMARY.md",
            "score_distribution_report": output_dir / "SCORE_DISTRIBUTION_REPORT.md",
            "audit_json": paths.data_dir / "equity_data_quality" / "a_share_scoring_audit.json",
            "audit_report": paths.outputs_dir / "audit" / "A_SHARE_SCORING_AUDIT.md",
        }
    )
    return artifacts


def _resolve_score_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_scores" / "daily"
    exact = base / as_of_date
    if (exact / SCORE_FILES["score_manifest"]).exists() or not allow_latest:
        return as_of_date, exact
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / SCORE_FILES["score_manifest"]).exists())
    if candidates:
        selected = candidates[-1]
        return selected.name, selected
    return as_of_date, exact


def _counts(frames: dict[str, pd.DataFrame], strict_rows: list[dict[str, Any]]) -> dict[str, int]:
    horizon = frames["horizon_scores"]
    composite = frames["composite_scores"]
    return {
        "strict_tradable_count": len(strict_rows),
        "scored_symbols": int(composite["symbol"].nunique()) if "symbol" in composite.columns else 0,
        "long_score_symbols": int(horizon.dropna(subset=["LongScore"])["symbol"].nunique()) if {"symbol", "LongScore"}.issubset(horizon.columns) else 0,
        "mid_score_symbols": int(horizon.dropna(subset=["MidScore"])["symbol"].nunique()) if {"symbol", "MidScore"}.issubset(horizon.columns) else 0,
        "short_score_symbols": int(horizon.dropna(subset=["ShortScore"])["symbol"].nunique()) if {"symbol", "ShortScore"}.issubset(horizon.columns) else 0,
        "composite_score_symbols": int(composite.dropna(subset=["CompositeOpportunityScore"])["symbol"].nunique()) if {"symbol", "CompositeOpportunityScore"}.issubset(composite.columns) else 0,
    }


def _score_ranges(frames: dict[str, pd.DataFrame]) -> dict[str, dict[str, float | None]]:
    ranges = {}
    for column in SCORE_COLUMNS:
        for frame in frames.values():
            if column in frame.columns:
                ranges[column] = score_range(frame, column)
                break
        ranges.setdefault(column, {"min": None, "max": None})
    return ranges


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    frames: dict[str, pd.DataFrame] = kwargs["frames"]
    strict_symbols = {row.get("symbol") for row in kwargs["strict_rows"] if row.get("symbol")}
    excluded_symbols = {row.get("symbol") for row in kwargs["excluded_rows"] if row.get("symbol")}
    score_symbols = {
        key: set(frame["symbol"].dropna().astype(str)) if not frame.empty and "symbol" in frame.columns else set()
        for key, frame in frames.items()
        if key != "score_component_breakdown"
    }
    counts = kwargs["counts"]
    ranges = kwargs["score_ranges"]
    checks = {
        "score_config_exists": artifacts["score_config"].exists(),
        "score_manifest_exists": artifacts["score_manifest"].exists(),
        "all_score_files_exist": all(artifacts[key].exists() for key in SCORE_FILES),
        "score_reports_exist": artifacts["scoring_summary_report"].exists() and artifacts["score_distribution_report"].exists(),
        "input_feature_manifest_exists": bool(kwargs["feature_manifest"]),
        "score_symbols_subset_of_strict_tradable_universe": all(symbols.issubset(strict_symbols) for symbols in score_symbols.values()),
        "excluded_symbols_absent_from_scores": not any(symbols.intersection(excluded_symbols) for symbols in score_symbols.values()),
        "score_symbols_count_equals_strict_tradable_count": counts["scored_symbols"] == counts["strict_tradable_count"] and counts["strict_tradable_count"] >= kwargs["minimum_strict_count"],
        "all_horizon_score_symbol_counts_equal_strict": counts["long_score_symbols"] == counts["strict_tradable_count"] and counts["mid_score_symbols"] == counts["strict_tradable_count"] and counts["short_score_symbols"] == counts["strict_tradable_count"],
        "composite_score_symbols_equal_strict": counts["composite_score_symbols"] == counts["strict_tradable_count"],
        "score_ranges_0_to_100": all(value["min"] is not None and value["max"] is not None and 0.0 <= float(value["min"]) <= 100.0 and 0.0 <= float(value["max"]) <= 100.0 for value in ranges.values()),
        "rank_columns_valid": _rank_columns_valid(frames["horizon_scores"], frames["composite_scores"], counts["strict_tradable_count"]),
        "percentile_columns_valid": _columns_in_range(frames, "percentile", 0.0, 100.0),
        "confidence_columns_valid": _columns_in_range(frames, "confidence", 0.0, 1.0),
        "component_breakdown_exists_for_all_scores": _component_breakdown_complete(frames["score_component_breakdown"], counts["strict_tradable_count"]),
        "no_candidate_artifacts_generated": kwargs["allow_existing_downstream_artifacts"] or not kwargs["forbidden_artifacts"]["candidate_artifacts_present"],
        "no_watchlist_artifacts_generated": not kwargs["forbidden_artifacts"]["watchlist_artifacts_present"],
        "no_virtual_portfolio_artifacts_generated": kwargs["allow_existing_downstream_artifacts"] or not kwargs["forbidden_artifacts"]["virtual_portfolio_artifacts_present"],
        "no_buy_sell_signal_columns": not _buy_sell_signal_columns(frames),
        "no_profit_or_live_trading_wording": not kwargs["forbidden_wording_hits"],
        "scores_generated_true": _boundary(kwargs["manifest"], kwargs["config"], kwargs["summary"], "scores_generated") is True,
        "candidates_generated_false": _boundary(kwargs["manifest"], kwargs["config"], kwargs["summary"], "candidates_generated") is False,
        "watchlists_generated_false": _boundary(kwargs["manifest"], kwargs["config"], kwargs["summary"], "watchlists_generated") is False,
        "virtual_portfolio_generated_false": _boundary(kwargs["manifest"], kwargs["config"], kwargs["summary"], "virtual_portfolio_generated") is False,
        "no_future_leakage_inherited_from_feature_manifest": kwargs["manifest"].get("no_future_leakage") is True and kwargs["feature_manifest"].get("no_future_leakage") is True,
        "target_version_matches": kwargs["manifest"].get("target_version") == TARGET_VERSION and kwargs["config"].get("target_version") == TARGET_VERSION and kwargs["summary"].get("target_version") == TARGET_VERSION,
        "score_date_exact_or_allowed": kwargs["effective_as_of_date"] == kwargs["requested_as_of_date"] or kwargs["allow_latest_feature_date"],
    }
    for key, expected in SCORE_BOUNDARY.items():
        checks[f"boundary_{key}_{str(expected).lower()}"] = _boundary(kwargs["manifest"], kwargs["config"], kwargs["summary"], key) is expected
    return checks


def _rank_columns_valid(horizon: pd.DataFrame, composite: pd.DataFrame, count: int) -> bool:
    if count <= 0:
        return False
    checks = []
    for frame, column in [(horizon, "LongRank"), (horizon, "MidRank"), (horizon, "ShortRank"), (composite, "CompositeRank")]:
        if column not in frame.columns:
            checks.append(False)
            continue
        ranks = pd.to_numeric(frame[column], errors="coerce").dropna().astype(int)
        checks.append(len(ranks) == count and set(ranks) == set(range(1, count + 1)))
    return all(checks)


def _columns_in_range(frames: dict[str, pd.DataFrame], token: str, lower: float, upper: float) -> bool:
    for frame in frames.values():
        for column in frame.columns:
            if token.lower() in column.lower():
                values = pd.to_numeric(frame[column], errors="coerce").dropna()
                if not values.empty and (float(values.min()) < lower or float(values.max()) > upper):
                    return False
    return True


def _component_breakdown_complete(frame: pd.DataFrame, strict_count: int) -> bool:
    expected = {"RiskScore", "LiquidityScore", "IndustryScore", "FundamentalScore", "LongScore", "MidScore", "ShortScore", "CompositeOpportunityScore"}
    if frame.empty or not {"symbol", "score_name"}.issubset(frame.columns):
        return False
    score_names = set(frame["score_name"].dropna().astype(str))
    if not expected.issubset(score_names):
        return False
    return all(int(frame[frame["score_name"] == score_name]["symbol"].nunique()) == strict_count for score_name in expected)


def _forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, list[str]]:
    result = {}
    for key, templates in FORBIDDEN_ARTIFACTS.items():
        present = []
        for template in templates:
            path = paths.project_root / template.format(date=as_of_date)
            if path.exists():
                present.append(str(path))
        result[f"{key}_present"] = present
    return result


def _buy_sell_signal_columns(frames: dict[str, pd.DataFrame]) -> list[str]:
    columns = []
    for frame in frames.values():
        for column in frame.columns:
            lowered = column.lower()
            if "signal" in lowered or lowered.startswith("buy") or lowered.startswith("sell") or "buy_" in lowered or "sell_" in lowered:
                columns.append(column)
    return sorted(set(columns))


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


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Scoring Audit",
            "",
            f"- target_version: {payload['target_version']}",
            f"- as_of_date: {payload['as_of_date']}",
            f"- overall_passed: {str(payload['overall_passed']).lower()}",
            f"- blocking_reasons: {payload['blocking_reasons']}",
            f"- warnings: {len(payload['warnings'])}",
            f"- counts: {payload['counts']}",
            f"- score_ranges: {payload['score_ranges']}",
            f"- forbidden_artifacts: {payload['forbidden_artifacts']}",
            "",
            "## Boundary",
            "- Scoring only.",
            "- Scores generated: true.",
            "- No candidates generated.",
            "- No watchlists generated.",
            "- No virtual portfolios generated.",
            "- Official forward dry-run status unchanged.",
            "- Day2 was not executed.",
            "- run-daily was not called.",
            "- No broker is connected.",
            "- No real orders were placed.",
            "- This is not a model profit guarantee.",
            "- Live trading ready: false.",
            "- Scores are not recommendations, buy/sell signals, or portfolio actions.",
            "",
        ]
    )
