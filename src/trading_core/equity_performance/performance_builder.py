"""Build v0.7.11 A-share multi-day performance artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_performance.drawdown_series import build_portfolio_drawdown_series
from trading_core.equity_performance.holding_mark_to_market import build_holding_mark_to_market_series, holding_records_from_tracking_snapshot
from trading_core.equity_performance.nav_series import build_portfolio_nav_series, merge_series_records, nav_records_from_tracking_snapshot
from trading_core.equity_performance.performance_append_log import build_performance_append_log
from trading_core.equity_performance.performance_config import (
    APPEND_MODE,
    CURRENT_SNAPSHOT_MODE,
    DEFAULT_AS_OF_DATE,
    DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    DEFAULT_ROLLING_WINDOW_DAYS,
    DEFAULT_TRACKING_START_DATE,
    PERFORMANCE_FILES,
    REBUILD_MODE,
    PerformanceConfig,
    performance_artifact_paths,
    performance_data_dir,
    performance_output_dir,
    validate_performance_config,
)
from trading_core.equity_performance.performance_data_availability import build_performance_data_availability
from trading_core.equity_performance.performance_inputs import (
    PerformanceInputs,
    available_tracking_snapshot_dates,
    load_performance_inputs,
    load_tracking_snapshot_for_date,
)
from trading_core.equity_performance.performance_limitations import build_performance_limitations
from trading_core.equity_performance.performance_manifest import build_performance_boundary_check, build_performance_manifest, build_performance_summary
from trading_core.equity_performance.performance_metrics import build_performance_metric_snapshot
from trading_core.equity_performance.performance_report import write_performance_reports
from trading_core.equity_performance.performance_source_trace import build_performance_source_trace
from trading_core.equity_performance.relative_performance import build_relative_performance_series
from trading_core.equity_performance.return_series import build_portfolio_return_series
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_multi_day_performance(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    tracking_start_date: str = DEFAULT_TRACKING_START_DATE,
    mode: str = CURRENT_SNAPSHOT_MODE,
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    rolling_window_days: int = DEFAULT_ROLLING_WINDOW_DAYS,
    allow_rebuild: bool = False,
    allow_historical_reconstruction: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = PerformanceConfig(
        as_of_date=as_of_date,
        tracking_start_date=tracking_start_date,
        mode=mode,
        minimum_required_observations=minimum_required_observations,
        rolling_window_days=rolling_window_days,
        allow_rebuild=allow_rebuild,
        allow_historical_reconstruction=allow_historical_reconstruction,
    )
    issues = validate_performance_config(config)
    if issues:
        raise ValueError("; ".join(issues))

    inputs = load_performance_inputs(paths=paths, as_of_date=as_of_date)
    generated_at = utc_now()
    data_dir = performance_data_dir(paths, as_of_date)
    output_dir = performance_output_dir(paths, as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = performance_artifact_paths(paths, as_of_date)

    write_json(artifacts["performance_config"], config.to_dict())
    nav_records, holding_records, append_meta = _records_for_mode(paths=paths, config=config, inputs=inputs)
    nav_series = build_portfolio_nav_series(config, nav_records)
    return_series = build_portfolio_return_series(config, nav_series["records"])
    drawdown_series = build_portfolio_drawdown_series(config, nav_series["records"])
    relative_series, benchmark_relative_series = build_relative_performance_series(
        config=config,
        return_series=return_series,
        drawdown_series=drawdown_series,
        benchmark_nav_snapshot=inputs.benchmark_artifacts["benchmark_nav_snapshot"],
    )
    holding_series = build_holding_mark_to_market_series(config, holding_records)
    data_availability = build_performance_data_availability(
        config=config,
        inputs=inputs,
        nav_series=nav_series,
        benchmark_nav_snapshot=inputs.benchmark_artifacts["benchmark_nav_snapshot"],
    )
    metric_snapshot = build_performance_metric_snapshot(
        config=config,
        return_series=return_series,
        drawdown_series=drawdown_series,
        relative_series=relative_series,
    )
    limitations = build_performance_limitations(config, data_availability)
    warnings = _warnings(data_availability=data_availability, holding_series=holding_series)
    append_log = build_performance_append_log(
        config=config,
        existing_dates=append_meta["existing_dates"],
        appended_dates=append_meta["appended_dates"],
        duplicate_dates=append_meta["duplicate_dates"],
        idempotent_dates=append_meta["idempotent_dates"],
        rebuilt_dates=append_meta["rebuilt_dates"],
        generated_at=generated_at,
    )
    boundary_check = build_performance_boundary_check(paths=paths, as_of_date=as_of_date, warnings=warnings, blocking_reasons=[])
    manifest = build_performance_manifest(
        paths=paths,
        config=config,
        generated_at=generated_at,
        artifacts=artifacts,
        data_availability=data_availability,
        boundary_check=boundary_check,
    )
    summary = build_performance_summary(
        config=config,
        nav_series=nav_series,
        return_series=return_series,
        drawdown_series=drawdown_series,
        relative_series=relative_series,
        data_availability=data_availability,
        boundary_check=boundary_check,
        warnings=warnings,
    )

    core_payloads = {
        "performance_data_availability": data_availability,
        "portfolio_nav_series": nav_series,
        "portfolio_return_series": return_series,
        "portfolio_drawdown_series": drawdown_series,
        "portfolio_relative_performance_series": relative_series,
        "portfolio_benchmark_relative_series": benchmark_relative_series,
        "holding_mark_to_market_series": holding_series,
        "performance_metric_snapshot": metric_snapshot,
        "performance_limitations": limitations,
        "performance_append_log": append_log,
        "performance_manifest": manifest,
        "performance_boundary_check": boundary_check,
        "performance_summary": summary,
    }
    for key, payload in core_payloads.items():
        write_json(artifacts[key], payload)

    source_trace = build_performance_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        input_paths=inputs.input_paths,
        price_panel_paths=inputs.price_panel_paths,
        output_artifacts=artifacts,
        limitations=limitations,
        assumptions=[
            "Only existing virtual tracking snapshots are used for portfolio observations.",
            "Historical benchmark data is not used to fabricate portfolio history.",
            "First-day initialization remains separate from observed multi-day performance.",
        ],
    )
    write_json(artifacts["performance_source_trace"], source_trace)

    payload = {
        "builder_id": "A-SHARE-MULTI-DAY-PERFORMANCE-BUILDER",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "performance_config": config.to_dict(),
        **core_payloads,
        "performance_source_trace": source_trace,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
    }
    reports = write_performance_reports(output_dir, payload)
    payload["reports"] = reports
    return json_safe(payload)


def _records_for_mode(*, paths: ProjectPaths, config: PerformanceConfig, inputs: PerformanceInputs) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, list[str]]]:
    current_nav = nav_records_from_tracking_snapshot(
        config=config,
        tracking_snapshot=inputs.tracking_artifacts,
        snapshot_date=config.as_of_date,
        source_tracking_snapshot=f"data/equity_portfolio_tracking/daily/{config.as_of_date}/portfolio_nav_snapshot.json",
    )
    current_holdings = holding_records_from_tracking_snapshot(
        config=config,
        tracking_snapshot=inputs.tracking_artifacts,
        snapshot_date=config.as_of_date,
        source_ledgers={
            "long": f"data/equity_portfolio_tracking/daily/{config.as_of_date}/long_paper_ledger.json",
            "mid": f"data/equity_portfolio_tracking/daily/{config.as_of_date}/mid_paper_ledger.json",
            "short": f"data/equity_portfolio_tracking/daily/{config.as_of_date}/short_paper_ledger.json",
        },
    )
    if config.mode == CURRENT_SNAPSHOT_MODE:
        return current_nav, current_holdings, _append_meta(appended_dates=[config.as_of_date])

    if config.mode == APPEND_MODE:
        existing_nav = _load_existing_series_records(paths, config=config, artifact_key="portfolio_nav_series")
        existing_holdings = _load_existing_series_records(paths, config=config, artifact_key="holding_mark_to_market_series")
        merged_nav, duplicate_dates, idempotent_dates = merge_series_records(
            existing=existing_nav,
            incoming=current_nav,
            allow_idempotent_append=config.allow_idempotent_append,
        )
        merged_holdings, holding_duplicates, holding_idempotent = merge_series_records(
            existing=existing_holdings,
            incoming=current_holdings,
            allow_idempotent_append=config.allow_idempotent_append,
            key_fields=("portfolio_id", "symbol", "as_of_date"),
        )
        existing_dates = sorted({str(row.get("as_of_date")) for row in existing_nav if row.get("as_of_date")})
        return merged_nav, merged_holdings, _append_meta(
            existing_dates=existing_dates,
            appended_dates=[config.as_of_date],
            duplicate_dates=duplicate_dates + holding_duplicates,
            idempotent_dates=idempotent_dates + holding_idempotent,
        )

    if config.mode == REBUILD_MODE:
        dates = available_tracking_snapshot_dates(paths, start_date=config.tracking_start_date, as_of_date=config.as_of_date)
        if len(dates) > 1 and not config.allow_historical_reconstruction:
            raise ValueError("multiple-day historical reconstruction requires allow_historical_reconstruction=true")
        nav_records: list[dict[str, Any]] = []
        holding_records: list[dict[str, Any]] = []
        for day in dates:
            snapshot = load_tracking_snapshot_for_date(paths, day)
            nav_records.extend(
                nav_records_from_tracking_snapshot(
                    config=config,
                    tracking_snapshot=snapshot,
                    snapshot_date=day,
                    source_tracking_snapshot=f"data/equity_portfolio_tracking/daily/{day}/portfolio_nav_snapshot.json",
                )
            )
            holding_records.extend(
                holding_records_from_tracking_snapshot(
                    config=config,
                    tracking_snapshot=snapshot,
                    snapshot_date=day,
                    source_ledgers={
                        "long": f"data/equity_portfolio_tracking/daily/{day}/long_paper_ledger.json",
                        "mid": f"data/equity_portfolio_tracking/daily/{day}/mid_paper_ledger.json",
                        "short": f"data/equity_portfolio_tracking/daily/{day}/short_paper_ledger.json",
                    },
                )
            )
        return nav_records, holding_records, _append_meta(rebuilt_dates=dates)

    raise ValueError(f"unsupported performance mode: {config.mode}")


def _load_existing_series_records(paths: ProjectPaths, *, config: PerformanceConfig, artifact_key: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    base = paths.data_dir / "equity_performance" / "daily"
    if not base.exists():
        return []
    filename = PERFORMANCE_FILES[artifact_key]
    for child in sorted(base.iterdir()):
        if not child.is_dir() or child.name < config.tracking_start_date or child.name > config.as_of_date:
            continue
        path = child / filename
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.extend(row for row in payload.get("records", []) if config.tracking_start_date <= str(row.get("as_of_date")) <= config.as_of_date)
    return records


def _append_meta(
    *,
    existing_dates: list[str] | None = None,
    appended_dates: list[str] | None = None,
    duplicate_dates: list[str] | None = None,
    idempotent_dates: list[str] | None = None,
    rebuilt_dates: list[str] | None = None,
) -> dict[str, list[str]]:
    return {
        "existing_dates": sorted(set(existing_dates or [])),
        "appended_dates": sorted(set(appended_dates or [])),
        "duplicate_dates": sorted(set(duplicate_dates or [])),
        "idempotent_dates": sorted(set(idempotent_dates or [])),
        "rebuilt_dates": sorted(set(rebuilt_dates or [])),
    }


def _warnings(*, data_availability: dict[str, Any], holding_series: dict[str, Any]) -> list[str]:
    warnings = []
    if data_availability.get("insufficient_history"):
        warnings.append("portfolio observation history is below the minimum required window")
    if holding_series.get("forbidden_fields_present"):
        warnings.append("holding mark-to-market contains forbidden fields")
    return sorted(set(warnings))
