"""Generate v0.7.5 A-share research candidate pools."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, read_frame, utc_now, write_json
from trading_core.equity_scoring.score_config import SCORE_FILES
from trading_core.equity_selection.candidate_config import CANDIDATE_BOUNDARY, CANDIDATE_FILES, DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, CandidateGenerationConfig, validate_candidate_config
from trading_core.equity_selection.candidate_explainer import component_highlights, confidence_notes, inclusion_reasons, json_text, risk_reasons
from trading_core.equity_selection.candidate_manifest import build_candidate_manifest
from trading_core.equity_selection.candidate_reason_taxonomy import validate_reasons
from trading_core.equity_selection.candidate_report import write_candidate_reports
from trading_core.equity_selection.filter_inputs import selection_data_dir
from trading_core.equity_selection.multi_horizon_candidates import build_multi_horizon_candidates
from trading_core.equity_selection.risk_downgraded_candidates import build_risk_downgraded_candidates
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class CandidateInputs:
    as_of_date: str
    requested_as_of_date: str
    score_dir: Path
    score_manifest_path: Path
    score_manifest: dict[str, Any]
    scoring_audit: dict[str, Any]
    strict_universe_path: Path
    strict_universe: pd.DataFrame
    score_frame: pd.DataFrame
    component_breakdown: pd.DataFrame


def load_candidate_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_score_date: bool = False,
) -> CandidateInputs:
    paths = default_paths(paths)
    selected_date, score_dir = _resolve_score_dir(paths, as_of_date, allow_latest_score_date)
    score_manifest_path = score_dir / SCORE_FILES["score_manifest"]
    score_manifest = _load_json(score_manifest_path)
    if not score_manifest:
        raise ValueError(f"score manifest not found: {score_manifest_path}")
    base_scores = read_frame(score_dir / SCORE_FILES["risk_liquidity_industry_fundamental_scores"])
    horizon_scores = read_frame(score_dir / SCORE_FILES["horizon_scores"])
    composite_scores = read_frame(score_dir / SCORE_FILES["composite_scores"])
    breakdown = read_frame(score_dir / SCORE_FILES["score_component_breakdown"])
    if base_scores.empty or horizon_scores.empty or composite_scores.empty:
        raise ValueError(f"score files are missing or empty for {selected_date}")
    strict_path = paths.data_dir / "equity_selection" / "daily" / selected_date / "strict_tradable_universe.json"
    strict = pd.DataFrame(_load_json_list(strict_path))
    if strict.empty:
        raise ValueError(f"strict tradable universe is empty: {strict_path}")
    frame = _merge_score_frame(base_scores, horizon_scores, composite_scores)
    return CandidateInputs(
        as_of_date=selected_date,
        requested_as_of_date=as_of_date,
        score_dir=score_dir,
        score_manifest_path=score_manifest_path,
        score_manifest=score_manifest,
        scoring_audit=_load_json(paths.data_dir / "equity_data_quality" / "a_share_scoring_audit.json"),
        strict_universe_path=strict_path,
        strict_universe=strict,
        score_frame=frame,
        component_breakdown=breakdown,
    )


def generate_a_share_candidates(
    *,
    config: CandidateGenerationConfig | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    long_count: int = 30,
    mid_count: int = 30,
    short_count: int = 30,
    extended_count: int = 100,
    allow_latest_score_date: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = config or CandidateGenerationConfig(
        as_of_date=as_of_date,
        long_count=long_count,
        mid_count=mid_count,
        short_count=short_count,
        extended_count=extended_count,
    )
    config_issues = validate_candidate_config(config)
    if config_issues:
        raise ValueError("; ".join(config_issues))
    inputs = load_candidate_inputs(paths=paths, as_of_date=config.as_of_date, allow_latest_score_date=allow_latest_score_date)
    created_at = utc_now()
    out_dir = selection_data_dir(paths, inputs.as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / CANDIDATE_FILES["candidate_generation_config"], config.to_dict())

    component_map = _component_map(inputs.component_breakdown)
    frame = inputs.score_frame.copy()
    long_candidates = _horizon_candidates(frame, "Long", config.long_count, _long_gate, config, component_map, inputs, created_at)
    mid_candidates = _horizon_candidates(frame, "Mid", config.mid_count, _mid_gate, config, component_map, inputs, created_at)
    short_candidates = _horizon_candidates(frame, "Short", config.short_count, _short_gate, config, component_map, inputs, created_at)
    extended_watch_pool = _extended_watch_pool(frame, config, component_map, inputs, created_at)
    strict_candidate_symbols = {row["symbol"] for row in [*long_candidates, *mid_candidates, *short_candidates]}
    multi_horizon = build_multi_horizon_candidates(frame, config, created_at)
    risk_downgraded = build_risk_downgraded_candidates(frame, config, strict_candidate_symbols, created_at)
    reason_breakdown = _reason_breakdown(long_candidates, mid_candidates, short_candidates, extended_watch_pool, risk_downgraded)
    candidate_counts = {
        "long_candidates": len(long_candidates),
        "mid_candidates": len(mid_candidates),
        "short_candidates": len(short_candidates),
        "extended_watch_pool": len(extended_watch_pool),
        "multi_horizon_candidates": len(multi_horizon),
        "risk_downgraded_candidates": len(risk_downgraded),
    }

    artifacts = _write_candidate_artifacts(
        out_dir,
        long_candidates,
        mid_candidates,
        short_candidates,
        extended_watch_pool,
        multi_horizon,
        risk_downgraded,
        reason_breakdown,
    )
    manifest = build_candidate_manifest(
        paths=paths,
        as_of_date=inputs.as_of_date,
        score_manifest_path=inputs.score_manifest_path,
        strict_tradable_count=len(inputs.strict_universe),
        scored_symbols=int(frame["symbol"].nunique()),
        candidate_counts=candidate_counts,
        artifacts=artifacts,
        created_at=created_at,
    )
    manifest_path = out_dir / CANDIDATE_FILES["candidate_manifest"]
    write_json(manifest_path, manifest)
    artifacts["candidate_manifest"] = manifest_path
    summary = _summary(inputs, candidate_counts, artifacts, created_at)
    summary_path = out_dir / CANDIDATE_FILES["candidate_generation_summary"]
    write_json(summary_path, summary)
    artifacts["candidate_generation_summary"] = summary_path
    reports = write_candidate_reports(
        paths,
        inputs.as_of_date,
        {
            **summary,
            "long_candidates": long_candidates,
            "mid_candidates": mid_candidates,
            "short_candidates": short_candidates,
            "multi_horizon_candidates": multi_horizon,
            "risk_downgraded_candidates": risk_downgraded,
        },
    )
    payload = {
        "builder_id": "A-SHARE-CANDIDATE-GENERATOR",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "strict_tradable_count": int(len(inputs.strict_universe)),
        "scored_symbols": int(frame["symbol"].nunique()),
        "candidate_counts": candidate_counts,
        "reason_breakdown": reason_breakdown,
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "reports": reports,
        "warnings": summary["warnings"],
        "boundary": dict(CANDIDATE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    return json_safe(payload)


def _merge_score_frame(base_scores: pd.DataFrame, horizon_scores: pd.DataFrame, composite_scores: pd.DataFrame) -> pd.DataFrame:
    base_columns = [
        "symbol",
        "RiskScore",
        "risk_percentile",
        "risk_confidence",
        "LiquidityScore",
        "liquidity_percentile",
        "liquidity_confidence",
        "IndustryScore",
        "industry_percentile",
        "industry_confidence",
        "FundamentalScore",
        "fundamental_percentile",
        "fundamental_confidence",
    ]
    composite_columns = ["symbol", "CompositeOpportunityScore", "CompositeRank", "CompositePercentile", "CompositeConfidence"]
    frame = horizon_scores.merge(base_scores[base_columns], on="symbol", how="left")
    frame = frame.merge(composite_scores[composite_columns], on="symbol", how="left")
    frame["RiskPercentile"] = frame["risk_percentile"]
    frame["LiquidityPercentile"] = frame["liquidity_percentile"]
    frame["IndustryPercentile"] = frame["industry_percentile"]
    return frame.sort_values("symbol").reset_index(drop=True)


def _horizon_candidates(frame: pd.DataFrame, horizon: str, count: int, gate, config: CandidateGenerationConfig, component_map: dict[tuple[str, str], dict[str, float]], inputs: CandidateInputs, created_at: str) -> list[dict[str, Any]]:
    eligible = frame[frame.apply(lambda row: gate(row, config, component_map), axis=1)].copy()
    eligible = eligible.sort_values([f"{horizon}Rank", "symbol"]).head(count)
    return [
        _candidate_record(row, horizon, rank, component_map, inputs, config, created_at)
        for rank, (_, row) in enumerate(eligible.iterrows(), start=1)
    ]


def _long_gate(row: pd.Series, config: CandidateGenerationConfig, component_map: dict[tuple[str, str], dict[str, float]]) -> bool:
    return (
        float(row.get("LongPercentile") or 0.0) >= config.long_percentile_min
        and (float(row.get("RiskPercentile") or 0.0) >= config.long_risk_percentile_min or float(row.get("RiskScore") or 0.0) >= config.long_risk_score_min)
        and (float(row.get("LiquidityPercentile") or 0.0) >= config.long_liquidity_percentile_min or float(row.get("LiquidityScore") or 0.0) >= config.long_liquidity_score_min)
        and float(row.get("fundamental_confidence") or 0.0) >= config.minimum_fundamental_confidence
    )


def _mid_gate(row: pd.Series, config: CandidateGenerationConfig, component_map: dict[tuple[str, str], dict[str, float]]) -> bool:
    return (
        float(row.get("MidPercentile") or 0.0) >= config.mid_percentile_min
        and (float(row.get("RiskPercentile") or 0.0) >= config.mid_risk_percentile_min or float(row.get("RiskScore") or 0.0) >= config.mid_risk_score_min)
        and (float(row.get("LiquidityPercentile") or 0.0) >= config.mid_liquidity_percentile_min or float(row.get("LiquidityScore") or 0.0) >= config.mid_liquidity_score_min)
        and float(row.get("IndustryPercentile") or 0.0) >= config.mid_industry_score_min_percentile
    )


def _short_gate(row: pd.Series, config: CandidateGenerationConfig, component_map: dict[tuple[str, str], dict[str, float]]) -> bool:
    overheat = component_map.get((str(row.get("symbol")), "ShortScore"), {}).get("overheat_penalty_component", 100.0)
    return (
        float(row.get("ShortPercentile") or 0.0) >= config.short_percentile_min
        and (float(row.get("LiquidityPercentile") or 0.0) >= config.short_liquidity_percentile_min or float(row.get("LiquidityScore") or 0.0) >= config.short_liquidity_score_min)
        and (float(row.get("RiskPercentile") or 0.0) >= config.short_risk_percentile_min or float(row.get("RiskScore") or 0.0) >= config.short_risk_score_min)
        and float(overheat) >= config.severe_overheat_component_max
    )


def _extended_watch_pool(frame: pd.DataFrame, config: CandidateGenerationConfig, component_map: dict[tuple[str, str], dict[str, float]], inputs: CandidateInputs, created_at: str) -> list[dict[str, Any]]:
    rows = []
    for horizon in ["Long", "Mid", "Short"]:
        subset = frame.sort_values([f"{horizon}Rank", "symbol"]).head(config.extended_count)
        for rank, (_, row) in enumerate(subset.iterrows(), start=1):
            record = _candidate_record(row, horizon, rank, component_map, inputs, config, created_at)
            record["candidate_horizon"] = f"Extended{horizon}"
            rows.append(record)
    return rows


def _candidate_record(row: pd.Series, horizon: str, candidate_rank: int, component_map: dict[tuple[str, str], dict[str, float]], inputs: CandidateInputs, config: CandidateGenerationConfig, created_at: str) -> dict[str, Any]:
    score_name = f"{horizon}Score"
    primary = inclusion_reasons(row, horizon)
    risks = risk_reasons(row, horizon, component_map, low_confidence_threshold=config.minimum_candidate_confidence)
    invalid_reasons = validate_reasons([*primary, *risks])
    if invalid_reasons:
        raise ValueError(f"invalid candidate reasons: {invalid_reasons}")
    return {
        "as_of_date": row["as_of_date"],
        "symbol": row["symbol"],
        "name": row.get("name", ""),
        "exchange": row.get("exchange", ""),
        "board": row.get("board", ""),
        "industry_level_1": row.get("industry_level_1", ""),
        "industry_level_2": row.get("industry_level_2", ""),
        "candidate_horizon": horizon,
        "candidate_rank": candidate_rank,
        "candidate_percentile": row.get(f"{horizon}Percentile"),
        "LongScore": row.get("LongScore"),
        "MidScore": row.get("MidScore"),
        "ShortScore": row.get("ShortScore"),
        "RiskScore": row.get("RiskScore"),
        "LiquidityScore": row.get("LiquidityScore"),
        "IndustryScore": row.get("IndustryScore"),
        "FundamentalScore": row.get("FundamentalScore"),
        "CompositeOpportunityScore": row.get("CompositeOpportunityScore"),
        "LongRank": row.get("LongRank"),
        "MidRank": row.get("MidRank"),
        "ShortRank": row.get("ShortRank"),
        "CompositeRank": row.get("CompositeRank"),
        "LongConfidence": row.get("LongConfidence"),
        "MidConfidence": row.get("MidConfidence"),
        "ShortConfidence": row.get("ShortConfidence"),
        "CompositeConfidence": row.get("CompositeConfidence"),
        "RiskPercentile": row.get("RiskPercentile"),
        "LiquidityPercentile": row.get("LiquidityPercentile"),
        "primary_inclusion_reasons": json_text(primary),
        "main_risk_reasons": json_text(risks),
        "component_highlights": json_text(component_highlights(str(row["symbol"]), score_name, component_map)),
        "confidence_notes": json_text(confidence_notes(row, horizon)),
        "source_score_manifest": str(inputs.score_manifest_path),
        "candidate_not_investment_advice": True,
        "not_buy_signal": True,
        "not_sell_signal": True,
        "not_order_instruction": True,
        "not_profit_guarantee": True,
        "created_at": created_at,
    }


def _component_map(breakdown: pd.DataFrame) -> dict[tuple[str, str], dict[str, float]]:
    result: dict[tuple[str, str], dict[str, float]] = {}
    if breakdown.empty:
        return result
    for _, row in breakdown.iterrows():
        key = (str(row.get("symbol")), str(row.get("score_name")))
        result.setdefault(key, {})[str(row.get("component_name"))] = float(row.get("component_value") or 0.0)
    return result


def _write_candidate_artifacts(
    out_dir: Path,
    long_candidates: list[dict[str, Any]],
    mid_candidates: list[dict[str, Any]],
    short_candidates: list[dict[str, Any]],
    extended_watch_pool: list[dict[str, Any]],
    multi_horizon: list[dict[str, Any]],
    risk_downgraded: list[dict[str, Any]],
    reason_breakdown: dict[str, Any],
) -> dict[str, Path]:
    artifacts = {
        "long_candidates_json": out_dir / CANDIDATE_FILES["long_candidates_json"],
        "long_candidates_parquet": out_dir / CANDIDATE_FILES["long_candidates_parquet"],
        "mid_candidates_json": out_dir / CANDIDATE_FILES["mid_candidates_json"],
        "mid_candidates_parquet": out_dir / CANDIDATE_FILES["mid_candidates_parquet"],
        "short_candidates_json": out_dir / CANDIDATE_FILES["short_candidates_json"],
        "short_candidates_parquet": out_dir / CANDIDATE_FILES["short_candidates_parquet"],
        "extended_watch_pool_json": out_dir / CANDIDATE_FILES["extended_watch_pool_json"],
        "extended_watch_pool_parquet": out_dir / CANDIDATE_FILES["extended_watch_pool_parquet"],
        "multi_horizon_candidates": out_dir / CANDIDATE_FILES["multi_horizon_candidates"],
        "risk_downgraded_candidates": out_dir / CANDIDATE_FILES["risk_downgraded_candidates"],
        "candidate_reason_breakdown": out_dir / CANDIDATE_FILES["candidate_reason_breakdown"],
    }
    _write_records(long_candidates, artifacts["long_candidates_json"], artifacts["long_candidates_parquet"])
    _write_records(mid_candidates, artifacts["mid_candidates_json"], artifacts["mid_candidates_parquet"])
    _write_records(short_candidates, artifacts["short_candidates_json"], artifacts["short_candidates_parquet"])
    _write_records(extended_watch_pool, artifacts["extended_watch_pool_json"], artifacts["extended_watch_pool_parquet"])
    write_json(artifacts["multi_horizon_candidates"], multi_horizon)
    write_json(artifacts["risk_downgraded_candidates"], risk_downgraded)
    write_json(artifacts["candidate_reason_breakdown"], reason_breakdown)
    return artifacts


def _write_records(records: list[dict[str, Any]], json_path: Path, parquet_path: Path) -> None:
    write_json(json_path, records)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_parquet(parquet_path, index=False)


def _reason_breakdown(*record_sets: list[dict[str, Any]]) -> dict[str, Any]:
    inclusion = Counter()
    risks = Counter()
    by_horizon: dict[str, int] = Counter()
    for records in record_sets:
        for row in records:
            by_horizon[str(row.get("candidate_horizon", row.get("trigger_horizon", "unknown")))] += 1
            for reason in _loads(row.get("primary_inclusion_reasons", "[]")):
                inclusion[reason] += 1
            for reason in _loads(row.get("main_risk_reasons", "[]")):
                risks[reason] += 1
            if row.get("downgrade_reason"):
                for reason in str(row["downgrade_reason"]).split(";"):
                    risks[reason] += 1
    return {
        "inclusion_reason_counts": dict(sorted(inclusion.items())),
        "risk_reason_counts": dict(sorted(risks.items())),
        "candidate_horizon_counts": dict(sorted(by_horizon.items())),
    }


def _summary(inputs: CandidateInputs, candidate_counts: dict[str, int], artifacts: dict[str, Path], created_at: str) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-CANDIDATE-GENERATION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "created_at": created_at,
        "strict_tradable_count": int(len(inputs.strict_universe)),
        "scored_symbols": int(inputs.score_frame["symbol"].nunique()),
        "candidate_counts": candidate_counts,
        "warnings": _warnings(candidate_counts),
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "boundary": dict(CANDIDATE_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _warnings(candidate_counts: dict[str, int]) -> list[str]:
    warnings = []
    for key in ["long_candidates", "mid_candidates", "short_candidates"]:
        if candidate_counts.get(key, 0) == 0:
            warnings.append(f"{key} is empty")
    return warnings


def _resolve_score_dir(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> tuple[str, Path]:
    base = paths.data_dir / "equity_scores" / "daily"
    exact = base / as_of_date
    if (exact / SCORE_FILES["score_manifest"]).exists():
        return as_of_date, exact
    if not allow_latest:
        raise ValueError(f"score files not found for as_of_date={as_of_date}")
    candidates = sorted(path for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and (path / SCORE_FILES["score_manifest"]).exists())
    if not candidates:
        raise ValueError(f"no score files available on or before {as_of_date}")
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


def _loads(value: Any) -> list[str]:
    try:
        parsed = json.loads(str(value))
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []
