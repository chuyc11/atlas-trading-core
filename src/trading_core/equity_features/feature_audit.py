"""Audit A-share multi-horizon feature artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, write_report
from trading_core.equity_features.feature_config import (
    COMMON_COLUMNS,
    DEFAULT_AS_OF_DATE,
    FEATURE_BOUNDARY,
    FEATURE_GROUP_FIELDS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
)
from trading_core.equity_features.feature_inputs import feature_data_dir, feature_output_dir
from trading_core.equity_features.multi_horizon import FEATURE_FILES
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


SYMBOL_COVERAGE_THRESHOLDS = {
    "short_horizon": 0.95,
    "mid_horizon": 0.95,
    "long_horizon": 0.90,
    "risk": 0.95,
    "liquidity": 0.95,
    "industry": 0.80,
    "fundamental": 0.60,
}
MANDATORY_FIELD_COVERAGE_THRESHOLDS = {
    "short_horizon": 0.90,
    "mid_horizon": 0.90,
    "long_horizon": 0.80,
    "risk": 0.90,
    "liquidity": 0.90,
    "industry": 0.70,
    "fundamental": 0.50,
}
FEATURE_COVERAGE_KEYS = {
    "short_horizon": "short_horizon_feature_coverage",
    "mid_horizon": "mid_horizon_feature_coverage",
    "long_horizon": "long_horizon_feature_coverage",
    "risk": "risk_feature_coverage",
    "liquidity": "liquidity_feature_coverage",
    "industry": "industry_feature_coverage",
    "fundamental": "fundamental_feature_coverage",
}
FIELD_COVERAGE_KEYS = {
    "short_horizon": "short_horizon_mandatory_field_coverage",
    "mid_horizon": "mid_horizon_mandatory_field_coverage",
    "long_horizon": "long_horizon_mandatory_field_coverage",
    "risk": "risk_mandatory_field_coverage",
    "liquidity": "liquidity_mandatory_field_coverage",
    "industry": "industry_mandatory_field_coverage",
    "fundamental": "fundamental_mandatory_field_coverage",
}
ALLOWED_RANK_COLUMNS = {
    "stock_rank_in_industry_by_return_20d",
    "stock_rank_in_industry_by_return_60d",
    "stock_rank_in_industry_by_return_120d",
}
FORBIDDEN_POSITIVE_WORDING = [
    '"scores_generated": true',
    '"candidates_generated": true',
    '"watchlist_generated": true',
    '"virtual_portfolio_generated": true',
    '"day2_executed": true',
    '"run_daily_called": true',
    '"broker_connected": true',
    '"real_orders_placed": true',
    '"model_profit_guaranteed": true',
    '"live_trading_ready": true',
    "scores generated: true",
    "candidates generated: true",
    "watchlist generated: true",
    "virtual portfolios generated: true",
    "broker connected: true",
    "real orders placed: true",
    "live trading ready: true",
    "guaranteed profit",
    "model can make money",
    "保证盈利",
    "实盘就绪",
]


def audit_a_share_multi_horizon_features(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    minimum_strict_count: int = 500,
    allow_latest_tradable_universe: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    effective_as_of_date, strict_universe_path = _resolve_strict_universe_path(paths, as_of_date, allow_latest_tradable_universe)
    data_dir = feature_data_dir(paths, effective_as_of_date)
    output_dir = feature_output_dir(paths, effective_as_of_date)
    artifact_paths = _artifact_paths(paths, data_dir, output_dir, strict_universe_path)
    strict_rows = _load_any(strict_universe_path, []) if strict_universe_path.exists() else []
    excluded_rows = _load_any(artifact_paths["excluded_universe"], [])
    frames = {group: read_frame(artifact_paths[group]) for group in FEATURE_FILES}
    manifest = _load_any(artifact_paths["feature_manifest"], {})
    coverage_payload = _load_any(artifact_paths["feature_field_coverage"], {})
    summary = _load_any(artifact_paths["feature_generation_summary"], {})

    counts = _counts(frames, strict_rows)
    symbol_coverage = _symbol_coverage(counts)
    mandatory_field_coverage = _mandatory_field_coverage(frames, coverage_payload)
    no_future_leakage = _no_future_leakage(manifest, effective_as_of_date)
    forbidden_columns = _forbidden_columns(frames)
    forbidden_wording_hits = _forbidden_wording_hits(artifact_paths)
    checks = _checks(
        artifact_paths=artifact_paths,
        strict_rows=strict_rows,
        excluded_rows=excluded_rows,
        frames=frames,
        counts=counts,
        symbol_coverage=symbol_coverage,
        mandatory_field_coverage=mandatory_field_coverage,
        no_future_leakage=no_future_leakage,
        forbidden_columns=forbidden_columns,
        forbidden_wording_hits=forbidden_wording_hits,
        manifest=manifest,
        coverage_payload=coverage_payload,
        summary=summary,
        minimum_strict_count=minimum_strict_count,
        requested_as_of_date=as_of_date,
        effective_as_of_date=effective_as_of_date,
        allow_latest_tradable_universe=allow_latest_tradable_universe,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    warnings = _warnings(summary, mandatory_field_coverage, as_of_date, effective_as_of_date)
    coverage = {
        **{FEATURE_COVERAGE_KEYS[group]: symbol_coverage[group] for group in FEATURE_FILES},
        **{FIELD_COVERAGE_KEYS[group]: mandatory_field_coverage[group] for group in FEATURE_FILES},
    }
    payload = {
        "audit_id": "A-SHARE-MULTI-HORIZON-FEATURE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": effective_as_of_date,
        "requested_as_of_date": as_of_date,
        "allow_latest_tradable_universe": allow_latest_tradable_universe,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "counts": counts,
        "coverage": coverage,
        "symbol_coverage_thresholds": SYMBOL_COVERAGE_THRESHOLDS,
        "mandatory_field_coverage_thresholds": MANDATORY_FIELD_COVERAGE_THRESHOLDS,
        "no_future_leakage": no_future_leakage,
        "forbidden_columns": forbidden_columns,
        "forbidden_wording_hits": forbidden_wording_hits,
        "artifacts": {key: str(path) for key, path in artifact_paths.items()},
        "boundary": dict(FEATURE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    json_path = paths.data_dir / "equity_data_quality" / "a_share_multi_horizon_feature_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_MULTI_HORIZON_FEATURE_AUDIT.md"
    return write_report(json_path, json_safe(payload), report_path, _markdown(payload))


def _artifact_paths(paths: ProjectPaths, data_dir: Path, output_dir: Path, strict_universe_path: Path) -> dict[str, Path]:
    artifacts = {group: data_dir / filename for group, filename in FEATURE_FILES.items()}
    artifacts.update(
        {
            "strict_tradable_universe": strict_universe_path,
            "excluded_universe": strict_universe_path.parent / "excluded_universe.json",
            "feature_manifest": data_dir / "feature_manifest.json",
            "feature_field_coverage": data_dir / "feature_field_coverage.json",
            "feature_generation_summary": data_dir / "feature_generation_summary.json",
            "summary_report": output_dir / "FEATURE_GENERATION_SUMMARY.md",
            "field_coverage_report": output_dir / "FEATURE_FIELD_COVERAGE.md",
            "audit_json": paths.data_dir / "equity_data_quality" / "a_share_multi_horizon_feature_audit.json",
            "audit_report": paths.outputs_dir / "audit" / "A_SHARE_MULTI_HORIZON_FEATURE_AUDIT.md",
        }
    )
    return artifacts


def _resolve_strict_universe_path(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_selection" / "daily"
    exact = base / as_of_date / "strict_tradable_universe.json"
    if exact.exists() or not allow_latest:
        return as_of_date, exact
    candidates = sorted(path for path in base.glob("*/strict_tradable_universe.json") if path.parent.name <= as_of_date)
    if candidates:
        latest = candidates[-1]
        return latest.parent.name, latest
    return as_of_date, exact


def _counts(frames: dict[str, pd.DataFrame], strict_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"strict_tradable_count": len(strict_rows)}
    for group, frame in frames.items():
        counts[f"{group}_feature_symbols"] = int(frame["symbol"].nunique()) if not frame.empty and "symbol" in frame.columns else 0
        counts[f"{group}_feature_rows"] = int(len(frame))
    return counts


def _symbol_coverage(counts: dict[str, int]) -> dict[str, float]:
    strict_count = counts["strict_tradable_count"]
    return {
        group: round(float(counts[f"{group}_feature_symbols"] / strict_count), 6) if strict_count else 0.0
        for group in FEATURE_FILES
    }


def _mandatory_field_coverage(frames: dict[str, pd.DataFrame], coverage_payload: dict[str, Any]) -> dict[str, float]:
    groups = coverage_payload.get("groups", {}) if isinstance(coverage_payload, dict) else {}
    result = {}
    for group, frame in frames.items():
        value = groups.get(group, {}).get("mandatory_field_coverage")
        if value is not None:
            result[group] = float(value)
            continue
        fields = FEATURE_GROUP_FIELDS[group]
        if frame.empty:
            result[group] = 0.0
            continue
        field_coverage = [float(frame[field].notna().mean()) if field in frame.columns else 0.0 for field in fields]
        result[group] = round(sum(field_coverage) / len(field_coverage), 6) if field_coverage else 0.0
    return result


def _no_future_leakage(manifest: dict[str, Any], as_of_date: str) -> dict[str, Any]:
    source_dates = manifest.get("source_dates", {}) if isinstance(manifest, dict) else {}
    future_dates = {key: value for key, value in source_dates.items() if value and str(value) > as_of_date}
    return {
        "passed": bool(manifest.get("no_future_leakage") is True and not future_dates),
        "manifest_no_future_leakage": manifest.get("no_future_leakage"),
        "source_dates": source_dates,
        "future_dates": future_dates,
        "as_of_date": as_of_date,
    }


def _forbidden_columns(frames: dict[str, pd.DataFrame]) -> dict[str, Any]:
    score_columns: dict[str, list[str]] = {}
    rank_columns: dict[str, list[str]] = {}
    signal_columns: dict[str, list[str]] = {}
    allowed_rank_columns: dict[str, list[str]] = {}
    for group, frame in frames.items():
        for column in frame.columns:
            lowered = column.lower()
            if "score" in lowered:
                score_columns.setdefault(group, []).append(column)
            if "rank" in lowered:
                if lowered in ALLOWED_RANK_COLUMNS:
                    allowed_rank_columns.setdefault(group, []).append(column)
                else:
                    rank_columns.setdefault(group, []).append(column)
            if "signal" in lowered:
                signal_columns.setdefault(group, []).append(column)
    return {
        "score_columns_present": score_columns,
        "rank_columns_present": rank_columns,
        "signal_columns_present": signal_columns,
        "allowed_feature_rank_columns_present": allowed_rank_columns,
    }


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifact_paths: dict[str, Path] = kwargs["artifact_paths"]
    frames: dict[str, pd.DataFrame] = kwargs["frames"]
    strict_rows: list[dict[str, Any]] = kwargs["strict_rows"]
    excluded_rows: list[dict[str, Any]] = kwargs["excluded_rows"]
    counts: dict[str, int] = kwargs["counts"]
    symbol_coverage: dict[str, float] = kwargs["symbol_coverage"]
    mandatory_field_coverage: dict[str, float] = kwargs["mandatory_field_coverage"]
    forbidden_columns: dict[str, Any] = kwargs["forbidden_columns"]
    strict_symbols = {row.get("symbol") for row in strict_rows if row.get("symbol")}
    excluded_symbols = {row.get("symbol") for row in excluded_rows if row.get("symbol")}
    feature_symbols = {
        group: set(frame["symbol"].dropna().astype(str)) if not frame.empty and "symbol" in frame.columns else set()
        for group, frame in frames.items()
    }
    checks = {
        "strict_universe_exact_or_allowed": artifact_paths["strict_tradable_universe"].exists() and (kwargs["effective_as_of_date"] == kwargs["requested_as_of_date"] or kwargs["allow_latest_tradable_universe"]),
        "strict_tradable_count_minimum": counts["strict_tradable_count"] >= kwargs["minimum_strict_count"],
        "all_feature_files_exist": all(artifact_paths[group].exists() for group in FEATURE_FILES),
        "feature_manifest_exists": artifact_paths["feature_manifest"].exists(),
        "feature_field_coverage_exists": artifact_paths["feature_field_coverage"].exists(),
        "feature_generation_summary_exists": artifact_paths["feature_generation_summary"].exists(),
        "feature_reports_exist": artifact_paths["summary_report"].exists() and artifact_paths["field_coverage_report"].exists(),
        "feature_symbols_subset_of_strict_universe": all(symbols.issubset(strict_symbols) for symbols in feature_symbols.values()),
        "excluded_symbols_absent_from_features": not any(symbols.intersection(excluded_symbols) for symbols in feature_symbols.values()),
        "no_duplicate_symbol_rows": all(_no_duplicate_symbols(frame) for frame in frames.values()),
        "required_fields_present": all(_required_fields_present(group, frame) for group, frame in frames.items()),
        "numeric_feature_values_finite": all(_numeric_values_finite(frame) for frame in frames.values()),
        "no_future_leakage": kwargs["no_future_leakage"]["passed"],
        "score_columns_absent": not forbidden_columns["score_columns_present"],
        "rank_columns_absent_except_allowed_industry_feature_ranks": not forbidden_columns["rank_columns_present"],
        "signal_columns_absent": not forbidden_columns["signal_columns_present"],
        "forbidden_positive_wording_absent": not kwargs["forbidden_wording_hits"],
        "target_version_matches": kwargs["manifest"].get("target_version") == TARGET_VERSION and kwargs["coverage_payload"].get("target_version") == TARGET_VERSION and kwargs["summary"].get("target_version") == TARGET_VERSION,
        "manifest_as_of_date_matches": kwargs["manifest"].get("as_of_date") == kwargs["effective_as_of_date"],
    }
    for group, threshold in SYMBOL_COVERAGE_THRESHOLDS.items():
        checks[f"{FEATURE_COVERAGE_KEYS[group]}_minimum"] = symbol_coverage[group] >= threshold
    for group, threshold in MANDATORY_FIELD_COVERAGE_THRESHOLDS.items():
        checks[f"{FIELD_COVERAGE_KEYS[group]}_minimum"] = mandatory_field_coverage[group] >= threshold
    checks.update(_boundary_checks(kwargs["manifest"], kwargs["summary"], kwargs["coverage_payload"]))
    return checks


def _required_fields_present(group: str, frame: pd.DataFrame) -> bool:
    required = [*COMMON_COLUMNS, *[field for field in FEATURE_GROUP_FIELDS[group] if field not in COMMON_COLUMNS]]
    return all(column in frame.columns for column in required)


def _no_duplicate_symbols(frame: pd.DataFrame) -> bool:
    if frame.empty or "symbol" not in frame.columns:
        return True
    return not frame["symbol"].duplicated().any()


def _numeric_values_finite(frame: pd.DataFrame) -> bool:
    numeric = frame.select_dtypes(include=["number"])
    if numeric.empty:
        return True
    values = numeric.to_numpy(dtype=float)
    return bool(np.isfinite(values[~np.isnan(values)]).all())


def _boundary_checks(manifest: dict[str, Any], summary: dict[str, Any], coverage: dict[str, Any]) -> dict[str, bool]:
    boundary = manifest.get("boundary") or summary.get("boundary") or coverage.get("boundary") or {}
    checks = {f"boundary_{key}_{str(expected).lower()}": boundary.get(key) is expected for key, expected in FEATURE_BOUNDARY.items()}
    checks.update(
        {
            "scores_generated_false": manifest.get("scores_generated") is False and boundary.get("scores_generated") is False,
            "candidates_generated_false": manifest.get("candidates_generated") is False and boundary.get("candidates_generated") is False,
            "watchlist_generated_false": manifest.get("watchlist_generated") is False and boundary.get("watchlist_generated") is False,
            "virtual_portfolio_generated_false": manifest.get("virtual_portfolio_generated") is False and boundary.get("virtual_portfolio_generated") is False,
        }
    )
    return checks


def _warnings(summary: dict[str, Any], mandatory_field_coverage: dict[str, float], requested_as_of_date: str, effective_as_of_date: str) -> list[str]:
    warnings = list(summary.get("warnings", [])) if isinstance(summary, dict) else []
    if mandatory_field_coverage.get("fundamental", 0.0) < 0.70 and mandatory_field_coverage.get("fundamental", 0.0) >= MANDATORY_FIELD_COVERAGE_THRESHOLDS["fundamental"]:
        warning = "fundamental field coverage is partial"
        if warning not in warnings:
            warnings.append(warning)
    if requested_as_of_date != effective_as_of_date:
        warnings.append(f"used latest available strict tradable universe {effective_as_of_date} for requested {requested_as_of_date}")
    return warnings


def _forbidden_wording_hits(artifact_paths: dict[str, Path]) -> list[str]:
    hits: list[str] = []
    for key, path in artifact_paths.items():
        if key.startswith("audit_") or not path.exists() or path.suffix not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            if phrase.lower() in text:
                hits.append(f"{path.name}:{phrase}")
    return hits


def _load_any(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# A-Share Multi-Horizon Feature Audit",
        "",
        f"- target_version: {payload['target_version']}",
        f"- as_of_date: {payload['as_of_date']}",
        f"- requested_as_of_date: {payload['requested_as_of_date']}",
        f"- overall_passed: {str(payload['overall_passed']).lower()}",
        f"- blocking_reasons: {payload['blocking_reasons']}",
        f"- warnings: {len(payload['warnings'])}",
        f"- counts: {payload['counts']}",
        f"- coverage: {payload['coverage']}",
        f"- no_future_leakage: {payload['no_future_leakage']}",
        f"- forbidden_columns: {payload['forbidden_columns']}",
        "",
        "## Boundary",
        "- Feature engineering only.",
        "- No stock scores generated.",
        "- No candidates generated.",
        "- No watchlist generated.",
        "- No virtual portfolios generated.",
        "- Official forward dry-run status unchanged.",
        "- Day2 was not executed.",
        "- run-daily was not called.",
        "- No broker is connected.",
        "- No real orders were placed.",
        "- This is not a model profit guarantee.",
        "- Live trading ready: false.",
        "",
    ]
    return "\n".join(lines)
