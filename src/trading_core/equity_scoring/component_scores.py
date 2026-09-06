"""Shared score construction helpers and v0.7.4 builder."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, utc_now, write_json
from trading_core.equity_features.multi_horizon import FEATURE_FILES
from trading_core.equity_scoring.score_config import COMMON_COLUMNS, DEFAULT_AS_OF_DATE, SCORE_BOUNDARY, SCORE_FILES, TARGET_VERSION, default_score_config, validate_score_config
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


@dataclass(frozen=True)
class ScoringInputs:
    as_of_date: str
    requested_as_of_date: str
    feature_dir: Path
    feature_manifest_path: Path
    feature_manifest: dict[str, Any]
    feature_field_coverage: dict[str, Any]
    strict_universe_path: Path
    strict_universe: pd.DataFrame
    excluded_symbols: set[str]
    features: dict[str, pd.DataFrame]


def score_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_scores" / "daily" / as_of_date


def score_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_scores" / "daily" / as_of_date


def load_scoring_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_feature_date: bool = False,
) -> ScoringInputs:
    paths = default_paths(paths)
    selected_date, feature_dir = _resolve_feature_dir(paths, as_of_date, allow_latest_feature_date)
    manifest_path = feature_dir / "feature_manifest.json"
    manifest = _load_json(manifest_path)
    if not manifest:
        raise ValueError(f"feature manifest not found: {manifest_path}")
    coverage = _load_json(feature_dir / "feature_field_coverage.json")
    features = {group: read_frame(feature_dir / filename) for group, filename in FEATURE_FILES.items()}
    missing = [group for group, frame in features.items() if frame.empty]
    if missing:
        raise ValueError(f"feature files are missing or empty for {selected_date}: {missing}")
    strict_path = paths.data_dir / "equity_selection" / "daily" / selected_date / "strict_tradable_universe.json"
    strict = pd.DataFrame(_load_json_list(strict_path))
    if strict.empty:
        raise ValueError(f"strict tradable universe is empty: {strict_path}")
    excluded_path = strict_path.parent / "excluded_universe.json"
    excluded = {str(row.get("symbol")) for row in _load_json_list(excluded_path) if row.get("symbol")}
    return ScoringInputs(
        as_of_date=selected_date,
        requested_as_of_date=as_of_date,
        feature_dir=feature_dir,
        feature_manifest_path=manifest_path,
        feature_manifest=manifest,
        feature_field_coverage=coverage,
        strict_universe_path=strict_path,
        strict_universe=strict,
        excluded_symbols=excluded,
        features=features,
    )


def build_a_share_scores(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_feature_date: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    from trading_core.equity_scoring.composite_score import build_composite_scores
    from trading_core.equity_scoring.fundamental_score import build_fundamental_scores
    from trading_core.equity_scoring.horizon_scores import build_horizon_scores
    from trading_core.equity_scoring.industry_score import build_industry_scores
    from trading_core.equity_scoring.liquidity_score import build_liquidity_scores
    from trading_core.equity_scoring.risk_score import build_risk_scores
    from trading_core.equity_scoring.score_manifest import build_score_distribution, build_score_manifest, build_scoring_summary
    from trading_core.equity_scoring.score_report import write_score_reports

    paths = default_paths(paths)
    inputs = load_scoring_inputs(paths=paths, as_of_date=as_of_date, allow_latest_feature_date=allow_latest_feature_date)
    created_at = utc_now()
    config = default_score_config(inputs.as_of_date, created_at)
    config_issues = validate_score_config(config)
    if config_issues:
        raise ValueError("; ".join(config_issues))
    out_dir = score_data_dir(paths, inputs.as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / SCORE_FILES["score_config"], config)

    risk, risk_breakdown = build_risk_scores(inputs.features["risk"], config, created_at)
    liquidity, liquidity_breakdown = build_liquidity_scores(inputs.features["liquidity"], config, created_at)
    industry, industry_breakdown = build_industry_scores(inputs.features["industry"], config, created_at)
    fundamental, fundamental_breakdown = build_fundamental_scores(inputs.features["fundamental"], config, created_at)
    base_scores = _merge_base_scores(risk, liquidity, industry, fundamental, created_at)
    horizon, horizon_breakdown = build_horizon_scores(inputs.features, base_scores, config, created_at)
    composite, composite_breakdown = build_composite_scores(horizon, base_scores, config, created_at)
    breakdown = pd.concat(
        [risk_breakdown, liquidity_breakdown, industry_breakdown, fundamental_breakdown, horizon_breakdown, composite_breakdown],
        ignore_index=True,
    )
    artifacts = {
        "risk_liquidity_industry_fundamental_scores": out_dir / SCORE_FILES["risk_liquidity_industry_fundamental_scores"],
        "horizon_scores": out_dir / SCORE_FILES["horizon_scores"],
        "composite_scores": out_dir / SCORE_FILES["composite_scores"],
        "score_component_breakdown": out_dir / SCORE_FILES["score_component_breakdown"],
    }
    for frame, path in [(base_scores, artifacts["risk_liquidity_industry_fundamental_scores"]), (horizon, artifacts["horizon_scores"]), (composite, artifacts["composite_scores"]), (breakdown, artifacts["score_component_breakdown"])]:
        _write_parquet(frame, path)
    distribution = build_score_distribution(base_scores, horizon, composite, inputs.as_of_date)
    distribution_path = out_dir / SCORE_FILES["score_distribution"]
    write_json(distribution_path, distribution)
    artifacts["score_distribution"] = distribution_path
    manifest = build_score_manifest(paths, inputs, config, artifacts, created_at)
    manifest_path = out_dir / SCORE_FILES["score_manifest"]
    write_json(manifest_path, manifest)
    artifacts["score_manifest"] = manifest_path
    summary = build_scoring_summary(paths, inputs, base_scores, horizon, composite, distribution, manifest, created_at)
    summary_path = out_dir / SCORE_FILES["scoring_summary"]
    write_json(summary_path, summary)
    artifacts["scoring_summary"] = summary_path
    reports = write_score_reports(paths, inputs.as_of_date, summary, distribution)
    payload = {
        "builder_id": "A-SHARE-SCORING-BUILDER",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "strict_tradable_count": int(len(inputs.strict_universe)),
        "scored_symbols": int(composite["symbol"].nunique()),
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "reports": reports,
        "warnings": summary.get("warnings", []),
        "boundary": dict(SCORE_BOUNDARY),
    }
    return json_safe(payload)


def weighted_score_frame(
    base: pd.DataFrame,
    *,
    score_name: str,
    percentile_name: str,
    confidence_name: str,
    component_values: dict[str, pd.Series],
    component_confidences: dict[str, pd.Series],
    component_weights: dict[str, float],
    created_at: str,
    rank_name: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    from trading_core.equity_scoring.normalization import json_breakdown, rank_and_percentile

    score = pd.Series(0.0, index=base.index, dtype=float)
    confidence = pd.Series(0.0, index=base.index, dtype=float)
    rows = []
    for component, weight in component_weights.items():
        value = component_values[component].astype(float).clip(0.0, 100.0)
        component_conf = component_confidences.get(component, pd.Series(1.0, index=base.index, dtype=float)).astype(float).clip(0.0, 1.0)
        contribution = value * float(weight)
        score = score + contribution
        confidence = confidence + component_conf * float(weight)
        rows.extend(
            _breakdown_rows(
                base,
                score_name,
                component,
                value,
                float(weight),
                contribution,
                component_conf,
                created_at,
            )
        )
    result = base[COMMON_COLUMNS].copy()
    result[score_name] = score.clip(0.0, 100.0).round(6)
    if rank_name:
        ranks, percentiles = rank_and_percentile(base["symbol"], result[score_name])
        result[rank_name] = ranks
        result[percentile_name] = percentiles.round(6)
    else:
        _, percentiles = rank_and_percentile(base["symbol"], result[score_name])
        result[percentile_name] = percentiles.round(6)
    result[confidence_name] = confidence.clip(0.0, 1.0).round(6)
    breakdown_values = {
        component: component_values[component].astype(float).round(6)
        for component in component_weights
    }
    result[f"{_score_prefix(score_name)}_component_breakdown"] = [
        json_breakdown({component: values.iloc[index] for component, values in breakdown_values.items()})
        for index in range(len(result))
    ]
    result["source"] = "strict_tradable_universe+v0.7.3_feature_scores"
    result["created_at"] = created_at
    breakdown = pd.DataFrame(rows)
    return result, breakdown


def component_values_from_fields(frame: pd.DataFrame, component_fields: dict[str, list[str]], config: dict[str, Any]) -> tuple[dict[str, pd.Series], dict[str, pd.Series]]:
    from trading_core.equity_scoring.normalization import component_score

    limits = config["winsorization_limits"]
    directions = config["feature_directions"]
    neutral = float(config["missing_value_policy"]["score_fill"])
    values = {}
    confidences = {}
    for component, fields in component_fields.items():
        values[component], confidences[component], _ = component_score(
            frame,
            fields,
            directions,
            lower=float(limits["lower"]),
            upper=float(limits["upper"]),
            neutral_score=neutral,
        )
    return values, confidences


def _merge_base_scores(risk: pd.DataFrame, liquidity: pd.DataFrame, industry: pd.DataFrame, fundamental: pd.DataFrame, created_at: str) -> pd.DataFrame:
    base = risk[COMMON_COLUMNS].copy()
    for frame, columns in [
        (risk, ["RiskScore", "risk_percentile", "risk_confidence", "risk_component_breakdown"]),
        (liquidity, ["LiquidityScore", "liquidity_percentile", "liquidity_confidence", "liquidity_component_breakdown"]),
        (industry, ["IndustryScore", "industry_percentile", "industry_confidence", "industry_component_breakdown"]),
        (fundamental, ["FundamentalScore", "fundamental_percentile", "fundamental_confidence", "fundamental_component_breakdown"]),
    ]:
        base = base.merge(frame[["symbol", *columns]], on="symbol", how="left")
    base["source"] = "strict_tradable_universe+v0.7.3_feature_scores"
    base["created_at"] = created_at
    return base


def _breakdown_rows(base: pd.DataFrame, score_name: str, component: str, value: pd.Series, weight: float, contribution: pd.Series, confidence: pd.Series, created_at: str) -> list[dict[str, Any]]:
    rows = []
    for index, row in base.iterrows():
        index = cast(int, index)
        rows.append(
            {
                "as_of_date": row["as_of_date"],
                "symbol": row["symbol"],
                "score_name": score_name,
                "component_name": component,
                "component_value": round(float(value.loc[index]), 6),
                "component_weight": weight,
                "component_contribution": round(float(contribution.loc[index]), 6),
                "component_confidence": round(float(confidence.loc[index]), 6),
                "source": "strict_tradable_universe+v0.7.3_feature_scores",
                "created_at": created_at,
            }
        )
    return rows


def _resolve_feature_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_features" / "daily"
    exact = base / as_of_date
    if (exact / "feature_manifest.json").exists():
        return as_of_date, exact
    if not allow_latest:
        raise ValueError(f"feature files not found for as_of_date={as_of_date}")
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / "feature_manifest.json").exists())
    if not candidates:
        raise ValueError(f"no feature files available on or before {as_of_date}")
    selected = candidates[-1]
    return selected.name, selected


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def _write_parquet(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def _score_prefix(score_name: str) -> str:
    if score_name == "CompositeOpportunityScore":
        return "composite"
    if score_name.endswith("Score"):
        return score_name[:-5].lower()
    return score_name.lower()


def artifact_records(paths: ProjectPaths, artifacts: dict[str, Path]) -> dict[str, dict[str, Any]]:
    from trading_core.equity_data_quality.common import sha256_file

    records = {}
    for key, path in artifacts.items():
        records[key] = {
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "rows": int(len(pd.read_parquet(path))) if path.exists() and path.suffix == ".parquet" else None,
            "sha256": sha256_file(path),
        }
    return records
