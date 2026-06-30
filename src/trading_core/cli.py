"""Command line entry point for the Trading Core project."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date as Date
from pathlib import Path

from trading_core import __version__
from trading_core.accounting.consistency_checker import check_consistency, check_consistency_range
from trading_core.backtest.batch_runner import run_backtest_batch
from trading_core.backtest.event_backtester import run_event_backtest
from trading_core.backtest.historical_backtester import run_historical_backtest
from trading_core.backtest.walk_forward import run_walk_forward
from trading_core.data.data_package_validator import validate_data_package
from trading_core.data.historical_prices import import_prices_csv
from trading_core.data.price_acquisition import fetch_prices, should_return_failure
from trading_core.data.price_dataset_merge import merge_price_data
from trading_core.evaluation.dry_run_auditor import audit_dry_run
from trading_core.evaluation.dry_run_validation_report import build_dry_run_validation_report
from trading_core.evaluation.historical_dry_run_replay import replay_dry_run, replay_last_trading_days
from trading_core.evaluation.real_data_validation_report import build_real_data_validation_report
from trading_core.evaluation.strategy_leaderboard import build_strategy_leaderboard
from trading_core.external_intake.report import build_external_project_intake
from trading_core.equity_data.adjusted_price import ingest_a_share_adjusted_prices
from trading_core.equity_data.daily_basic import ingest_a_share_daily_basic
from trading_core.equity_data.daily_price import ingest_a_share_daily_prices
from trading_core.equity_data.full_market_symbol_queue import build_a_share_historical_backfill_symbol_queue
from trading_core.equity_data.historical_adjusted_price import backfill_a_share_adjusted_price_history
from trading_core.equity_data.historical_backfill import backfill_a_share_historical_panels
from trading_core.equity_data.historical_backfill_scheduler import backfill_a_share_historical_panels_full_market
from trading_core.equity_data.historical_daily_basic import backfill_a_share_daily_basic_history
from trading_core.equity_data.historical_daily_price import backfill_a_share_daily_price_history
from trading_core.equity_data_quality.coverage_audit import audit_a_share_data_coverage
from trading_core.equity_data_quality.feature_readiness_audit import audit_a_share_feature_readiness
from trading_core.equity_data_quality.foundation import build_a_share_data_foundation
from trading_core.equity_data_quality.historical_backfill_root_cause import diagnose_a_share_historical_backfill_coverage
from trading_core.equity_data_quality.historical_coverage_audit import audit_a_share_historical_panel_coverage
from trading_core.equity_data_quality.history_manifest import build_a_share_historical_backfill_plan
from trading_core.equity_data_quality.schema_audit import audit_a_share_data_schema
from trading_core.equity_data_quality.source_manifest import build_a_share_data_source_manifest
from trading_core.equity_fundamental.basic_financials import ingest_a_share_basic_financials
from trading_core.equity_fundamental.historical_financials import backfill_a_share_financial_history
from trading_core.equity_features.feature_audit import audit_a_share_multi_horizon_features
from trading_core.equity_features.feature_config import DEFAULT_AS_OF_DATE
from trading_core.equity_features.multi_horizon import build_a_share_multi_horizon_features
from trading_core.equity_industry.classification import ingest_a_share_industry_classification
from trading_core.equity_scoring.component_scores import build_a_share_scores
from trading_core.equity_scoring.score_config import DEFAULT_AS_OF_DATE as DEFAULT_SCORE_AS_OF_DATE
from trading_core.equity_scoring.scoring_audit import audit_a_share_scores
from trading_core.equity_portfolios.portfolio_config import DEFAULT_AS_OF_DATE as DEFAULT_PORTFOLIO_AS_OF_DATE
from trading_core.equity_portfolios.virtual_portfolio_audit import audit_a_share_virtual_portfolios
from trading_core.equity_portfolios.virtual_portfolio_builder import build_a_share_virtual_portfolios
from trading_core.equity_briefings.briefing_config import DEFAULT_AS_OF_DATE as DEFAULT_BRIEFING_AS_OF_DATE
from trading_core.equity_briefings.briefing_audit import audit_a_share_daily_stock_selection_briefing
from trading_core.equity_briefings.daily_stock_selection_briefing import build_a_share_daily_stock_selection_briefing
from trading_core.equity_portfolio_tracking.tracking_audit import audit_a_share_virtual_portfolio_tracking
from trading_core.equity_portfolio_tracking.tracking_builder import build_a_share_virtual_portfolio_tracking
from trading_core.equity_portfolio_tracking.tracking_config import DEFAULT_AS_OF_DATE as DEFAULT_TRACKING_AS_OF_DATE
from trading_core.equity_benchmarks.benchmark_audit import audit_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_builder import build_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_config import DEFAULT_AS_OF_DATE as DEFAULT_BENCHMARK_AS_OF_DATE
from trading_core.equity_performance.performance_audit import audit_a_share_multi_day_performance
from trading_core.equity_performance.performance_builder import build_a_share_multi_day_performance
from trading_core.equity_performance.performance_config import ALLOWED_MODES as A_SHARE_PERFORMANCE_MODES
from trading_core.equity_performance.performance_config import DEFAULT_AS_OF_DATE as DEFAULT_PERFORMANCE_AS_OF_DATE
from trading_core.equity_performance.performance_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS, DEFAULT_ROLLING_WINDOW_DAYS, DEFAULT_TRACKING_START_DATE
from trading_core.equity_attribution.attribution_audit import audit_a_share_performance_attribution
from trading_core.equity_attribution.attribution_builder import build_a_share_performance_attribution
from trading_core.equity_attribution.attribution_config import ALLOWED_MODES as A_SHARE_ATTRIBUTION_MODES
from trading_core.equity_attribution.attribution_config import DEFAULT_AS_OF_DATE as DEFAULT_ATTRIBUTION_AS_OF_DATE
from trading_core.equity_attribution.attribution_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS as DEFAULT_ATTRIBUTION_MINIMUM_REQUIRED_OBSERVATIONS
from trading_core.equity_data_refresh.data_refresh_audit import audit_a_share_daily_data_refresh
from trading_core.equity_data_refresh.data_refresh_builder import build_a_share_daily_data_refresh
from trading_core.equity_data_refresh.data_refresh_config import ALLOWED_MODES as A_SHARE_DATA_REFRESH_MODES
from trading_core.equity_data_refresh.data_refresh_config import DEFAULT_AS_OF_DATE as DEFAULT_DATA_REFRESH_AS_OF_DATE
from trading_core.equity_current_day.current_day_audit import audit_a_share_current_day_research_run
from trading_core.equity_current_day.current_day_config import ALLOWED_MODES as A_SHARE_CURRENT_DAY_MODES
from trading_core.equity_current_day.current_day_config import ALLOWED_WORKFLOW_MODES as A_SHARE_CURRENT_DAY_WORKFLOW_MODES
from trading_core.equity_current_day.current_day_config import DEFAULT_AS_OF_DATE as DEFAULT_CURRENT_DAY_AS_OF_DATE
from trading_core.equity_current_day.current_day_runner import run_a_share_current_day_research, validate_a_share_current_day_readiness
from trading_core.equity_current_day_builds.gated_build_audit import audit_a_share_gated_build
from trading_core.equity_current_day_builds.gated_build_builder import build_a_share_gated_build, validate_a_share_gated_build_inputs
from trading_core.equity_current_day_builds.gated_build_config import ALLOWED_MODES as A_SHARE_GATED_BUILD_MODES
from trading_core.equity_current_day_builds.gated_build_config import DEFAULT_AS_OF_DATE as DEFAULT_GATED_BUILD_AS_OF_DATE
from trading_core.equity_build_repeatability.repeatability_audit import audit_a_share_build_repeatability
from trading_core.equity_build_repeatability.repeatability_builder import (
    build_a_share_build_repeatability,
    validate_a_share_build_repeatability_inputs,
)
from trading_core.equity_build_repeatability.repeatability_config import ALLOWED_MODES as A_SHARE_BUILD_REPEATABILITY_MODES
from trading_core.equity_build_repeatability.repeatability_config import DEFAULT_AS_OF_DATE as DEFAULT_BUILD_REPEATABILITY_AS_OF_DATE
from trading_core.equity_build_output_dashboard.build_output_dashboard_audit import audit_a_share_build_output_owner_dashboard
from trading_core.equity_build_output_dashboard.build_output_dashboard_builder import (
    build_a_share_build_output_owner_dashboard,
    validate_a_share_build_output_owner_dashboard_inputs,
)
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import ALLOWED_MODES as A_SHARE_BUILD_OUTPUT_DASHBOARD_MODES
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import DEFAULT_AS_OF_DATE as DEFAULT_BUILD_OUTPUT_DASHBOARD_AS_OF_DATE
from trading_core.equity_build_output_ops_refresh.build_output_ops_audit import audit_a_share_build_output_ops_refresh
from trading_core.equity_build_output_ops_refresh.build_output_ops_builder import (
    build_a_share_build_output_ops_refresh,
    validate_a_share_build_output_ops_refresh_inputs,
)
from trading_core.equity_build_output_ops_refresh.build_output_ops_config import ALLOWED_MODES as A_SHARE_BUILD_OUTPUT_OPS_MODES
from trading_core.equity_build_output_ops_refresh.build_output_ops_config import DEFAULT_AS_OF_DATE as DEFAULT_BUILD_OUTPUT_OPS_AS_OF_DATE
from trading_core.equity_owner_dashboard.dashboard_audit import audit_a_share_owner_dashboard
from trading_core.equity_owner_dashboard.dashboard_builder import build_a_share_owner_dashboard, validate_a_share_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.dashboard_config import ALLOWED_MODES as A_SHARE_OWNER_DASHBOARD_MODES
from trading_core.equity_owner_dashboard.dashboard_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_DASHBOARD_AS_OF_DATE
from trading_core.equity_owner_monitoring.monitoring_audit import audit_a_share_owner_monitoring
from trading_core.equity_owner_monitoring.monitoring_builder import build_a_share_owner_monitoring, validate_a_share_owner_monitoring_inputs
from trading_core.equity_owner_monitoring.monitoring_config import ALLOWED_MODES as A_SHARE_OWNER_MONITORING_MODES
from trading_core.equity_owner_monitoring.monitoring_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_MONITORING_AS_OF_DATE
from trading_core.equity_owner_monitoring.monitoring_config import DEFAULT_HISTORY_WINDOW_DAYS, DEFAULT_MINIMUM_HISTORY_OBSERVATIONS
from trading_core.equity_owner_remediation.remediation_audit import audit_a_share_owner_remediation
from trading_core.equity_owner_remediation.remediation_builder import build_a_share_owner_remediation, validate_a_share_owner_remediation_inputs
from trading_core.equity_owner_remediation.remediation_config import ALLOWED_MODES as A_SHARE_OWNER_REMEDIATION_MODES
from trading_core.equity_owner_remediation.remediation_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_REMEDIATION_AS_OF_DATE
from trading_core.equity_ops_center.ops_audit import audit_a_share_daily_ops_center
from trading_core.equity_ops_center.ops_builder import build_a_share_daily_ops_center, validate_a_share_daily_ops_inputs
from trading_core.equity_ops_center.ops_config import ALLOWED_MODES as A_SHARE_OPS_CENTER_MODES
from trading_core.equity_ops_center.ops_config import DEFAULT_AS_OF_DATE as DEFAULT_OPS_CENTER_AS_OF_DATE
from trading_core.equity_ops_history.ops_history_audit import audit_a_share_ops_history_baseline
from trading_core.equity_ops_history.ops_history_builder import build_a_share_ops_history_baseline, validate_a_share_ops_history_inputs
from trading_core.equity_ops_history.ops_history_config import ALLOWED_MODES as A_SHARE_OPS_HISTORY_MODES
from trading_core.equity_ops_history.ops_history_config import DEFAULT_AS_OF_DATE as DEFAULT_OPS_HISTORY_AS_OF_DATE
from trading_core.equity_ops_history.ops_history_config import DEFAULT_BASELINE_WINDOW_OBSERVATIONS as DEFAULT_OPS_HISTORY_BASELINE_WINDOW_OBSERVATIONS
from trading_core.equity_ops_history.ops_history_config import DEFAULT_HISTORY_WINDOW_DAYS as DEFAULT_OPS_HISTORY_WINDOW_DAYS
from trading_core.equity_ops_history.ops_history_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS as DEFAULT_OPS_HISTORY_MINIMUM_REQUIRED_OBSERVATIONS
from trading_core.equity_workflows.workflow_audit import audit_a_share_daily_research_workflow
from trading_core.equity_workflows.workflow_config import ALLOWED_MODES as A_SHARE_WORKFLOW_MODES
from trading_core.equity_workflows.workflow_config import DEFAULT_AS_OF_DATE as DEFAULT_WORKFLOW_AS_OF_DATE
from trading_core.equity_workflows.workflow_preflight import preflight_a_share_daily_workflow
from trading_core.equity_workflows.workflow_runner import run_a_share_daily_research_workflow
from trading_core.equity_selection.candidate_config import DEFAULT_AS_OF_DATE as DEFAULT_CANDIDATE_AS_OF_DATE
from trading_core.equity_selection.candidate_generation_audit import audit_a_share_candidates
from trading_core.equity_selection.candidate_generator import generate_a_share_candidates
from trading_core.equity_selection.filter_config import TradableUniverseFilterConfig, parse_bool
from trading_core.equity_selection.tradable_universe_audit import audit_a_share_tradable_universe
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe
from trading_core.equity_universe.calendar import build_a_share_trading_calendar
from trading_core.equity_universe.master import build_a_share_equity_master
from trading_core.execution.ashare_execution_gap_plan import build_ashare_execution_gap_plan
from trading_core.execution.ashare_execution_rules_audit import audit_ashare_execution_rules
from trading_core.execution.ashare_lot_position_contract import build_lot_position_contract
from trading_core.execution.execution_aware_replay_smoke import run_execution_aware_replay_smoke
from trading_core.execution.execution_cost_contract import build_execution_cost_contract
from trading_core.execution.execution_timeline_contract import build_execution_timeline_contract
from trading_core.execution.isolated_ledger_invariant_audit import audit_isolated_ledger_invariants
from trading_core.execution.price_status_contract import build_price_status_contract
from trading_core.execution.trading_calendar_audit import audit_trading_calendar
from trading_core.execution.trading_calendar_contract import build_trading_calendar_contract
from trading_core.execution.virtual_execution_contract import build_virtual_execution_contract
from trading_core.forward_dry_run.day0_blocking_conditions import build_day0_blocking_conditions
from trading_core.forward_dry_run.day0_data_freeze import build_day0_data_freeze
from trading_core.forward_dry_run.day0_manual_confirmation import build_day0_manual_confirmation_packet
from trading_core.forward_dry_run.day0_readiness_audit import audit_day0_readiness
from trading_core.forward_dry_run.day0_readiness_report import build_day0_readiness_report
from trading_core.forward_dry_run.day0_run_daily_preflight import build_day0_run_daily_preflight
from trading_core.forward_dry_run.day0_warning_register import build_day0_warning_register
from trading_core.forward_dry_run.current_daily_workflow_readiness_snapshot import build_current_daily_workflow_readiness_snapshot
from trading_core.forward_dry_run.authorization_materialization_audit import audit_forward_dry_run_authorization_materialization
from trading_core.forward_dry_run.completed_manual_confirmation_checklist_v2 import complete_forward_dry_run_manual_confirmation_checklist_v2
from trading_core.forward_dry_run.day1_artifact_manifest import build_day1_artifact_manifest
from trading_core.forward_dry_run.day1_continuation_artifact_audit import audit_day1_continuation_artifacts
from trading_core.forward_dry_run.day1_continuation_gap_analysis import build_day1_continuation_gap_analysis
from trading_core.forward_dry_run.day1_continuation_blocker_note import build_day1_continuation_blocker_note
from trading_core.forward_dry_run.day1_data_reproducibility_appendix import build_day1_data_reproducibility_appendix
from trading_core.forward_dry_run.day1_input_snapshot import build_day1_input_snapshot
from trading_core.forward_dry_run.day1_isolated_ledger_report import build_day1_isolated_ledger_report
from trading_core.forward_dry_run.day1_ledger_snapshot import build_day1_ledger_snapshot
from trading_core.forward_dry_run.day1_operator_report import build_day1_operator_report
from trading_core.forward_dry_run.day1_owner_report_audit import audit_day1_owner_report_pack
from trading_core.forward_dry_run.day1_owner_report_pack_summary import build_day1_owner_report_pack_summary
from trading_core.forward_dry_run.day1_owner_report_scope_plan import build_day1_owner_report_scope_plan
from trading_core.forward_dry_run.day1_owner_summary_report import build_day1_owner_summary_report
from trading_core.forward_dry_run.day1_post_execution_audit import audit_forward_dry_run_day1
from trading_core.forward_dry_run.day1_pre_execution_gate import build_day1_pre_execution_gate
from trading_core.forward_dry_run.day1_prompt_eligibility_report import build_forward_dry_run_day1_prompt_eligibility
from trading_core.forward_dry_run.day1_prompt_eligibility_revalidation_v0621 import revalidate_forward_dry_run_day1_prompt_eligibility
from trading_core.forward_dry_run.day1_reproducibility_manifest import build_day1_reproducibility_manifest
from trading_core.forward_dry_run.day1_risk_and_boundary_report import build_day1_risk_and_boundary_report
from trading_core.forward_dry_run.day1_strategy_signal_explanation import build_day1_strategy_signal_explanation
from trading_core.forward_dry_run.day1_strategy_signals import build_day1_strategy_signals
from trading_core.forward_dry_run.day1_virtual_execution_result import build_day1_virtual_execution_result
from trading_core.forward_dry_run.day1_virtual_order_fill_report import build_day1_virtual_order_fill_report
from trading_core.forward_dry_run.day1_virtual_order_preview import build_day1_virtual_order_preview
from trading_core.forward_dry_run.day2_continuation_gate_preview import build_day2_continuation_gate_preview
from trading_core.forward_dry_run.day2_readiness_packet import build_day2_readiness_packet
from trading_core.forward_dry_run.forward_dry_run_status import build_forward_dry_run_status
from trading_core.forward_dry_run.manual_confirmation_checklist_v2 import build_forward_dry_run_manual_confirmation_checklist_v2
from trading_core.forward_dry_run.operating_calendar import build_forward_dry_run_operating_calendar
from trading_core.forward_dry_run.owner_manual_confirmation_record import build_owner_manual_confirmation_record
from trading_core.forward_dry_run.owner_authorization_packet import build_forward_dry_run_owner_authorization_packet
from trading_core.forward_dry_run.run_daily_command_preview_metadata import build_forward_dry_run_run_daily_command_preview
from trading_core.forward_dry_run.start_authorization_audit import audit_forward_dry_run_start_authorization
from trading_core.forward_dry_run.start_authorization_scope_plan import build_forward_dry_run_authorization_scope_plan
from trading_core.forward_dry_run.start_gate_revalidation_v0621 import revalidate_forward_dry_run_start_gate_v0621
from trading_core.forward_dry_run.start_gate_validator import validate_forward_dry_run_start_gate_v062
from trading_core.forward_dry_run.start_prerequisite_inventory import build_forward_dry_run_start_prerequisite_inventory
from trading_core.forward_dry_run.updated_owner_authorization_packet import update_forward_dry_run_owner_authorization_packet
from trading_core.daily_workflow.daily_baseline_signal_binding import build_daily_baseline_signals
from trading_core.daily_workflow.daily_data_quality_audit import audit_daily_data_quality
from trading_core.daily_workflow.daily_input_freeze_manifest import build_daily_input_freeze_manifest
from trading_core.daily_workflow.daily_isolated_execution_preview import build_daily_isolated_execution_preview
from trading_core.daily_workflow.daily_market_data_snapshot import build_daily_market_data_snapshot
from trading_core.daily_workflow.daily_order_preview_binding import build_daily_order_preview
from trading_core.daily_workflow.daily_report_packet import build_daily_report_packet
from trading_core.daily_workflow.daily_workflow_audit import audit_daily_workflow
from trading_core.daily_workflow.daily_workflow_scope_plan import build_daily_workflow_scope_plan
from trading_core.daily_workflow.protected_path_residue_scanner import scan_protected_path_residue
from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.evidence_quality_audit import audit_global_briefing_evidence_quality
from trading_core.global_briefing.evidence_quality_report import build_global_briefing_evidence_quality_report
from trading_core.global_briefing.full_historical_proxy_workflow import run_full_historical_proxy_replay
from trading_core.global_briefing.historical_data_acquisition_audit import audit_historical_data_acquisition
from trading_core.global_briefing.historical_data_acquisition_report import build_historical_data_acquisition_report
from trading_core.global_briefing.historical_data_gap_closure_audit import audit_historical_data_gap_closure
from trading_core.global_briefing.historical_data_gap_closure_report import build_historical_data_gap_closure_report
from trading_core.global_briefing.historical_data_gap_closure_workflow import close_historical_data_gaps
from trading_core.global_briefing.historical_data_downloaders import download_historical_data_packages
from trading_core.global_briefing.historical_data_quality_audit import audit_historical_data_quality
from trading_core.global_briefing.historical_data_source_resolver import resolve_historical_data_sources
from trading_core.global_briefing.historical_package_normalizer import normalize_historical_data_packages
from trading_core.global_briefing.historical_warning_inventory import build_historical_warning_inventory
from trading_core.global_briefing.isolated_replay_adapter_audit import audit_isolated_replay_adapter
from trading_core.global_briefing.production_package_acceptance import build_global_briefing_production_acceptance_criteria
from trading_core.global_briefing.real_package_coverage_audit import audit_global_briefing_package_coverage
from trading_core.global_briefing.real_package_integration_audit import audit_global_briefing_real_package_integration
from trading_core.global_briefing.real_package_integration_report import build_global_briefing_real_package_report
from trading_core.global_briefing.real_package_manifest import build_global_briefing_package_manifest
from trading_core.global_briefing.real_package_normalizer import normalize_global_briefing_package
from trading_core.global_briefing.real_package_replay_workflow import run_global_briefing_real_package_replay
from trading_core.global_briefing.replay_audit import audit_global_briefing_replay
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle
from trading_core.global_briefing.replay_evaluation_report import build_global_briefing_replay_report
from trading_core.global_briefing.signal_contract import build_signal_contract
from trading_core.global_briefing.signal_package_validator import validate_global_briefing_signals
from trading_core.global_briefing.warning_triage import build_global_briefing_warning_triage
from trading_core.planning.artifact_coverage_scanner import build_artifact_coverage_scan
from trading_core.planning.day1_blocker_classifier import classify_day1_blockers
from trading_core.planning.day1_blocker_reclassification import reclassify_day1_blockers_after_execution_hardening
from trading_core.planning.day1_blocker_reclassification_v060 import reclassify_day1_blockers_after_baseline_strategies
from trading_core.planning.day1_blocker_reclassification_v061 import reclassify_day1_blockers_after_daily_workflow
from trading_core.planning.day1_blocker_reclassification_v062 import reclassify_day1_blockers_after_start_authorization
from trading_core.planning.day1_blocker_reclassification_v0621 import reclassify_day1_blockers_after_authorization_materialization
from trading_core.planning.day1_blocker_reclassification_v063 import reclassify_day1_blockers_after_forward_dry_run_day1
from trading_core.planning.day1_continuation_reclassification_v0631 import reclassify_day1_continuation_artifacts_v0631
from trading_core.planning.mvp_gap_classifier import classify_mvp_gaps
from trading_core.planning.mvp_requirement_map import build_mvp_requirement_map
from trading_core.planning.next_work_register import build_next_work_register
from trading_core.planning.plan_alignment_audit import audit_plan_alignment
from trading_core.planning.plan_checklist_extractor import build_plan_checklist
from trading_core.evolution.admission_gate import run_admission
from trading_core.experiments.experiment_registry import (
    ExperimentRegistry,
    get_experiment,
    list_experiments,
    register_experiment,
)
from trading_core.experiments.experiment_dashboard import build_experiment_dashboard
from trading_core.experiments.experiment_system_audit import audit_experiment_system
from trading_core.experiments.parameter_sweep import run_parameter_sweep_from_config
from trading_core.experiments.mistake_pattern_library import (
    MistakePatternLibraryInputError,
    update_mistake_pattern_library,
)
from trading_core.experiments.promotion_simulation import (
    PromotionSimulationInputError,
    run_promotion_simulation,
)
from trading_core.experiments.strategy_comparison import (
    StrategyComparisonInputError,
    build_strategy_comparison,
)
from trading_core.features.feature_store import build_feature_matrix
from trading_core.labels.label_store import build_label_matrix
from trading_core.ml.prediction_engine import generate_ml_shadow_predictions
from trading_core.ml.shadow_leaderboard import build_ml_shadow_leaderboard
from trading_core.ml.shadow_model import train_ml_shadow_model
from trading_core.ml.shadow_report import build_ml_shadow_report
from trading_core.ml.shadow_signal_generator import generate_ml_shadow_signals
from trading_core.ml.walk_forward_dataset import build_walk_forward_dataset
from trading_core.reports.acceptance_report import write_acceptance_materials
from trading_core.reports.monthly_research_report import build_monthly_research_report
from trading_core.reports.project_status_report import build_project_status_report
from trading_core.reports.reporting_system_audit import audit_reporting_system
from trading_core.reports.research_pipeline import run_research_pipeline
from trading_core.reports.system_dashboard import build_system_dashboard
from trading_core.reports.trading_summary import export_trading_summary
from trading_core.reports.weekly_research_report import build_weekly_research_report
from trading_core.runtime.health import load_health, summarize_health
from trading_core.signals.macro_signal_loader import load_macro_signals
from trading_core.storage.file_paths import ensure_project_dirs, project_paths
from trading_core.system.artifact_inventory import build_artifact_inventory
from trading_core.system.artifact_browser import build_artifact_browser
from trading_core.system.boundary_regression_audit import run_boundary_regression_audit
from trading_core.system.cli_inventory import build_cli_inventory
from trading_core.system.final_handoff_review import build_final_handoff_review
from trading_core.system.forward_dry_run_readiness import run_forward_dry_run_readiness
from trading_core.system.latest_artifact import locate_latest_artifact
from trading_core.system.quick_status import build_quick_status
from trading_core.system.report_index import build_report_index
from trading_core.system.system_integrity_audit import run_system_integrity_audit
from trading_core.system.system_smoke_test import run_system_smoke_test
from trading_core.system.usability_audit import run_usability_audit
from trading_core.strategies.baseline_benchmark_comparison import compare_baseline_strategy_benchmarks
from trading_core.strategies.baseline_order_preview import build_baseline_order_preview
from trading_core.strategies.baseline_signal_engine import generate_baseline_strategy_signals
from trading_core.strategies.baseline_strategy_contract import build_baseline_strategy_contract
from trading_core.strategies.baseline_strategy_pack_audit import audit_baseline_strategy_pack
from trading_core.strategies.baseline_strategy_pack_summary import build_baseline_strategy_pack_summary
from trading_core.strategies.baseline_strategy_registry import build_baseline_strategy_registry
from trading_core.strategies.baseline_strategy_report import build_baseline_strategy_report
from trading_core.strategies.baseline_strategy_replay import replay_baseline_strategy
from trading_core.strategies.baseline_strategy_scope_plan import build_baseline_strategy_scope_plan


PLANNED_COMMANDS = (
    "init",
    "load-macro",
    "generate-signals",
    "generate-orders",
    "execute",
    "mark",
    "benchmark",
    "attribution",
    "score-signals",
    "classify-mistakes",
    "score-strategies",
    "update-rule-memory",
    "update-experiment-queue",
    "run-evolution",
    "report",
    "run-daily",
    "health",
    "export-summary",
)


def run_daily(date: str):
    from trading_core.daily_run import run_daily as _run_daily

    return _run_daily(date)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading-core",
        description=(
            "File-backed virtual trading research core. "
            "First-stage virtual trading, reporting, evolution, backtest, and walk-forward commands."
        ),
        epilog="Planned commands: " + ", ".join(PLANNED_COMMANDS) + ".",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    for command in PLANNED_COMMANDS:
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--date", default=Date.today().isoformat())
    backtest = subparsers.add_parser("backtest")
    backtest.add_argument("--start-date", required=True)
    backtest.add_argument("--end-date", required=True)
    backtest.add_argument("--strategy", dest="strategy_id")
    walk = subparsers.add_parser("walk-forward")
    walk.add_argument("--start-date", required=True)
    walk.add_argument("--end-date", required=True)
    walk.add_argument("--window-days", type=int, default=5)
    summarize = subparsers.add_parser("summarize-health")
    summarize.add_argument("--start-date", required=True)
    summarize.add_argument("--end-date", required=True)
    importer = subparsers.add_parser("import-prices")
    importer.add_argument("--input", required=True)
    importer.add_argument("--market", required=True)
    admission = subparsers.add_parser("admission")
    admission.add_argument("--strategy", required=True, dest="strategy_id")
    admission.add_argument("--date", required=True)
    subparsers.add_parser("acceptance-report")
    leaderboard = subparsers.add_parser("leaderboard")
    leaderboard.add_argument("--start-date", required=True)
    leaderboard.add_argument("--end-date", required=True)
    validator = subparsers.add_parser("validate-data-package")
    validator.add_argument("--input", required=True)
    batch = subparsers.add_parser("run-backtest-batch")
    batch.add_argument("--start-date", required=True)
    batch.add_argument("--end-date", required=True)
    batch.add_argument("--data", required=True)
    audit = subparsers.add_parser("audit-dry-run")
    audit.add_argument("--start-date", required=True)
    audit.add_argument("--end-date", required=True)
    consistency = subparsers.add_parser("check-consistency")
    consistency.add_argument("--date", required=True)
    consistency_range = subparsers.add_parser("check-consistency-range")
    consistency_range.add_argument("--start-date", required=True)
    consistency_range.add_argument("--end-date", required=True)
    consistency_range.add_argument("--mode", choices=["daily", "backtest", "auto"], default="daily")
    consistency_range.add_argument("--artifact-dir")
    fetch = subparsers.add_parser("fetch-prices")
    fetch.add_argument("--start-date", required=True)
    fetch.add_argument("--end-date", required=True)
    fetch.add_argument("--output", required=True)
    fetch.add_argument("--source", choices=["akshare", "yfinance", "auto"], default="akshare")
    merge = subparsers.add_parser("merge-price-data")
    merge.add_argument("--inputs", nargs="+", required=True)
    merge.add_argument("--output", required=True)
    validation_report = subparsers.add_parser("real-data-validation-report")
    validation_report.add_argument("--artifact-dir", required=True)
    dry_run_validation = subparsers.add_parser("dry-run-validation-report")
    dry_run_validation.add_argument("--start-date", required=True)
    dry_run_validation.add_argument("--end-date", required=True)
    replay = subparsers.add_parser("replay-dry-run")
    replay.add_argument("--start-date", required=True)
    replay.add_argument("--end-date", required=True)
    replay.add_argument("--data", required=True)
    replay.add_argument("--write-main-ledger", action="store_true")
    replay_last = subparsers.add_parser("replay-last-trading-days")
    replay_last.add_argument("--days", type=int, required=True)
    replay_last.add_argument("--end-date", required=True)
    replay_last.add_argument("--data", required=True)
    replay_last.add_argument("--write-main-ledger", action="store_true")
    features = subparsers.add_parser("build-features")
    features.add_argument("--start-date", required=True)
    features.add_argument("--end-date", required=True)
    features.add_argument("--data", required=True)
    labels = subparsers.add_parser("build-labels")
    labels.add_argument("--start-date", required=True)
    labels.add_argument("--end-date", required=True)
    labels.add_argument("--data", required=True)
    ml_dataset = subparsers.add_parser("build-ml-dataset")
    ml_dataset.add_argument("--features", required=True)
    ml_dataset.add_argument("--labels", required=True)
    ml_dataset.add_argument("--start-date", required=True)
    ml_dataset.add_argument("--end-date", required=True)
    ml_dataset.add_argument("--train-days", type=int, required=True)
    ml_dataset.add_argument("--validation-days", type=int, required=True)
    ml_dataset.add_argument("--test-days", type=int, required=True)
    ml_dataset.add_argument("--step-days", type=int, required=True)
    ml_dataset.add_argument("--label-column", required=True)
    train_ml = subparsers.add_parser("train-ml-shadow")
    train_ml.add_argument("--dataset", required=True)
    train_ml.add_argument("--rows", required=True)
    train_ml.add_argument("--model-type", choices=["mock", "lightgbm"], required=True)
    train_ml.add_argument("--label-column", required=True)
    predict_ml = subparsers.add_parser("predict-ml-shadow")
    predict_ml.add_argument("--model", required=True)
    predict_ml.add_argument("--rows", required=True)
    shadow_signals = subparsers.add_parser("generate-ml-shadow-signals")
    shadow_signals.add_argument("--predictions", required=True)
    shadow_signals.add_argument("--top-k", type=int, required=True)
    shadow_signals.add_argument("--target-weight", type=float, required=True)
    shadow_leaderboard = subparsers.add_parser("ml-shadow-leaderboard")
    shadow_leaderboard.add_argument("--predictions", required=True)
    shadow_leaderboard.add_argument("--signals", required=True)
    shadow_leaderboard.add_argument("--benchmark", default="EQUAL_ETF")
    shadow_report = subparsers.add_parser("ml-shadow-report")
    shadow_report.add_argument("--dataset", required=True)
    shadow_report.add_argument("--model", required=True)
    shadow_report.add_argument("--predictions", required=True)
    shadow_report.add_argument("--signals", required=True)
    shadow_report.add_argument("--leaderboard", required=True)
    register_exp = subparsers.add_parser("register-experiment")
    register_exp.add_argument("--config", required=True, help="Path to experiment config YAML/JSON file")
    subparsers.add_parser("list-experiments")
    show_exp = subparsers.add_parser("show-experiment")
    show_exp.add_argument("--experiment-id", required=True, help="Experiment ID to show")

    sweep_parser = subparsers.add_parser("run-parameter-sweep")
    sweep_parser.add_argument("--config", required=True, help="Path to parameter sweep config YAML/JSON file")

    dashboard_parser = subparsers.add_parser("experiment-dashboard")
    dashboard_parser.add_argument("--experiments-dir")
    dashboard_parser.add_argument("--shadow-dir")
    dashboard_parser.add_argument("--output-dir")

    promotion_sim = subparsers.add_parser("simulate-promotion")
    promotion_sim.add_argument("--comparison", required=True)
    promotion_sim.add_argument("--score-threshold", type=float, default=5.0)
    promotion_sim.add_argument("--strict", action="store_true")

    compare_strategies = subparsers.add_parser("compare-strategies")
    compare_strategies.add_argument("--inputs", nargs="+", required=True)

    mistake_patterns = subparsers.add_parser("update-mistake-patterns")
    mistake_patterns.add_argument("--inputs", nargs="+", required=True)
    mistake_patterns.add_argument("--min-evidence", type=int, default=2)

    experiment_audit = subparsers.add_parser("audit-experiment-system")
    experiment_audit.add_argument("--experiments-dir")
    experiment_audit.add_argument("--shadow-dir")
    experiment_audit.add_argument("--outputs-dir")
    experiment_audit.add_argument("--audit-dir")

    weekly_research = subparsers.add_parser("weekly-research-report")
    weekly_research.add_argument("--start-date", required=True)
    weekly_research.add_argument("--end-date", required=True)
    weekly_research.add_argument("--include-experiments", action="store_true")
    weekly_research.add_argument("--include-ml-shadow", action="store_true")
    weekly_research.add_argument("--include-mistakes", action="store_true")

    monthly_research = subparsers.add_parser("monthly-research-report")
    monthly_research.add_argument("--start-date")
    monthly_research.add_argument("--end-date")
    monthly_research.add_argument("--month")
    monthly_research.add_argument("--include-weekly", action="store_true")
    monthly_research.add_argument("--include-experiments", action="store_true")
    monthly_research.add_argument("--include-ml-shadow", action="store_true")

    system_dash = subparsers.add_parser("system-dashboard")
    system_dash.add_argument("--include-artifact-inventory", action="store_true")
    system_dash.add_argument("--include-release-status", action="store_true")

    project_status = subparsers.add_parser("project-status-report")
    project_status.add_argument("--include-next-steps", action="store_true")
    project_status.add_argument("--include-risk-register", action="store_true")

    research_pipeline = subparsers.add_parser("run-research-pipeline")
    research_pipeline.add_argument("--start-date", required=True)
    research_pipeline.add_argument("--end-date", required=True)
    research_pipeline.add_argument("--skip-weekly", action="store_true")
    research_pipeline.add_argument("--skip-monthly", action="store_true")
    research_pipeline.add_argument("--skip-dashboard", action="store_true")
    research_pipeline.add_argument("--skip-project-status", action="store_true")

    reporting_audit = subparsers.add_parser("audit-reporting-system")
    reporting_audit.add_argument("--reports-dir")
    reporting_audit.add_argument("--system-dir")
    reporting_audit.add_argument("--audit-dir")

    subparsers.add_parser("cli-inventory")
    subparsers.add_parser("artifact-inventory")
    smoke = subparsers.add_parser("system-smoke-test")
    smoke.add_argument("--fast", action="store_true")
    smoke.add_argument("--include-reports", action="store_true")
    smoke.add_argument("--include-inventory", action="store_true")
    subparsers.add_parser("boundary-regression-audit")
    subparsers.add_parser("system-integrity-audit")
    subparsers.add_parser("final-handoff-review")
    report_index = subparsers.add_parser("report-index")
    report_index.add_argument("--include-audit", action="store_true")
    report_index.add_argument("--include-experiments", action="store_true")
    report_index.add_argument("--include-system", action="store_true")
    latest_artifact = subparsers.add_parser("latest-artifact")
    latest_artifact.add_argument("--type", required=True, choices=["report", "audit", "experiment", "ml-shadow", "handoff", "dashboard", "all"])
    latest_artifact.add_argument("--json", action="store_true", dest="json_output")
    latest_artifact.add_argument("--open-command", action="store_true")
    artifact_browser = subparsers.add_parser("artifact-browser")
    artifact_browser.add_argument("--include-missing", action="store_true")
    artifact_browser.add_argument("--group-by", choices=["category", "trust-level"], default="category")
    quick_status = subparsers.add_parser("quick-status")
    quick_status.add_argument("--json", action="store_true", dest="json_output")
    subparsers.add_parser("usability-audit")
    readiness = subparsers.add_parser("forward-dry-run-readiness")
    readiness.add_argument("--start-date")
    readiness.add_argument("--trading-days", type=int, default=30)
    readiness.add_argument("--calendar")
    readiness.add_argument("--strict", action="store_true")
    subparsers.add_parser("global-briefing-contract")
    gb_validate = subparsers.add_parser("validate-global-briefing-signals")
    gb_validate.add_argument("--input", required=True)
    gb_validate.add_argument("--start-date")
    gb_validate.add_argument("--end-date")
    gb_validate.add_argument("--strict", action="store_true")
    gb_bundle = subparsers.add_parser("build-global-briefing-replay-bundle")
    gb_bundle.add_argument("--signals", required=True)
    gb_bundle.add_argument("--prices", required=True)
    gb_bundle.add_argument("--start-date", required=True)
    gb_bundle.add_argument("--end-date", required=True)
    gb_bundle.add_argument("--decision-time", default="09:00:00")
    gb_bundle.add_argument("--allow-carry-forward", action="store_true")
    gb_replay = subparsers.add_parser("replay-global-briefing-history")
    gb_replay.add_argument("--bundle", required=True)
    gb_replay.add_argument("--prices", required=True)
    gb_replay.add_argument("--start-date", required=True)
    gb_replay.add_argument("--end-date", required=True)
    gb_replay.add_argument("--initial-cash", type=float, default=1_000_000.0)
    gb_replay.add_argument("--execution-mode", choices=["isolated", "no-trade"], default="isolated")
    gb_replay.add_argument("--max-symbol-weight", type=float, default=0.15)
    gb_replay.add_argument("--max-total-weight", type=float, default=0.50)
    gb_replay.add_argument("--lot-size", type=int, default=100)
    gb_replay.add_argument("--commission-rate", type=float, default=0.0005)
    gb_replay.add_argument("--isolated-output-root")
    gb_replay.add_argument("--report-output-root")
    gb_report = subparsers.add_parser("global-briefing-replay-report")
    gb_report.add_argument("--replay", required=True)
    gb_report.add_argument("--bundle")
    gb_report.add_argument("--validation")
    gb_audit = subparsers.add_parser("audit-global-briefing-replay")
    gb_audit.add_argument("--validation")
    gb_audit.add_argument("--bundle")
    gb_audit.add_argument("--replay")
    gb_audit.add_argument("--evaluation")
    adapter_audit = subparsers.add_parser("audit-isolated-replay-adapter")
    adapter_audit.add_argument("--replay")
    adapter_audit.add_argument("--evaluation")
    package_manifest = subparsers.add_parser("global-briefing-package-manifest")
    package_manifest.add_argument("--root")
    package_manifest.add_argument("--include", action="append")
    package_manifest.add_argument("--output")
    package_normalize = subparsers.add_parser("normalize-global-briefing-package")
    package_normalize.add_argument("--input", required=True)
    package_normalize.add_argument("--package-id")
    package_normalize.add_argument("--region")
    package_normalize.add_argument("--source")
    package_normalize.add_argument("--version")
    package_normalize.add_argument("--output")
    package_normalize.add_argument("--strict", action="store_true")
    package_coverage = subparsers.add_parser("audit-global-briefing-package-coverage")
    package_coverage.add_argument("--signals", required=True)
    package_coverage.add_argument("--prices")
    package_coverage.add_argument("--calendar")
    package_coverage.add_argument("--start-date", required=True)
    package_coverage.add_argument("--end-date", required=True)
    package_coverage.add_argument("--min-coverage", type=float, default=0.80)
    package_coverage.add_argument("--strict", action="store_true")
    package_workflow = subparsers.add_parser("run-global-briefing-real-package-replay")
    package_workflow.add_argument("--input", required=True)
    package_workflow.add_argument("--prices", required=True)
    package_workflow.add_argument("--start-date", required=True)
    package_workflow.add_argument("--end-date", required=True)
    package_workflow.add_argument("--package-id")
    package_workflow.add_argument("--region")
    package_workflow.add_argument("--source")
    package_workflow.add_argument("--version")
    package_workflow.add_argument("--allow-carry-forward", action="store_true")
    package_workflow.add_argument("--min-coverage", type=float, default=0.80)
    package_workflow.add_argument("--execution-mode", choices=["isolated", "no-trade"], default="isolated")
    package_workflow.add_argument("--strict", action="store_true")
    real_report = subparsers.add_parser("global-briefing-real-package-report")
    real_report.add_argument("--manifest")
    real_report.add_argument("--workflow")
    real_report.add_argument("--coverage")
    real_report.add_argument("--evaluation")
    real_audit = subparsers.add_parser("audit-global-briefing-real-package-integration")
    real_audit.add_argument("--manifest")
    real_audit.add_argument("--workflow")
    real_audit.add_argument("--report")
    warning_triage = subparsers.add_parser("global-briefing-warning-triage")
    warning_triage.add_argument("--coverage")
    warning_triage.add_argument("--workflow")
    warning_triage.add_argument("--report")
    warning_triage.add_argument("--audit")
    evidence_quality = subparsers.add_parser("global-briefing-evidence-quality-report")
    evidence_quality.add_argument("--triage")
    evidence_quality.add_argument("--coverage")
    evidence_quality.add_argument("--workflow")
    evidence_quality.add_argument("--audit")
    subparsers.add_parser("global-briefing-production-acceptance-criteria")
    evidence_audit = subparsers.add_parser("audit-global-briefing-evidence-quality")
    evidence_audit.add_argument("--triage")
    evidence_audit.add_argument("--evidence")
    evidence_audit.add_argument("--criteria")
    source_resolution = subparsers.add_parser("historical-data-source-resolution")
    source_resolution.add_argument("--packages")
    source_resolution.add_argument("--start-date", default="2018-01-01")
    source_resolution.add_argument("--end-date", default="latest")
    source_resolution.add_argument("--preferred-source")
    hist_download = subparsers.add_parser("download-historical-data-packages")
    hist_download.add_argument("--packages")
    hist_download.add_argument("--start-date", default="2018-01-01")
    hist_download.add_argument("--end-date", default="latest")
    hist_download.add_argument("--continue-on-error", action="store_true")
    hist_download.add_argument("--source-mode", choices=["auto", "fixture"], default="auto")
    hist_download.add_argument("--timeout-seconds", type=int, default=8)
    hist_download.add_argument("--max-retries", type=int, default=1)
    hist_normalize = subparsers.add_parser("normalize-historical-data-packages")
    hist_normalize.add_argument("--download-manifest")
    hist_normalize.add_argument("--start-date", default="2018-01-01")
    hist_normalize.add_argument("--end-date", default="latest")
    hist_quality = subparsers.add_parser("audit-historical-data-quality")
    hist_quality.add_argument("--download-manifest")
    hist_quality.add_argument("--normalization")
    hist_quality.add_argument("--start-date")
    hist_quality.add_argument("--end-date")
    proxy_replay = subparsers.add_parser("run-full-historical-proxy-replay")
    proxy_replay.add_argument("--signals")
    proxy_replay.add_argument("--prices")
    proxy_replay.add_argument("--start-date", default="2018-01-01")
    proxy_replay.add_argument("--end-date", default="latest")
    proxy_replay.add_argument("--min-coverage", type=float, default=0.80)
    proxy_replay.add_argument("--execution-mode", choices=["isolated", "no-trade"], default="isolated")
    proxy_replay.add_argument("--strict", action="store_true")
    hist_report = subparsers.add_parser("historical-data-acquisition-report")
    hist_report.add_argument("--download-manifest")
    hist_report.add_argument("--normalization")
    hist_report.add_argument("--quality-audit")
    hist_report.add_argument("--proxy-workflow")
    hist_audit = subparsers.add_parser("audit-historical-data-acquisition")
    hist_audit.add_argument("--source-resolution")
    hist_audit.add_argument("--download-manifest")
    hist_audit.add_argument("--normalization")
    hist_audit.add_argument("--quality-audit")
    hist_audit.add_argument("--proxy-workflow")
    hist_audit.add_argument("--report")
    warning_inventory = subparsers.add_parser("historical-warning-inventory")
    warning_inventory.add_argument("--quality-audit")
    warning_inventory.add_argument("--workflow")
    warning_inventory.add_argument("--download-manifest")
    gap_close = subparsers.add_parser("close-historical-data-gaps")
    gap_close.add_argument("--start-date", default="2018-01-01")
    gap_close.add_argument("--end-date", default="latest")
    gap_close.add_argument("--replay-start-date", default="2024-01-02")
    gap_close.add_argument("--replay-end-date", default="2024-12-31")
    gap_close.add_argument("--min-coverage", type=float, default=0.80)
    gap_close.add_argument("--continue-on-error", action="store_true")
    gap_report = subparsers.add_parser("historical-data-gap-closure-report")
    gap_report.add_argument("--workflow")
    gap_audit = subparsers.add_parser("audit-historical-data-gap-closure")
    gap_audit.add_argument("--workflow")
    gap_audit.add_argument("--report")
    data_freeze = subparsers.add_parser("day0-data-freeze")
    data_freeze.add_argument("--download-manifest")
    data_freeze.add_argument("--quality-audit")
    data_freeze.add_argument("--gap-closure-audit")
    data_freeze.add_argument("--proxy-package")
    day0_warnings = subparsers.add_parser("day0-warning-register")
    day0_warnings.add_argument("--warning-inventory")
    day0_warnings.add_argument("--gap-closure-report")
    day0_conditions = subparsers.add_parser("day0-blocking-conditions")
    day0_conditions.add_argument("--data-freeze")
    day0_conditions.add_argument("--warning-register")
    day0_conditions.add_argument("--gap-closure-audit")
    day0_preflight = subparsers.add_parser("day0-run-daily-preflight")
    day0_preflight.add_argument("--data-freeze")
    day0_preflight.add_argument("--warning-register")
    day0_preflight.add_argument("--blocking-conditions")
    subparsers.add_parser("day0-manual-confirmation-packet")
    operating_calendar = subparsers.add_parser("forward-dry-run-operating-calendar")
    operating_calendar.add_argument("--start-date")
    operating_calendar.add_argument("--trading-days", type=int, default=30)
    subparsers.add_parser("day0-readiness-report")
    subparsers.add_parser("audit-day0-readiness")
    plan_checklist = subparsers.add_parser("plan-checklist")
    plan_checklist.add_argument("--plan")
    requirement_map = subparsers.add_parser("mvp-requirement-map")
    requirement_map.add_argument("--checklist")
    subparsers.add_parser("artifact-coverage-scanner")
    mvp_gaps = subparsers.add_parser("classify-mvp-gaps")
    mvp_gaps.add_argument("--checklist")
    mvp_gaps.add_argument("--requirement-map")
    mvp_gaps.add_argument("--artifact-scan")
    day1_blockers = subparsers.add_parser("classify-day1-blockers")
    day1_blockers.add_argument("--mvp-gap-classification")
    next_work = subparsers.add_parser("next-work-register")
    next_work.add_argument("--mvp-gap-classification")
    next_work.add_argument("--day1-blocker-classification")
    subparsers.add_parser("audit-plan-alignment")
    ashare_gap = subparsers.add_parser("ashare-execution-gap-plan")
    ashare_gap.add_argument("--mvp-gaps")
    ashare_gap.add_argument("--day1-blockers")
    ashare_gap.add_argument("--next-work")
    subparsers.add_parser("ashare-trading-calendar-audit")
    subparsers.add_parser("execution-timeline-contract")
    subparsers.add_parser("ashare-price-status-contract")
    subparsers.add_parser("ashare-lot-and-position-contract")
    subparsers.add_parser("ashare-execution-cost-contract")
    subparsers.add_parser("virtual-execution-contract")
    ledger_audit = subparsers.add_parser("audit-isolated-ledger-invariants")
    ledger_audit.add_argument("--ledger-dir")
    replay_smoke = subparsers.add_parser("execution-aware-replay-smoke")
    replay_smoke.add_argument("--start-date", default="2024-01-02")
    replay_smoke.add_argument("--end-date", default="2024-01-08")
    replay_smoke.add_argument("--execution-mode", default="isolated")
    reclassify = subparsers.add_parser("reclassify-day1-blockers-after-execution-hardening")
    reclassify.add_argument("--baseline")
    subparsers.add_parser("audit-ashare-execution-rules")
    subparsers.add_parser("baseline-strategy-scope-plan")
    subparsers.add_parser("baseline-strategy-contract")
    subparsers.add_parser("baseline-strategy-registry")
    baseline_signals = subparsers.add_parser("generate-baseline-strategy-signals")
    baseline_signals.add_argument("--strategy", default="all")
    baseline_signals.add_argument("--start-date", default="2024-01-02")
    baseline_signals.add_argument("--end-date", default="2024-12-31")
    baseline_preview = subparsers.add_parser("build-baseline-order-preview")
    baseline_preview.add_argument("--strategy", default="all")
    baseline_preview.add_argument("--signals")
    baseline_preview.add_argument("--execution-mode", default="isolated")
    baseline_replay = subparsers.add_parser("replay-baseline-strategy")
    baseline_replay.add_argument("--strategy", default="all")
    baseline_replay.add_argument("--start-date", default="2024-01-02")
    baseline_replay.add_argument("--end-date", default="2024-12-31")
    baseline_replay.add_argument("--execution-mode", default="isolated")
    baseline_compare = subparsers.add_parser("compare-baseline-strategy-benchmarks")
    baseline_compare.add_argument("--strategy", default="all")
    baseline_compare.add_argument("--start-date", default="2024-01-02")
    baseline_compare.add_argument("--end-date", default="2024-12-31")
    baseline_report = subparsers.add_parser("baseline-strategy-report")
    baseline_report.add_argument("--strategy", default="all")
    baseline_report.add_argument("--start-date", default="2024-01-02")
    baseline_report.add_argument("--end-date", default="2024-12-31")
    subparsers.add_parser("baseline-strategy-pack-summary")
    subparsers.add_parser("audit-baseline-strategy-pack")
    subparsers.add_parser("reclassify-day1-blockers-after-baseline-strategies")
    subparsers.add_parser("daily-workflow-scope-plan")
    daily_snapshot = subparsers.add_parser("daily-market-data-snapshot")
    daily_snapshot.add_argument("--as-of-date")
    daily_quality = subparsers.add_parser("audit-daily-data-quality")
    daily_quality.add_argument("--snapshot")
    daily_freeze = subparsers.add_parser("daily-input-freeze-manifest")
    daily_freeze.add_argument("--as-of-date", default="2024-12-31")
    daily_signals = subparsers.add_parser("daily-baseline-signals")
    daily_signals.add_argument("--as-of-date", default="2024-12-31")
    daily_signals.add_argument("--strategy", default="all")
    daily_order = subparsers.add_parser("daily-order-preview")
    daily_order.add_argument("--as-of-date", default="2024-12-31")
    daily_order.add_argument("--strategy", default="all")
    daily_order.add_argument("--execution-mode", default="isolated")
    daily_execution = subparsers.add_parser("daily-isolated-execution-preview")
    daily_execution.add_argument("--as-of-date", default="2024-12-31")
    daily_execution.add_argument("--execution-mode", default="isolated")
    daily_report = subparsers.add_parser("daily-report-packet")
    daily_report.add_argument("--as-of-date", default="2024-12-31")
    subparsers.add_parser("protected-path-residue-scan")
    daily_audit = subparsers.add_parser("audit-daily-workflow")
    daily_audit.add_argument("--as-of-date", default="2024-12-31")
    subparsers.add_parser("reclassify-day1-blockers-after-daily-workflow")
    subparsers.add_parser("forward-dry-run-authorization-scope-plan")
    subparsers.add_parser("forward-dry-run-start-prerequisite-inventory")
    subparsers.add_parser("current-daily-workflow-readiness-snapshot")
    subparsers.add_parser("forward-dry-run-manual-confirmation-checklist-v2")
    subparsers.add_parser("forward-dry-run-owner-authorization-packet")
    subparsers.add_parser("validate-forward-dry-run-start-gate-v062")
    subparsers.add_parser("forward-dry-run-run-daily-command-preview")
    subparsers.add_parser("forward-dry-run-day1-prompt-eligibility")
    subparsers.add_parser("audit-forward-dry-run-start-authorization")
    subparsers.add_parser("reclassify-day1-blockers-after-start-authorization")
    subparsers.add_parser("forward-dry-run-owner-manual-confirmation-record")
    subparsers.add_parser("complete-forward-dry-run-manual-confirmation-checklist-v2")
    subparsers.add_parser("update-forward-dry-run-owner-authorization-packet")
    subparsers.add_parser("revalidate-forward-dry-run-start-gate-v0621")
    subparsers.add_parser("revalidate-forward-dry-run-day1-prompt-eligibility")
    subparsers.add_parser("audit-forward-dry-run-authorization-materialization")
    subparsers.add_parser("reclassify-day1-blockers-after-authorization-materialization")
    day1_gate = subparsers.add_parser("forward-dry-run-day1-pre-execution-gate")
    day1_gate.add_argument("--allow-rerun", action="store_true")
    day1_snapshot = subparsers.add_parser("forward-dry-run-day1-input-snapshot")
    day1_snapshot.add_argument("--as-of-date")
    subparsers.add_parser("forward-dry-run-day1-strategy-signals")
    subparsers.add_parser("forward-dry-run-day1-virtual-order-preview")
    subparsers.add_parser("forward-dry-run-day1-virtual-execution")
    subparsers.add_parser("forward-dry-run-day1-ledger-snapshot")
    subparsers.add_parser("forward-dry-run-day1-risk-boundary-report")
    subparsers.add_parser("forward-dry-run-day1-operator-report")
    subparsers.add_parser("audit-forward-dry-run-day1")
    subparsers.add_parser("forward-dry-run-status")
    subparsers.add_parser("reclassify-day1-blockers-after-forward-dry-run-day1")
    subparsers.add_parser("forward-dry-run-day1-continuation-gap-analysis")
    subparsers.add_parser("forward-dry-run-day1-artifact-manifest")
    subparsers.add_parser("forward-dry-run-day1-reproducibility-manifest")
    subparsers.add_parser("forward-dry-run-day2-readiness-packet")
    subparsers.add_parser("forward-dry-run-day2-continuation-gate-preview")
    subparsers.add_parser("audit-forward-dry-run-day1-continuation-artifacts")
    subparsers.add_parser("reclassify-day1-continuation-artifacts-v0631")
    subparsers.add_parser("forward-dry-run-day1-owner-report-scope-plan")
    subparsers.add_parser("forward-dry-run-day1-owner-summary-report")
    subparsers.add_parser("forward-dry-run-day1-strategy-signal-explanation")
    subparsers.add_parser("forward-dry-run-day1-virtual-order-fill-report")
    subparsers.add_parser("forward-dry-run-day1-isolated-ledger-report")
    subparsers.add_parser("forward-dry-run-day1-data-reproducibility-appendix")
    subparsers.add_parser("forward-dry-run-day1-continuation-blocker-note")
    subparsers.add_parser("forward-dry-run-day1-owner-report-pack-summary")
    subparsers.add_parser("audit-forward-dry-run-day1-owner-report-pack")
    subparsers.add_parser("external-project-intake")
    subparsers.add_parser("equity-data-source-manifest")
    subparsers.add_parser("build-a-share-equity-master")
    subparsers.add_parser("build-a-share-trading-calendar")
    subparsers.add_parser("ingest-a-share-daily-prices")
    subparsers.add_parser("ingest-a-share-adjusted-prices")
    subparsers.add_parser("ingest-a-share-daily-basic")
    subparsers.add_parser("ingest-a-share-industry-classification")
    subparsers.add_parser("ingest-a-share-basic-financials")
    subparsers.add_parser("audit-a-share-data-coverage")
    subparsers.add_parser("audit-a-share-data-schema")
    subparsers.add_parser("build-a-share-data-foundation")
    historical_plan = subparsers.add_parser("a-share-historical-backfill-plan")
    historical_plan.add_argument("--target-start-date", default="2021-01-01")
    historical_plan.add_argument("--minimum-start-date", default="2023-01-01")
    historical_plan.add_argument("--end-date", default="2026-06-26")
    subparsers.add_parser("diagnose-a-share-historical-backfill-coverage")
    symbol_queue = subparsers.add_parser("build-a-share-historical-backfill-symbol-queue")
    symbol_queue.add_argument("--target-start-date", default="2021-01-01")
    symbol_queue.add_argument("--end-date", default="2026-06-26")
    history_price = subparsers.add_parser("backfill-a-share-daily-price-history")
    history_price.add_argument("--start-date", required=True)
    history_price.add_argument("--end-date", required=True)
    history_price.add_argument("--max-symbols", type=int, default=0)
    history_price.add_argument("--provider-priority", default=None)
    history_price.add_argument("--rate-limit-per-minute", type=int, default=60)
    history_price.add_argument("--retry", type=int, default=2)
    history_adjusted = subparsers.add_parser("backfill-a-share-adjusted-price-history")
    history_adjusted.add_argument("--start-date", required=True)
    history_adjusted.add_argument("--end-date", required=True)
    history_basic = subparsers.add_parser("backfill-a-share-daily-basic-history")
    history_basic.add_argument("--start-date", required=True)
    history_basic.add_argument("--end-date", required=True)
    history_financial = subparsers.add_parser("backfill-a-share-financial-history")
    history_financial.add_argument("--start-date", required=True)
    history_financial.add_argument("--end-date", required=True)
    subparsers.add_parser("audit-a-share-historical-panel-coverage")
    subparsers.add_parser("audit-a-share-feature-readiness")
    historical_all = subparsers.add_parser("backfill-a-share-historical-panels")
    historical_all.add_argument("--target-start-date", required=True)
    historical_all.add_argument("--minimum-start-date", required=True)
    historical_all.add_argument("--end-date", required=True)
    historical_all.add_argument("--max-symbols", type=int, default=0)
    historical_full = subparsers.add_parser("backfill-a-share-historical-panels-full-market")
    historical_full.add_argument("--target-start-date", required=True)
    historical_full.add_argument("--minimum-start-date", required=True)
    historical_full.add_argument("--end-date", required=True)
    historical_full.add_argument("--batch-size", type=int, default=100)
    historical_full.add_argument("--max-symbols", type=int, default=0)
    historical_full.add_argument("--resume", action="store_true")
    historical_full.add_argument("--provider-priority", default="eastmoney,akshare,baostock,tushare,local")
    historical_full.add_argument("--rate-limit-per-minute", type=int, default=60)
    historical_full.add_argument("--retry", type=int, default=2)
    historical_full.add_argument("--sample-size", type=int)
    tradable_build = subparsers.add_parser("build-a-share-tradable-universe")
    _add_tradable_universe_arguments(tradable_build)
    tradable_audit = subparsers.add_parser("audit-a-share-tradable-universe")
    _add_tradable_universe_arguments(tradable_audit)
    tradable_all = subparsers.add_parser("build-and-audit-a-share-tradable-universe")
    _add_tradable_universe_arguments(tradable_all)
    feature_build = subparsers.add_parser("build-a-share-multi-horizon-features")
    _add_multi_horizon_feature_arguments(feature_build)
    feature_audit = subparsers.add_parser("audit-a-share-multi-horizon-features")
    _add_multi_horizon_feature_arguments(feature_audit)
    feature_all = subparsers.add_parser("build-and-audit-a-share-multi-horizon-features")
    _add_multi_horizon_feature_arguments(feature_all)
    score_build = subparsers.add_parser("build-a-share-scores")
    _add_a_share_score_arguments(score_build)
    score_audit = subparsers.add_parser("audit-a-share-scores")
    _add_a_share_score_arguments(score_audit)
    score_all = subparsers.add_parser("build-and-audit-a-share-scores")
    _add_a_share_score_arguments(score_all)
    candidate_build = subparsers.add_parser("generate-a-share-candidates")
    _add_a_share_candidate_arguments(candidate_build)
    candidate_audit = subparsers.add_parser("audit-a-share-candidates")
    _add_a_share_candidate_arguments(candidate_audit)
    candidate_all = subparsers.add_parser("generate-and-audit-a-share-candidates")
    _add_a_share_candidate_arguments(candidate_all)
    portfolio_build = subparsers.add_parser("build-a-share-virtual-portfolios")
    _add_a_share_virtual_portfolio_arguments(portfolio_build)
    portfolio_audit = subparsers.add_parser("audit-a-share-virtual-portfolios")
    _add_a_share_virtual_portfolio_arguments(portfolio_audit)
    portfolio_all = subparsers.add_parser("build-and-audit-a-share-virtual-portfolios")
    _add_a_share_virtual_portfolio_arguments(portfolio_all)
    briefing_build = subparsers.add_parser("build-a-share-daily-stock-selection-briefing")
    _add_a_share_daily_stock_selection_briefing_arguments(briefing_build)
    briefing_audit = subparsers.add_parser("audit-a-share-daily-stock-selection-briefing")
    _add_a_share_daily_stock_selection_briefing_arguments(briefing_audit)
    briefing_all = subparsers.add_parser("build-and-audit-a-share-daily-stock-selection-briefing")
    _add_a_share_daily_stock_selection_briefing_arguments(briefing_all)
    tracking_build = subparsers.add_parser("build-a-share-virtual-portfolio-tracking")
    _add_a_share_virtual_portfolio_tracking_arguments(tracking_build)
    tracking_audit = subparsers.add_parser("audit-a-share-virtual-portfolio-tracking")
    _add_a_share_virtual_portfolio_tracking_arguments(tracking_audit)
    tracking_all = subparsers.add_parser("build-and-audit-a-share-virtual-portfolio-tracking")
    _add_a_share_virtual_portfolio_tracking_arguments(tracking_all)
    workflow_preflight = subparsers.add_parser("preflight-a-share-daily-workflow")
    _add_a_share_daily_workflow_arguments(workflow_preflight, include_mode=False)
    workflow_run = subparsers.add_parser("run-a-share-daily-research-workflow")
    _add_a_share_daily_workflow_arguments(workflow_run)
    workflow_audit = subparsers.add_parser("audit-a-share-daily-research-workflow")
    _add_a_share_daily_workflow_arguments(workflow_audit)
    workflow_all = subparsers.add_parser("run-and-audit-a-share-daily-research-workflow")
    _add_a_share_daily_workflow_arguments(workflow_all)
    benchmark_build = subparsers.add_parser("build-a-share-benchmark-comparison")
    _add_a_share_benchmark_comparison_arguments(benchmark_build)
    benchmark_audit = subparsers.add_parser("audit-a-share-benchmark-comparison")
    _add_a_share_benchmark_comparison_arguments(benchmark_audit)
    benchmark_all = subparsers.add_parser("build-and-audit-a-share-benchmark-comparison")
    _add_a_share_benchmark_comparison_arguments(benchmark_all)
    performance_build = subparsers.add_parser("build-a-share-multi-day-performance")
    _add_a_share_multi_day_performance_arguments(performance_build)
    performance_audit = subparsers.add_parser("audit-a-share-multi-day-performance")
    _add_a_share_multi_day_performance_arguments(performance_audit)
    performance_all = subparsers.add_parser("build-and-audit-a-share-multi-day-performance")
    _add_a_share_multi_day_performance_arguments(performance_all)
    attribution_build = subparsers.add_parser("build-a-share-performance-attribution")
    _add_a_share_performance_attribution_arguments(attribution_build)
    attribution_audit = subparsers.add_parser("audit-a-share-performance-attribution")
    _add_a_share_performance_attribution_arguments(attribution_audit)
    attribution_all = subparsers.add_parser("build-and-audit-a-share-performance-attribution")
    _add_a_share_performance_attribution_arguments(attribution_all)
    data_refresh_build = subparsers.add_parser("build-a-share-daily-data-refresh")
    _add_a_share_daily_data_refresh_arguments(data_refresh_build)
    data_refresh_audit = subparsers.add_parser("audit-a-share-daily-data-refresh")
    _add_a_share_daily_data_refresh_arguments(data_refresh_audit)
    data_refresh_all = subparsers.add_parser("build-and-audit-a-share-daily-data-refresh")
    _add_a_share_daily_data_refresh_arguments(data_refresh_all)
    current_day_readiness = subparsers.add_parser("validate-a-share-current-day-readiness")
    _add_a_share_current_day_arguments(current_day_readiness, include_mode=False)
    current_day_run = subparsers.add_parser("run-a-share-current-day-research")
    _add_a_share_current_day_arguments(current_day_run)
    current_day_audit = subparsers.add_parser("audit-a-share-current-day-research-run")
    _add_a_share_current_day_arguments(current_day_audit)
    current_day_all = subparsers.add_parser("run-and-audit-a-share-current-day-research")
    _add_a_share_current_day_arguments(current_day_all)
    owner_dashboard_validate = subparsers.add_parser("validate-a-share-owner-dashboard-inputs")
    _add_a_share_owner_dashboard_arguments(owner_dashboard_validate, include_mode=False)
    owner_dashboard_build = subparsers.add_parser("build-a-share-owner-dashboard")
    _add_a_share_owner_dashboard_arguments(owner_dashboard_build)
    owner_dashboard_audit = subparsers.add_parser("audit-a-share-owner-dashboard")
    _add_a_share_owner_dashboard_arguments(owner_dashboard_audit, include_mode=False)
    owner_dashboard_all = subparsers.add_parser("build-and-audit-a-share-owner-dashboard")
    _add_a_share_owner_dashboard_arguments(owner_dashboard_all)
    owner_monitoring_validate = subparsers.add_parser("validate-a-share-owner-monitoring-inputs")
    _add_a_share_owner_monitoring_arguments(owner_monitoring_validate, include_mode=False)
    owner_monitoring_build = subparsers.add_parser("build-a-share-owner-monitoring")
    _add_a_share_owner_monitoring_arguments(owner_monitoring_build)
    owner_monitoring_audit = subparsers.add_parser("audit-a-share-owner-monitoring")
    _add_a_share_owner_monitoring_arguments(owner_monitoring_audit, include_mode=False)
    owner_monitoring_all = subparsers.add_parser("build-and-audit-a-share-owner-monitoring")
    _add_a_share_owner_monitoring_arguments(owner_monitoring_all)
    owner_remediation_validate = subparsers.add_parser("validate-a-share-owner-remediation-inputs")
    _add_a_share_owner_remediation_arguments(owner_remediation_validate, include_mode=False)
    owner_remediation_build = subparsers.add_parser("build-a-share-owner-remediation")
    _add_a_share_owner_remediation_arguments(owner_remediation_build)
    owner_remediation_audit = subparsers.add_parser("audit-a-share-owner-remediation")
    _add_a_share_owner_remediation_arguments(owner_remediation_audit, include_mode=False)
    owner_remediation_all = subparsers.add_parser("build-and-audit-a-share-owner-remediation")
    _add_a_share_owner_remediation_arguments(owner_remediation_all)
    ops_center_validate = subparsers.add_parser("validate-a-share-daily-ops-inputs")
    _add_a_share_daily_ops_center_arguments(ops_center_validate, include_mode=False)
    ops_center_build = subparsers.add_parser("build-a-share-daily-ops-center")
    _add_a_share_daily_ops_center_arguments(ops_center_build)
    ops_center_audit = subparsers.add_parser("audit-a-share-daily-ops-center")
    _add_a_share_daily_ops_center_arguments(ops_center_audit, include_mode=False)
    ops_center_all = subparsers.add_parser("build-and-audit-a-share-daily-ops-center")
    _add_a_share_daily_ops_center_arguments(ops_center_all)
    ops_history_validate = subparsers.add_parser("validate-a-share-ops-history-inputs")
    _add_a_share_ops_history_arguments(ops_history_validate, include_mode=False)
    ops_history_build = subparsers.add_parser("build-a-share-ops-history-baseline")
    _add_a_share_ops_history_arguments(ops_history_build)
    ops_history_audit = subparsers.add_parser("audit-a-share-ops-history-baseline")
    _add_a_share_ops_history_arguments(ops_history_audit, include_mode=False)
    ops_history_all = subparsers.add_parser("build-and-audit-a-share-ops-history-baseline")
    _add_a_share_ops_history_arguments(ops_history_all)
    gated_build_validate = subparsers.add_parser("validate-a-share-gated-build-inputs")
    _add_a_share_gated_build_arguments(gated_build_validate, include_mode=False)
    gated_build = subparsers.add_parser("build-a-share-gated-build-from-existing-data")
    _add_a_share_gated_build_arguments(gated_build)
    gated_build_audit = subparsers.add_parser("audit-a-share-gated-build-from-existing-data")
    _add_a_share_gated_build_arguments(gated_build_audit, include_mode=False)
    gated_build_all = subparsers.add_parser("build-and-audit-a-share-gated-build-from-existing-data")
    _add_a_share_gated_build_arguments(gated_build_all)
    repeatability_validate = subparsers.add_parser("validate-a-share-build-repeatability-inputs")
    _add_a_share_build_repeatability_arguments(repeatability_validate, include_mode=False)
    repeatability_build = subparsers.add_parser("build-a-share-build-repeatability")
    _add_a_share_build_repeatability_arguments(repeatability_build)
    repeatability_audit = subparsers.add_parser("audit-a-share-build-repeatability")
    _add_a_share_build_repeatability_arguments(repeatability_audit, include_mode=False)
    repeatability_all = subparsers.add_parser("build-and-audit-a-share-build-repeatability")
    _add_a_share_build_repeatability_arguments(repeatability_all)
    build_output_dashboard_validate = subparsers.add_parser("validate-a-share-build-output-owner-dashboard-inputs")
    _add_a_share_build_output_dashboard_arguments(build_output_dashboard_validate, include_mode=False)
    build_output_dashboard_build = subparsers.add_parser("build-a-share-build-output-owner-dashboard")
    _add_a_share_build_output_dashboard_arguments(build_output_dashboard_build)
    build_output_dashboard_audit = subparsers.add_parser("audit-a-share-build-output-owner-dashboard")
    _add_a_share_build_output_dashboard_arguments(build_output_dashboard_audit, include_mode=False)
    build_output_dashboard_all = subparsers.add_parser("build-and-audit-a-share-build-output-owner-dashboard")
    _add_a_share_build_output_dashboard_arguments(build_output_dashboard_all)
    build_output_ops_validate = subparsers.add_parser("validate-a-share-build-output-ops-refresh-inputs")
    _add_a_share_build_output_ops_arguments(build_output_ops_validate, include_mode=False)
    build_output_ops_build = subparsers.add_parser("build-a-share-build-output-ops-refresh")
    _add_a_share_build_output_ops_arguments(build_output_ops_build)
    build_output_ops_audit = subparsers.add_parser("audit-a-share-build-output-ops-refresh")
    _add_a_share_build_output_ops_arguments(build_output_ops_audit, include_mode=False)
    build_output_ops_all = subparsers.add_parser("build-and-audit-a-share-build-output-ops-refresh")
    _add_a_share_build_output_ops_arguments(build_output_ops_all)

    return parser


def _add_tradable_universe_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default="2026-06-26")
    parser.add_argument("--min-listing-trading-days", type=int, default=120)
    parser.add_argument("--min-avg-amount-20d", type=float, default=50_000_000)
    parser.add_argument("--min-avg-amount-60d", type=float, default=30_000_000)
    parser.add_argument("--min-total-mv", type=float, default=3_000_000_000)
    parser.add_argument("--min-circ-mv", type=float, default=2_000_000_000)
    parser.add_argument("--min-close-price", type=float, default=2.0)
    parser.add_argument("--include-caution", nargs="?", const=True, default=False, type=parse_bool)
    parser.add_argument("--allow-previous-trading-day", nargs="?", const=True, default=False, type=parse_bool)


def _tradable_universe_config(args: argparse.Namespace) -> TradableUniverseFilterConfig:
    return TradableUniverseFilterConfig(
        as_of_date=args.as_of_date,
        min_listing_trading_days=args.min_listing_trading_days,
        min_avg_amount_20d=args.min_avg_amount_20d,
        min_avg_amount_60d=args.min_avg_amount_60d,
        min_total_mv=args.min_total_mv,
        min_circ_mv=args.min_circ_mv,
        min_close_price=args.min_close_price,
        include_caution=args.include_caution,
        allow_previous_trading_day=args.allow_previous_trading_day,
    )


def _add_multi_horizon_feature_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_AS_OF_DATE)
    parser.add_argument("--allow-latest-tradable-universe", nargs="?", const=True, default=False, type=parse_bool)


def _add_a_share_score_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_SCORE_AS_OF_DATE)
    parser.add_argument("--allow-latest-feature-date", nargs="?", const=True, default=False, type=parse_bool)


def _add_a_share_candidate_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_CANDIDATE_AS_OF_DATE)
    parser.add_argument("--allow-latest-score-date", nargs="?", const=True, default=False, type=parse_bool)
    parser.add_argument("--long-count", type=int, default=30)
    parser.add_argument("--mid-count", type=int, default=30)
    parser.add_argument("--short-count", type=int, default=30)
    parser.add_argument("--extended-count", type=int, default=100)


def _add_a_share_virtual_portfolio_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_PORTFOLIO_AS_OF_DATE)
    parser.add_argument("--allow-latest-candidate-date", nargs="?", const=True, default=False, type=parse_bool)
    parser.add_argument("--long-holdings", type=int, default=30)
    parser.add_argument("--mid-holdings", type=int, default=30)
    parser.add_argument("--short-holdings", type=int, default=20)


def _add_a_share_daily_stock_selection_briefing_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_BRIEFING_AS_OF_DATE)
    parser.add_argument("--allow-latest-artifact-date", nargs="?", const=True, default=False, type=parse_bool)


def _add_a_share_virtual_portfolio_tracking_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_TRACKING_AS_OF_DATE)


def _add_a_share_benchmark_comparison_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_BENCHMARK_AS_OF_DATE)
    parser.add_argument("--lookback-trading-days", type=int, default=250)
    parser.add_argument("--minimum-required-trading-days", type=int, default=20)
    parser.add_argument("--allow-placeholder-benchmarks", action="store_true")
    parser.add_argument("--fail-on-placeholder-benchmarks", nargs="?", const=True, default=True, type=parse_bool)


def _benchmark_fail_on_placeholder(args: argparse.Namespace) -> bool:
    return False if args.allow_placeholder_benchmarks else bool(args.fail_on_placeholder_benchmarks)


def _add_a_share_multi_day_performance_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_PERFORMANCE_AS_OF_DATE)
    parser.add_argument("--mode", choices=A_SHARE_PERFORMANCE_MODES, default="current_snapshot")
    parser.add_argument("--tracking-start-date", default=DEFAULT_TRACKING_START_DATE)
    parser.add_argument("--minimum-required-observations", type=int, default=DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS)
    parser.add_argument("--rolling-window-days", type=int, default=DEFAULT_ROLLING_WINDOW_DAYS)
    parser.add_argument("--allow-rebuild", action="store_true")
    parser.add_argument("--allow-historical-reconstruction", action="store_true")


def _add_a_share_performance_attribution_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_ATTRIBUTION_AS_OF_DATE)
    parser.add_argument("--mode", choices=A_SHARE_ATTRIBUTION_MODES, default="current_exposure_diagnostics")
    parser.add_argument("--minimum-required-observations", type=int, default=DEFAULT_ATTRIBUTION_MINIMUM_REQUIRED_OBSERVATIONS)
    parser.add_argument("--allow-limited-history", nargs="?", const=True, default=True, type=parse_bool)


def _add_a_share_daily_data_refresh_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_DATA_REFRESH_AS_OF_DATE)
    parser.add_argument("--mode", choices=A_SHARE_DATA_REFRESH_MODES, default="validate_existing_data")
    parser.add_argument("--resolve-latest-completed-trading-day", action="store_true")
    parser.add_argument("--allow-network-providers", action="store_true")
    parser.add_argument("--allow-public-providers", action="store_true")
    parser.add_argument("--allow-intraday-research-refresh", action="store_true")
    parser.add_argument("--allow-non-trading-day", action="store_true")
    parser.add_argument("--allow-partial-refresh", action="store_true")
    parser.add_argument("--allow-latest-available-if-exact-missing", action="store_true")
    parser.add_argument("--allow-research-workflow-after-refresh", action="store_true")


def _add_a_share_current_day_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_CURRENT_DAY_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_CURRENT_DAY_MODES, default="run_research_from_existing_refresh")
    else:
        parser.add_argument("--mode", choices=A_SHARE_CURRENT_DAY_MODES, default="validate_current_day_readiness")
    parser.add_argument("--workflow-mode", choices=A_SHARE_CURRENT_DAY_WORKFLOW_MODES, default="validate_existing_artifacts")
    parser.add_argument("--use-data-refresh-resolved-date", action="store_true")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-refresh-before-run", action="store_true")
    parser.add_argument("--allow-network-providers", action="store_true")
    parser.add_argument("--allow-public-providers", action="store_true")
    parser.add_argument("--run-post-workflow-modules", action="store_true")
    parser.add_argument("--allow-post-workflow-warnings-only", action="store_true")


def _add_a_share_owner_dashboard_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_DASHBOARD_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_DASHBOARD_MODES, default="build_dashboard_from_existing_run")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_DASHBOARD_MODES, default="validate_existing_dashboard_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--fail-on-missing-optional-card", action="store_true")
    parser.add_argument("--compact-only", action="store_true")


def _add_a_share_owner_monitoring_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_MONITORING_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_MONITORING_MODES, default="build_monitoring_dashboard")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_MONITORING_MODES, default="validate_monitoring_inputs")
    parser.add_argument("--history-window-days", type=int, default=DEFAULT_HISTORY_WINDOW_DAYS)
    parser.add_argument("--minimum-history-observations", type=int, default=DEFAULT_MINIMUM_HISTORY_OBSERVATIONS)
    parser.add_argument("--allow-rebuild-history", action="store_true")
    parser.add_argument("--send-external-notifications", action="store_true")


def _add_a_share_owner_remediation_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_REMEDIATION_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_REMEDIATION_MODES, default="build_remediation_runbook")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_REMEDIATION_MODES, default="validate_remediation_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-safe-local-dry-run", action="store_true")
    parser.add_argument("--allow-data-refresh-rerun", action="store_true")
    parser.add_argument("--allow-research-workflow-rerun", action="store_true")
    parser.add_argument("--allow-dashboard-rerun", action="store_true")
    parser.add_argument("--allow-monitoring-rerun", action="store_true")


def _add_a_share_daily_ops_center_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OPS_CENTER_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OPS_CENTER_MODES, default="aggregate_existing_ops_artifacts")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OPS_CENTER_MODES, default="validate_ops_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-safe-validation-chain", action="store_true")


def _add_a_share_ops_history_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OPS_HISTORY_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OPS_HISTORY_MODES, default="build_trend_baselines")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OPS_HISTORY_MODES, default="validate_history_inputs")
    parser.add_argument("--history-window-days", type=int, default=DEFAULT_OPS_HISTORY_WINDOW_DAYS)
    parser.add_argument("--minimum-required-observations", type=int, default=DEFAULT_OPS_HISTORY_MINIMUM_REQUIRED_OBSERVATIONS)
    parser.add_argument("--baseline-window-observations", type=int, default=DEFAULT_OPS_HISTORY_BASELINE_WINDOW_OBSERVATIONS)
    parser.add_argument("--allow-rebuild-history", action="store_true")
    parser.add_argument("--allow-synthetic-history", action="store_true")


def _add_a_share_gated_build_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_GATED_BUILD_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_GATED_BUILD_MODES, default="run_gated_build_from_existing_data")
    else:
        parser.add_argument("--mode", choices=A_SHARE_GATED_BUILD_MODES, default="validate_gated_build_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--minimum-ops-health-score", type=int, default=60)
    parser.add_argument("--allow-public-network-refresh", action="store_true")
    parser.add_argument("--allow-full-research-run", action="store_true")
    parser.add_argument("--allow-old-run-daily", action="store_true")
    parser.add_argument("--allow-broker", action="store_true")
    parser.add_argument("--allow-real-orders", action="store_true")
    parser.add_argument("--allow-order-preview", action="store_true")
    parser.add_argument("--allow-buy-sell-signals", action="store_true")


def _add_a_share_build_repeatability_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_BUILD_REPEATABILITY_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_BUILD_REPEATABILITY_MODES, default="run_repeat_build_from_existing_data")
    else:
        parser.add_argument("--mode", choices=A_SHARE_BUILD_REPEATABILITY_MODES, default="validate_repeatability_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-business-output-drift", action="store_true")


def _add_a_share_build_output_dashboard_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_BUILD_OUTPUT_DASHBOARD_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_BUILD_OUTPUT_DASHBOARD_MODES, default="build_owner_dashboard_from_build_output")
    else:
        parser.add_argument("--mode", choices=A_SHARE_BUILD_OUTPUT_DASHBOARD_MODES, default="validate_build_output_dashboard_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-required-validate-fallback", action="store_true")
    parser.add_argument("--allow-business-output-drift", action="store_true")


def _add_a_share_build_output_ops_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_BUILD_OUTPUT_OPS_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_BUILD_OUTPUT_OPS_MODES, default="build_build_output_monitoring_remediation_ops_refresh")
    else:
        parser.add_argument("--mode", choices=A_SHARE_BUILD_OUTPUT_OPS_MODES, default="validate_build_output_ops_refresh_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-business-output-drift", action="store_true")


def _add_a_share_daily_workflow_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_WORKFLOW_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_WORKFLOW_MODES, default="validate_existing_artifacts")
    else:
        parser.add_argument("--mode", choices=A_SHARE_WORKFLOW_MODES, default="validate_existing_artifacts")
    parser.add_argument("--allow-latest-artifact-date", nargs="?", const=True, default=False, type=parse_bool)
    parser.add_argument("--allow-public-data-refresh", nargs="?", const=True, default=False, type=parse_bool)
    parser.add_argument("--fail-on-build-timestamp-drift", action="store_true")
    parser.add_argument("--allow-build-timestamp-drift", nargs="?", const=True, default=True, type=parse_bool)
    parser.add_argument("--allow-version-shim-warning", nargs="?", const=True, default=False, type=parse_bool)


def _resolve_cli_path(value: str, paths) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return path


def _resolve_project_path(value: str | None, paths) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    parts = [part.lower() for part in path.parts]
    if len(parts) >= 2 and parts[0] == "work" and parts[1] == "trading-core":
        return paths.workspace_root / path
    return paths.project_root / path


def _split_csv_arg(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        return 0
    paths = project_paths()
    if args.command == "init":
        ensure_project_dirs(paths)
        print(f"initialized {paths.project_root}")
        return 0
    if args.command == "load-macro":
        rows, limitations = load_macro_signals(args.date, paths)
        print({"macro_signals": len(rows), "limitations": limitations})
        return 0
    if args.command == "backtest":
        if args.strategy_id:
            result = run_historical_backtest(args.start_date, args.end_date, args.strategy_id)
            print({"days": result["days"], "trades": result["trades_count"], "strategy_id": result["strategy_id"]})
        else:
            result = run_event_backtest(args.start_date, args.end_date)
            print({"days": result["days"], "total_return": result["total_return"]})
        return 0
    if args.command == "walk-forward":
        result = run_walk_forward(args.start_date, args.end_date, args.window_days)
        print({"windows": len(result["windows"])})
        return 0
    if args.command == "summarize-health":
        result = summarize_health(args.start_date, args.end_date)
        print(result)
        return 0
    if args.command == "import-prices":
        result = import_prices_csv(_resolve_cli_path(args.input, paths), args.market)
        print(result)
        return 0
    if args.command == "validate-data-package":
        result = validate_data_package(_resolve_cli_path(args.input, paths), paths)
        print({"passed": result["passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "run-backtest-batch":
        result = run_backtest_batch(args.start_date, args.end_date, _resolve_cli_path(args.data, paths), paths)
        print({"passed": result["passed"], "output_dir": result["output_dir"]})
        return 0
    if args.command == "audit-dry-run":
        result = audit_dry_run(args.start_date, args.end_date, paths)
        print({"passed": result["passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "check-consistency":
        result = check_consistency(args.date, paths)
        print({"passed": result["passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "check-consistency-range":
        artifact_dir = _resolve_cli_path(args.artifact_dir, paths) if args.artifact_dir else None
        result = check_consistency_range(args.start_date, args.end_date, paths, mode=args.mode, artifact_dir=artifact_dir)
        print(
            {
                "passed": result["passed"],
                "mode": result["mode"],
                "items": len(result.get("items", [])),
                "report_path": result.get("report_path"),
            }
        )
        return 0
    if args.command == "fetch-prices":
        try:
            result = fetch_prices(
                args.start_date,
                args.end_date,
                _resolve_cli_path(args.output, paths),
                paths,
                source_mode=args.source,
            )
        except RuntimeError as exc:
            print(str(exc))
            return 1
        print(
            {
                "manifest_path": result["manifest_path"],
                "symbols_success": result["manifest"]["symbols_success"],
                "symbols_failed": result["manifest"]["symbols_failed"],
                "validation_passed": result["validation"]["passed"],
            }
        )
        return 1 if should_return_failure(result) else 0
    if args.command == "merge-price-data":
        result = merge_price_data(
            [_resolve_cli_path(value, paths) for value in args.inputs],
            _resolve_cli_path(args.output, paths),
            paths,
        )
        print({"passed": result["manifest"]["passed"], "manifest_path": result["manifest_path"]})
        return 0 if result["manifest"]["passed"] else 1
    if args.command == "real-data-validation-report":
        result = build_real_data_validation_report(_resolve_cli_path(args.artifact_dir, paths), paths)
        print({"release_candidate_passed": result["release_candidate_passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "dry-run-validation-report":
        result = build_dry_run_validation_report(args.start_date, args.end_date, paths)
        print({"dry_run_30d_passed": result["dry_run_30d_passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "replay-dry-run":
        result = replay_dry_run(
            args.start_date,
            args.end_date,
            _resolve_cli_path(args.data, paths),
            paths,
            write_main_ledger=args.write_main_ledger,
        )
        print({"historical_replay_passed": result["historical_replay_passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "replay-last-trading-days":
        result = replay_last_trading_days(
            args.days,
            args.end_date,
            _resolve_cli_path(args.data, paths),
            paths,
            write_main_ledger=args.write_main_ledger,
        )
        print({"historical_replay_passed": result["historical_replay_passed"], "report_path": result["report_path"]})
        return 0
    if args.command == "build-features":
        result = build_feature_matrix(args.start_date, args.end_date, _resolve_cli_path(args.data, paths), paths)
        print({"rows": result["rows"], "output_path": result["output_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "build-labels":
        result = build_label_matrix(args.start_date, args.end_date, _resolve_cli_path(args.data, paths), paths)
        print({"rows": result["rows"], "output_path": result["output_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "build-ml-dataset":
        result = build_walk_forward_dataset(
            _resolve_cli_path(args.features, paths),
            _resolve_cli_path(args.labels, paths),
            args.start_date,
            args.end_date,
            args.train_days,
            args.validation_days,
            args.test_days,
            args.step_days,
            args.label_column,
            paths,
        )
        print({"windows": len(result["windows"]), "rows": result["rows"], "output_path": result["output_path"]})
        return 0
    if args.command == "train-ml-shadow":
        try:
            result = train_ml_shadow_model(
                _resolve_cli_path(args.dataset, paths),
                _resolve_cli_path(args.rows, paths),
                args.model_type,
                args.label_column,
                paths,
            )
        except RuntimeError as exc:
            print(str(exc))
            return 1
        print({"model_id": result["model_id"], "model_path": result["model_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "predict-ml-shadow":
        result = generate_ml_shadow_predictions(
            _resolve_cli_path(args.model, paths),
            _resolve_cli_path(args.rows, paths),
            paths,
        )
        print({"predictions": result["prediction_count"], "output_path": result["output_path"]})
        return 0
    if args.command == "generate-ml-shadow-signals":
        result = generate_ml_shadow_signals(
            _resolve_cli_path(args.predictions, paths),
            args.top_k,
            args.target_weight,
            paths,
        )
        print({"signals": result["signal_count"], "output_path": result["output_path"]})
        return 0
    if args.command == "ml-shadow-leaderboard":
        result = build_ml_shadow_leaderboard(
            _resolve_cli_path(args.predictions, paths),
            _resolve_cli_path(args.signals, paths),
            args.benchmark,
            paths,
        )
        print({"recommendation": result["shadow_recommendation"], "output_path": result["output_path"]})
        return 0
    if args.command == "ml-shadow-report":
        result = build_ml_shadow_report(
            _resolve_cli_path(args.dataset, paths),
            _resolve_cli_path(args.model, paths),
            _resolve_cli_path(args.predictions, paths),
            _resolve_cli_path(args.signals, paths),
            _resolve_cli_path(args.leaderboard, paths),
            paths,
        )
        print({"model_id": result["model_id"], "report_path": result["report_path"]})
        return 0
    if args.command == "register-experiment":
        try:
            result = register_experiment(_resolve_cli_path(args.config, paths), paths)
        except Exception as exc:
            print(str(exc))
            return 1
        print({"experiment_id": result["experiment_id"], "status": result["status"]})
        return 0
    if args.command == "list-experiments":
        experiments = list_experiments(paths)
        print({"total": len(experiments), "experiments": [
            {"experiment_id": exp["experiment_id"], "status": exp.get("status", "unknown")}
            for exp in experiments
        ]})
        return 0
    if args.command == "show-experiment":
        experiment = get_experiment(args.experiment_id, paths)
        if experiment is None:
            print(f"Experiment '{args.experiment_id}' not found")
            return 1
        print(experiment)
        return 0
    if args.command == "run-parameter-sweep":
        try:
            result = run_parameter_sweep_from_config(
                _resolve_cli_path(args.config, paths), paths
            )
        except Exception as exc:
            print(str(exc))
            return 1
        print({
            "experiment_id": result["experiment_id"],
            "parameter_grid_size": result["parameter_grid_size"],
            "best_shadow_candidate": result["best_shadow_candidate"],
            "warnings": result["warnings"],
        })
        return 0
    if args.command == "experiment-dashboard":
        result = build_experiment_dashboard(
            experiments_dir=_resolve_project_path(args.experiments_dir, paths),
            shadow_dir=_resolve_project_path(args.shadow_dir, paths),
            output_dir=_resolve_project_path(args.output_dir, paths),
            paths=paths,
        )
        print({
            "dashboard_id": result["dashboard_id"],
            "registry_experiment_count": result["registry"]["experiment_count"],
            "parameter_sweep_count": len(result["parameter_sweeps"]),
            "ml_shadow_result_count": len(result["ml_shadow_results"]),
            "strategy_comparison_count": len(result["strategy_comparisons"]),
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0
    if args.command == "simulate-promotion":
        try:
            result = run_promotion_simulation(
                args.comparison,
                score_threshold=args.score_threshold,
                strict=args.strict,
                paths=paths,
            )
        except PromotionSimulationInputError as exc:
            print(str(exc))
            return 1
        print({
            "simulation_id": result["simulation_id"],
            "items": result["summary"]["total_items"],
            "reject": result["summary"]["reject"],
            "watch": result["summary"]["watch"],
            "shadow_candidate": result["summary"]["shadow_candidate"],
            "active_small_candidate": result["summary"]["active_small_candidate"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0
    if args.command == "compare-strategies":
        try:
            result = build_strategy_comparison(args.inputs, paths)
        except StrategyComparisonInputError as exc:
            print(str(exc))
            return 1
        print({
            "comparison_id": result["comparison_id"],
            "items": result["item_count"],
            "best_by_score": result["best_by_score"],
            "best_by_excess_return": result["best_by_excess_return"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0
    if args.command == "update-mistake-patterns":
        try:
            result = update_mistake_pattern_library(
                args.inputs,
                min_evidence=args.min_evidence,
                paths=paths,
            )
        except MistakePatternLibraryInputError as exc:
            print(str(exc))
            return 1
        print({
            "library_id": result["library_id"],
            "inputs": len(result["inputs"]),
            "patterns": len(result["patterns"]),
            "pattern_types": [pattern["pattern_type"] for pattern in result["patterns"]],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0
    if args.command == "audit-experiment-system":
        result = audit_experiment_system(
            experiments_dir=_resolve_project_path(args.experiments_dir, paths),
            shadow_dir=_resolve_project_path(args.shadow_dir, paths),
            outputs_dir=_resolve_project_path(args.outputs_dir, paths),
            audit_dir=_resolve_project_path(args.audit_dir, paths),
            paths=paths,
        )
        print({
            "audit_id": result["audit_id"],
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "weekly-research-report":
        result = build_weekly_research_report(
            args.start_date,
            args.end_date,
            include_experiments=args.include_experiments,
            include_ml_shadow=args.include_ml_shadow,
            include_mistakes=args.include_mistakes,
            paths=paths,
        )
        print({
            "report_id": result["report_id"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
            "warnings": len(result["warnings"]),
        })
        return 0
    if args.command == "monthly-research-report":
        try:
            result = build_monthly_research_report(
                start_date=args.start_date,
                end_date=args.end_date,
                month=args.month,
                include_weekly=args.include_weekly,
                include_experiments=args.include_experiments,
                include_ml_shadow=args.include_ml_shadow,
                paths=paths,
            )
        except ValueError as exc:
            print(str(exc))
            return 1
        print({
            "report_id": result["report_id"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
            "warnings": len(result["warnings"]),
        })
        return 0
    if args.command == "system-dashboard":
        result = build_system_dashboard(
            include_artifact_inventory=args.include_artifact_inventory,
            include_release_status=args.include_release_status,
            paths=paths,
        )
        print({
            "dashboard_id": result["dashboard_id"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
            "warnings": len(result["warnings"]),
        })
        return 0
    if args.command == "project-status-report":
        result = build_project_status_report(
            include_next_steps=args.include_next_steps,
            include_risk_register=args.include_risk_register,
            paths=paths,
        )
        print({
            "report_id": result["report_id"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
            "warnings": len(result["warnings"]),
        })
        return 0
    if args.command == "run-research-pipeline":
        result = run_research_pipeline(
            args.start_date,
            args.end_date,
            skip_weekly=args.skip_weekly,
            skip_monthly=args.skip_monthly,
            skip_dashboard=args.skip_dashboard,
            skip_project_status=args.skip_project_status,
            paths=paths,
        )
        print({
            "pipeline_id": result["pipeline_id"],
            "status": result["status"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
            "warnings": len(result["warnings"]),
            "failures": len(result["failures"]),
        })
        return 0
    if args.command == "audit-reporting-system":
        result = audit_reporting_system(
            reports_dir=_resolve_project_path(args.reports_dir, paths),
            system_dir=_resolve_project_path(args.system_dir, paths),
            audit_dir=_resolve_project_path(args.audit_dir, paths),
            paths=paths,
        )
        print({
            "audit_id": result["audit_id"],
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "cli-inventory":
        result = build_cli_inventory(paths)
        print({"commands": len(result["commands"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "artifact-inventory":
        result = build_artifact_inventory(paths)
        print({"artifacts": len(result["artifacts"]), "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "system-smoke-test":
        result = run_system_smoke_test(
            fast=args.fast,
            include_reports=args.include_reports,
            include_inventory=args.include_inventory,
            paths=paths,
        )
        print({
            "passed": result["passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["passed"] else 1
    if args.command == "boundary-regression-audit":
        result = run_boundary_regression_audit(paths=paths)
        print({
            "passed": result["passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["passed"] else 1
    if args.command == "system-integrity-audit":
        result = run_system_integrity_audit(paths)
        print({
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "final-handoff-review":
        result = build_final_handoff_review(paths)
        print({
            "review_id": result["review_id"],
            "overall_status": result["overall_status"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0
    if args.command == "report-index":
        result = build_report_index(
            include_audit=args.include_audit,
            include_experiments=args.include_experiments,
            include_system=args.include_system,
            paths=paths,
        )
        print({"reports": len(result["reports"]), "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "latest-artifact":
        try:
            result = locate_latest_artifact(args.type, open_command=args.open_command, paths=paths)
        except ValueError as exc:
            print(str(exc))
            return 1
        if args.json_output:
            print(result)
        else:
            print({
                "query_type": result["query_type"],
                "latest": result["latest"] or result["latest_by_type"],
                "warnings": len(result["warnings"]),
                "open_command": result["open_command"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            })
        return 0
    if args.command == "artifact-browser":
        result = build_artifact_browser(
            include_missing=args.include_missing,
            group_by=args.group_by,
            paths=paths,
        )
        print({"start_here": len(result["start_here"]), "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "quick-status":
        result = build_quick_status(paths)
        if args.json_output:
            print(result)
        else:
            print({
                "current_version": result["current_version"],
                "recommended_next_command": result["recommended_next_command"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            })
        return 0
    if args.command == "usability-audit":
        result = run_usability_audit(paths)
        print({
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-readiness":
        result = run_forward_dry_run_readiness(
            start_date=args.start_date,
            trading_days=args.trading_days,
            calendar=args.calendar,
            strict=args.strict,
            paths=paths,
        )
        print({
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
            "day0_checklist_path": result["day0_checklist_path"],
            "plan_path": result["plan_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "global-briefing-contract":
        result = build_signal_contract(paths)
        print({"contract_id": result["contract_id"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "validate-global-briefing-signals":
        result = validate_global_briefing_signals(
            args.input,
            start_date=args.start_date,
            end_date=args.end_date,
            strict=args.strict,
            paths=paths,
        )
        print({
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "build-global-briefing-replay-bundle":
        try:
            result = build_global_briefing_replay_bundle(
                args.signals,
                args.prices,
                start_date=args.start_date,
                end_date=args.end_date,
                decision_time=args.decision_time,
                allow_carry_forward=args.allow_carry_forward,
                paths=paths,
            )
        except ValueError as exc:
            print(str(exc))
            return 1
        print({
            "bundle_id": result["bundle_id"],
            "replay_days": result["coverage"]["replay_days"],
            "future_signal_used": result["point_in_time"]["future_signal_used"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if not result["point_in_time"]["future_signal_used"] else 1
    if args.command == "replay-global-briefing-history":
        try:
            result = replay_global_briefing_history(
                args.bundle,
                args.prices,
                start_date=args.start_date,
                end_date=args.end_date,
                initial_cash=args.initial_cash,
                execution_mode=args.execution_mode,
                max_symbol_weight=args.max_symbol_weight,
                max_total_weight=args.max_total_weight,
                lot_size=args.lot_size,
                commission_rate=args.commission_rate,
                isolated_output_root=args.isolated_output_root,
                report_output_root=args.report_output_root,
                paths=paths,
            )
        except ValueError as exc:
            print(str(exc))
            return 1
        print({
            "replay_id": result["replay_id"],
            "isolated": result["isolated"],
            "execution_mode": result["execution"]["mode"],
            "no_trade_fallback": result["execution"]["no_trade_fallback"],
            "main_ledger_written": result["boundary"]["main_ledger_written"],
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["isolated"] and not result["boundary"]["main_ledger_written"] else 1
    if args.command == "global-briefing-replay-report":
        result = build_global_briefing_replay_report(
            args.replay,
            bundle_path=args.bundle,
            validation_path=args.validation,
            paths=paths,
        )
        print({
            "evaluation_id": result["evaluation_id"],
            "overall_status": result["overall_status"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_status"] == "research_review_ready" else 1
    if args.command == "audit-global-briefing-replay":
        result = audit_global_briefing_replay(
            validation_path=args.validation,
            bundle_path=args.bundle,
            replay_path=args.replay,
            evaluation_path=args.evaluation,
            paths=paths,
        )
        print({
            "audit_id": result["audit_id"],
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-isolated-replay-adapter":
        result = audit_isolated_replay_adapter(
            replay_path=args.replay,
            evaluation_path=args.evaluation,
            paths=paths,
        )
        print({
            "audit_id": result["audit_id"],
            "overall_passed": result["overall_passed"],
            "blocking_reasons": result["blocking_reasons"],
            "warnings": len(result["warnings"]),
            "json_path": result["json_path"],
            "report_path": result["report_path"],
        })
        return 0 if result["overall_passed"] else 1
    if args.command == "global-briefing-package-manifest":
        result = build_global_briefing_package_manifest(root=args.root, include=args.include, output=args.output, paths=paths)
        print({"packages": result["counts"]["packages"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "normalize-global-briefing-package":
        result = normalize_global_briefing_package(
            args.input,
            package_id=args.package_id,
            region=args.region,
            source=args.source,
            version=args.version,
            output=args.output,
            strict=args.strict,
            paths=paths,
        )
        print({"overall_passed": result["overall_passed"], "rows_out": result["rows_out"], "blocking_reasons": result["blocking_reasons"], "output": result["output"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-global-briefing-package-coverage":
        result = audit_global_briefing_package_coverage(
            args.signals,
            prices_path=args.prices,
            calendar_path=args.calendar,
            start_date=args.start_date,
            end_date=args.end_date,
            min_coverage=args.min_coverage,
            strict=args.strict,
            paths=paths,
        )
        print({"overall_passed": result["overall_passed"], "coverage_ratio": result["coverage"]["coverage_ratio"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "run-global-briefing-real-package-replay":
        result = run_global_briefing_real_package_replay(
            args.input,
            args.prices,
            start_date=args.start_date,
            end_date=args.end_date,
            package_id=args.package_id,
            region=args.region,
            source=args.source,
            version=args.version,
            allow_carry_forward=args.allow_carry_forward,
            min_coverage=args.min_coverage,
            execution_mode=args.execution_mode,
            strict=args.strict,
            paths=paths,
        )
        print({"workflow_id": result["workflow_id"], "overall_status": result["overall_status"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_status"] == "research_review_ready" else 1
    if args.command == "global-briefing-real-package-report":
        result = build_global_briefing_real_package_report(
            manifest_path=args.manifest,
            workflow_path=args.workflow,
            coverage_path=args.coverage,
            evaluation_path=args.evaluation,
            paths=paths,
        )
        print({"report_id": result["report_id"], "overall_status": result["overall_status"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-global-briefing-real-package-integration":
        result = audit_global_briefing_real_package_integration(
            manifest_path=args.manifest,
            workflow_path=args.workflow,
            report_path=args.report,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "global-briefing-warning-triage":
        result = build_global_briefing_warning_triage(
            coverage_path=args.coverage,
            workflow_path=args.workflow,
            report_path=args.report,
            audit_path=args.audit,
            paths=paths,
        )
        print({"triage_id": result["triage_id"], "warning_count": result["warning_count"], "production_blockers": result["production_blockers"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "global-briefing-evidence-quality-report":
        result = build_global_briefing_evidence_quality_report(
            triage_path=args.triage,
            coverage_path=args.coverage,
            workflow_path=args.workflow,
            audit_path=args.audit,
            paths=paths,
        )
        print({"report_id": result["report_id"], "overall_evidence_status": result["overall_evidence_status"], "production_ready": result["production_readiness"]["ready"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "global-briefing-production-acceptance-criteria":
        result = build_global_briefing_production_acceptance_criteria(paths=paths)
        print({"criteria_id": result["criteria_id"], "json_path": result["json_path"], "report_path": result["report_path"], "docs_path": result["docs_path"]})
        return 0
    if args.command == "audit-global-briefing-evidence-quality":
        result = audit_global_briefing_evidence_quality(
            triage_path=args.triage,
            evidence_path=args.evidence,
            criteria_path=args.criteria,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "historical-data-source-resolution":
        result = resolve_historical_data_sources(
            packages=_split_csv_arg(args.packages),
            start_date=args.start_date,
            end_date=args.end_date,
            preferred_source=args.preferred_source,
            paths=paths,
        )
        print({"resolution_id": result["resolution_id"], "packages": len(result["packages"]), "overall_passed": result["overall_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "download-historical-data-packages":
        result = download_historical_data_packages(
            packages=_split_csv_arg(args.packages),
            start_date=args.start_date,
            end_date=args.end_date,
            continue_on_error=args.continue_on_error,
            source_mode=args.source_mode,
            timeout_seconds=args.timeout_seconds,
            max_retries=args.max_retries,
            paths=paths,
        )
        print({"manifest_id": result["manifest_id"], "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "normalize-historical-data-packages":
        result = normalize_historical_data_packages(
            download_manifest_path=args.download_manifest,
            start_date=args.start_date,
            end_date=args.end_date,
            paths=paths,
        )
        print({"normalization_id": result["normalization_id"], "proxy_validated": result["proxy_package"]["validated"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["proxy_package"]["validated"] else 1
    if args.command == "audit-historical-data-quality":
        result = audit_historical_data_quality(
            download_manifest_path=args.download_manifest,
            normalization_path=args.normalization,
            start_date=args.start_date,
            end_date=args.end_date,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "run-full-historical-proxy-replay":
        result = run_full_historical_proxy_replay(
            signals_path=args.signals,
            prices_path=args.prices,
            start_date=args.start_date,
            end_date=args.end_date,
            min_coverage=args.min_coverage,
            execution_mode=args.execution_mode,
            strict=args.strict,
            paths=paths,
        )
        print({"workflow_id": result["workflow_id"], "overall_status": result["overall_status"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_status"] == "research_review_ready" else 1
    if args.command == "historical-data-acquisition-report":
        result = build_historical_data_acquisition_report(
            download_manifest_path=args.download_manifest,
            normalization_path=args.normalization,
            quality_audit_path=args.quality_audit,
            proxy_workflow_path=args.proxy_workflow,
            paths=paths,
        )
        print({"report_id": result["report_id"], "overall_status": result["overall_status"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-historical-data-acquisition":
        result = audit_historical_data_acquisition(
            source_resolution_path=args.source_resolution,
            download_manifest_path=args.download_manifest,
            normalization_path=args.normalization,
            quality_audit_path=args.quality_audit,
            proxy_workflow_path=args.proxy_workflow,
            report_path=args.report,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "historical-warning-inventory":
        result = build_historical_warning_inventory(
            quality_audit_path=args.quality_audit,
            workflow_path=args.workflow,
            download_manifest_path=args.download_manifest,
            paths=paths,
        )
        print({"inventory_id": result["inventory_id"], "raw_warning_count": result["raw_warning_count"], "grouped_warning_count": result["grouped_warning_count"], "unknown_warning_count": result["unknown_warning_count"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["unknown_warning_count"] == 0 else 1
    if args.command == "close-historical-data-gaps":
        result = close_historical_data_gaps(
            start_date=args.start_date,
            end_date=args.end_date,
            replay_start_date=args.replay_start_date,
            replay_end_date=args.replay_end_date,
            min_coverage=args.min_coverage,
            continue_on_error=args.continue_on_error,
            paths=paths,
        )
        print({"workflow_id": result["workflow_id"], "overall_status": result["overall_status"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_status"] in {"passed", "passed_with_warnings"} else 1
    if args.command == "historical-data-gap-closure-report":
        result = build_historical_data_gap_closure_report(workflow_path=args.workflow, paths=paths)
        print({"report_id": result["report_id"], "overall_status": result["overall_status"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-historical-data-gap-closure":
        result = audit_historical_data_gap_closure(workflow_path=args.workflow, report_path=args.report, paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "day0-data-freeze":
        result = build_day0_data_freeze(download_manifest_path=args.download_manifest, quality_audit_path=args.quality_audit, gap_closure_audit_path=args.gap_closure_audit, proxy_package_path=args.proxy_package, paths=paths)
        print({"freeze_id": result["freeze_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "day0-warning-register":
        result = build_day0_warning_register(warning_inventory_path=args.warning_inventory, gap_closure_report_path=args.gap_closure_report, paths=paths)
        print({"register_id": result["register_id"], "accepted_count": result["accepted_count"], "unresolved_count": result["unresolved_count"], "blocking_count": result["blocking_count"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["blocking_count"] == 0 else 1
    if args.command == "day0-blocking-conditions":
        result = build_day0_blocking_conditions(data_freeze_path=args.data_freeze, warning_register_path=args.warning_register, gap_closure_audit_path=args.gap_closure_audit, paths=paths)
        print({"register_id": result["register_id"], "current_blocking_count": result["current_blocking_count"], "manual_confirmation_still_required": result["manual_confirmation_still_required"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["current_blocking_count"] == 0 else 1
    if args.command == "day0-run-daily-preflight":
        result = build_day0_run_daily_preflight(data_freeze_path=args.data_freeze, warning_register_path=args.warning_register, blocking_conditions_path=args.blocking_conditions, paths=paths)
        print({"preflight_id": result["preflight_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "executed": result["run_daily_command_preview"]["executed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "day0-manual-confirmation-packet":
        result = build_day0_manual_confirmation_packet(paths=paths)
        print({"packet_id": result["packet_id"], "manual_confirmation_complete": result["manual_confirmation_complete"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-operating-calendar":
        result = build_forward_dry_run_operating_calendar(start_date=args.start_date, trading_days=args.trading_days, paths=paths)
        print({"calendar_id": result["calendar_id"], "calendar_status": result["calendar_status"], "days": len(result["days"]), "json_path": result["json_path"], "report_path": result["report_path"], "daily_log_template_path": result["daily_log_template_path"]})
        return 0
    if args.command == "day0-readiness-report":
        result = build_day0_readiness_report(paths=paths)
        print({"report_id": result["report_id"], "overall_status": result["overall_status"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-day0-readiness":
        result = audit_day0_readiness(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "plan-checklist":
        result = build_plan_checklist(plan_path=args.plan, paths=paths)
        print({"checklist_id": result["checklist_id"], "requirements": len(result["requirements"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "mvp-requirement-map":
        result = build_mvp_requirement_map(checklist_path=args.checklist, paths=paths)
        print({"map_id": result["map_id"], "requirements": len(result["requirements"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "artifact-coverage-scanner":
        result = build_artifact_coverage_scan(paths=paths)
        print({"scan_id": result["scan_id"], "counts": result["counts"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "classify-mvp-gaps":
        result = classify_mvp_gaps(checklist_path=args.checklist, requirement_map_path=args.requirement_map, artifact_scan_path=args.artifact_scan, paths=paths)
        print({"classification_id": result["classification_id"], "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "classify-day1-blockers":
        result = classify_day1_blockers(mvp_gap_classification_path=args.mvp_gap_classification, paths=paths)
        print({"classifier_id": result["classifier_id"], "day1_allowed": result["day1_allowed"], "blocking_count": result["blocking_count"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "next-work-register":
        result = build_next_work_register(mvp_gap_classification_path=args.mvp_gap_classification, day1_blocker_classification_path=args.day1_blocker_classification, paths=paths)
        print({"register_id": result["register_id"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-plan-alignment":
        result = audit_plan_alignment(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "ashare-execution-gap-plan":
        result = build_ashare_execution_gap_plan(mvp_gaps_path=args.mvp_gaps, day1_blockers_path=args.day1_blockers, next_work_path=args.next_work, paths=paths)
        print({"plan_id": result["plan_id"], "baseline_day1_blocker_count": result["baseline_day1_blocker_count"], "target_day1_blocker_count": result["target_day1_blocker_count"], "work_items": len(result["work_items"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "ashare-trading-calendar-audit":
        contract = build_trading_calendar_contract(paths=paths)
        result = audit_trading_calendar(paths=paths)
        print({"contract_path": contract["json_path"], "audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "execution-timeline-contract":
        result = build_execution_timeline_contract(paths=paths)
        print({"contract_id": result["contract_id"], "same_day_close_signal_execution_rejected": result["same_day_close_signal_execution_rejected"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "ashare-price-status-contract":
        result = build_price_status_contract(paths=paths)
        print({"contract_id": result["contract_id"], "statuses": len(result["supported_statuses"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "ashare-lot-and-position-contract":
        result = build_lot_position_contract(paths=paths)
        print({"contract_id": result["contract_id"], "default_board_lot": result["default_board_lot"], "t_plus_1_available_after_settlement": result["t_plus_1_available_after_settlement"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "ashare-execution-cost-contract":
        result = build_execution_cost_contract(paths=paths)
        print({"contract_id": result["contract_id"], "commission_bps": result["commission_bps"], "slippage_bps": result["slippage_bps"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "virtual-execution-contract":
        result = build_virtual_execution_contract(paths=paths)
        print({"contract_id": result["contract_id"], "integrates": len(result["integrates"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-isolated-ledger-invariants":
        result = audit_isolated_ledger_invariants(ledger_dir=args.ledger_dir, paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "execution-aware-replay-smoke":
        result = run_execution_aware_replay_smoke(start_date=args.start_date, end_date=args.end_date, execution_mode=args.execution_mode, paths=paths)
        print({"smoke_id": result["smoke_id"], "overall_passed": result["overall_passed"], "included_scenarios": result["included_scenarios"], "ledger_invariant_audit_passed": result["ledger_invariant_audit_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "reclassify-day1-blockers-after-execution-hardening":
        result = reclassify_day1_blockers_after_execution_hardening(baseline_path=args.baseline, paths=paths)
        print({"reclassification_id": result["reclassification_id"], "baseline_day1_blocker_count": result["baseline_day1_blocker_count"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-ashare-execution-rules":
        result = audit_ashare_execution_rules(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "baseline-strategy-scope-plan":
        result = build_baseline_strategy_scope_plan(paths=paths)
        print({"plan_id": result["plan_id"], "execution_day1_blockers_closed": result["execution_day1_blockers_closed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "baseline-strategy-contract":
        result = build_baseline_strategy_contract(paths=paths)
        print({"contract_id": result["contract_id"], "strategies": len(result["strategies"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "baseline-strategy-registry":
        result = build_baseline_strategy_registry(paths=paths)
        print({"registry_id": result["registry_id"], "strategies": len(result["strategies"]), "parameter_versions": result["parameter_versions"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "generate-baseline-strategy-signals":
        result = generate_baseline_strategy_signals(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, paths=paths)
        print({"strategies": result["strategies"], "all_signals_generated": result["all_signals_generated"], "all_pit_constraints_passed": result["all_pit_constraints_passed"], "paths": result["paths"]})
        return 0 if result["all_signals_generated"] and result["all_pit_constraints_passed"] else 1
    if args.command == "build-baseline-order-preview":
        result = build_baseline_order_preview(strategy=args.strategy, signals=args.signals, execution_mode=args.execution_mode, paths=paths)
        print({"strategy": result["strategy"], "execution_mode": result["execution_mode"], "preview_only": result["preview_only"], "executed": result["executed"], "paths": result["paths"]})
        return 0 if result["preview_only"] and not result["executed"] else 1
    if args.command == "replay-baseline-strategy":
        result = replay_baseline_strategy(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, execution_mode=args.execution_mode, paths=paths)
        print({"strategy": result["strategy"], "execution_mode": result["execution_mode"], "all_replays_complete": result["all_replays_complete"], "paths": result["paths"]})
        return 0 if result["all_replays_complete"] else 1
    if args.command == "compare-baseline-strategy-benchmarks":
        result = compare_baseline_strategy_benchmarks(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, paths=paths)
        print({"comparison_id": result["comparison_id"], "strategies": list(result["strategies"].keys()), "benchmarks": list(result["benchmarks"].keys()), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "baseline-strategy-report":
        result = build_baseline_strategy_report(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, paths=paths)
        print({"strategy": result["strategy"], "all_reports_generated": result["all_reports_generated"], "paths": result["paths"]})
        return 0 if result["all_reports_generated"] else 1
    if args.command == "baseline-strategy-pack-summary":
        result = build_baseline_strategy_pack_summary(paths=paths)
        print({"summary_id": result["summary_id"], "all_strategies_complete": result["all_strategies_complete"], "strategy_count": result["strategy_count"], "strategies_complete": result["strategies_complete"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-baseline-strategy-pack":
        result = audit_baseline_strategy_pack(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "reclassify-day1-blockers-after-baseline-strategies":
        result = reclassify_day1_blockers_after_baseline_strategies(paths=paths)
        print({"reclassification_id": result["reclassification_id"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_version": result["recommended_next_version"], "day1_start_allowed": result["day1_start_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "daily-workflow-scope-plan":
        result = build_daily_workflow_scope_plan(paths=paths)
        print({"plan_id": result["plan_id"], "target_version": result["target_version"], "baseline_strategy_pack_complete": result["baseline_strategy_pack_complete"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "daily-market-data-snapshot":
        result = build_daily_market_data_snapshot(as_of_date=args.as_of_date, paths=paths)
        print({"snapshot_id": result["snapshot_id"], "as_of_date": result["as_of_date"], "latest_available_trading_date": result["latest_available_trading_date"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-daily-data-quality":
        result = audit_daily_data_quality(snapshot=args.snapshot, paths=paths)
        print({"as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "daily-input-freeze-manifest":
        result = build_daily_input_freeze_manifest(as_of_date=args.as_of_date, paths=paths)
        print({"manifest_id": result["manifest_id"], "as_of_date": result["as_of_date"], "latest_available_trading_date": result["latest_available_trading_date"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "daily-baseline-signals":
        result = build_daily_baseline_signals(as_of_date=args.as_of_date, strategy=args.strategy, paths=paths)
        print({"as_of_date": result["as_of_date"], "strategies_total": result["strategies_total"], "all_pit_constraints_passed": result["all_pit_constraints_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["all_pit_constraints_passed"] else 1
    if args.command == "daily-order-preview":
        result = build_daily_order_preview(as_of_date=args.as_of_date, strategy=args.strategy, execution_mode=args.execution_mode, paths=paths)
        print({"as_of_date": result["as_of_date"], "proposal_count": result["proposal_count"], "preview_only": result["preview_only"], "executed": result["executed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["preview_only"] and not result["executed"] else 1
    if args.command == "daily-isolated-execution-preview":
        result = build_daily_isolated_execution_preview(as_of_date=args.as_of_date, execution_mode=args.execution_mode, paths=paths)
        print({"as_of_date": result["as_of_date"], "execution_mode": result["execution_mode"], "preview_only": result["preview_only"], "executed": result["executed"], "state_updated": result["state_updated"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["preview_only"] and not result["executed"] and not result["state_updated"] else 1
    if args.command == "daily-report-packet":
        result = build_daily_report_packet(as_of_date=args.as_of_date, paths=paths)
        print({"as_of_date": result["as_of_date"], "latest_available_trading_date": result["latest_available_trading_date"], "signals": len(result["signals_summary_by_strategy"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "protected-path-residue-scan":
        result = scan_protected_path_residue(paths=paths)
        print({"scan_id": result["scan_id"], "overall_passed": result["overall_passed"], "blocker_count": result["blocker_count"], "warning_count": result["warning_count"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-daily-workflow":
        result = audit_daily_workflow(as_of_date=args.as_of_date, paths=paths)
        print({"release_candidate": result["release_candidate"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "reclassify-day1-blockers-after-daily-workflow":
        result = reclassify_day1_blockers_after_daily_workflow(paths=paths)
        print({"reclassification_id": result["reclassification_id"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_version": result["recommended_next_version"], "day1_start_allowed": result["day1_start_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-authorization-scope-plan":
        result = build_forward_dry_run_authorization_scope_plan(paths=paths)
        print({"plan_id": result["plan_id"], "target_version": result["target_version"], "daily_workflow_audit_passed": result["daily_workflow_audit_passed"], "known_day1_blockers_closed": result["known_day1_blockers_closed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-start-prerequisite-inventory":
        result = build_forward_dry_run_start_prerequisite_inventory(paths=paths)
        print({"inventory_id": result["inventory_id"], "overall_day1_allowed": result["overall_day1_allowed"], "prerequisites": len(result["prerequisites"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "current-daily-workflow-readiness-snapshot":
        result = build_current_daily_workflow_readiness_snapshot(paths=paths)
        print({"snapshot_id": result["snapshot_id"], "historical_daily_workflow_fixture_passed": result["historical_daily_workflow_fixture_passed"], "current_production_daily_workflow_authorized": result["current_production_daily_workflow_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-manual-confirmation-checklist-v2":
        result = build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
        print({"checklist_id": result["checklist_id"], "manual_confirmation_complete": result["manual_confirmation_complete"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-owner-authorization-packet":
        result = build_forward_dry_run_owner_authorization_packet(paths=paths)
        print({"authorization_packet_id": result["authorization_packet_id"], "authorization_status": result["authorization_status"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "validate-forward-dry-run-start-gate-v062":
        result = validate_forward_dry_run_start_gate_v062(paths=paths)
        print({"gate_id": result["gate_id"], "day1_start_allowed": result["day1_start_allowed"], "deny_reasons": result["deny_reasons"], "run_daily_command_preview": result["run_daily_command_preview"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-run-daily-command-preview":
        result = build_forward_dry_run_run_daily_command_preview(paths=paths)
        print({"preview_id": result["preview_id"], "preview_only": result["preview_only"], "executed": result["executed"], "run_daily_called": result["run_daily_called"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-day1-prompt-eligibility":
        result = build_forward_dry_run_day1_prompt_eligibility(paths=paths)
        print({"eligibility_id": result["eligibility_id"], "day1_prompt_eligible": result["day1_prompt_eligible"], "day1_prompt_generated": result["day1_prompt_generated"], "deny_reasons": result["deny_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-forward-dry-run-start-authorization":
        result = audit_forward_dry_run_start_authorization(paths=paths)
        print({"release_candidate": result["release_candidate"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "reclassify-day1-blockers-after-start-authorization":
        result = reclassify_day1_blockers_after_start_authorization(paths=paths)
        print({"reclassification_id": result["reclassification_id"], "technical_day1_blocker_count": result["technical_day1_blocker_count"], "authorization_blocker_count": result["authorization_blocker_count"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_action": result["recommended_next_action"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-owner-manual-confirmation-record":
        result = build_owner_manual_confirmation_record(paths=paths)
        print({"record_id": result["record_id"], "owner_confirmation_recorded": result["owner_confirmation_recorded"], "owner_authorized_next_step": result["owner_authorized_next_step"], "owner_authorized_day1_execution": result["owner_authorized_day1_execution"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "complete-forward-dry-run-manual-confirmation-checklist-v2":
        result = complete_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)
        print({"checklist_id": result["checklist_id"], "manual_confirmation_complete": result["manual_confirmation_complete"], "day1_execution_authorized": result["day1_execution_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "update-forward-dry-run-owner-authorization-packet":
        result = update_forward_dry_run_owner_authorization_packet(paths=paths)
        print({"authorization_packet_id": result["authorization_packet_id"], "authorization_status": result["authorization_status"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "day1_execution_authorized": result["day1_execution_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "revalidate-forward-dry-run-start-gate-v0621":
        result = revalidate_forward_dry_run_start_gate_v0621(paths=paths)
        print({"gate_id": result["gate_id"], "technical_prerequisites_passed": result["technical_prerequisites_passed"], "manual_confirmation_complete": result["manual_confirmation_complete"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "day1_prompt_eligible": result["day1_prompt_eligible"], "day1_start_allowed": result["day1_start_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "revalidate-forward-dry-run-day1-prompt-eligibility":
        result = revalidate_forward_dry_run_day1_prompt_eligibility(paths=paths)
        print({"eligibility_id": result["eligibility_id"], "day1_prompt_eligible": result["day1_prompt_eligible"], "day1_prompt_generated": result["day1_prompt_generated"], "next_required_action": result["next_required_action"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-forward-dry-run-authorization-materialization":
        result = audit_forward_dry_run_authorization_materialization(paths=paths)
        print({"release_candidate": result["release_candidate"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "reclassify-day1-blockers-after-authorization-materialization":
        result = reclassify_day1_blockers_after_authorization_materialization(paths=paths)
        print({"reclassification_id": result["reclassification_id"], "technical_day1_blocker_count": result["technical_day1_blocker_count"], "authorization_blocker_count": result["authorization_blocker_count"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_action": result["recommended_next_action"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-day1-pre-execution-gate":
        result = build_day1_pre_execution_gate(allow_rerun=args.allow_rerun, paths=paths)
        print({"gate_id": result["gate_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-day1-input-snapshot":
        result = build_day1_input_snapshot(as_of_date=args.as_of_date, paths=paths)
        print({"snapshot_id": result["snapshot_id"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-day1-strategy-signals":
        result = build_day1_strategy_signals(paths=paths)
        print({"signals_id": result["signals_id"], "as_of_date": result["as_of_date"], "strategies_total": result["strategies_total"], "strategies_generated": result["strategies_generated"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["strategies_generated"] == result["strategies_total"] else 1
    if args.command == "forward-dry-run-day1-virtual-order-preview":
        result = build_day1_virtual_order_preview(paths=paths)
        print({"order_preview_id": result["order_preview_id"], "as_of_date": result["as_of_date"], "orders_total": result["summary"]["orders_total"], "orders_rejected": result["summary"]["orders_rejected"], "preview_only": result["preview_only"], "real_order": result["real_order"], "broker_order": result["broker_order"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["preview_only"] and not result["real_order"] and not result["broker_order"] else 1
    if args.command == "forward-dry-run-day1-virtual-execution":
        result = build_day1_virtual_execution_result(paths=paths)
        print({"execution_result_id": result["execution_result_id"], "as_of_date": result["as_of_date"], "execution_mode": result["execution_mode"], "virtual_execution": result["virtual_execution"], "real_execution": result["real_execution"], "broker_execution": result["broker_execution"], "fills": len(result["fills"]), "rejects": len(result["rejects"]), "ledger_writes": result["ledger_writes"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["virtual_execution"] and not result["real_execution"] and not result["broker_execution"] else 1
    if args.command == "forward-dry-run-day1-ledger-snapshot":
        result = build_day1_ledger_snapshot(paths=paths)
        print({"ledger_snapshot_id": result["ledger_snapshot_id"], "forward_dry_run_started": result["forward_dry_run_started"], "forward_dry_run_days_completed": result["forward_dry_run_days_completed"], "next_day_index": result["next_day_index"], "fills_count": result["fills_count"], "rejects_count": result["rejects_count"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-day1-risk-boundary-report":
        result = build_day1_risk_and_boundary_report(paths=paths)
        print({"report_id": result["report_id"], "risk_summary": result["risk_summary"], "boundary_summary": result["boundary_summary"], "warnings": len(result["warnings"]), "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if not result["blocking_reasons"] else 1
    if args.command == "forward-dry-run-day1-operator-report":
        result = build_day1_operator_report(paths=paths)
        print({"report_id": result["report_id"], "as_of_date": result["as_of_date"], "execution_date": result["execution_date"], "strategies_included": result["strategies_included"], "next_allowed_action": result["next_allowed_action"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "audit-forward-dry-run-day1":
        result = audit_forward_dry_run_day1(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-status":
        result = build_forward_dry_run_status(paths=paths)
        print({"status_id": result["status_id"], "forward_dry_run_started": result["forward_dry_run_started"], "forward_dry_run_days_completed": result["forward_dry_run_days_completed"], "next_day_index": result["next_day_index"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "reclassify-day1-blockers-after-forward-dry-run-day1":
        result = reclassify_day1_blockers_after_forward_dry_run_day1(paths=paths)
        print({"reclassification_id": result["reclassification_id"], "remaining_day1_blocker_count": result["remaining_day1_blocker_count"], "day2_blocker_count": result["day2_blocker_count"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-day1-continuation-gap-analysis":
        result = build_day1_continuation_gap_analysis(paths=paths)
        print({"analysis_id": result["analysis_id"], "day1_core_execution_passed": result["day1_core_execution_passed"], "v064_preflight_blocked": result["v064_preflight_blocked"], "missing_artifacts": result["missing_artifacts"], "day2_execution_allowed_in_this_stage": result["day2_execution_allowed_in_this_stage"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-day1-artifact-manifest":
        result = build_day1_artifact_manifest(paths=paths)
        print({"manifest_id": result["manifest_id"], "required_artifacts_total": result["required_artifacts_total"], "required_artifacts_present": result["required_artifacts_present"], "missing_required_artifacts": result["missing_required_artifacts"], "overall_passed": result["overall_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-day1-reproducibility-manifest":
        result = build_day1_reproducibility_manifest(paths=paths)
        print({"manifest_id": result["manifest_id"], "baseline_tag": result["baseline_tag"], "day1_as_of_date": result["day1_as_of_date"], "external_api_called": result["external_api_called"], "real_time_market_data_downloaded": result["real_time_market_data_downloaded"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-day2-readiness-packet":
        result = build_day2_readiness_packet(paths=paths)
        print({"packet_id": result["packet_id"], "day1_passed": result["day1_passed"], "day1_artifacts_complete": result["day1_artifacts_complete"], "day2_prompt_eligible_after_operator_review": result["day2_prompt_eligible_after_operator_review"], "operator_review_required": result["operator_review_required"], "day2_executed": result["day2_executed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "forward-dry-run-day2-continuation-gate-preview":
        result = build_day2_continuation_gate_preview(paths=paths)
        print({"preview_id": result["preview_id"], "day2_continuation_structurally_eligible": result["day2_continuation_structurally_eligible"], "operator_review_required": result["operator_review_required"], "day2_execution_authorized_in_this_artifact": result["day2_execution_authorized_in_this_artifact"], "day2_executed": result["day2_executed"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-forward-dry-run-day1-continuation-artifacts":
        result = audit_day1_continuation_artifacts(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "reclassify-day1-continuation-artifacts-v0631":
        result = reclassify_day1_continuation_artifacts_v0631(paths=paths)
        print({"reclassification_id": result["reclassification_id"], "continuation_artifact_gap_resolved": result["continuation_artifact_gap_resolved"], "remaining_continuation_artifact_gap_count": result["remaining_continuation_artifact_gap_count"], "day2_blocker_count": result["day2_blocker_count"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["continuation_artifact_gap_resolved"] else 1
    if args.command == "forward-dry-run-day1-owner-report-scope-plan":
        result = build_day1_owner_report_scope_plan(paths=paths)
        print({"scope_plan_id": result["scope_plan_id"], "target_version": result["target_version"], "report_only": result["report_only"], "day2_execution_allowed": result["day2_execution_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-day1-owner-summary-report":
        result = build_day1_owner_summary_report(paths=paths)
        print({"report_id": result["report_id"], "as_of_date": result["as_of_date"], "key_numbers": result["key_numbers"], "day2_executed": result["boundary"]["day2_executed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "forward-dry-run-day1-strategy-signal-explanation":
        result = build_day1_strategy_signal_explanation(paths=paths)
        print({"report_id": result["report_id"], "strategies_total": result["strategies_total"], "strategies_explained": result["strategies_explained"], "promotion_triggered": result["boundary"]["promotion_triggered"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["strategies_explained"] == result["strategies_total"] else 1
    if args.command == "forward-dry-run-day1-virtual-order-fill-report":
        result = build_day1_virtual_order_fill_report(paths=paths)
        print({"report_id": result["report_id"], "orders_total": result["orders_total"], "fills_total": result["fills_total"], "rejects_total": result["rejects_total"], "real_orders_placed": result["real_orders_placed"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if not result["real_orders_placed"] and not result["broker_orders_placed"] else 1
    if args.command == "forward-dry-run-day1-isolated-ledger-report":
        result = build_day1_isolated_ledger_report(paths=paths)
        print({"report_id": result["report_id"], "forward_dry_run_ledger_written": result["forward_dry_run_ledger_written"], "ledger_hash": result["ledger_hash"], "invariants": result["invariants"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["forward_dry_run_ledger_written"] and all(result["invariants"].values()) else 1
    if args.command == "forward-dry-run-day1-data-reproducibility-appendix":
        result = build_day1_data_reproducibility_appendix(paths=paths)
        print({"appendix_id": result["appendix_id"], "day1_as_of_date": result["day1_as_of_date"], "external_api_called": result["external_api_called"], "real_time_market_data_downloaded": result["real_time_market_data_downloaded"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if not result["external_api_called"] and not result["real_time_market_data_downloaded"] else 1
    if args.command == "forward-dry-run-day1-continuation-blocker-note":
        result = build_day1_continuation_blocker_note(paths=paths)
        print({"note_id": result["note_id"], "day1_completed": result["day1_completed"], "day2_executed": result["day2_executed"], "blocker_type": result["blocker_type"], "latest_common_local_data_date": result["latest_common_local_data_date"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["day1_completed"] and not result["day2_executed"] else 1
    if args.command == "forward-dry-run-day1-owner-report-pack-summary":
        result = build_day1_owner_report_pack_summary(paths=paths)
        print({"summary_id": result["summary_id"], "reports_total": result["reports_total"], "reports_complete": result["reports_complete"], "missing_reports": result["missing_reports"], "owner_report_pack_complete": result["owner_report_pack_complete"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["owner_report_pack_complete"] else 1
    if args.command == "audit-forward-dry-run-day1-owner-report-pack":
        result = audit_day1_owner_report_pack(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "external-project-intake":
        result = build_external_project_intake(paths=paths)
        print({"intake_id": result["intake_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "projects_downloaded": result["projects_downloaded"], "top_priority_repos": result["top_priority_repos"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "equity-data-source-manifest":
        result = build_a_share_data_source_manifest(paths=paths)
        print({"manifest_id": result["manifest_id"], "selected_provider": result["selected_provider"], "rows_available": result["rows_available"], "providers_succeeded": result["providers_succeeded"], "external_api_called": result["external_api_called"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["data_written_to_local_store"] else 1
    if args.command == "build-a-share-equity-master":
        result = build_a_share_equity_master(paths=paths)
        print({"artifact_id": result["artifact_id"], "symbols": result["symbols"], "exchanges": result["exchanges"], "parquet_path": result["parquet_path"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["symbols"] > 0 else 1
    if args.command == "build-a-share-trading-calendar":
        result = build_a_share_trading_calendar(paths=paths)
        print({"artifact_id": result["artifact_id"], "trading_days": result["trading_days"], "min_date": result["min_date"], "max_date": result["max_date"], "parquet_path": result["parquet_path"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["trading_days"] > 0 else 1
    if args.command == "ingest-a-share-daily-prices":
        result = ingest_a_share_daily_prices(paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "min_date": result["min_date"], "max_date": result["max_date"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["symbol_count"] > 0 and result["non_positive_prices"] == 0 else 1
    if args.command == "ingest-a-share-adjusted-prices":
        result = ingest_a_share_adjusted_prices(paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "adjustment_types": result["adjustment_types"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["symbol_count"] > 0 else 1
    if args.command == "ingest-a-share-daily-basic":
        result = ingest_a_share_daily_basic(paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "partial_fields": result["partial_fields"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["symbol_count"] > 0 else 1
    if args.command == "ingest-a-share-industry-classification":
        result = ingest_a_share_industry_classification(paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "industry_standard": result["industry_standard"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["symbol_count"] > 0 else 1
    if args.command == "ingest-a-share-basic-financials":
        result = ingest_a_share_basic_financials(paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "report_date_coverage": result["report_date_coverage"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["symbol_count"] > 0 else 1
    if args.command == "audit-a-share-data-coverage":
        result = audit_a_share_data_coverage(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "coverage": result["coverage"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-data-schema":
        result = audit_a_share_data_schema(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-data-foundation":
        result = build_a_share_data_foundation(paths=paths)
        print({"foundation_id": result["foundation_id"], "overall_passed": result["overall_passed"], "coverage_overall_passed": result["coverage_audit"]["overall_passed"], "schema_overall_passed": result["schema_audit"]["overall_passed"], "coverage": result["coverage_audit"]["coverage"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "a-share-historical-backfill-plan":
        result = build_a_share_historical_backfill_plan(target_start_date=args.target_start_date, minimum_start_date=args.minimum_start_date, end_date=args.end_date, paths=paths)
        print({"plan_id": result["plan_id"], "target_start_date": result["target_start_date"], "minimum_start_date": result["minimum_start_date"], "end_date": result["end_date"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "diagnose-a-share-historical-backfill-coverage":
        result = diagnose_a_share_historical_backfill_coverage(paths=paths)
        print({"diagnostic_id": result["diagnostic_id"], "overall_diagnosis_passed": result["overall_diagnosis_passed"], "confirmed_root_causes": result["confirmed_root_causes"], "historical_price_symbols": result["historical_price_symbols"], "backfill_input_symbols": result["backfill_input_symbols"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0
    if args.command == "build-a-share-historical-backfill-symbol-queue":
        result = build_a_share_historical_backfill_symbol_queue(target_start_date=args.target_start_date, end_date=args.end_date, paths=paths)
        print({"queue_id": result["queue_id"], "queue_total_symbols": result["queue_total_symbols"], "eligible_price_backfill_symbols": result["eligible_price_backfill_symbols"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["queue_total_symbols"] > 0 else 1
    if args.command == "backfill-a-share-daily-price-history":
        result = backfill_a_share_daily_price_history(start_date=args.start_date, end_date=args.end_date, max_symbols=args.max_symbols, provider_priority=args.provider_priority, rate_limit_per_minute=args.rate_limit_per_minute, retry=args.retry, paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "date_count": result["date_count"], "min_date": result["min_date"], "max_date": result["max_date"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["rows"] > 0 else 1
    if args.command == "backfill-a-share-adjusted-price-history":
        result = backfill_a_share_adjusted_price_history(start_date=args.start_date, end_date=args.end_date, paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "adjustment_types": result["adjustment_types"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["rows"] > 0 else 1
    if args.command == "backfill-a-share-daily-basic-history":
        result = backfill_a_share_daily_basic_history(start_date=args.start_date, end_date=args.end_date, paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["rows"] > 0 else 1
    if args.command == "backfill-a-share-financial-history":
        result = backfill_a_share_financial_history(start_date=args.start_date, end_date=args.end_date, paths=paths)
        print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "report_date_coverage": result["report_date_coverage"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})
        return 0 if result["rows"] > 0 else 1
    if args.command == "audit-a-share-historical-panel-coverage":
        result = audit_a_share_historical_panel_coverage(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "coverage": result["coverage"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-feature-readiness":
        result = audit_a_share_feature_readiness(paths=paths)
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "readiness": result["readiness"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "backfill-a-share-historical-panels":
        result = backfill_a_share_historical_panels(target_start_date=args.target_start_date, minimum_start_date=args.minimum_start_date, end_date=args.end_date, max_symbols=args.max_symbols, paths=paths)
        print({"backfill_id": result["backfill_id"], "overall_passed": result["overall_passed"], "coverage_overall_passed": result["coverage_audit"]["overall_passed"], "feature_readiness_overall_passed": result["feature_readiness_audit"]["overall_passed"], "coverage": result["coverage_audit"]["coverage"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "backfill-a-share-historical-panels-full-market":
        result = backfill_a_share_historical_panels_full_market(
            target_start_date=args.target_start_date,
            minimum_start_date=args.minimum_start_date,
            end_date=args.end_date,
            batch_size=args.batch_size,
            max_symbols=args.max_symbols,
            resume=args.resume,
            provider_priority=args.provider_priority,
            rate_limit_per_minute=args.rate_limit_per_minute,
            retry=args.retry,
            sample_size=args.sample_size,
            paths=paths,
        )
        print({"scheduler_id": result["scheduler_id"], "overall_passed": result["overall_passed"], "release_eligible": result["release_eligible"], "queue": result["queue"], "coverage_overall_passed": result["coverage_audit"]["overall_passed"], "feature_readiness_overall_passed": result["feature_readiness_audit"]["overall_passed"], "blocking_reasons": result["feature_readiness_audit"]["blocking_reasons"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-tradable-universe":
        result = build_a_share_tradable_universe(config=_tradable_universe_config(args), paths=paths)
        print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "counts": result["counts"], "warnings": len(result["warnings"]), "tradable_universe_path": result["artifacts"]["tradable_universe_json"], "manifest_path": result["artifacts"]["manifest"]})
        return 0 if result["counts"]["strict_tradable_count"] > 0 else 1
    if args.command == "audit-a-share-tradable-universe":
        result = audit_a_share_tradable_universe(
            as_of_date=args.as_of_date,
            min_listing_trading_days=args.min_listing_trading_days,
            min_avg_amount_20d=args.min_avg_amount_20d,
            min_avg_amount_60d=args.min_avg_amount_60d,
            min_total_mv=args.min_total_mv,
            min_circ_mv=args.min_circ_mv,
            min_close_price=args.min_close_price,
            allow_previous_trading_day=args.allow_previous_trading_day,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-tradable-universe":
        build_result = build_a_share_tradable_universe(config=_tradable_universe_config(args), paths=paths)
        audit_result = audit_a_share_tradable_universe(
            as_of_date=args.as_of_date,
            min_listing_trading_days=args.min_listing_trading_days,
            min_avg_amount_20d=args.min_avg_amount_20d,
            min_avg_amount_60d=args.min_avg_amount_60d,
            min_total_mv=args.min_total_mv,
            min_circ_mv=args.min_circ_mv,
            min_close_price=args.min_close_price,
            allow_previous_trading_day=args.allow_previous_trading_day,
            paths=paths,
        )
        print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "recommended_next_version": audit_result["recommended_next_version"]})
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-multi-horizon-features":
        result = build_a_share_multi_horizon_features(
            as_of_date=args.as_of_date,
            allow_latest_tradable_universe=args.allow_latest_tradable_universe,
            paths=paths,
        )
        print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "strict_tradable_count": result["strict_tradable_count"], "feature_groups": result["feature_groups"], "warnings": len(result["warnings"]), "feature_manifest_path": result["feature_manifest_path"]})
        return 0 if result["strict_tradable_count"] > 0 else 1
    if args.command == "audit-a-share-multi-horizon-features":
        result = audit_a_share_multi_horizon_features(
            as_of_date=args.as_of_date,
            allow_latest_tradable_universe=args.allow_latest_tradable_universe,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "coverage": result["coverage"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-multi-horizon-features":
        build_result = build_a_share_multi_horizon_features(
            as_of_date=args.as_of_date,
            allow_latest_tradable_universe=args.allow_latest_tradable_universe,
            paths=paths,
        )
        audit_result = audit_a_share_multi_horizon_features(
            as_of_date=args.as_of_date,
            allow_latest_tradable_universe=args.allow_latest_tradable_universe,
            paths=paths,
        )
        print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "coverage": audit_result["coverage"], "recommended_next_version": audit_result["recommended_next_version"]})
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-scores":
        result = build_a_share_scores(
            as_of_date=args.as_of_date,
            allow_latest_feature_date=args.allow_latest_feature_date,
            paths=paths,
        )
        print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "strict_tradable_count": result["strict_tradable_count"], "scored_symbols": result["scored_symbols"], "warnings": len(result["warnings"]), "score_manifest_path": result["artifacts"]["score_manifest"]})
        return 0 if result["scored_symbols"] == result["strict_tradable_count"] else 1
    if args.command == "audit-a-share-scores":
        result = audit_a_share_scores(
            as_of_date=args.as_of_date,
            allow_latest_feature_date=args.allow_latest_feature_date,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "score_ranges": result["score_ranges"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-scores":
        build_result = build_a_share_scores(
            as_of_date=args.as_of_date,
            allow_latest_feature_date=args.allow_latest_feature_date,
            paths=paths,
        )
        audit_result = audit_a_share_scores(
            as_of_date=args.as_of_date,
            allow_latest_feature_date=args.allow_latest_feature_date,
            paths=paths,
        )
        print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "score_ranges": audit_result["score_ranges"], "recommended_next_version": audit_result["recommended_next_version"]})
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "generate-a-share-candidates":
        result = generate_a_share_candidates(
            as_of_date=args.as_of_date,
            long_count=args.long_count,
            mid_count=args.mid_count,
            short_count=args.short_count,
            extended_count=args.extended_count,
            allow_latest_score_date=args.allow_latest_score_date,
            paths=paths,
        )
        print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "candidate_counts": result["candidate_counts"], "warnings": len(result["warnings"]), "recommended_next_version": result["recommended_next_version"]})
        return 0 if result["candidate_counts"]["long_candidates"] == args.long_count and result["candidate_counts"]["mid_candidates"] == args.mid_count and result["candidate_counts"]["short_candidates"] == args.short_count else 1
    if args.command == "audit-a-share-candidates":
        result = audit_a_share_candidates(
            as_of_date=args.as_of_date,
            allow_latest_score_date=args.allow_latest_score_date,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "generate-and-audit-a-share-candidates":
        build_result = generate_a_share_candidates(
            as_of_date=args.as_of_date,
            long_count=args.long_count,
            mid_count=args.mid_count,
            short_count=args.short_count,
            extended_count=args.extended_count,
            allow_latest_score_date=args.allow_latest_score_date,
            paths=paths,
        )
        audit_result = audit_a_share_candidates(
            as_of_date=args.as_of_date,
            allow_latest_score_date=args.allow_latest_score_date,
            paths=paths,
        )
        print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "recommended_next_version": audit_result["recommended_next_version"]})
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-virtual-portfolios":
        result = build_a_share_virtual_portfolios(
            as_of_date=args.as_of_date,
            long_holdings=args.long_holdings,
            mid_holdings=args.mid_holdings,
            short_holdings=args.short_holdings,
            allow_latest_candidate_date=args.allow_latest_candidate_date,
            paths=paths,
        )
        counts = {
            "long_holdings": len(result["long_virtual_portfolio"]),
            "mid_holdings": len(result["mid_virtual_portfolio"]),
            "short_holdings": len(result["short_virtual_portfolio"]),
        }
        print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "counts": counts, "warnings": len(result["warnings"]), "recommended_next_version": result["recommended_next_version"]})
        return 0 if counts["long_holdings"] == args.long_holdings and counts["mid_holdings"] == args.mid_holdings and counts["short_holdings"] == args.short_holdings else 1
    if args.command == "audit-a-share-virtual-portfolios":
        result = audit_a_share_virtual_portfolios(
            as_of_date=args.as_of_date,
            allow_latest_candidate_date=args.allow_latest_candidate_date,
            paths=paths,
        )
        print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "weight_checks": result["weight_checks"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-virtual-portfolios":
        build_result = build_a_share_virtual_portfolios(
            as_of_date=args.as_of_date,
            long_holdings=args.long_holdings,
            mid_holdings=args.mid_holdings,
            short_holdings=args.short_holdings,
            allow_latest_candidate_date=args.allow_latest_candidate_date,
            paths=paths,
        )
        audit_result = audit_a_share_virtual_portfolios(
            as_of_date=args.as_of_date,
            allow_latest_candidate_date=args.allow_latest_candidate_date,
            paths=paths,
        )
        print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "weight_checks": audit_result["weight_checks"], "recommended_next_version": audit_result["recommended_next_version"]})
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-daily-stock-selection-briefing":
        result = build_a_share_daily_stock_selection_briefing(
            as_of_date=args.as_of_date,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            paths=paths,
        )
        print(
            {
                "briefing_id": result["briefing_id"],
                "as_of_date": result["as_of_date"],
                "long_candidates_top10": len(result["long_candidates_top10"]),
                "mid_candidates_top10": len(result["mid_candidates_top10"]),
                "short_candidates_top10": len(result["short_candidates_top10"]),
                "source_trace_complete": result["source_trace_complete"],
                "recommended_next_version": result["recommended_next_version"],
            }
        )
        return 0 if result["source_trace_complete"] else 1
    if args.command == "audit-a-share-daily-stock-selection-briefing":
        result = audit_a_share_daily_stock_selection_briefing(
            as_of_date=args.as_of_date,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "required_sections": result["required_sections"],
                "source_trace_complete": result["checks"]["source_trace_complete"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-daily-stock-selection-briefing":
        build_result = build_a_share_daily_stock_selection_briefing(
            as_of_date=args.as_of_date,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            paths=paths,
        )
        audit_result = audit_a_share_daily_stock_selection_briefing(
            as_of_date=args.as_of_date,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            paths=paths,
        )
        print(
            {
                "briefing_id": build_result["briefing_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "required_sections": audit_result["required_sections"],
                "source_trace_complete": audit_result["checks"]["source_trace_complete"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-virtual-portfolio-tracking":
        result = build_a_share_virtual_portfolio_tracking(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        counts = result["tracking_summary"]["counts"]
        print(
            {
                "builder_id": result["builder_id"],
                "as_of_date": result["as_of_date"],
                "counts": counts,
                "first_day_initialization": result["tracking_summary"]["first_day_initialization"],
                "performance_not_yet_observed": result["tracking_summary"]["performance_not_yet_observed"],
                "recommended_next_version": result["recommended_next_version"],
            }
        )
        return 0 if all(counts.get(f"{key}_holdings", 0) > 0 for key in ["long", "mid", "short"]) else 1
    if args.command == "audit-a-share-virtual-portfolio-tracking":
        result = audit_a_share_virtual_portfolio_tracking(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "counts": result["counts"],
                "nav_checks": result["nav_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-virtual-portfolio-tracking":
        build_result = build_a_share_virtual_portfolio_tracking(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        audit_result = audit_a_share_virtual_portfolio_tracking(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "counts": audit_result["counts"],
                "nav_checks": audit_result["nav_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "preflight-a-share-daily-workflow":
        allow_build_timestamp_drift = False if args.fail_on_build_timestamp_drift else args.allow_build_timestamp_drift
        result = preflight_a_share_daily_workflow(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            allow_public_data_refresh=args.allow_public_data_refresh,
            allow_build_timestamp_drift=allow_build_timestamp_drift,
            fail_on_build_timestamp_drift=args.fail_on_build_timestamp_drift,
            allow_version_shim_warning=args.allow_version_shim_warning,
            paths=paths,
        )
        print(
            {
                "preflight_id": result["preflight_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "git_status_clean": result["git_status_clean"],
                "version_consistent": result["version_consistent"],
                "json_path": result["json_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "run-a-share-daily-research-workflow":
        allow_build_timestamp_drift = False if args.fail_on_build_timestamp_drift else args.allow_build_timestamp_drift
        result = run_a_share_daily_research_workflow(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            allow_public_data_refresh=args.allow_public_data_refresh,
            allow_build_timestamp_drift=allow_build_timestamp_drift,
            fail_on_build_timestamp_drift=args.fail_on_build_timestamp_drift,
            allow_version_shim_warning=args.allow_version_shim_warning,
            paths=paths,
        )
        run_manifest = result["workflow_run_manifest"]
        print(
            {
                "workflow_id": result["workflow_id"],
                "overall_passed": run_manifest["overall_passed"],
                "blocking_reasons": run_manifest["blocking_reasons"],
                "warnings": len(run_manifest["warnings"]),
                "mode": run_manifest["mode"],
                "stage_count": len(run_manifest["stages"]),
                "recommended_next_version": result["recommended_next_version"],
            }
        )
        return 0 if run_manifest["overall_passed"] else 1
    if args.command == "audit-a-share-daily-research-workflow":
        result = audit_a_share_daily_research_workflow(
            as_of_date=args.as_of_date,
            mode=args.mode,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "stage_counts": result["stage_counts"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "run-and-audit-a-share-daily-research-workflow":
        allow_build_timestamp_drift = False if args.fail_on_build_timestamp_drift else args.allow_build_timestamp_drift
        run_result = run_a_share_daily_research_workflow(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_latest_artifact_date=args.allow_latest_artifact_date,
            allow_public_data_refresh=args.allow_public_data_refresh,
            allow_build_timestamp_drift=allow_build_timestamp_drift,
            fail_on_build_timestamp_drift=args.fail_on_build_timestamp_drift,
            allow_version_shim_warning=args.allow_version_shim_warning,
            paths=paths,
        )
        audit_result = audit_a_share_daily_research_workflow(
            as_of_date=args.as_of_date,
            mode=args.mode,
            paths=paths,
        )
        print(
            {
                "workflow_id": run_result["workflow_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "stage_counts": audit_result["stage_counts"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-benchmark-comparison":
        result = build_a_share_benchmark_comparison(
            as_of_date=args.as_of_date,
            lookback_trading_days=args.lookback_trading_days,
            minimum_required_trading_days=args.minimum_required_trading_days,
            allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,
            fail_on_placeholder_benchmarks=_benchmark_fail_on_placeholder(args),
            paths=paths,
        )
        availability = {
            row["benchmark_id"]: row["status"]
            for row in result["benchmark_data_availability"]["benchmarks"]
        }
        print(
            {
                "builder_id": result["builder_id"],
                "as_of_date": result["as_of_date"],
                "benchmark_availability": availability,
                "limited_history_flagged": result["relative_performance_snapshot"]["limited_history_flagged"],
                "performance_not_yet_observed": result["relative_performance_snapshot"]["performance_not_yet_observed"],
                "recommended_next_version": result["benchmark_summary"]["recommended_next_version"],
            }
        )
        return 0 if all(status == "available" for status in availability.values()) else 1
    if args.command == "audit-a-share-benchmark-comparison":
        result = audit_a_share_benchmark_comparison(
            as_of_date=args.as_of_date,
            allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,
            fail_on_placeholder_benchmarks=_benchmark_fail_on_placeholder(args),
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "benchmark_availability_checks": result["benchmark_availability_checks"],
                "comparison_checks": result["comparison_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-benchmark-comparison":
        build_result = build_a_share_benchmark_comparison(
            as_of_date=args.as_of_date,
            lookback_trading_days=args.lookback_trading_days,
            minimum_required_trading_days=args.minimum_required_trading_days,
            allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,
            fail_on_placeholder_benchmarks=_benchmark_fail_on_placeholder(args),
            paths=paths,
        )
        audit_result = audit_a_share_benchmark_comparison(
            as_of_date=args.as_of_date,
            allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,
            fail_on_placeholder_benchmarks=_benchmark_fail_on_placeholder(args),
            paths=paths,
        )
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "benchmark_availability_checks": audit_result["benchmark_availability_checks"],
                "comparison_checks": audit_result["comparison_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-multi-day-performance":
        result = build_a_share_multi_day_performance(
            as_of_date=args.as_of_date,
            tracking_start_date=args.tracking_start_date,
            mode=args.mode,
            minimum_required_observations=args.minimum_required_observations,
            rolling_window_days=args.rolling_window_days,
            allow_rebuild=args.allow_rebuild,
            allow_historical_reconstruction=args.allow_historical_reconstruction,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "as_of_date": result["as_of_date"],
                "mode": result["performance_config"]["mode"],
                "portfolio_observation_counts": result["performance_data_availability"]["portfolio_observation_counts"],
                "sufficient_history": result["performance_data_availability"]["sufficient_history"],
                "performance_not_yet_observed": result["performance_summary"]["performance_not_yet_observed"],
                "recommended_next_version": result["performance_summary"]["recommended_next_version"],
            }
        )
        return 0
    if args.command == "audit-a-share-multi-day-performance":
        result = audit_a_share_multi_day_performance(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "observation_checks": result["observation_checks"],
                "series_checks": result["series_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-multi-day-performance":
        build_result = build_a_share_multi_day_performance(
            as_of_date=args.as_of_date,
            tracking_start_date=args.tracking_start_date,
            mode=args.mode,
            minimum_required_observations=args.minimum_required_observations,
            rolling_window_days=args.rolling_window_days,
            allow_rebuild=args.allow_rebuild,
            allow_historical_reconstruction=args.allow_historical_reconstruction,
            paths=paths,
        )
        audit_result = audit_a_share_multi_day_performance(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "observation_checks": audit_result["observation_checks"],
                "series_checks": audit_result["series_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-performance-attribution":
        result = build_a_share_performance_attribution(
            as_of_date=args.as_of_date,
            mode=args.mode,
            minimum_required_observations=args.minimum_required_observations,
            allow_limited_history=args.allow_limited_history,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "as_of_date": result["as_of_date"],
                "mode": result["attribution_config"]["mode"],
                "limited_history": result["attribution_data_availability"]["limited_history"],
                "structural_diagnostics_available": result["attribution_data_availability"]["structural_diagnostics_available"],
                "realized_performance_attribution_available": result["attribution_data_availability"]["realized_performance_attribution_available"],
                "recommended_next_version": result["attribution_summary"]["recommended_next_version"],
            }
        )
        return 0
    if args.command == "audit-a-share-performance-attribution":
        result = audit_a_share_performance_attribution(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "availability_checks": result["availability_checks"],
                "reconciliation_checks": result["reconciliation_checks"],
                "risk_checks": result["risk_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-performance-attribution":
        build_result = build_a_share_performance_attribution(
            as_of_date=args.as_of_date,
            mode=args.mode,
            minimum_required_observations=args.minimum_required_observations,
            allow_limited_history=args.allow_limited_history,
            paths=paths,
        )
        audit_result = audit_a_share_performance_attribution(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "availability_checks": audit_result["availability_checks"],
                "reconciliation_checks": audit_result["reconciliation_checks"],
                "risk_checks": audit_result["risk_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "build-a-share-daily-data-refresh":
        result = build_a_share_daily_data_refresh(
            as_of_date=args.as_of_date,
            mode=args.mode,
            resolve_latest_completed_trading_day=args.resolve_latest_completed_trading_day,
            allow_network_providers=args.allow_network_providers,
            allow_public_providers=args.allow_public_providers,
            allow_intraday_research_refresh=args.allow_intraday_research_refresh,
            allow_non_trading_day=args.allow_non_trading_day,
            allow_partial_refresh=args.allow_partial_refresh,
            allow_latest_available_if_exact_missing=args.allow_latest_available_if_exact_missing,
            allow_research_workflow_after_refresh=args.allow_research_workflow_after_refresh,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "as_of_date": result["as_of_date"],
                "mode": result["data_refresh_config"]["mode"],
                "resolved_as_of_date": result["date_resolution"]["resolved_as_of_date"],
                "schema_validation_status": result["dataset_schema_validation"]["schema_validation_status"],
                "freshness_validation_status": result["dataset_freshness_validation"]["freshness_validation_status"],
                "coverage_validation_status": result["dataset_coverage_summary"]["coverage_validation_status"],
                "recommended_next_version": result["data_refresh_summary"]["recommended_next_version"],
            }
        )
        return 0
    if args.command == "audit-a-share-daily-data-refresh":
        result = audit_a_share_daily_data_refresh(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "dataset_checks": result["dataset_checks"],
                "provider_checks": result["provider_checks"],
                "validation_checks": result["validation_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-daily-data-refresh":
        build_result = build_a_share_daily_data_refresh(
            as_of_date=args.as_of_date,
            mode=args.mode,
            resolve_latest_completed_trading_day=args.resolve_latest_completed_trading_day,
            allow_network_providers=args.allow_network_providers,
            allow_public_providers=args.allow_public_providers,
            allow_intraday_research_refresh=args.allow_intraday_research_refresh,
            allow_non_trading_day=args.allow_non_trading_day,
            allow_partial_refresh=args.allow_partial_refresh,
            allow_latest_available_if_exact_missing=args.allow_latest_available_if_exact_missing,
            allow_research_workflow_after_refresh=args.allow_research_workflow_after_refresh,
            paths=paths,
        )
        audit_result = audit_a_share_daily_data_refresh(
            as_of_date=build_result["as_of_date"],
            paths=paths,
        )
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "dataset_checks": audit_result["dataset_checks"],
                "provider_checks": audit_result["provider_checks"],
                "validation_checks": audit_result["validation_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-current-day-readiness":
        result = validate_a_share_current_day_readiness(
            as_of_date=args.as_of_date,
            use_data_refresh_resolved_date=args.use_data_refresh_resolved_date,
            allow_date_mismatch=args.allow_date_mismatch,
            workflow_mode=args.workflow_mode,
            paths=paths,
        )
        readiness = result["current_day_readiness"]
        print(
            {
                "runner_id": result["runner_id"],
                "readiness_id": readiness["readiness_id"],
                "overall_passed": readiness["overall_passed"],
                "blocking_reasons": readiness["blocking_reasons"],
                "warnings": len(readiness["warnings"]),
                "resolved_as_of_date": readiness["resolved_as_of_date"],
                "recommended_next_version": result["current_day_run_manifest"]["recommended_next_version"],
            }
        )
        return 0 if readiness["overall_passed"] else 1
    if args.command == "run-a-share-current-day-research":
        result = run_a_share_current_day_research(
            as_of_date=args.as_of_date,
            mode=args.mode,
            workflow_mode=args.workflow_mode,
            use_data_refresh_resolved_date=args.use_data_refresh_resolved_date,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_refresh_before_run=args.allow_refresh_before_run,
            allow_network_providers=args.allow_network_providers,
            allow_public_providers=args.allow_public_providers,
            run_post_workflow_modules=args.run_post_workflow_modules,
            allow_post_workflow_warnings_only=args.allow_post_workflow_warnings_only,
            paths=paths,
        )
        manifest = result["current_day_run_manifest"]
        print(
            {
                "runner_id": result["runner_id"],
                "overall_passed": manifest["overall_passed"],
                "blocking_reasons": manifest["blocking_reasons"],
                "warnings": len(manifest["warnings"]),
                "mode": manifest["mode"],
                "workflow_mode": manifest["workflow_mode"],
                "workflow_audit_passed": manifest["workflow_audit_passed"],
                "recommended_next_version": manifest["recommended_next_version"],
            }
        )
        return 0 if manifest["overall_passed"] else 1
    if args.command == "audit-a-share-current-day-research-run":
        result = audit_a_share_current_day_research_run(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "readiness_checks": result["readiness_checks"],
                "workflow_checks": result["workflow_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "run-and-audit-a-share-current-day-research":
        run_result = run_a_share_current_day_research(
            as_of_date=args.as_of_date,
            mode=args.mode,
            workflow_mode=args.workflow_mode,
            use_data_refresh_resolved_date=args.use_data_refresh_resolved_date,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_refresh_before_run=args.allow_refresh_before_run,
            allow_network_providers=args.allow_network_providers,
            allow_public_providers=args.allow_public_providers,
            run_post_workflow_modules=args.run_post_workflow_modules,
            allow_post_workflow_warnings_only=args.allow_post_workflow_warnings_only,
            paths=paths,
        )
        audit_result = audit_a_share_current_day_research_run(
            as_of_date=args.as_of_date,
            paths=paths,
        )
        print(
            {
                "runner_id": run_result["runner_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "workflow_checks": audit_result["workflow_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-owner-dashboard-inputs":
        result = validate_a_share_owner_dashboard_inputs(
            as_of_date=args.as_of_date,
            allow_date_mismatch=args.allow_date_mismatch,
            fail_on_missing_optional_card=args.fail_on_missing_optional_card,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "resolved_as_of_date": result["resolved_as_of_date"],
                "dashboard_input_availability_path": result["dashboard_input_availability_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-owner-dashboard":
        result = build_a_share_owner_dashboard(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            fail_on_missing_optional_card=args.fail_on_missing_optional_card,
            compact_only=args.compact_only,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "overall_status": result["overall_status"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "recommended_next_version": result["recommended_next_version"],
                "dashboard_report_path": result["dashboard_report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-owner-dashboard":
        result = audit_a_share_owner_dashboard(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-owner-dashboard":
        build_result = build_a_share_owner_dashboard(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            fail_on_missing_optional_card=args.fail_on_missing_optional_card,
            compact_only=args.compact_only,
            paths=paths,
        )
        audit_result = audit_a_share_owner_dashboard(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-owner-monitoring-inputs":
        result = validate_a_share_owner_monitoring_inputs(
            as_of_date=args.as_of_date,
            history_window_days=args.history_window_days,
            minimum_history_observations=args.minimum_history_observations,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "monitoring_input_availability_path": result["monitoring_input_availability_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-owner-monitoring":
        result = build_a_share_owner_monitoring(
            as_of_date=args.as_of_date,
            mode=args.mode,
            history_window_days=args.history_window_days,
            minimum_history_observations=args.minimum_history_observations,
            allow_rebuild_history=args.allow_rebuild_history,
            send_external_notifications=args.send_external_notifications,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "overall_monitoring_status": result["overall_monitoring_status"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "owner_monitoring_summary_report": result["owner_monitoring_summary_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-owner-monitoring":
        result = audit_a_share_owner_monitoring(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-owner-monitoring":
        build_result = build_a_share_owner_monitoring(
            as_of_date=args.as_of_date,
            mode=args.mode,
            history_window_days=args.history_window_days,
            minimum_history_observations=args.minimum_history_observations,
            allow_rebuild_history=args.allow_rebuild_history,
            send_external_notifications=args.send_external_notifications,
            paths=paths,
        )
        audit_result = audit_a_share_owner_monitoring(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-owner-remediation-inputs":
        result = validate_a_share_owner_remediation_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "input_artifact_count": result["input_artifact_count"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-owner-remediation":
        result = build_a_share_owner_remediation(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_safe_local_dry_run=args.allow_safe_local_dry_run,
            allow_data_refresh_rerun=args.allow_data_refresh_rerun,
            allow_research_workflow_rerun=args.allow_research_workflow_rerun,
            allow_dashboard_rerun=args.allow_dashboard_rerun,
            allow_monitoring_rerun=args.allow_monitoring_rerun,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "issue_count": result["issue_count"],
                "safe_action_count": result["safe_action_count"],
                "automatic_action_count": result["automatic_action_count"],
                "owner_remediation_runbook_report": result["owner_remediation_runbook_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-owner-remediation":
        result = audit_a_share_owner_remediation(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-owner-remediation":
        build_result = build_a_share_owner_remediation(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_safe_local_dry_run=args.allow_safe_local_dry_run,
            allow_data_refresh_rerun=args.allow_data_refresh_rerun,
            allow_research_workflow_rerun=args.allow_research_workflow_rerun,
            allow_dashboard_rerun=args.allow_dashboard_rerun,
            allow_monitoring_rerun=args.allow_monitoring_rerun,
            paths=paths,
        )
        audit_result = audit_a_share_owner_remediation(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-daily-ops-inputs":
        result = validate_a_share_daily_ops_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "required_modules_available": result["required_modules_available"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-daily-ops-center":
        result = build_a_share_daily_ops_center(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_safe_validation_chain=args.allow_safe_validation_chain,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "ops_health_score": result["ops_health_score"],
                "ops_health_grade": result["ops_health_grade"],
                "overall_status": result["overall_status"],
                "commands_executed": result["commands_executed"],
                "ops_command_center_report": result["ops_command_center_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-daily-ops-center":
        result = audit_a_share_daily_ops_center(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-daily-ops-center":
        build_result = build_a_share_daily_ops_center(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_safe_validation_chain=args.allow_safe_validation_chain,
            paths=paths,
        )
        audit_result = audit_a_share_daily_ops_center(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-ops-history-inputs":
        result = validate_a_share_ops_history_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "ops_center_audit_passed": result["ops_center_audit_passed"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-ops-history-baseline":
        result = build_a_share_ops_history_baseline(
            as_of_date=args.as_of_date,
            mode=args.mode,
            history_window_days=args.history_window_days,
            minimum_required_observations=args.minimum_required_observations,
            baseline_window_observations=args.baseline_window_observations,
            allow_rebuild_history=args.allow_rebuild_history,
            allow_synthetic_history=args.allow_synthetic_history,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "run_history_observation_count": result["run_history_observation_count"],
                "trend_analysis_available": result["trend_analysis_available"],
                "baseline_status": result["baseline_status"],
                "append_completed": result["append_completed"],
                "idempotent_append": result["idempotent_append"],
                "commands_executed": result["commands_executed"],
                "ops_run_history_baseline_report": result["ops_run_history_baseline_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-ops-history-baseline":
        result = audit_a_share_ops_history_baseline(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "trend_sufficiency": result["trend_sufficiency"],
                "append_result": result["append_result"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-ops-history-baseline":
        build_result = build_a_share_ops_history_baseline(
            as_of_date=args.as_of_date,
            mode=args.mode,
            history_window_days=args.history_window_days,
            minimum_required_observations=args.minimum_required_observations,
            baseline_window_observations=args.baseline_window_observations,
            allow_rebuild_history=args.allow_rebuild_history,
            allow_synthetic_history=args.allow_synthetic_history,
            paths=paths,
        )
        audit_result = audit_a_share_ops_history_baseline(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": len(audit_result["warnings"]),
                "trend_sufficiency": audit_result["trend_sufficiency"],
                "append_result": audit_result["append_result"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-gated-build-inputs":
        result = validate_a_share_gated_build_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "ops_history_audit_passed": result["ops_history_audit_passed"],
                "ops_center_audit_passed": result["ops_center_audit_passed"],
                "current_day_audit_passed": result["current_day_audit_passed"],
                "data_refresh_audit_passed": result["data_refresh_audit_passed"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-gated-build-from-existing-data":
        result = build_a_share_gated_build(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            minimum_ops_health_score=args.minimum_ops_health_score,
            allow_public_network_refresh=args.allow_public_network_refresh,
            allow_full_research_run=args.allow_full_research_run,
            allow_broker=args.allow_broker,
            allow_real_orders=args.allow_real_orders,
            allow_order_preview=args.allow_order_preview,
            allow_buy_sell_signals=args.allow_buy_sell_signals,
            allow_old_run_daily=args.allow_old_run_daily,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": len(result["warnings"]),
                "preflight_gate_passed": result["preflight_gate_passed"],
                "gated_build_execution_performed": result["gated_build_execution_performed"],
                "workflow_mode": result["workflow_mode"],
                "workflow_audit_passed": result["workflow_audit_passed"],
                "comparison_completed": result["comparison_completed"],
                "recommended_next_version": result["recommended_next_version"],
                "gated_build_dry_run_report": result["gated_build_dry_run_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-gated-build-from-existing-data":
        result = audit_a_share_gated_build(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "preflight_checks": result["preflight_checks"],
                "execution_checks": result["execution_checks"],
                "comparison_checks": result["comparison_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-gated-build-from-existing-data":
        build_result = build_a_share_gated_build(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            minimum_ops_health_score=args.minimum_ops_health_score,
            allow_public_network_refresh=args.allow_public_network_refresh,
            allow_full_research_run=args.allow_full_research_run,
            allow_broker=args.allow_broker,
            allow_real_orders=args.allow_real_orders,
            allow_order_preview=args.allow_order_preview,
            allow_buy_sell_signals=args.allow_buy_sell_signals,
            allow_old_run_daily=args.allow_old_run_daily,
            paths=paths,
        )
        audit_result = audit_a_share_gated_build(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": audit_result["warnings"],
                "preflight_checks": audit_result["preflight_checks"],
                "execution_checks": audit_result["execution_checks"],
                "comparison_checks": audit_result["comparison_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-build-repeatability-inputs":
        result = validate_a_share_build_repeatability_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "gated_build_audit_passed": result["gated_build_audit_passed"],
                "gated_build_workflow_mode": result["gated_build_workflow_mode"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-build-repeatability":
        result = build_a_share_build_repeatability(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_business_output_drift=args.allow_business_output_drift,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "workflow_mode": result["workflow_mode"],
                "repeat_build_execution_performed": result["repeat_build_execution_performed"],
                "repeat_build_audit_passed": result["repeat_build_audit_passed"],
                "comparison_completed": result["comparison_completed"],
                "business_output_drift_count": result["business_output_drift_count"],
                "timestamp_only_drift_count": result["timestamp_only_drift_count"],
                "metadata_hash_drift_count": result["metadata_hash_drift_count"],
                "missing_required_artifact_count": result["missing_required_artifact_count"],
                "protected_path_modifications_detected": result["protected_path_modifications_detected"],
                "recommended_next_version": result["recommended_next_version"],
                "repeatability_report": result["repeatability_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-build-repeatability":
        result = audit_a_share_build_repeatability(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "input_checks": result["input_checks"],
                "execution_checks": result["execution_checks"],
                "comparison_checks": result["comparison_checks"],
                "protected_path_checks": result["protected_path_checks"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-build-repeatability":
        build_result = build_a_share_build_repeatability(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_business_output_drift=args.allow_business_output_drift,
            paths=paths,
        )
        audit_result = audit_a_share_build_repeatability(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": audit_result["warnings"],
                "execution_checks": audit_result["execution_checks"],
                "comparison_checks": audit_result["comparison_checks"],
                "protected_path_checks": audit_result["protected_path_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-build-output-owner-dashboard-inputs":
        result = validate_a_share_build_output_owner_dashboard_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "repeatability_audit_passed": result["repeatability_audit_passed"],
                "gated_build_audit_passed": result["gated_build_audit_passed"],
                "validate_source_dashboard_audit_passed": result["validate_source_dashboard_audit_passed"],
                "data_refresh_audit_passed": result["data_refresh_audit_passed"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-build-output-owner-dashboard":
        result = build_a_share_build_output_owner_dashboard(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_required_validate_fallback=args.allow_required_validate_fallback,
            allow_business_output_drift=args.allow_business_output_drift,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "source_workflow_mode": result["source_workflow_mode"],
                "gated_build_audit_passed": result["gated_build_audit_passed"],
                "repeatability_audit_passed": result["repeatability_audit_passed"],
                "business_output_drift_count": result["business_output_drift_count"],
                "protected_path_modifications_detected": result["protected_path_modifications_detected"],
                "required_cards_present": result["required_cards_present"],
                "optional_cards_present": result["optional_cards_present"],
                "required_validate_fallback_used": result["required_validate_fallback_used"],
                "optional_validate_fallback_used": result["optional_validate_fallback_used"],
                "comparison_completed": result["comparison_completed"],
                "recommended_next_version": result["recommended_next_version"],
                "dashboard_report": result["dashboard_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-build-output-owner-dashboard":
        result = audit_a_share_build_output_owner_dashboard(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "input_checks": result["input_checks"],
                "dashboard_checks": result["dashboard_checks"],
                "boundary": result["boundary"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-build-output-owner-dashboard":
        build_result = build_a_share_build_output_owner_dashboard(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_required_validate_fallback=args.allow_required_validate_fallback,
            allow_business_output_drift=args.allow_business_output_drift,
            paths=paths,
        )
        audit_result = audit_a_share_build_output_owner_dashboard(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": audit_result["warnings"],
                "input_checks": audit_result["input_checks"],
                "dashboard_checks": audit_result["dashboard_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "validate-a-share-build-output-ops-refresh-inputs":
        result = validate_a_share_build_output_ops_refresh_inputs(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "build_output_dashboard_audit_passed": result["build_output_dashboard_audit_passed"],
                "repeatability_audit_passed": result["repeatability_audit_passed"],
                "gated_build_audit_passed": result["gated_build_audit_passed"],
                "original_monitoring_audit_passed": result["original_monitoring_audit_passed"],
                "original_remediation_audit_passed": result["original_remediation_audit_passed"],
                "original_ops_center_audit_passed": result["original_ops_center_audit_passed"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-a-share-build-output-ops-refresh":
        result = build_a_share_build_output_ops_refresh(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_business_output_drift=args.allow_business_output_drift,
            paths=paths,
        )
        print(
            {
                "builder_id": result["builder_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "source_workflow_mode": result["source_workflow_mode"],
                "build_output_dashboard_audit_passed": result["build_output_dashboard_audit_passed"],
                "repeatability_audit_passed": result["repeatability_audit_passed"],
                "gated_build_audit_passed": result["gated_build_audit_passed"],
                "original_monitoring_audit_passed": result["original_monitoring_audit_passed"],
                "original_remediation_audit_passed": result["original_remediation_audit_passed"],
                "original_ops_center_audit_passed": result["original_ops_center_audit_passed"],
                "monitoring_refresh_performed": result["monitoring_refresh_performed"],
                "remediation_refresh_performed": result["remediation_refresh_performed"],
                "ops_center_refresh_performed": result["ops_center_refresh_performed"],
                "ops_history_refresh_performed": result["ops_history_refresh_performed"],
                "build_from_existing_data_rerun": result["build_from_existing_data_rerun"],
                "business_output_drift_count": result["business_output_drift_count"],
                "protected_path_modifications_detected": result["protected_path_modifications_detected"],
                "execute_remediation_actions": result["execute_remediation_actions"],
                "external_notifications_sent": result["external_notifications_sent"],
                "automatic_action_count": result["automatic_action_count"],
                "comparison_completed": result["comparison_completed"],
                "ops_health_score": result["ops_health_score"],
                "ops_health_grade": result["ops_health_grade"],
                "overall_status": result["overall_status"],
                "recommended_next_version": result["recommended_next_version"],
                "ops_refresh_report": result["ops_refresh_report"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "audit-a-share-build-output-ops-refresh":
        result = audit_a_share_build_output_ops_refresh(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "audit_id": result["audit_id"],
                "overall_passed": result["overall_passed"],
                "blocking_reasons": result["blocking_reasons"],
                "warnings": result["warnings"],
                "input_checks": result["input_checks"],
                "refresh_checks": result["refresh_checks"],
                "boundary": result["boundary"],
                "recommended_next_version": result["recommended_next_version"],
                "json_path": result["json_path"],
                "report_path": result["report_path"],
            }
        )
        return 0 if result["overall_passed"] else 1
    if args.command == "build-and-audit-a-share-build-output-ops-refresh":
        build_result = build_a_share_build_output_ops_refresh(
            as_of_date=args.as_of_date,
            mode=args.mode,
            allow_date_mismatch=args.allow_date_mismatch,
            allow_business_output_drift=args.allow_business_output_drift,
            paths=paths,
        )
        audit_result = audit_a_share_build_output_ops_refresh(as_of_date=args.as_of_date, paths=paths)
        print(
            {
                "builder_id": build_result["builder_id"],
                "audit_id": audit_result["audit_id"],
                "overall_passed": audit_result["overall_passed"],
                "blocking_reasons": audit_result["blocking_reasons"],
                "warnings": audit_result["warnings"],
                "input_checks": audit_result["input_checks"],
                "refresh_checks": audit_result["refresh_checks"],
                "recommended_next_version": audit_result["recommended_next_version"],
            }
        )
        return 0 if audit_result["overall_passed"] else 1
    if args.command == "admission":
        result = run_admission(args.strategy_id, args.date)
        print(result)
        return 0
    if args.command == "acceptance-report":
        result = write_acceptance_materials(paths)
        print(result)
        return 0
    if args.command == "leaderboard":
        result = build_strategy_leaderboard(args.start_date, args.end_date, paths)
        print({"items": len(result["items"]), "report_path": result["report_path"]})
        return 0
    if args.command == "health":
        health = load_health(args.date)
        if health is None:
            health = run_daily(args.date)["health"]
        print(health)
        return 0
    if args.command == "export-summary":
        result = export_trading_summary(args.date)
        print(result)
        return 0
    result = run_daily(args.date)
    print(
        {
            "date": result["date"],
            "signals": len(result["signals"]),
            "orders": len(result["orders"]),
            "trades": len(result["trades"]),
            "limitations": result["limitations"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
