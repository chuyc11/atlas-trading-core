"""Build v0.7.6 A-share research-only virtual portfolios."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_portfolios.industry_constraints import industry_bucket, industry_cap_violations, industry_exposure, max_industry_weight
from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_BOUNDARY, PORTFOLIO_FILES, DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, PortfolioConstructionConfig, validate_portfolio_config
from trading_core.equity_portfolios.portfolio_inputs import PortfolioInputs, load_portfolio_inputs, portfolio_data_dir
from trading_core.equity_portfolios.portfolio_manifest import build_portfolio_manifest
from trading_core.equity_portfolios.portfolio_report import write_portfolio_reports
from trading_core.equity_portfolios.risk_constraints import liquidity_summary, passes_horizon_risk_constraints, risk_notes
from trading_core.equity_portfolios.weighting import assign_target_weights, raw_weight_score
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_a_share_virtual_portfolios(
    *,
    config: PortfolioConstructionConfig | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    long_holdings: int = 30,
    mid_holdings: int = 30,
    short_holdings: int = 20,
    allow_latest_candidate_date: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = config or PortfolioConstructionConfig(
        as_of_date=as_of_date,
        long_holdings=long_holdings,
        mid_holdings=mid_holdings,
        short_holdings=short_holdings,
    )
    config_issues = validate_portfolio_config(config)
    if config_issues:
        raise ValueError("; ".join(config_issues))
    inputs = load_portfolio_inputs(paths=paths, as_of_date=config.as_of_date, allow_latest_candidate_date=allow_latest_candidate_date)
    created_at = utc_now()
    out_dir = portfolio_data_dir(paths, inputs.as_of_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / PORTFOLIO_FILES["portfolio_construction_config"], config.to_dict())

    long_portfolio = _build_portfolio(inputs, config, "Long", "long_virtual_portfolio", config.long_holdings, created_at)
    mid_portfolio = _build_portfolio(inputs, config, "Mid", "mid_virtual_portfolio", config.mid_holdings, created_at)
    short_portfolio = _build_portfolio(inputs, config, "Short", "short_virtual_portfolio", config.short_holdings, created_at)
    portfolio_records = {
        "long_virtual_portfolio": long_portfolio,
        "mid_virtual_portfolio": mid_portfolio,
        "short_virtual_portfolio": short_portfolio,
    }
    summaries = _summaries(portfolio_records, config)
    artifacts = _write_portfolio_artifacts(out_dir, portfolio_records, summaries)
    manifest = build_portfolio_manifest(
        paths=paths,
        as_of_date=inputs.as_of_date,
        candidate_manifest_path=inputs.candidate_manifest_path,
        score_manifest_path=inputs.score_manifest_path,
        portfolio_records=portfolio_records,
        artifacts=artifacts,
        created_at=created_at,
    )
    manifest_path = out_dir / PORTFOLIO_FILES["portfolio_manifest"]
    write_json(manifest_path, manifest)
    artifacts["portfolio_manifest"] = manifest_path
    payload = {
        "builder_id": "A-SHARE-VIRTUAL-PORTFOLIO-BUILDER",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "long_virtual_portfolio": long_portfolio,
        "mid_virtual_portfolio": mid_portfolio,
        "short_virtual_portfolio": short_portfolio,
        "portfolio_weight_summary": summaries["portfolio_weight_summary"],
        "portfolio_industry_exposure": summaries["portfolio_industry_exposure"],
        "portfolio_risk_liquidity_summary": summaries["portfolio_risk_liquidity_summary"],
        "artifacts": {key: str(path) for key, path in artifacts.items()},
        "warnings": _warnings(summaries),
        "boundary": dict(PORTFOLIO_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    reports = write_portfolio_reports(paths, inputs.as_of_date, payload)
    payload["reports"] = reports
    return json_safe(payload)


def _build_portfolio(inputs: PortfolioInputs, config: PortfolioConstructionConfig, horizon: str, portfolio_id: str, holdings: int, created_at: str) -> list[dict[str, Any]]:
    pool = _candidate_pool(inputs, config, horizon)
    selected = pool.head(holdings).to_dict("records")
    if len(selected) < holdings:
        raise ValueError(f"not enough eligible {horizon} candidates: {len(selected)} < {holdings}")
    records = [_portfolio_record(row, inputs, horizon, portfolio_id, created_at) for row in selected]
    return assign_target_weights(records, horizon=horizon, config=config)


def _candidate_pool(inputs: PortfolioInputs, config: PortfolioConstructionConfig, horizon: str) -> pd.DataFrame:
    primary = getattr(inputs, f"{horizon.lower()}_candidates").copy()
    primary["candidate_source"] = f"{horizon.lower()}_candidates"
    multi = inputs.multi_horizon_candidates.copy()
    if not multi.empty:
        multi["candidate_source"] = "multi_horizon_candidates"
        multi["candidate_rank"] = multi.get(f"{horizon}Rank", multi.get("CompositeRank"))
        multi["candidate_percentile"] = multi.get(f"{horizon}Percentile", multi.get("CompositePercentile"))
    columns = sorted(set(primary.columns).union(set(multi.columns if not multi.empty else [])))
    frames = [primary.reindex(columns=columns)]
    if not multi.empty:
        frames.append(multi.reindex(columns=columns))
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=["symbol"]).drop_duplicates("symbol", keep="first")
    combined = combined[~combined["symbol"].astype(str).isin(inputs.risk_downgraded_symbols)]
    combined = combined[~combined["symbol"].astype(str).isin(inputs.excluded_symbols)]
    if not config.allow_caution_universe:
        combined = combined[~combined["symbol"].astype(str).isin(inputs.caution_symbols)]
    if not config.allow_unknown_universe:
        combined = combined[~combined["symbol"].astype(str).isin(inputs.unknown_symbols)]
    combined = combined[combined.apply(lambda row: str(row.get("symbol")) in inputs.strict_symbols, axis=1)]
    combined = combined[combined.apply(lambda row: passes_horizon_risk_constraints(row, horizon, config), axis=1)]
    combined["industry"] = combined.apply(industry_bucket, axis=1)
    combined["raw_weight_score"] = combined.apply(lambda row: raw_weight_score(row, horizon), axis=1)
    source_priority = {f"{horizon.lower()}_candidates": 0, "multi_horizon_candidates": 1}
    combined["source_priority"] = combined["candidate_source"].map(source_priority).fillna(9)
    rank_column = f"{horizon}Rank"
    if rank_column not in combined.columns:
        combined[rank_column] = combined["candidate_rank"]
    return combined.sort_values(["source_priority", rank_column, "symbol"]).reset_index(drop=True)


def _portfolio_record(row: dict[str, Any], inputs: PortfolioInputs, horizon: str, portfolio_id: str, created_at: str) -> dict[str, Any]:
    notes = risk_notes(row, horizon)
    record = {
        "as_of_date": row.get("as_of_date") or inputs.as_of_date,
        "portfolio_id": portfolio_id,
        "portfolio_horizon": horizon,
        "symbol": row.get("symbol"),
        "name": row.get("name", ""),
        "exchange": row.get("exchange", ""),
        "board": row.get("board", ""),
        "industry_level_1": row.get("industry_level_1", ""),
        "industry_level_2": row.get("industry_level_2", ""),
        "industry": row.get("industry") or industry_bucket(row),
        "candidate_source": row.get("candidate_source", ""),
        "candidate_rank": _value(row.get("candidate_rank") or row.get(f"{horizon}Rank") or row.get("CompositeRank")),
        "LongScore": _value(row.get("LongScore")),
        "MidScore": _value(row.get("MidScore")),
        "ShortScore": _value(row.get("ShortScore")),
        "RiskScore": _value(row.get("RiskScore")),
        "LiquidityScore": _value(row.get("LiquidityScore")),
        "IndustryScore": _value(row.get("IndustryScore")),
        "FundamentalScore": _value(row.get("FundamentalScore")),
        "CompositeOpportunityScore": _value(row.get("CompositeOpportunityScore")),
        "weight_reason": "",
        "risk_notes": json.dumps(notes, ensure_ascii=False),
        "confidence_notes": row.get("confidence_notes") or json.dumps([f"{horizon} confidence retained from score artifacts"], ensure_ascii=False),
        "source_candidate_manifest": str(inputs.candidate_manifest_path),
        "source_score_manifest": str(inputs.score_manifest_path),
        "virtual_only": True,
        "research_only": True,
        "not_investment_advice": True,
        "not_buy_signal": True,
        "not_sell_signal": True,
        "not_order_instruction": True,
        "not_profit_guarantee": True,
        "not_live_trading_ready": True,
        "created_at": created_at,
    }
    if horizon == "Short":
        record["overheat_risk_notes"] = json.dumps(_short_overheat_notes(row), ensure_ascii=False)
        record["liquidity_risk_notes"] = json.dumps(["liquidity gate passed", *([notes[0]] if "liquidity_score_watch" in notes else [])], ensure_ascii=False)
        record["short_horizon_validity_notes"] = json.dumps(["5-20 trading-day research horizon only", "not an intraday or order instruction"], ensure_ascii=False)
    return record


def _short_overheat_notes(row: dict[str, Any]) -> list[str]:
    text = str(row.get("main_risk_reasons") or "")
    if "overheat_risk" in text:
        return ["overheat_risk"]
    return ["no_severe_overheat_flag_detected"]


def _summaries(portfolios: dict[str, list[dict[str, Any]]], config: PortfolioConstructionConfig) -> dict[str, Any]:
    weight_summary = {}
    industry = {}
    risk_liquidity = {}
    for portfolio_id, rows in portfolios.items():
        horizon = str(rows[0]["portfolio_horizon"]).lower() if rows else portfolio_id.split("_")[0]
        industry_cap = float(getattr(config, f"{horizon}_max_industry_weight"))
        weights = [float(row.get("target_weight") or 0.0) for row in rows]
        weight_summary[portfolio_id] = {
            "holdings": len(rows),
            "weight_sum": round(sum(weights), 6),
            "max_single_weight": round(max(weights or [0.0]), 6),
            "max_industry_weight": round(max_industry_weight(rows), 6),
        }
        exposure = industry_exposure(rows)
        industry[portfolio_id] = {
            **exposure,
            "industry_cap_violations": industry_cap_violations(rows, industry_cap),
        }
        risk_liquidity[portfolio_id] = liquidity_summary(rows)
    return {
        "portfolio_weight_summary": weight_summary,
        "portfolio_industry_exposure": industry,
        "portfolio_risk_liquidity_summary": risk_liquidity,
    }


def _write_portfolio_artifacts(out_dir, portfolios: dict[str, list[dict[str, Any]]], summaries: dict[str, Any]) -> dict[str, Any]:
    artifacts = {
        "long_virtual_portfolio_json": out_dir / PORTFOLIO_FILES["long_virtual_portfolio_json"],
        "long_virtual_portfolio_parquet": out_dir / PORTFOLIO_FILES["long_virtual_portfolio_parquet"],
        "mid_virtual_portfolio_json": out_dir / PORTFOLIO_FILES["mid_virtual_portfolio_json"],
        "mid_virtual_portfolio_parquet": out_dir / PORTFOLIO_FILES["mid_virtual_portfolio_parquet"],
        "short_virtual_portfolio_json": out_dir / PORTFOLIO_FILES["short_virtual_portfolio_json"],
        "short_virtual_portfolio_parquet": out_dir / PORTFOLIO_FILES["short_virtual_portfolio_parquet"],
        "portfolio_weight_summary": out_dir / PORTFOLIO_FILES["portfolio_weight_summary"],
        "portfolio_industry_exposure": out_dir / PORTFOLIO_FILES["portfolio_industry_exposure"],
        "portfolio_risk_liquidity_summary": out_dir / PORTFOLIO_FILES["portfolio_risk_liquidity_summary"],
    }
    _write_records(portfolios["long_virtual_portfolio"], artifacts["long_virtual_portfolio_json"], artifacts["long_virtual_portfolio_parquet"])
    _write_records(portfolios["mid_virtual_portfolio"], artifacts["mid_virtual_portfolio_json"], artifacts["mid_virtual_portfolio_parquet"])
    _write_records(portfolios["short_virtual_portfolio"], artifacts["short_virtual_portfolio_json"], artifacts["short_virtual_portfolio_parquet"])
    write_json(artifacts["portfolio_weight_summary"], summaries["portfolio_weight_summary"])
    write_json(artifacts["portfolio_industry_exposure"], summaries["portfolio_industry_exposure"])
    write_json(artifacts["portfolio_risk_liquidity_summary"], summaries["portfolio_risk_liquidity_summary"])
    return artifacts


def _write_records(records: list[dict[str, Any]], json_path, parquet_path) -> None:
    write_json(json_path, records)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_parquet(parquet_path, index=False)


def _warnings(summaries: dict[str, Any]) -> list[str]:
    warnings = []
    for portfolio_id, exposure in summaries["portfolio_industry_exposure"].items():
        raw = exposure.get("raw_industry_weight_by_level_1", {})
        if raw.get("Unclassified", 0.0) > 0:
            warnings.append(f"{portfolio_id}: raw industry_level_1 includes Unclassified; industry caps use auditable fallback industry buckets")
    return warnings


def _value(value: Any) -> Any:
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    return value
