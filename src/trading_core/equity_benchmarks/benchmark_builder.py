"""Build v0.7.10 A-share benchmark comparison artifacts."""

from __future__ import annotations

from typing import Any

import pandas as pd

from trading_core.equity_benchmarks.benchmark_config import (
    BENCHMARK_FLAGS,
    BENCHMARK_IDS,
    DEFAULT_AS_OF_DATE,
    INDEX_BENCHMARK_IDS,
    BenchmarkConfig,
    benchmark_artifact_paths,
    benchmark_data_dir,
    benchmark_output_dir,
    validate_benchmark_config,
)
from trading_core.equity_benchmarks.benchmark_inputs import load_benchmark_inputs
from trading_core.equity_benchmarks.benchmark_manifest import build_benchmark_boundary_check, build_benchmark_manifest, build_benchmark_summary
from trading_core.equity_benchmarks.benchmark_nav import build_benchmark_nav_records
from trading_core.equity_benchmarks.benchmark_report import write_benchmark_reports
from trading_core.equity_benchmarks.benchmark_returns import returns_from_price_frame
from trading_core.equity_benchmarks.benchmark_source_trace import build_benchmark_source_trace
from trading_core.equity_benchmarks.cash_benchmark import build_cash_benchmark_returns
from trading_core.equity_benchmarks.equal_weight_benchmark import build_equal_weight_benchmark
from trading_core.equity_benchmarks.index_benchmarks import availability_from_index_prices, load_index_benchmark_prices
from trading_core.equity_benchmarks.portfolio_comparison import build_portfolio_benchmark_comparison
from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_benchmark_comparison(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    lookback_trading_days: int = 250,
    minimum_required_trading_days: int = 20,
    allow_placeholder_benchmarks: bool = False,
    fail_on_placeholder_benchmarks: bool = True,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = BenchmarkConfig(
        as_of_date=as_of_date,
        lookback_trading_days=lookback_trading_days,
        minimum_required_trading_days=minimum_required_trading_days,
        allow_placeholder_benchmarks=allow_placeholder_benchmarks,
        fail_on_placeholder_benchmarks=fail_on_placeholder_benchmarks,
    )
    issues = validate_benchmark_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    inputs = load_benchmark_inputs(paths=paths, as_of_date=as_of_date, lookback_trading_days=lookback_trading_days)
    generated_at = utc_now()
    data_dir = benchmark_data_dir(paths, as_of_date)
    output_dir = benchmark_output_dir(paths, as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = benchmark_artifact_paths(paths, as_of_date)
    write_json(artifacts["benchmark_config"], config.to_dict())

    index_prices, index_source_meta = load_index_benchmark_prices(paths=paths, config=config, generated_at=generated_at)
    index_availability = availability_from_index_prices(index_prices, config=config, source_meta=index_source_meta)
    missing_index = [row["benchmark_id"] for row in index_availability if row["status"] != "available" and row["status"] != "placeholder_allowed"]
    placeholder_index = [row["benchmark_id"] for row in index_availability if row.get("is_placeholder")]
    if (missing_index or placeholder_index) and fail_on_placeholder_benchmarks:
        raise ValueError(f"index benchmark data unavailable or placeholder: missing={missing_index}; placeholder={placeholder_index}")

    index_return_records = returns_from_price_frame(index_prices)
    benchmark_dates = sorted({row["date"] for row in index_return_records if row["date"] <= as_of_date})
    cash_records, cash_availability = build_cash_benchmark_returns(benchmark_dates, config=config)
    strict_records, strict_availability, strict_exclusions = build_equal_weight_benchmark(
        benchmark_id="EQUAL_WEIGHT_STRICT_TRADABLE",
        symbols=inputs.strict_tradable_symbols,
        adjusted_prices=inputs.adjusted_prices,
        daily_prices=inputs.daily_prices,
        config=config,
    )
    candidate_records, candidate_availability, candidate_exclusions = build_equal_weight_benchmark(
        benchmark_id="EQUAL_WEIGHT_CANDIDATE_POOL",
        symbols=inputs.candidate_symbols,
        adjusted_prices=inputs.adjusted_prices,
        daily_prices=inputs.daily_prices,
        config=config,
    )

    return_records = index_return_records + cash_records + strict_records + candidate_records
    nav_records = build_benchmark_nav_records(return_records)
    availability = index_availability + [cash_availability, strict_availability, candidate_availability]
    warnings = _availability_warnings(availability)
    price_snapshot = _price_snapshot(config=config, index_prices=index_prices, nav_records=nav_records, availability=availability)
    return_snapshot = _return_snapshot(config=config, records=return_records)
    nav_snapshot = _nav_snapshot(config=config, records=nav_records)
    universe_snapshot = _universe_snapshot(config=config, inputs=inputs, strict_exclusions=strict_exclusions, candidate_exclusions=candidate_exclusions)
    exclusion_report = {
        "report_id": "A-SHARE-BENCHMARK-EXCLUSION-REPORT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": as_of_date,
        "benchmarks": [strict_exclusions, candidate_exclusions],
    }
    comparison, relative_snapshot = build_portfolio_benchmark_comparison(
        config=config,
        portfolio_performance_snapshot=inputs.tracking_artifacts["portfolio_performance_snapshot"],
        nav_records=nav_records,
    )
    boundary_check = build_benchmark_boundary_check(paths=paths, as_of_date=as_of_date, warnings=warnings, blocking_reasons=[])
    data_availability = {
        "availability_id": "A-SHARE-BENCHMARK-DATA-AVAILABILITY",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": as_of_date,
        "benchmarks": availability,
        "all_required_benchmarks_available": all(row["status"] == "available" for row in availability),
        "placeholder_benchmarks_used": [row["benchmark_id"] for row in availability if row.get("is_placeholder")],
        **BENCHMARK_FLAGS,
    }

    core_payloads = {
        "benchmark_data_availability": data_availability,
        "benchmark_universe_snapshot": universe_snapshot,
        "benchmark_price_snapshot": price_snapshot,
        "benchmark_return_snapshot": return_snapshot,
        "benchmark_nav_snapshot": nav_snapshot,
        "portfolio_benchmark_comparison": comparison,
        "relative_performance_snapshot": relative_snapshot,
        "benchmark_exclusion_report": exclusion_report,
        "benchmark_boundary_check": boundary_check,
    }
    for key, payload in core_payloads.items():
        write_json(artifacts[key], payload)

    manifest = build_benchmark_manifest(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        artifacts=artifacts,
        availability=availability,
        comparison=comparison,
    )
    summary = build_benchmark_summary(
        as_of_date=as_of_date,
        availability=availability,
        comparison=comparison,
        boundary_check=boundary_check,
        warnings=warnings,
    )
    write_json(artifacts["benchmark_manifest"], manifest)
    write_json(artifacts["benchmark_summary"], summary)
    trace = build_benchmark_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        input_paths=inputs.input_paths,
        output_artifacts=artifacts,
        index_source_meta=index_source_meta,
    )
    write_json(artifacts["benchmark_source_trace"], trace)

    payload = {
        "builder_id": "A-SHARE-BENCHMARK-COMPARISON-BUILDER",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "benchmark_config": config.to_dict(),
        "benchmark_data_availability": data_availability,
        "benchmark_universe_snapshot": universe_snapshot,
        "benchmark_price_snapshot": price_snapshot,
        "benchmark_return_snapshot": return_snapshot,
        "benchmark_nav_snapshot": nav_snapshot,
        "portfolio_benchmark_comparison": comparison,
        "relative_performance_snapshot": relative_snapshot,
        "benchmark_exclusion_report": exclusion_report,
        "benchmark_source_trace": trace,
        "benchmark_manifest": manifest,
        "benchmark_boundary_check": boundary_check,
        "benchmark_summary": summary,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        **BENCHMARK_FLAGS,
    }
    reports = write_benchmark_reports(output_dir, payload)
    payload["reports"] = reports
    return json_safe(payload)


def _availability_warnings(availability: list[dict[str, Any]]) -> list[str]:
    warnings = []
    for row in availability:
        if row["status"] != "available":
            warnings.append(f"{row['benchmark_id']} status={row['status']}")
        elif row["trading_days_available"] < 20:
            warnings.append(f"{row['benchmark_id']} limited benchmark history")
    warnings.append("portfolio relative metrics limited by first-day initialization")
    return sorted(set(warnings))


def _price_snapshot(*, config: BenchmarkConfig, index_prices: pd.DataFrame, nav_records: list[dict[str, Any]], availability: list[dict[str, Any]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    if not index_prices.empty:
        for _, row in index_prices.iterrows():
            records.append(
                {
                    "benchmark_id": row["benchmark_id"],
                    "date": row["date"],
                    "close": row["close"],
                    "symbol_or_index_code": row.get("symbol_or_index_code"),
                    "source_type": row.get("source_type"),
                    "is_placeholder": bool(row.get("is_placeholder", False)),
                }
            )
    nav_as_price = {(row["benchmark_id"], row["date"]): row for row in nav_records if row["benchmark_id"] not in INDEX_BENCHMARK_IDS}
    for row in nav_as_price.values():
        records.append(
            {
                "benchmark_id": row["benchmark_id"],
                "date": row["date"],
                "close": row["benchmark_nav"],
                "symbol_or_index_code": "synthetic_nav_price",
                "source_type": "benchmark_return_nav_series",
                "is_placeholder": bool(row.get("is_placeholder", False)),
            }
        )
    return {
        "snapshot_id": "A-SHARE-BENCHMARK-PRICE-SNAPSHOT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "records": sorted(records, key=lambda item: (item["benchmark_id"], item["date"])),
        "availability": {row["benchmark_id"]: row["status"] for row in availability},
        **BENCHMARK_FLAGS,
    }


def _return_snapshot(*, config: BenchmarkConfig, records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "snapshot_id": "A-SHARE-BENCHMARK-RETURN-SNAPSHOT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "records": sorted(records, key=lambda item: (item["benchmark_id"], item["date"])),
        **BENCHMARK_FLAGS,
    }


def _nav_snapshot(*, config: BenchmarkConfig, records: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {}
    for benchmark_id in BENCHMARK_IDS:
        rows = [row for row in records if row["benchmark_id"] == benchmark_id]
        if rows:
            summary[benchmark_id] = {
                "first_day_nav": rows[0]["first_day_nav"],
                "as_of_nav": rows[-1]["benchmark_nav"],
                "available_trading_days": len(rows),
                "benchmark_cumulative_return": rows[-1]["benchmark_cumulative_return"],
            }
    return {
        "snapshot_id": "A-SHARE-BENCHMARK-NAV-SNAPSHOT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "base_nav": 1.0,
        "summary": summary,
        "records": sorted(records, key=lambda item: (item["benchmark_id"], item["date"])),
        **BENCHMARK_FLAGS,
    }


def _universe_snapshot(*, config: BenchmarkConfig, inputs, strict_exclusions: dict[str, Any], candidate_exclusions: dict[str, Any]) -> dict[str, Any]:
    return {
        "snapshot_id": "A-SHARE-BENCHMARK-UNIVERSE-SNAPSHOT",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": config.as_of_date,
        "benchmark_ids": list(BENCHMARK_IDS),
        "strict_tradable_universe": {
            "source_rows": len(inputs.strict_tradable_rows),
            "filter_passed_symbols": len(inputs.strict_tradable_symbols),
            "constituent_count": strict_exclusions["constituent_count"],
            "excluded_constituent_count": strict_exclusions["excluded_constituent_count"],
        },
        "candidate_pool": {
            "source_files": {key: len(rows) for key, rows in inputs.candidate_rows.items()},
            "unique_symbols": len(inputs.candidate_symbols),
            "constituent_count": candidate_exclusions["constituent_count"],
            "excluded_constituent_count": candidate_exclusions["excluded_constituent_count"],
        },
        "index_code_map": config.to_dict()["index_code_map"],
        "cash_benchmark": {"daily_return": 0.0},
        **BENCHMARK_FLAGS,
    }
