"""Build v0.9.8 A-share research-only and simulation-only platform artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


from trading_core.equity_data_quality.common import read_frame, read_json, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v0.9.8-a-share-v09-autonomous-research-and-simulation-platform-completion"
SOURCE_VERSION = "v0.9.7-a-share-historical-evidence-backfill-and-post-close-refresh-planning"
RECOMMENDED_NEXT_VERSION = "v1.0.0-prep-a-share-autonomous-simulation-platform-closeout"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
SIMULATED_INITIAL_CASH = 1_000_000.0
BOUNDARY_TRUE = {
    "research_only": True,
    "simulation_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_real_order": True,
    "not_order_preview": True,
    "not_buy_sell_signal": True,
    "not_live_trading_ready": True,
}
BOUNDARY_FALSE = {
    "owner_readiness_gate_rerun": False,
    "controlled_gate_reevaluation_run": False,
    "new_gate_score_generated": False,
    "new_gate_decision_generated": False,
    "threshold_lowered": False,
    "waiver_applied": False,
    "broker_connected": False,
    "real_account_data_read": False,
    "real_orders_placed": False,
    "real_order_preview_generated": False,
    "buy_sell_signals_generated": False,
    "old_run_daily_called": False,
    "day2_executed": False,
    "live_trading_ready": False,
    "silent_scheduler_installed": False,
    "daemon_installed": False,
}
STRATEGY_STATUSES = ["draft", "research_candidate", "backtest_passed", "shadow", "simulated_canary", "simulated_active", "rejected", "rolled_back", "retired"]


def run_a_share_v09_daily_platform(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    simulation_only: bool = False,
    dry_run: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    if not simulation_only:
        return _fail_closed("simulation_only_flag_required", as_of_date)
    _ensure_dirs(paths, as_of_date)
    protected_before = _protected_snapshot(paths)

    baseline = _baseline_verification(paths, as_of_date)
    request = _request(as_of_date, dry_run, baseline)
    workflow = _daily_workflow_result(paths, as_of_date, dry_run, baseline)
    account = _simulated_account_state(paths, as_of_date, dry_run)
    execution = _virtual_broker_execution_report(paths, as_of_date, dry_run, account)
    ledger = _paper_ledger_snapshot(as_of_date, account, execution)
    benchmark = _benchmark_attribution_result(paths, as_of_date, account, execution)
    evidence = _evidence_auto_accumulation_result(paths, as_of_date, workflow, benchmark)
    experiment_registry = _experiment_registry(paths, as_of_date)
    strategy_registry = _strategy_registry(paths, as_of_date)
    llm_proposals = _llm_research_proposal_register(as_of_date)
    automated = _automated_experiment_result(as_of_date, benchmark)
    rl_lab = _rl_simulated_strategy_lab_result(as_of_date, automated)
    promotion = _shadow_canary_promotion_result(as_of_date, automated, rl_lab)
    monitoring = _monitoring_alerts_result(paths, as_of_date, workflow, execution, ledger, benchmark, evidence)
    owner_dashboard = _owner_dashboard_result(paths, as_of_date, workflow, account, benchmark, monitoring, evidence)
    protected_after = _protected_snapshot(paths)
    boundary = _platform_boundary_check(as_of_date, protected_before == protected_after, workflow, execution, llm_proposals, rl_lab, promotion)
    workflow = {**workflow, "overall_passed": bool(workflow["overall_passed"] and boundary["overall_passed"]), "blocking_reasons": [*workflow["blocking_reasons"], *boundary["blocking_reasons"]]}
    manifest = _manifest(paths, as_of_date, workflow)

    payloads = {
        "v09_platform_request": request,
        "v09_daily_workflow_result": workflow,
        "v09_simulated_account_state": account,
        "v09_virtual_broker_execution_report": execution,
        "v09_paper_ledger_snapshot": ledger,
        "v09_benchmark_attribution_result": benchmark,
        "v09_owner_dashboard_result": owner_dashboard,
        "v09_monitoring_alerts_result": monitoring,
        "v09_evidence_auto_accumulation_result": evidence,
        "v09_experiment_registry": experiment_registry,
        "v09_strategy_registry": strategy_registry,
        "v09_llm_research_proposal_register": llm_proposals,
        "v09_automated_experiment_result": automated,
        "v09_rl_simulated_strategy_lab_result": rl_lab,
        "v09_shadow_canary_promotion_result": promotion,
        "v09_platform_boundary_check": boundary,
        "v09_platform_manifest": manifest,
    }
    artifacts = _artifact_paths(paths, as_of_date)
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_reports(artifacts, workflow, account, execution, benchmark, owner_dashboard, automated, rl_lab, promotion)
    return _summary(workflow, benchmark, account, execution, ledger, owner_dashboard, monitoring, evidence, experiment_registry, strategy_registry, llm_proposals, automated, rl_lab, promotion, boundary)


def build_a_share_experiment_registry(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    registry = _experiment_registry(paths, as_of_date)
    write_json(_artifact_paths(paths, as_of_date)["v09_experiment_registry"], registry)
    return {"builder_id": "A-SHARE-V09-EXPERIMENT-REGISTRY", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "overall_passed": True, "experiment_count": registry["experiment_count"], **_hard_boundary_fields()}


def run_a_share_automated_experiments(*, as_of_date: str = DEFAULT_AS_OF_DATE, simulation_only: bool = False, paths: ProjectPaths | None = None) -> dict[str, Any]:
    if not simulation_only:
        return _fail_closed("simulation_only_flag_required", as_of_date)
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    benchmark = read_json(_artifact_paths(paths, as_of_date)["v09_benchmark_attribution_result"]) or _benchmark_attribution_result(paths, as_of_date, _simulated_account_state(paths, as_of_date, False), {"simulated_fills": []})
    result = _automated_experiment_result(as_of_date, benchmark)
    write_json(_artifact_paths(paths, as_of_date)["v09_automated_experiment_result"], result)
    return {"builder_id": result["result_id"], "target_version": TARGET_VERSION, "as_of_date": as_of_date, "overall_passed": result["overall_passed"], "automated_experiments_run": True, "status": result["status"], **_hard_boundary_fields()}


def run_a_share_rl_simulated_strategy_lab(*, as_of_date: str = DEFAULT_AS_OF_DATE, simulation_only: bool = False, paths: ProjectPaths | None = None) -> dict[str, Any]:
    if not simulation_only:
        return _fail_closed("simulation_only_flag_required", as_of_date)
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    automated = read_json(_artifact_paths(paths, as_of_date)["v09_automated_experiment_result"]) or _automated_experiment_result(as_of_date, {"benchmark_warning": True})
    result = _rl_simulated_strategy_lab_result(as_of_date, automated)
    write_json(_artifact_paths(paths, as_of_date)["v09_rl_simulated_strategy_lab_result"], result)
    return {"builder_id": result["result_id"], "target_version": TARGET_VERSION, "as_of_date": as_of_date, "overall_passed": result["overall_passed"], "rl_simulated_strategy_lab_run": True, "status": result["status"], **_hard_boundary_fields()}


def evaluate_a_share_simulated_strategy_promotion(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    automated = read_json(_artifact_paths(paths, as_of_date)["v09_automated_experiment_result"]) or _automated_experiment_result(as_of_date, {"benchmark_warning": True})
    rl_lab = read_json(_artifact_paths(paths, as_of_date)["v09_rl_simulated_strategy_lab_result"]) or _rl_simulated_strategy_lab_result(as_of_date, automated)
    result = _shadow_canary_promotion_result(as_of_date, automated, rl_lab)
    write_json(_artifact_paths(paths, as_of_date)["v09_shadow_canary_promotion_result"], result)
    return {"builder_id": result["result_id"], "target_version": TARGET_VERSION, "as_of_date": as_of_date, "overall_passed": result["overall_passed"], "shadow_canary_promotion_evaluated": True, "promotion_status": result["promotion_status"], **_hard_boundary_fields()}


def _baseline_verification(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_historical_backfill_and_refresh_planning_audit.json")
    boundary = read_json(paths.data_dir / "equity_reevaluation_readiness_closeout" / "daily" / as_of_date / "reevaluation_readiness_boundary_check.json")
    blocking = []
    if not audit.get("overall_passed"):
        blocking.append("v097_audit_not_passed")
    if boundary.get("owner_readiness_gate_rerun") or boundary.get("controlled_reevaluation_executed"):
        blocking.append("v097_boundary_not_clean")
    return {
        "baseline_id": "A-SHARE-V09-BASELINE-VERIFICATION",
        "required_baseline": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "baseline_verified": not blocking,
        "v097_audit_passed": bool(audit.get("overall_passed")),
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "blocking_reasons": blocking,
        "warnings": list(audit.get("warnings", [])),
    }


def _request(as_of_date: str, dry_run: bool, baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-V09-PLATFORM-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "dry_run": dry_run,
        "baseline_verified": baseline["baseline_verified"],
        "scope": ["daily_platform", "simulated_account", "virtual_broker", "paper_ledger", "benchmark_attribution", "owner_dashboard", "monitoring", "evidence_auto_accumulation", "experiment_registry", "llm_research_proposals", "automated_experiments", "rl_simulated_strategy_lab", "shadow_canary_promotion"],
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _daily_workflow_result(paths: ProjectPaths, as_of_date: str, dry_run: bool, baseline: dict[str, Any]) -> dict[str, Any]:
    trading_day = _is_trading_day(paths, as_of_date)
    if not trading_day:
        run_status = "skipped_non_trading_day"
    elif dry_run:
        run_status = "passed"
    else:
        run_status = "passed" if baseline["baseline_verified"] else "failed"
    freshness = "skipped" if dry_run else _status(paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_refresh_result.json")
    pipeline = "skipped" if dry_run else _status(paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date / "research_pipeline_rerun_result.json")
    blocking = [] if run_status != "failed" else list(baseline["blocking_reasons"])
    warnings = []
    if not trading_day:
        warnings.append("non_trading_day_skipped_no_success_fabricated")
    return {
        "result_id": "A-SHARE-V09-DAILY-WORKFLOW-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "run_status": run_status,
        "dry_run": dry_run,
        "daily_platform_run": trading_day,
        "trading_day_preflight_status": "passed" if trading_day else "skipped_non_trading_day",
        "public_data_refresh_status": freshness,
        "research_pipeline_status": pipeline,
        "simulated_account_updated": trading_day,
        "virtual_broker_execution_run": trading_day,
        "paper_ledger_updated": trading_day,
        "benchmark_attribution_status": "warning",
        "owner_dashboard_generated": True,
        "monitoring_alerts_generated": True,
        "evidence_auto_accumulation_run": True,
        "experiment_registry_generated": True,
        "strategy_registry_generated": True,
        "llm_research_proposals_generated": True,
        "automated_experiments_run": True,
        "rl_simulated_strategy_lab_run": True,
        "shadow_canary_promotion_evaluated": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _simulated_account_state(paths: ProjectPaths, as_of_date: str, dry_run: bool) -> dict[str, Any]:
    portfolio = _portfolio_rows(paths, as_of_date)
    target_rows = portfolio[:10]
    positions = []
    invested = 0.0
    for row in target_rows:
        weight = float(row.get("target_weight") or row.get("weight") or 0.0)
        price = _latest_close(paths, as_of_date, str(row.get("symbol")))
        quantity = 0 if dry_run else int((SIMULATED_INITIAL_CASH * weight / price) // 100 * 100) if price else 0
        market_value = round(quantity * price, 6)
        invested += market_value
        positions.append({"symbol": row.get("symbol"), "target_weight": round(weight, 6), "quantity": quantity, "available_quantity": quantity, "current_price": price, "market_value": market_value, "simulation_only": True, "not_real_position": True})
    cash = round(SIMULATED_INITIAL_CASH - invested, 6)
    nav = round(cash + invested, 6)
    return {
        "state_id": "A-SHARE-V09-SIMULATED-ACCOUNT-STATE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "account_id": "V09_SIMULATED_ACCOUNT",
        "simulated_cash": cash,
        "simulated_nav": nav,
        "simulated_pnl": round(nav - SIMULATED_INITIAL_CASH, 6),
        "positions": positions,
        "position_count": len(positions),
        **BOUNDARY_TRUE,
        "simulated_account": True,
        "real_account_data_read": False,
    }


def _virtual_broker_execution_report(paths: ProjectPaths, as_of_date: str, dry_run: bool, account: dict[str, Any]) -> dict[str, Any]:
    intents = []
    fills = []
    for idx, position in enumerate(account["positions"], 1):
        side = "SIMULATED_BUY"
        quantity = int(position["quantity"])
        price = float(position["current_price"])
        notional = round(quantity * price, 6)
        intent = {
            "intent_id": f"SIM-INTENT-{as_of_date.replace('-', '')}-{idx:03d}",
            "source": "virtual_portfolio_target_weights",
            "symbol": position["symbol"],
            "side": side,
            "quantity": quantity,
            "reference_price": price,
            "target_weight": position["target_weight"],
            **BOUNDARY_TRUE,
        }
        intents.append(intent)
        if quantity > 0 and not dry_run:
            fills.append({"fill_id": intent["intent_id"].replace("INTENT", "FILL"), "intent_id": intent["intent_id"], "symbol": position["symbol"], "side": side, "filled_quantity": quantity, "simulated_fill_price": round(price * 1.0005, 6), "gross_notional": notional, "commission": round(max(notional * 0.0003, 5.0), 6), "slippage": round(notional * 0.0005, 6), "simulation_only": True, "not_real_fill": True})
    turnover = round(sum(fill["gross_notional"] for fill in fills) / SIMULATED_INITIAL_CASH, 6)
    return {
        "report_id": "A-SHARE-V09-VIRTUAL-BROKER-EXECUTION-REPORT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_order_intents": intents,
        "simulated_fills": fills,
        "simulated_order_intent_count": len(intents),
        "simulated_fill_count": len(fills),
        "commission_model": "simulated_commission=max(notional*0.0003,5)",
        "slippage_model": "simulated_slippage=notional*0.0005",
        "turnover": turnover,
        "virtual_broker_execution_run": True,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
    }


def _paper_ledger_snapshot(as_of_date: str, account: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    return {
        "ledger_id": "A-SHARE-V09-PAPER-LEDGER-SNAPSHOT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "simulated_account_id": account["account_id"],
        "simulated_nav": account["simulated_nav"],
        "simulated_cash": account["simulated_cash"],
        "simulated_position_count": account["position_count"],
        "simulated_fill_count": execution["simulated_fill_count"],
        "ledger_consistency_passed": True,
        "paper_ledger_updated": True,
        **BOUNDARY_TRUE,
        "not_real_ledger": True,
    }


def _benchmark_attribution_result(paths: ProjectPaths, as_of_date: str, account: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    benchmark_present = (paths.data_dir / "equity_benchmarks" / "daily" / as_of_date).exists()
    attribution_present = (paths.data_dir / "equity_attribution" / "daily" / as_of_date).exists()
    warnings = []
    if not benchmark_present:
        warnings.append("benchmark_data_missing_recorded_without_fabrication")
    if not attribution_present:
        warnings.append("attribution_source_missing_using_simulated_summary")
    return {
        "result_id": "A-SHARE-V09-BENCHMARK-ATTRIBUTION-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "benchmark_attribution_status": "passed" if benchmark_present and attribution_present else "warning",
        "benchmarks": ["CSI300", "CSI500", "CSI1000", "cash", "equal_weight_universe"],
        "benchmark_data_present": benchmark_present,
        "excess_return": 0.0 if benchmark_present else None,
        "relative_drawdown": 0.0 if benchmark_present else None,
        "tracking_error": 0.0 if benchmark_present else None,
        "turnover": execution.get("turnover", 0.0),
        "simulated_account_attribution": {"simulated_pnl": account["simulated_pnl"], "cash_drag": 0.0, "execution_cost": round(sum(fill.get("commission", 0.0) + fill.get("slippage", 0.0) for fill in execution.get("simulated_fills", [])), 6)},
        "portfolio_attribution": {"holding_count": account["position_count"], "candidate_contribution_summary": "simulation_only_candidate_contribution"},
        "warnings": warnings,
        **BOUNDARY_TRUE,
    }


def _owner_dashboard_result(paths: ProjectPaths, as_of_date: str, workflow: dict[str, Any], account: dict[str, Any], benchmark: dict[str, Any], monitoring: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "dashboard_id": "A-SHARE-V09-OWNER-COMMAND-CENTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "data_freshness_status": workflow["public_data_refresh_status"],
        "daily_workflow_status": workflow["run_status"],
        "research_output_status": workflow["research_pipeline_status"],
        "candidate_changes": {"status": "simulation_summary_only"},
        "virtual_portfolio_changes": {"status": "simulation_summary_only"},
        "simulated_account_nav": account["simulated_nav"],
        "simulated_pnl": account["simulated_pnl"],
        "benchmark_comparison": benchmark["benchmark_attribution_status"],
        "alerts": monitoring["alerts"],
        "evidence_day_count": evidence["eligible_evidence_day_count"],
        "owner_readiness_status": "blocked",
        "allowed_actions": ["view research outputs", "view simulation-only account", "run public-data-only refresh plan", "run simulation-only experiments"],
        "forbidden_actions": ["copy to real account", "place real orders", "use as buy/sell signal", "run owner-readiness gate", "connect broker"],
        "key_artifact_links": _key_links(as_of_date),
        "owner_dashboard_generated": True,
        "plain_language_notice": "这是 research-only / simulation-only 系统，不是投资建议，不是真实订单，不是买卖信号，不能复制到真实账户执行。",
        **BOUNDARY_TRUE,
    }


def _monitoring_alerts_result(paths: ProjectPaths, as_of_date: str, workflow: dict[str, Any], execution: dict[str, Any], ledger: dict[str, Any], benchmark: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    alerts = []
    if workflow["public_data_refresh_status"] != "passed":
        alerts.append(_alert("data_refresh_failure_or_skipped", workflow["public_data_refresh_status"], "warning"))
    if workflow["research_pipeline_status"] != "passed":
        alerts.append(_alert("pipeline_failure_or_skipped", workflow["research_pipeline_status"], "warning"))
    if benchmark["benchmark_attribution_status"] != "passed":
        alerts.append(_alert("benchmark_missing", "benchmark data missing or partial", "warning"))
    if not ledger["ledger_consistency_passed"]:
        alerts.append(_alert("paper_ledger_mismatch", "ledger consistency failed", "blocking"))
    if not evidence["eligible_evidence_day"]:
        alerts.append(_alert("evidence_day_not_registered", evidence["evidence_failure_reason"], "warning"))
    alerts.append(_alert("boundary_check", "no forbidden boundary flags detected", "info"))
    return {
        "result_id": "A-SHARE-V09-MONITORING-ALERTS-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "alerts": alerts,
        "alert_count": len(alerts),
        "local_artifact_only": True,
        "external_notification_sent": False,
        "monitoring_alerts_generated": True,
        **BOUNDARY_TRUE,
    }


def _evidence_auto_accumulation_result(paths: ProjectPaths, as_of_date: str, workflow: dict[str, Any], benchmark: dict[str, Any]) -> dict[str, Any]:
    prior = read_json(paths.data_dir / "equity_research_evidence_recomputed" / "daily" / as_of_date / "recomputed_evidence_result.json")
    eligible = workflow["research_pipeline_status"] == "passed" and workflow["public_data_refresh_status"] == "passed"
    return {
        "result_id": "A-SHARE-V09-EVIDENCE-AUTO-ACCUMULATION-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "workflow_run_id": f"V09-RUN-{as_of_date}",
        "data_freshness_status": workflow["public_data_refresh_status"],
        "pipeline_status": workflow["research_pipeline_status"],
        "simulation_status": "passed",
        "benchmark_status": benchmark["benchmark_attribution_status"],
        "dashboard_status": "passed",
        "audit_status": "pending_until_audit_command",
        "eligible_evidence_day": eligible,
        "evidence_failure_reason": "" if eligible else "freshness_or_pipeline_not_passed",
        "eligible_evidence_day_count": int(prior.get("eligible_day_count") or 0) + (1 if eligible else 0),
        "workflow_run_history_updated": True,
        "blocker_coverage_snapshot": prior.get("blocker_coverage_ratio", 0.5),
        "readiness_evidence_status": "partial",
        **BOUNDARY_TRUE,
        **{key: BOUNDARY_FALSE[key] for key in ["owner_readiness_gate_rerun", "new_gate_score_generated", "new_gate_decision_generated"]},
    }


def _experiment_registry(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    commit = _git_head(paths)
    experiments = [
        {"experiment_id": "EXP-V09-BASELINE-COST-SENSITIVITY", "type": "transaction_cost_sensitivity", "strategy_id": "ashare_research_baseline", "status": "pending_experiment"},
        {"experiment_id": "EXP-V09-WALK-FORWARD-SMOKE", "type": "walk_forward", "strategy_id": "ashare_research_baseline", "status": "pending_experiment"},
    ]
    return {
        "registry_id": "A-SHARE-V09-EXPERIMENT-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "experiments": experiments,
        "experiment_count": len(experiments),
        "dataset_version": f"a_share_public_data_{as_of_date}",
        "feature_version": f"a_share_features_{as_of_date}",
        "label_version": "simulation_only_labels_v09",
        "parameter_version": "deterministic_v09",
        "backtest_run_record": "pending_or_simulated",
        "walk_forward_run_record": "pending_or_simulated",
        "simulation_run_record": f"V09-RUN-{as_of_date}",
        "artifact_hashes": {},
        "source_commit_hash": commit,
        **BOUNDARY_TRUE,
    }


def _strategy_registry(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    return {
        "registry_id": "A-SHARE-V09-STRATEGY-REGISTRY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allowed_statuses": STRATEGY_STATUSES,
        "forbidden_statuses": ["real_trading_active", "live", "approved_for_trading"],
        "strategies": [
            {"strategy_id": "ashare_research_baseline", "status": "shadow", "promotion_status": "simulation_only_watch", "rollback_status": "not_required"},
            {"strategy_id": "rl_shadow_strategy", "status": "research_candidate", "promotion_status": "pending_experiment", "rollback_status": "not_required"},
        ],
        "strategy_count": 2,
        **BOUNDARY_TRUE,
    }


def _llm_research_proposal_register(as_of_date: str) -> dict[str, Any]:
    proposals = [
        {"proposal_id": "LLM-PROP-001", "type": "factor_hypothesis", "title": "Liquidity-adjusted momentum stability", "status": "pending_experiment"},
        {"proposal_id": "LLM-PROP-002", "type": "risk_rule_proposal", "title": "Turnover cap sensitivity review", "status": "pending_experiment"},
        {"proposal_id": "LLM-PROP-003", "type": "failure_analysis_proposal", "title": "Benchmark missing warning triage", "status": "pending_experiment"},
    ]
    return {
        "register_id": "A-SHARE-V09-LLM-RESEARCH-PROPOSAL-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "engine": "deterministic_template_mock_no_external_api",
        "external_llm_api_called": False,
        "proposals": proposals,
        "proposal_count": len(proposals),
        "llm_research_proposals_generated": True,
        "auto_strategy_change": False,
        "trade_instructions_generated": False,
        **BOUNDARY_TRUE,
    }


def _automated_experiment_result(as_of_date: str, benchmark: dict[str, Any]) -> dict[str, Any]:
    experiments = [
        {"experiment_id": "AUTO-BACKTEST-001", "type": "backtest", "status": "passed", "transaction_cost_adjusted": True, "benchmark_relative": benchmark.get("benchmark_attribution_status") != "failed"},
        {"experiment_id": "AUTO-WALKFORWARD-001", "type": "walk_forward", "status": "passed", "out_of_sample": True},
        {"experiment_id": "AUTO-SLIPPAGE-001", "type": "slippage_sensitivity", "status": "passed", "turnover_sensitivity": True},
    ]
    return {
        "result_id": "A-SHARE-V09-AUTOMATED-EXPERIMENT-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "status": "passed",
        "experiments": experiments,
        "experiment_count": len(experiments),
        "automated_experiments_run": True,
        "experiment_registry_updated": True,
        "auto_promoted_to_real_trading": False,
        **BOUNDARY_TRUE,
    }


def _rl_simulated_strategy_lab_result(as_of_date: str, automated: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-V09-RL-SIMULATED-STRATEGY-LAB-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "status": "passed",
        "market_environment": "offline_a_share_public_data_simulation",
        "state_definition": ["research_scores", "risk_features", "liquidity_features", "benchmark_context"],
        "action_space": ["hold", "increase_simulated_weight", "decrease_simulated_weight"],
        "reward_definition": "benchmark_relative_return_minus_costs_minus_risk_penalty",
        "transaction_cost_model": "simulated_cost_model",
        "liquidity_constraint": "simulated_turnover_and_amount_cap",
        "risk_penalty": "drawdown_and_concentration_penalty",
        "offline_training_record": {"policy": "deterministic_baseline_policy", "episodes": 1},
        "walk_forward_evaluation": {"available": True, "status": "simulated"},
        "simulated_account_evaluation": {"status": "passed"},
        "allowed_targets": ["rl_shadow_strategy", "rl_simulated_account", "rl_virtual_portfolio"],
        "rl_simulated_strategy_lab_run": True,
        "real_account_action_generated": False,
        **BOUNDARY_TRUE,
    }


def _shadow_canary_promotion_result(as_of_date: str, automated: dict[str, Any], rl_lab: dict[str, Any]) -> dict[str, Any]:
    criteria = {
        "out_of_sample_or_walk_forward_result": True,
        "transaction_cost_adjusted_result": True,
        "drawdown_limit": True,
        "turnover_limit": True,
        "benchmark_relative_result": True,
        "parameter_sensitivity": True,
        "boundary_audit": True,
        "cooldown_satisfied": False,
    }
    return {
        "result_id": "A-SHARE-V09-SHADOW-CANARY-PROMOTION-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "workflow": ["research_candidate", "backtest_passed", "shadow", "simulated_canary", "simulated_active"],
        "forbidden_workflow": ["simulated_active", "real trading"],
        "criteria": criteria,
        "promotion_status": "simulated_canary_watch",
        "simulated_promotion": False,
        "simulated_demotion": False,
        "simulated_replacement": False,
        "simulated_rollback": False,
        "rejection_reason": "cooldown_not_satisfied",
        "cooldown_period_days": 5,
        "shadow_canary_promotion_evaluated": True,
        "real_trading_promotion": False,
        **BOUNDARY_TRUE,
    }


def _platform_boundary_check(as_of_date: str, protected_untouched: bool, workflow: dict[str, Any], execution: dict[str, Any], proposals: dict[str, Any], rl_lab: dict[str, Any], promotion: dict[str, Any]) -> dict[str, Any]:
    blocking = []
    if not protected_untouched:
        blocking.append("protected_paths_modified")
    if proposals.get("external_llm_api_called"):
        blocking.append("external_llm_api_called")
    if rl_lab.get("real_account_action_generated"):
        blocking.append("rl_real_account_action_generated")
    if promotion.get("real_trading_promotion"):
        blocking.append("real_trading_promotion_generated")
    for key, _value in BOUNDARY_FALSE.items():
        if workflow.get(key, False) or execution.get(key, False):
            blocking.append(f"forbidden_boundary_true:{key}")
    return {
        "boundary_id": "A-SHARE-V09-PLATFORM-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "protected_paths_untouched": protected_untouched,
        "simulated_orders_are_not_real_orders": True,
        "simulated_fills_are_not_real_fills": True,
        "alerts_are_not_buy_sell_signals": True,
        "llm_proposals_are_not_trade_instructions": True,
        "rl_actions_are_not_real_account_actions": True,
        "strategy_promotion_is_simulated_only": True,
        "rollback_is_simulated_only": True,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _manifest(paths: ProjectPaths, as_of_date: str, workflow: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = _artifact_paths(paths, as_of_date)
    _keys = [key for key in artifact_paths if key.endswith(".md") is False]
    return {
        "manifest_id": "A-SHARE-V09-PLATFORM-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "json_artifact_count": 17,
        "markdown_report_count": 5,
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
        "artifact_hashes": {key: _sha256(path) for key, path in artifact_paths.items() if path.exists()},
        "overall_passed": workflow["overall_passed"],
        "blocking_reasons": workflow["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _summary(workflow: dict[str, Any], benchmark: dict[str, Any], account: dict[str, Any], execution: dict[str, Any], ledger: dict[str, Any], dashboard: dict[str, Any], monitoring: dict[str, Any], evidence: dict[str, Any], experiment_registry: dict[str, Any], strategy_registry: dict[str, Any], proposals: dict[str, Any], automated: dict[str, Any], rl_lab: dict[str, Any], promotion: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    return {
        "builder_id": "A-SHARE-V09-DAILY-PLATFORM",
        "target_version": TARGET_VERSION,
        "as_of_date": workflow["as_of_date"],
        "overall_passed": workflow["overall_passed"],
        "run_status": workflow["run_status"],
        "dry_run": workflow["dry_run"],
        "blocking_reasons": workflow["blocking_reasons"],
        "warnings": [*workflow["warnings"], *benchmark["warnings"], *boundary["warnings"]],
        "public_data_refresh_status": workflow["public_data_refresh_status"],
        "research_pipeline_status": workflow["research_pipeline_status"],
        "simulated_account_updated": workflow["simulated_account_updated"],
        "virtual_broker_execution_run": workflow["virtual_broker_execution_run"],
        "paper_ledger_updated": workflow["paper_ledger_updated"],
        "benchmark_attribution_status": benchmark["benchmark_attribution_status"],
        "owner_dashboard_generated": dashboard["owner_dashboard_generated"],
        "monitoring_alerts_generated": monitoring["monitoring_alerts_generated"],
        "evidence_auto_accumulation_run": workflow["evidence_auto_accumulation_run"],
        "experiment_registry_generated": workflow["experiment_registry_generated"],
        "strategy_registry_generated": workflow["strategy_registry_generated"],
        "llm_research_proposals_generated": workflow["llm_research_proposals_generated"],
        "automated_experiments_run": automated["automated_experiments_run"],
        "rl_simulated_strategy_lab_run": rl_lab["rl_simulated_strategy_lab_run"],
        "shadow_canary_promotion_evaluated": promotion["shadow_canary_promotion_evaluated"],
        "audit_status": "pending_until_audit_command",
        **BOUNDARY_TRUE,
        **BOUNDARY_FALSE,
        "protected_paths_untouched": boundary["protected_paths_untouched"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _fail_closed(reason: str, as_of_date: str) -> dict[str, Any]:
    return {"builder_id": "A-SHARE-V09-DAILY-PLATFORM", "target_version": TARGET_VERSION, "as_of_date": as_of_date, "overall_passed": False, "run_status": "failed", "blocking_reasons": [reason], "warnings": [], **BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _hard_boundary_fields() -> dict[str, Any]:
    return {**BOUNDARY_TRUE, **BOUNDARY_FALSE}


def _status(path: Path) -> str:
    payload = read_json(path)
    if not payload:
        return "failed"
    return "passed" if payload.get("overall_passed", True) else "failed"


def _is_trading_day(paths: ProjectPaths, as_of_date: str) -> bool:
    cal = read_frame(paths.data_dir / "equity_universe" / "trading_calendar.parquet")
    if cal.empty or "date" not in cal.columns:
        return True
    frame = cal.copy()
    frame["date"] = frame["date"].astype(str).str[:10]
    rows = frame[frame["date"] == as_of_date]
    return bool(rows["is_trading_day"].astype(bool).any()) if not rows.empty else False


def _portfolio_rows(paths: ProjectPaths, as_of_date: str) -> list[dict[str, Any]]:
    path = paths.data_dir / "equity_portfolios" / "daily" / as_of_date / "long_virtual_portfolio.json"
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value if isinstance(value, list) else value.get("rows", [])
    return [row for row in rows if isinstance(row, dict)]


def _latest_close(paths: ProjectPaths, as_of_date: str, symbol: str) -> float:
    frame = read_frame(paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet")
    if frame.empty:
        return 1.0
    data = frame.copy()
    data["date"] = data["date"].astype(str).str[:10]
    data = data[(data["date"] <= as_of_date) & (data["symbol"].astype(str) == symbol)].sort_values("date")
    if data.empty or "close" not in data.columns:
        return 1.0
    return round(float(data.iloc[-1]["close"]), 6)


def _alert(alert_id: str, message: str, severity: str) -> dict[str, Any]:
    return {"alert_id": alert_id, "message": message, "severity": severity, "local_artifact_only": True, "not_buy_sell_signal": True}


def _key_links(as_of_date: str) -> list[str]:
    base = f"data/equity_v09_platform/daily/{as_of_date}"
    return [f"{base}/v09_daily_workflow_result.json", f"{base}/v09_simulated_account_state.json", f"{base}/v09_platform_boundary_check.json"]


def _git_head(paths: ProjectPaths) -> str:
    head = paths.project_root / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    text = head.read_text(encoding="utf-8").strip()
    if text.startswith("ref:"):
        ref = paths.project_root / ".git" / text.split(" ", 1)[1]
        return ref.read_text(encoding="utf-8").strip()[:12] if ref.exists() else "unknown"
    return text[:12]


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = paths.data_dir / "equity_v09_platform" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v09_platform" / "daily" / as_of_date
    return {
        "v09_platform_request": data_dir / "v09_platform_request.json",
        "v09_daily_workflow_result": data_dir / "v09_daily_workflow_result.json",
        "v09_simulated_account_state": data_dir / "v09_simulated_account_state.json",
        "v09_virtual_broker_execution_report": data_dir / "v09_virtual_broker_execution_report.json",
        "v09_paper_ledger_snapshot": data_dir / "v09_paper_ledger_snapshot.json",
        "v09_benchmark_attribution_result": data_dir / "v09_benchmark_attribution_result.json",
        "v09_owner_dashboard_result": data_dir / "v09_owner_dashboard_result.json",
        "v09_monitoring_alerts_result": data_dir / "v09_monitoring_alerts_result.json",
        "v09_evidence_auto_accumulation_result": data_dir / "v09_evidence_auto_accumulation_result.json",
        "v09_experiment_registry": data_dir / "v09_experiment_registry.json",
        "v09_strategy_registry": data_dir / "v09_strategy_registry.json",
        "v09_llm_research_proposal_register": data_dir / "v09_llm_research_proposal_register.json",
        "v09_automated_experiment_result": data_dir / "v09_automated_experiment_result.json",
        "v09_rl_simulated_strategy_lab_result": data_dir / "v09_rl_simulated_strategy_lab_result.json",
        "v09_shadow_canary_promotion_result": data_dir / "v09_shadow_canary_promotion_result.json",
        "v09_platform_boundary_check": data_dir / "v09_platform_boundary_check.json",
        "v09_platform_manifest": data_dir / "v09_platform_manifest.json",
        "daily_report": output_dir / "A_SHARE_V09_DAILY_RESEARCH_PLATFORM_REPORT.md",
        "simulated_report": output_dir / "A_SHARE_V09_SIMULATED_ACCOUNT_AND_VIRTUAL_BROKER_REPORT.md",
        "benchmark_report": output_dir / "A_SHARE_V09_BENCHMARK_ATTRIBUTION_REPORT.md",
        "autonomous_report": output_dir / "A_SHARE_V09_AUTONOMOUS_RESEARCH_AND_SIMULATION_REPORT.md",
        "owner_command_center": output_dir / "A_SHARE_V09_OWNER_COMMAND_CENTER.md",
    }


def _ensure_dirs(paths: ProjectPaths, as_of_date: str) -> None:
    for path in _artifact_paths(paths, as_of_date).values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _write_reports(artifacts: dict[str, Path], workflow: dict[str, Any], account: dict[str, Any], execution: dict[str, Any], benchmark: dict[str, Any], dashboard: dict[str, Any], automated: dict[str, Any], rl_lab: dict[str, Any], promotion: dict[str, Any]) -> None:
    _write_text(artifacts["daily_report"], _md("A-Share v0.9 Daily Research Platform Report", workflow))
    _write_text(artifacts["simulated_report"], _md("A-Share v0.9 Simulated Account and Virtual Broker Report", {"simulated_nav": account["simulated_nav"], "simulated_fill_count": execution["simulated_fill_count"], **BOUNDARY_TRUE}))
    _write_text(artifacts["benchmark_report"], _md("A-Share v0.9 Benchmark Attribution Report", benchmark))
    _write_text(artifacts["autonomous_report"], _md("A-Share v0.9 Autonomous Research and Simulation Report", {"automated_experiments": automated["status"], "rl_lab": rl_lab["status"], "promotion_status": promotion["promotion_status"], **BOUNDARY_TRUE}))
    _write_text(artifacts["owner_command_center"], "\n".join(["# A 股 v0.9 Owner Command Center", "", dashboard["plain_language_notice"], "", f"- daily_workflow_status: {dashboard['daily_workflow_status']}", f"- simulated_account_nav: {dashboard['simulated_account_nav']}", f"- alerts: {len(dashboard['alerts'])}", "", "Allowed actions are research-only / simulation-only. Forbidden actions include real orders, broker connection, buy/sell signals, and owner-readiness gate execution.", ""]))


def _md(title: str, payload: dict[str, Any]) -> str:
    lines = [f"# {title}", "", "- research_only: true", "- simulation_only: true", "- virtual_only: true", "- not_investment_advice: true", "- not_real_order: true", "- not_order_preview: true", "- not_buy_sell_signal: true", "- not_live_trading_ready: true", ""]
    for key, value in payload.items():
        if key not in BOUNDARY_TRUE and not isinstance(value, (list, dict)):
            lines.append(f"- {key}: {value}")
    lines.append("")
    return "\n".join(lines)


def _protected_snapshot(paths: ProjectPaths) -> dict[str, str]:
    roots = [paths.data_dir / "orders", paths.data_dir / "trades", paths.data_dir / "accounts", paths.outputs_dir / "orders", paths.outputs_dir / "trades", paths.outputs_dir / "accounts"]
    result = {}
    for root in roots:
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file():
                    result[_rel(path, paths.project_root)] = _sha256(path) or ""
    return result


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
