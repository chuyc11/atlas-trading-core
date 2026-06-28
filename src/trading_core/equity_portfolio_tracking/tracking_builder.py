"""Build v0.7.8 A-share virtual portfolio tracking artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_portfolio_tracking.benchmark_comparison import build_benchmark_comparison_snapshot
from trading_core.equity_portfolio_tracking.drawdown import build_drawdown_snapshot
from trading_core.equity_portfolio_tracking.exposure import build_exposure_snapshot
from trading_core.equity_portfolio_tracking.nav import build_holdings_snapshot, build_nav_snapshot, calculate_nav
from trading_core.equity_portfolio_tracking.paper_ledger import build_paper_ledger
from trading_core.equity_portfolio_tracking.performance import build_performance_snapshot
from trading_core.equity_portfolio_tracking.tracking_config import (
    DEFAULT_AS_OF_DATE,
    PORTFOLIO_KEYS,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
    TRACKING_BOUNDARY,
    TRACKING_FILES,
    TRACKING_FLAGS,
    TRACKING_REPORTS,
    TrackingConfig,
    validate_tracking_config,
)
from trading_core.equity_portfolio_tracking.tracking_inputs import load_tracking_inputs, tracking_data_dir, tracking_output_dir
from trading_core.equity_portfolio_tracking.tracking_manifest import build_tracking_manifest, build_tracking_source_trace
from trading_core.equity_portfolio_tracking.tracking_report import write_tracking_reports
from trading_core.equity_portfolio_tracking.valuation import build_valuation_prices
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_virtual_portfolio_tracking(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = TrackingConfig(as_of_date=as_of_date, ledger_start_date=as_of_date)
    config_issues = validate_tracking_config(config)
    if config_issues:
        raise ValueError("; ".join(config_issues))

    inputs = load_tracking_inputs(paths=paths, as_of_date=as_of_date)
    generated_at = utc_now()
    data_dir = tracking_data_dir(paths, inputs.as_of_date)
    output_dir = tracking_output_dir(paths, inputs.as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = _artifact_paths(data_dir, output_dir)

    write_json(artifacts["tracking_config"], config.to_dict())
    valuation_prices = build_valuation_prices(inputs)
    ledgers = {
        key: build_paper_ledger(
            inputs=inputs,
            config=config,
            portfolio_key=key,
            valuation_prices=valuation_prices,
            created_at=generated_at,
        )
        for key in PORTFOLIO_KEYS
    }
    for key, ledger in ledgers.items():
        write_json(artifacts[f"{key}_paper_ledger"], ledger)

    nav_records = {key: calculate_nav(portfolio_key=key, ledger=ledgers[key], config=config) for key in PORTFOLIO_KEYS}
    holdings_snapshots = {
        key: build_holdings_snapshot(
            portfolio_key=key,
            ledger=ledgers[key],
            source_rows=inputs.portfolios[key],
            config=config,
        )
        for key in PORTFOLIO_KEYS
    }
    for key, snapshot in holdings_snapshots.items():
        write_json(artifacts[f"{key}_holdings_snapshot"], snapshot)

    nav_snapshot = build_nav_snapshot(config, nav_records)
    performance_snapshot = build_performance_snapshot(config, nav_records)
    drawdown_snapshot = build_drawdown_snapshot(config, nav_records)
    exposure_snapshot = build_exposure_snapshot(config, holdings_snapshots)
    benchmark_snapshot = build_benchmark_comparison_snapshot(config=config, performance_snapshot=performance_snapshot)
    write_json(artifacts["portfolio_nav_snapshot"], nav_snapshot)
    write_json(artifacts["portfolio_performance_snapshot"], performance_snapshot)
    write_json(artifacts["portfolio_drawdown_snapshot"], drawdown_snapshot)
    write_json(artifacts["portfolio_exposure_snapshot"], exposure_snapshot)
    write_json(artifacts["benchmark_comparison_snapshot"], benchmark_snapshot)

    source_trace = build_tracking_source_trace(paths=paths, inputs=inputs, artifacts=artifacts, generated_at=generated_at)
    write_json(artifacts["tracking_source_trace"], source_trace)
    tracking_summary = _tracking_summary(
        paths=paths,
        inputs=inputs,
        config=config,
        artifacts=artifacts,
        generated_at=generated_at,
        ledgers=ledgers,
        nav_snapshot=nav_snapshot,
        performance_snapshot=performance_snapshot,
        drawdown_snapshot=drawdown_snapshot,
        exposure_snapshot=exposure_snapshot,
        benchmark_snapshot=benchmark_snapshot,
        source_trace=source_trace,
    )
    write_json(artifacts["tracking_summary"], tracking_summary)

    payload = {
        "builder_id": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-BUILDER",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "tracking_config": config.to_dict(),
        "long_paper_ledger": ledgers["long"],
        "mid_paper_ledger": ledgers["mid"],
        "short_paper_ledger": ledgers["short"],
        "long_holdings_snapshot": holdings_snapshots["long"],
        "mid_holdings_snapshot": holdings_snapshots["mid"],
        "short_holdings_snapshot": holdings_snapshots["short"],
        "portfolio_nav_snapshot": nav_snapshot,
        "portfolio_performance_snapshot": performance_snapshot,
        "portfolio_drawdown_snapshot": drawdown_snapshot,
        "portfolio_exposure_snapshot": exposure_snapshot,
        "benchmark_comparison_snapshot": benchmark_snapshot,
        "tracking_source_trace": source_trace,
        "tracking_summary": tracking_summary,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    reports = write_tracking_reports(output_dir, payload)
    payload["reports"] = reports

    manifest = build_tracking_manifest(paths=paths, inputs=inputs, artifacts=artifacts, generated_at=generated_at)
    write_json(artifacts["tracking_manifest"], manifest)
    payload["tracking_manifest"] = manifest
    return json_safe(payload)


def _artifact_paths(data_dir: Path, output_dir: Path) -> dict[str, Path]:
    artifacts = {key: data_dir / filename for key, filename in TRACKING_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in TRACKING_REPORTS.items()})
    return artifacts


def _tracking_summary(
    *,
    paths: ProjectPaths,
    inputs,
    config: TrackingConfig,
    artifacts: dict[str, Path],
    generated_at: str,
    ledgers: dict[str, list[dict[str, Any]]],
    nav_snapshot: dict[str, Any],
    performance_snapshot: dict[str, Any],
    drawdown_snapshot: dict[str, Any],
    exposure_snapshot: dict[str, Any],
    benchmark_snapshot: dict[str, Any],
    source_trace: dict[str, Any],
) -> dict[str, Any]:
    portfolios = {}
    for key in PORTFOLIO_KEYS:
        nav = nav_snapshot["portfolios"][key]
        performance = performance_snapshot["portfolios"][key]
        drawdown = drawdown_snapshot["portfolios"][key]
        exposure = exposure_snapshot["portfolios"][key]
        portfolios[key] = {
            "portfolio_nav": nav["portfolio_nav"],
            "cash_balance": nav["cash_balance"],
            "gross_exposure": nav["gross_exposure"],
            "net_exposure": nav["net_exposure"],
            "daily_return": performance["daily_return"],
            "cumulative_return": performance["cumulative_return"],
            "max_drawdown": drawdown["max_drawdown"],
            "portfolio_volatility_if_enough_history": performance["portfolio_volatility_if_enough_history"],
            "holding_count": nav["holding_count"],
            "weight_sum": nav["weight_sum"],
            "max_single_weight": nav["max_single_weight"],
            "max_industry_weight": exposure["max_industry_weight"],
            "industry_exposure": exposure["industry_exposure"],
            "risk_score_weighted_avg": exposure["risk_score_weighted_avg"],
            "liquidity_score_weighted_avg": exposure["liquidity_score_weighted_avg"],
            "long_score_weighted_avg": exposure["long_score_weighted_avg"],
            "mid_score_weighted_avg": exposure["mid_score_weighted_avg"],
            "short_score_weighted_avg": exposure["short_score_weighted_avg"],
            "composite_score_weighted_avg": exposure["composite_score_weighted_avg"],
        }
    return {
        "tracking_id": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": inputs.as_of_date,
        "requested_as_of_date": inputs.requested_as_of_date,
        "generated_at": generated_at,
        "ledger_start_date": config.ledger_start_date,
        "initial_virtual_capital": {key: config.initial_capital(key) for key in PORTFOLIO_KEYS},
        "counts": {
            f"{key}_holdings": int(nav_snapshot["portfolios"][key]["holding_count"])
            for key in PORTFOLIO_KEYS
        }
        | {f"{key}_ledger_records": len(ledgers[key]) for key in PORTFOLIO_KEYS},
        "portfolios": portfolios,
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        "benchmark_data_available": benchmark_snapshot["benchmark_data_available"],
        "source_trace_complete": source_trace["source_trace_complete"],
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "warnings": _warnings(benchmark_snapshot),
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _warnings(benchmark_snapshot: dict[str, Any]) -> list[str]:
    warnings = []
    if not benchmark_snapshot.get("benchmark_data_available"):
        warnings.append(str(benchmark_snapshot.get("benchmark_gap_reason") or "benchmark data unavailable"))
    return warnings
