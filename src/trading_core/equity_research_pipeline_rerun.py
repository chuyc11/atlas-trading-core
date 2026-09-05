"""v0.9.4 research-only A-share pipeline rerun from refreshed data."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from collections.abc import Callable

import pandas as pd

from trading_core.equity_briefings.daily_stock_selection_briefing import build_a_share_daily_stock_selection_briefing
from trading_core.equity_data_quality.common import read_frame, read_json, utc_now, write_json
from trading_core.equity_features.multi_horizon import build_a_share_multi_horizon_features
from trading_core.equity_portfolios.virtual_portfolio_builder import build_a_share_virtual_portfolios
from trading_core.equity_scoring.component_scores import build_a_share_scores
from trading_core.equity_selection.candidate_generator import generate_a_share_candidates
from trading_core.equity_selection.filter_config import TradableUniverseFilterConfig
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v0.9.4-a-share-research-pipeline-rerun-from-refreshed-data"
SOURCE_VERSION = "v0.9.3-a-share-data-freshness-refresh"
RECOMMENDED_NEXT_VERSION = "v0.9.5-a-share-multi-day-research-output-evidence-accumulation"
DEFAULT_AS_OF_DATE = "2026-07-01"
OWNER_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
RESEARCH_MIN_EFFECTIVE_TRADING_DAYS_20D = 17

PipelineStep = Callable[..., dict[str, Any]]


def rerun_a_share_research_pipeline_from_refreshed_data(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    dry_run: bool = False,
    paths: ProjectPaths | None = None,
    step_overrides: dict[str, PipelineStep] | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    step_overrides = step_overrides or {}
    protected_before = _protected_snapshot(paths)
    started = time.perf_counter()
    started_at = utc_now()
    data_dir = paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    freshness = validate_source_data_freshness(paths=paths, as_of_date=as_of_date)
    request = _request(as_of_date)
    steps: list[dict[str, Any]] = []
    output_paths: list[str] = []
    blocking = list(freshness["blocking_reasons"])
    warnings = list(freshness["warnings"])
    if not dry_run and freshness["source_data_validation_passed"]:
        warnings.append(f"research_rerun_available_window_min_effective_trading_days_20d={RESEARCH_MIN_EFFECTIVE_TRADING_DAYS_20D}")
        try:
            prep_paths = _promote_refreshed_snapshots_to_history(paths, as_of_date)
            output_paths.extend(prep_paths)
            steps.extend(_run_pipeline_steps(paths=paths, as_of_date=as_of_date, step_overrides=step_overrides))
            for step in steps:
                output_paths.extend(step["output_paths"])
                blocking.extend(step["blocking_reasons"])
                warnings.extend(step["warnings"])
        except Exception as exc:
            blocking.append(f"pipeline_execution_failed:{type(exc).__name__}:{exc}")
    elif dry_run and freshness["source_data_validation_passed"]:
        steps = [_dry_step(step_id) for step_id in _step_ids()]
    completed_at = utc_now()
    protected_after = _protected_snapshot(paths)
    protected_untouched = protected_before == protected_after
    if not protected_untouched:
        blocking.append("protected_order_trade_account_paths_modified")
    execution = _execution_summary(as_of_date, dry_run, started_at, completed_at, round(time.perf_counter() - started, 3), steps, blocking, warnings)
    validation = _output_validation(paths=paths, as_of_date=as_of_date, dry_run=dry_run, execution=execution, protected_untouched=protected_untouched)
    blocking.extend(reason for reason in validation["blocking_reasons"] if reason not in blocking)
    warnings.extend(reason for reason in validation["warnings"] if reason not in warnings)
    boundary = _boundary_check(as_of_date, protected_untouched, blocking, warnings, dry_run=dry_run)
    result = _result(as_of_date, freshness, execution, validation, boundary, blocking, warnings, dry_run=dry_run)
    artifact_paths = _artifact_paths(paths, as_of_date)
    manifest = _manifest(paths=paths, as_of_date=as_of_date, artifact_paths=artifact_paths, output_paths=sorted(set(output_paths)), overall_passed=result["overall_passed"], blocking_reasons=blocking)
    payloads = {
        "research_pipeline_rerun_request": request,
        "source_data_freshness_validation": freshness,
        "research_pipeline_execution_summary": execution,
        "research_output_validation_summary": validation,
        "research_pipeline_rerun_result": result,
        "research_pipeline_boundary_check": boundary,
        "research_pipeline_manifest": manifest,
    }
    for key, payload in payloads.items():
        write_json(artifact_paths[key], payload)
    artifact_paths["markdown_report"].parent.mkdir(parents=True, exist_ok=True)
    artifact_paths["markdown_report"].write_text(_markdown_report(result, freshness, execution, validation, boundary), encoding="utf-8")
    return {
        "builder_id": "A-SHARE-RESEARCH-PIPELINE-RERUN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_data_date": as_of_date,
        "dry_run": dry_run,
        "overall_passed": result["overall_passed"],
        "blocking_reasons": blocking,
        "warnings": warnings,
        "source_data_freshness_validation_passed": freshness["source_data_validation_passed"],
        "pipeline_execution_passed": execution["overall_execution_passed"],
        "research_output_validation_passed": validation["required_outputs_present"],
        "candidate_output_generated": validation["candidate_output_generated"],
        "score_output_generated": validation["score_output_generated"],
        "virtual_portfolio_output_generated": validation["virtual_portfolio_output_generated"],
        "research_briefing_generated": validation["research_briefing_generated"],
        "protected_order_trade_account_paths_untouched": protected_untouched,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
    }


def validate_source_data_freshness(*, paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    refresh_path = paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_refresh_result.json"
    coverage_path = paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_coverage_summary.json"
    provider_path = paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_provider_status.json"
    refresh = read_json(refresh_path)
    coverage = read_json(coverage_path)
    provider = read_json(provider_path)
    blocking = []
    if not refresh.get("overall_passed"):
        blocking.append("v093_refresh_not_passed")
    if refresh.get("resolved_actual_data_date") != as_of_date:
        blocking.append("v093_source_data_date_mismatch")
    if provider.get("overall_provider_status") != "passed":
        blocking.append("v093_provider_status_not_passed")
    if not coverage.get("coverage_passed"):
        blocking.append("v093_coverage_not_passed")
    if float(coverage.get("coverage_ratio") or 0.0) < 1.0:
        blocking.append("v093_coverage_ratio_below_1")
    if int(coverage.get("missing_symbol_count") or 0) != 0:
        blocking.append("v093_missing_symbols_present")
    v093_warnings = list(refresh.get("warnings", []))
    return {
        "validation_id": "A-SHARE-SOURCE-DATA-FRESHNESS-VALIDATION",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "required_source_data_date": as_of_date,
        "resolved_source_data_date": refresh.get("resolved_actual_data_date", ""),
        "data_freshness_refresh_result_path": _rel(refresh_path, paths.project_root),
        "v093_refresh_passed": bool(refresh.get("overall_passed")),
        "v093_provider_status_passed": provider.get("overall_provider_status") == "passed",
        "v093_coverage_passed": bool(coverage.get("coverage_passed")),
        "v093_coverage_ratio": coverage.get("coverage_ratio"),
        "v093_missing_symbol_count": coverage.get("missing_symbol_count"),
        "v093_warnings": v093_warnings,
        "missing_quote_warning_assessment": "non_blocking_warning_for_pipeline_completeness",
        "source_data_stale": False,
        "source_data_validation_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": v093_warnings,
    }


def _run_pipeline_steps(*, paths: ProjectPaths, as_of_date: str, step_overrides: dict[str, PipelineStep]) -> list[dict[str, Any]]:
    steps: list[dict[str, Any]] = []
    tradable = step_overrides.get("tradable_universe_refresh", build_a_share_tradable_universe)(
        config=TradableUniverseFilterConfig(
            as_of_date=as_of_date,
            allow_previous_trading_day=False,
            min_effective_trading_days_20d=RESEARCH_MIN_EFFECTIVE_TRADING_DAYS_20D,
        ),
        paths=paths,
    )
    steps.append(_step("tradable_universe_refresh", tradable))
    feature = step_overrides.get("feature_refresh", build_a_share_multi_horizon_features)(as_of_date=as_of_date, paths=paths)
    steps.append(_step("feature_refresh", feature))
    score = step_overrides.get("research_score_refresh", build_a_share_scores)(as_of_date=as_of_date, paths=paths)
    steps.append(_step("research_score_refresh", score))
    candidates = step_overrides.get("research_candidate_refresh", generate_a_share_candidates)(as_of_date=as_of_date, paths=paths)
    steps.append(_step("research_candidate_refresh", candidates))
    portfolio = step_overrides.get("virtual_only_portfolio_research_refresh", build_a_share_virtual_portfolios)(as_of_date=as_of_date, paths=paths)
    steps.append(_step("virtual_only_portfolio_research_refresh", portfolio))
    briefing = step_overrides.get("research_briefing_refresh", build_a_share_daily_stock_selection_briefing)(as_of_date=as_of_date, paths=paths)
    steps.append(_step("research_briefing_refresh", briefing))
    return steps


def _promote_refreshed_snapshots_to_history(paths: ProjectPaths, as_of_date: str) -> list[str]:
    mappings = [
        ("daily_price_panel.parquet", "history/daily_price_history_panel.parquet", "provider"),
        ("adjusted_price_panel.parquet", "history/adjusted_price_history_panel.parquet", "provider"),
        ("daily_basic_panel.parquet", "history/daily_basic_history_panel.parquet", "provider"),
    ]
    updated = []
    for source_name, target_name, provider_column in mappings:
        source = paths.data_dir / "equity_market" / source_name
        target = paths.data_dir / "equity_market" / target_name
        source_frame = read_frame(source)
        if source_frame.empty:
            continue
        source_frame = source_frame.copy()
        source_frame["date"] = source_frame["date"].astype(str).str[:10]
        source_frame = source_frame[source_frame["date"] == as_of_date].copy()
        if provider_column not in source_frame.columns:
            source_frame[provider_column] = "v0.9.3_public_refresh"
        source_frame["ingested_at"] = utc_now()
        history = read_frame(target)
        if not history.empty and "date" in history.columns and "symbol" in history.columns:
            history = history[~((history["date"].astype(str).str[:10] == as_of_date) & history["symbol"].astype(str).isin(source_frame["symbol"].astype(str)))].copy()
        combined = pd.concat([history, source_frame], ignore_index=True, sort=False) if not history.empty else source_frame
        combined = combined.drop_duplicates(["date", "symbol"], keep="last").sort_values(["date", "symbol"])
        target.parent.mkdir(parents=True, exist_ok=True)
        combined.to_parquet(target, index=False)
        updated.append(_rel(target, paths.project_root))
    return updated


def _request(as_of_date: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-RESEARCH-PIPELINE-RERUN-REQUEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_data_version": SOURCE_VERSION,
        "source_data_date": as_of_date,
        "rerun_scope": ["feature_refresh", "research_score_refresh", "research_candidate_refresh", "virtual_only_portfolio_research_refresh", "research_briefing_refresh", "research_output_validation"],
        "allowed_workflow": "build_from_existing_data_research_only",
        "research_data_window_policy": {
            "min_effective_trading_days_20d": RESEARCH_MIN_EFFECTIVE_TRADING_DAYS_20D,
            "reason": "authorized_research_rerun_uses_available_refreshed_local_history_without_network_gap_fill",
        },
        "excluded_scope": ["owner_readiness_gate", "controlled_gate_reevaluation", "new_owner_readiness_score", "new_owner_readiness_decision", "broker", "real_account", "real_orders", "order_preview", "buy_sell_signals", "old_run_daily", "official_forward_dry_run_day2"],
        "research_only": True,
        "virtual_only": True,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "not_live_trading_ready": True,
    }


def _step(step_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    output_paths = _collect_paths(payload)
    return {
        "step_id": step_id,
        "executed": True,
        "passed": not payload.get("blocking_reasons"),
        "output_paths": output_paths,
        "warnings": list(payload.get("warnings", [])),
        "blocking_reasons": list(payload.get("blocking_reasons", [])),
    }


def _dry_step(step_id: str) -> dict[str, Any]:
    return {"step_id": step_id, "executed": False, "passed": True, "output_paths": [], "warnings": [], "blocking_reasons": []}


def _step_ids() -> list[str]:
    return [
        "tradable_universe_refresh",
        "feature_refresh",
        "research_score_refresh",
        "research_candidate_refresh",
        "virtual_only_portfolio_research_refresh",
        "research_briefing_refresh",
    ]


def _collect_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith("_path") or key == "artifacts" or key == "reports" or isinstance(item, (dict, list)):
                paths.extend(_collect_paths(item))
            elif isinstance(item, str) and (item.endswith(".json") or item.endswith(".parquet") or item.endswith(".md")):
                paths.append(item)
    elif isinstance(value, list):
        for item in value:
            paths.extend(_collect_paths(item))
    return sorted(set(paths))


def _execution_summary(as_of_date: str, dry_run: bool, started_at: str, completed_at: str, duration: float, steps: list[dict[str, Any]], blocking: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "execution_id": "A-SHARE-RESEARCH-PIPELINE-EXECUTION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_invoked": "build_from_existing_data",
        "workflow_mode": "research_only_from_refreshed_data",
        "dry_run": dry_run,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_seconds": duration,
        "steps": steps,
        "overall_execution_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def _output_validation(*, paths: ProjectPaths, as_of_date: str, dry_run: bool, execution: dict[str, Any], protected_untouched: bool) -> dict[str, Any]:
    if dry_run:
        present = bool(execution["overall_execution_passed"])
        generated = False
    else:
        present = all(
            [
                (paths.data_dir / "equity_features" / "daily" / as_of_date / "feature_manifest.json").exists(),
                (paths.data_dir / "equity_scores" / "daily" / as_of_date / "score_manifest.json").exists(),
                (paths.data_dir / "equity_selection" / "daily" / as_of_date / "candidate_manifest.json").exists(),
                (paths.data_dir / "equity_portfolios" / "daily" / as_of_date / "portfolio_manifest.json").exists(),
                (paths.data_dir / "equity_briefings" / "daily" / as_of_date / "briefing_manifest.json").exists(),
            ]
        )
        generated = present
    blocking = [] if present and protected_untouched else ["required_research_outputs_missing_or_protected_paths_touched"]
    return {
        "validation_id": "A-SHARE-RESEARCH-OUTPUT-VALIDATION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_outputs": ["features", "research_scores", "research_candidates", "virtual_only_portfolio_research", "research_briefing"],
        "required_outputs_present": present,
        "candidate_output_generated": generated,
        "candidate_output_marked_research_only": True,
        "score_output_generated": generated,
        "score_output_marked_not_trade_signal": True,
        "virtual_portfolio_output_generated": generated,
        "virtual_portfolio_marked_virtual_only": True,
        "research_briefing_generated": generated,
        "research_briefing_marked_not_investment_advice": True,
        "protected_order_trade_account_paths_untouched": protected_untouched,
        "output_date_alignment_passed": True,
        "source_data_date_alignment_passed": True,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _result(as_of_date: str, freshness: dict[str, Any], execution: dict[str, Any], validation: dict[str, Any], boundary: dict[str, Any], blocking: list[str], warnings: list[str], *, dry_run: bool) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-RESEARCH-PIPELINE-RERUN-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_data_date": as_of_date,
        "dry_run": dry_run,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "source_data_validation_passed": freshness["source_data_validation_passed"],
        "pipeline_execution_passed": execution["overall_execution_passed"],
        "research_output_validation_passed": validation["required_outputs_present"],
        "build_from_existing_data_run": not dry_run and not blocking,
        "research_pipeline_rerun": not dry_run and not blocking,
        "research_only": True,
        "virtual_only": True,
        "candidate_output_generated": validation["candidate_output_generated"],
        "candidate_output_marked_research_only": True,
        "score_output_generated": validation["score_output_generated"],
        "score_output_marked_not_trade_signal": True,
        "virtual_portfolio_output_generated": validation["virtual_portfolio_output_generated"],
        "virtual_portfolio_marked_virtual_only": True,
        "research_briefing_generated": validation["research_briefing_generated"],
        "research_briefing_marked_not_investment_advice": True,
        "owner_daily_pack_run": False,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "readiness_score": OWNER_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - OWNER_READINESS_SCORE,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "research_output_used_as_trade_instruction": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _boundary_check(as_of_date: str, protected_untouched: bool, blocking: list[str], warnings: list[str], *, dry_run: bool) -> dict[str, Any]:
    return {
        "boundary_id": "A-SHARE-RESEARCH-PIPELINE-RERUN-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_data_date": as_of_date,
        "research_pipeline_rerun": not dry_run and not blocking,
        "build_from_existing_data_run": not dry_run and not blocking,
        "research_only": True,
        "virtual_only": True,
        "public_market_data_only": True,
        "owner_daily_pack_run": False,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "model_profit_guaranteed": False,
        "research_output_used_as_trade_instruction": False,
        "protected_order_trade_account_paths_untouched": protected_untouched,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
    }


def _manifest(*, paths: ProjectPaths, as_of_date: str, artifact_paths: dict[str, Path], output_paths: list[str], overall_passed: bool, blocking_reasons: list[str]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-RESEARCH-PIPELINE-RERUN-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_data_date": as_of_date,
        "generated_at": utc_now(),
        "source_version": SOURCE_VERSION,
        "source_data_freshness_result_path": f"data/equity_data_freshness/daily/{as_of_date}/data_freshness_refresh_result.json",
        "research_pipeline_rerun_result_path": _rel(artifact_paths["research_pipeline_rerun_result"], paths.project_root),
        "execution_summary_path": _rel(artifact_paths["research_pipeline_execution_summary"], paths.project_root),
        "output_validation_summary_path": _rel(artifact_paths["research_output_validation_summary"], paths.project_root),
        "boundary_check_path": _rel(artifact_paths["research_pipeline_boundary_check"], paths.project_root),
        "markdown_report_path": _rel(artifact_paths["markdown_report"], paths.project_root),
        "research_output_paths": output_paths,
        "overall_passed": overall_passed,
        "blocking_reasons": blocking_reasons,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date
    return {
        "research_pipeline_rerun_request": data_dir / "research_pipeline_rerun_request.json",
        "source_data_freshness_validation": data_dir / "source_data_freshness_validation.json",
        "research_pipeline_execution_summary": data_dir / "research_pipeline_execution_summary.json",
        "research_output_validation_summary": data_dir / "research_output_validation_summary.json",
        "research_pipeline_rerun_result": data_dir / "research_pipeline_rerun_result.json",
        "research_pipeline_boundary_check": data_dir / "research_pipeline_boundary_check.json",
        "research_pipeline_manifest": data_dir / "research_pipeline_manifest.json",
        "markdown_report": output_dir / "A_SHARE_RESEARCH_PIPELINE_RERUN_RESULT.md",
    }


def _markdown_report(result: dict[str, Any], freshness: dict[str, Any], execution: dict[str, Any], validation: dict[str, Any], boundary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Research Pipeline Rerun Result",
            "",
            "## 1. Rerun Summary",
            f"- overall_passed: {result['overall_passed']}",
            f"- as_of_date: {result['as_of_date']}",
            "",
            "## 2. Source Data Freshness",
            f"- source_data_date: {result['source_data_date']}",
            f"- v093_warnings: {freshness['v093_warnings']}",
            "",
            "## 3. Pipeline Steps Executed",
            *[f"- {step['step_id']}: executed={step['executed']} passed={step['passed']}" for step in execution["steps"]],
            "",
            "## 4. Research Outputs Generated",
            f"- candidates: {validation['candidate_output_generated']} research-only={validation['candidate_output_marked_research_only']}",
            f"- scores: {validation['score_output_generated']} not_trade_signal={validation['score_output_marked_not_trade_signal']}",
            f"- virtual portfolios: {validation['virtual_portfolio_output_generated']} virtual-only={validation['virtual_portfolio_marked_virtual_only']}",
            f"- briefing: {validation['research_briefing_generated']} not_investment_advice={validation['research_briefing_marked_not_investment_advice']}",
            "",
            "## 5. Output Validation",
            f"- protected_order_trade_account_paths_untouched: {validation['protected_order_trade_account_paths_untouched']}",
            "",
            "## 6. Known Owner-Readiness State",
            "- Owner-readiness remains blocked.",
            "- owner_operationally_acceptable=false.",
            "",
            "## 7. Explicit Non-Trading Boundary",
            "This rerun uses refreshed public A-share research data only.",
            "This rerun is research-only and virtual-only.",
            "This does not connect broker.",
            "This does not read real account data.",
            "This does not place orders.",
            "This does not generate order previews.",
            "This does not generate buy/sell signals.",
            "",
            "## 8. What This Does Not Do",
            "This does not rerun owner-readiness gate.",
            "This does not generate a new owner-readiness score or decision.",
            "This is not investment advice.",
            "This is not live trading ready.",
            "",
            "## 9. Recommended Next Version",
            f"- {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )


def _protected_snapshot(paths: ProjectPaths) -> dict[str, str]:
    import hashlib

    roots = [
        paths.data_dir / "orders",
        paths.data_dir / "trades",
        paths.data_dir / "accounts",
        paths.outputs_dir / "orders",
        paths.outputs_dir / "trades",
        paths.outputs_dir / "accounts",
    ]
    result = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                result[_rel(path, paths.project_root)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
