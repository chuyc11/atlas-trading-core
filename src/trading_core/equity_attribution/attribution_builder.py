"""Build v0.7.12 A-share attribution artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_config import (
    CURRENT_EXPOSURE_MODE,
    DEFAULT_AS_OF_DATE,
    DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    AttributionConfig,
    attribution_artifact_paths,
    attribution_data_dir,
    attribution_output_dir,
    validate_attribution_config,
)
from trading_core.equity_attribution.attribution_data_availability import build_attribution_data_availability
from trading_core.equity_attribution.attribution_inputs import load_attribution_inputs
from trading_core.equity_attribution.attribution_limitations import build_attribution_limitations
from trading_core.equity_attribution.attribution_manifest import build_attribution_boundary_check, build_attribution_manifest, build_attribution_summary
from trading_core.equity_attribution.attribution_report import write_attribution_reports
from trading_core.equity_attribution.attribution_source_trace import build_attribution_source_trace
from trading_core.equity_attribution.benchmark_relative_attribution import build_benchmark_relative_attribution_snapshot
from trading_core.equity_attribution.candidate_source_contribution import build_candidate_source_contribution_snapshot
from trading_core.equity_attribution.concentration_diagnostics import build_portfolio_concentration_diagnostics
from trading_core.equity_attribution.factor_exposure import build_factor_exposure_snapshot
from trading_core.equity_attribution.holding_contribution import build_holding_contribution_snapshot
from trading_core.equity_attribution.industry_contribution import build_industry_contribution_snapshot
from trading_core.equity_attribution.industry_diagnostics import build_industry_diagnostics_snapshot
from trading_core.equity_attribution.liquidity_bucket_contribution import build_liquidity_bucket_contribution_snapshot
from trading_core.equity_attribution.liquidity_diagnostics import build_liquidity_diagnostics_snapshot
from trading_core.equity_attribution.risk_bucket_contribution import build_risk_bucket_contribution_snapshot
from trading_core.equity_attribution.risk_diagnostics import build_risk_diagnostics_snapshot
from trading_core.equity_attribution.score_bucket_contribution import build_score_bucket_contribution_snapshot
from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_performance_attribution(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = CURRENT_EXPOSURE_MODE,
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    allow_limited_history: bool = True,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = AttributionConfig(
        as_of_date=as_of_date,
        mode=mode,
        minimum_required_observations=minimum_required_observations,
        allow_limited_history=allow_limited_history,
    )
    issues = validate_attribution_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    inputs = load_attribution_inputs(paths=paths, as_of_date=as_of_date)
    generated_at = utc_now()
    data_dir = attribution_data_dir(paths, as_of_date)
    output_dir = attribution_output_dir(paths, as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = attribution_artifact_paths(paths, as_of_date)

    data_availability = build_attribution_data_availability(config, inputs)
    holding = build_holding_contribution_snapshot(config, inputs)
    industry = build_industry_contribution_snapshot(config, inputs)
    candidate_source = build_candidate_source_contribution_snapshot(config, inputs)
    score_bucket = build_score_bucket_contribution_snapshot(config, inputs)
    risk_bucket = build_risk_bucket_contribution_snapshot(config, inputs)
    liquidity_bucket = build_liquidity_bucket_contribution_snapshot(config, inputs)
    benchmark_relative = build_benchmark_relative_attribution_snapshot(config, inputs)
    concentration = build_portfolio_concentration_diagnostics(config, inputs)
    risk_diagnostics = build_risk_diagnostics_snapshot(config, inputs)
    liquidity_diagnostics = build_liquidity_diagnostics_snapshot(config, inputs)
    industry_diagnostics = build_industry_diagnostics_snapshot(config, inputs)
    factor_exposure = build_factor_exposure_snapshot(config, inputs)
    limitations = build_attribution_limitations(config, data_availability)
    warnings = ["portfolio observation history is below the minimum required window"]
    boundary = build_attribution_boundary_check(as_of_date=as_of_date, warnings=warnings)
    manifest = build_attribution_manifest(
        paths=paths,
        config=config,
        generated_at=generated_at,
        artifacts=artifacts,
        data_availability=data_availability,
        boundary=boundary,
    )
    summary = build_attribution_summary(
        config=config,
        holding=holding,
        industry=industry,
        score_bucket=score_bucket,
        risk_bucket=risk_bucket,
        liquidity_bucket=liquidity_bucket,
        benchmark_relative=benchmark_relative,
        concentration=concentration,
        boundary=boundary,
        warnings=warnings,
    )

    core_payloads = {
        "attribution_data_availability": data_availability,
        "holding_contribution_snapshot": holding,
        "industry_contribution_snapshot": industry,
        "candidate_source_contribution_snapshot": candidate_source,
        "score_bucket_contribution_snapshot": score_bucket,
        "risk_bucket_contribution_snapshot": risk_bucket,
        "liquidity_bucket_contribution_snapshot": liquidity_bucket,
        "benchmark_relative_attribution_snapshot": benchmark_relative,
        "portfolio_concentration_diagnostics": concentration,
        "risk_diagnostics_snapshot": risk_diagnostics,
        "liquidity_diagnostics_snapshot": liquidity_diagnostics,
        "industry_diagnostics_snapshot": industry_diagnostics,
        "factor_exposure_snapshot": factor_exposure,
        "attribution_limitations": limitations,
        "attribution_manifest": manifest,
        "attribution_boundary_check": boundary,
        "attribution_summary": summary,
    }
    write_json(artifacts["attribution_config"], config.to_dict())
    for key, payload in core_payloads.items():
        write_json(artifacts[key], payload)

    source_trace = build_attribution_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        input_paths=inputs.input_paths,
        output_artifacts=artifacts,
        limitations=limitations,
        assumptions=[
            "Only existing virtual portfolio and performance artifacts are used.",
            "One-observation attribution remains structural until additional observations exist.",
            "Benchmark constituent exposure is only computed where source constituents are available.",
        ],
    )
    write_json(artifacts["attribution_source_trace"], source_trace)
    payload = {
        "builder_id": "A-SHARE-PERFORMANCE-ATTRIBUTION-BUILDER",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "attribution_config": config.to_dict(),
        **core_payloads,
        "attribution_source_trace": source_trace,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
    }
    reports = write_attribution_reports(output_dir, payload)
    source_trace = build_attribution_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        input_paths=inputs.input_paths,
        output_artifacts=artifacts,
        limitations=limitations,
        assumptions=payload["attribution_source_trace"]["assumptions"],
    )
    write_json(artifacts["attribution_source_trace"], source_trace)
    payload["attribution_source_trace"] = source_trace
    payload["reports"] = reports
    return json_safe(payload)
