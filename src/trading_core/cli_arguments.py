"""Per-command argument registration helpers split out of the CLI entry point."""

from __future__ import annotations

from trading_core.cli_defaults import (
    DEFAULT_V09_PLATFORM_AS_OF_DATE,
)
import argparse
from datetime import date as Date

from trading_core.equity_attribution.attribution_config import ALLOWED_MODES as A_SHARE_ATTRIBUTION_MODES
from trading_core.equity_attribution.attribution_config import DEFAULT_AS_OF_DATE as DEFAULT_ATTRIBUTION_AS_OF_DATE
from trading_core.equity_attribution.attribution_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS as DEFAULT_ATTRIBUTION_MINIMUM_REQUIRED_OBSERVATIONS
from trading_core.equity_benchmarks.benchmark_config import DEFAULT_AS_OF_DATE as DEFAULT_BENCHMARK_AS_OF_DATE
from trading_core.equity_briefings.briefing_config import DEFAULT_AS_OF_DATE as DEFAULT_BRIEFING_AS_OF_DATE
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import ALLOWED_MODES as A_SHARE_BUILD_OUTPUT_DASHBOARD_MODES
from trading_core.equity_build_output_dashboard.build_output_dashboard_config import DEFAULT_AS_OF_DATE as DEFAULT_BUILD_OUTPUT_DASHBOARD_AS_OF_DATE
from trading_core.equity_build_output_ops_refresh.build_output_ops_config import ALLOWED_MODES as A_SHARE_BUILD_OUTPUT_OPS_MODES
from trading_core.equity_build_output_ops_refresh.build_output_ops_config import DEFAULT_AS_OF_DATE as DEFAULT_BUILD_OUTPUT_OPS_AS_OF_DATE
from trading_core.equity_build_repeatability.repeatability_config import ALLOWED_MODES as A_SHARE_BUILD_REPEATABILITY_MODES
from trading_core.equity_build_repeatability.repeatability_config import DEFAULT_AS_OF_DATE as DEFAULT_BUILD_REPEATABILITY_AS_OF_DATE
from trading_core.equity_current_day.current_day_config import ALLOWED_MODES as A_SHARE_CURRENT_DAY_MODES
from trading_core.equity_current_day.current_day_config import ALLOWED_WORKFLOW_MODES as A_SHARE_CURRENT_DAY_WORKFLOW_MODES
from trading_core.equity_current_day.current_day_config import DEFAULT_AS_OF_DATE as DEFAULT_CURRENT_DAY_AS_OF_DATE
from trading_core.equity_current_day_builds.gated_build_config import ALLOWED_MODES as A_SHARE_GATED_BUILD_MODES
from trading_core.equity_current_day_builds.gated_build_config import DEFAULT_AS_OF_DATE as DEFAULT_GATED_BUILD_AS_OF_DATE
from trading_core.equity_data_refresh.data_refresh_config import ALLOWED_MODES as A_SHARE_DATA_REFRESH_MODES
from trading_core.equity_data_refresh.data_refresh_config import DEFAULT_AS_OF_DATE as DEFAULT_DATA_REFRESH_AS_OF_DATE
from trading_core.equity_features.feature_config import DEFAULT_AS_OF_DATE
from trading_core.equity_historical_evidence_backfill import DEFAULT_AS_OF_DATE as DEFAULT_HISTORICAL_EVIDENCE_BACKFILL_AS_OF_DATE
from trading_core.equity_historical_evidence_backfill import DEFAULT_LOOKBACK_START, DEFAULT_TARGET_EVIDENCE_DAYS
from trading_core.equity_ops_center.ops_config import ALLOWED_MODES as A_SHARE_OPS_CENTER_MODES
from trading_core.equity_ops_center.ops_config import DEFAULT_AS_OF_DATE as DEFAULT_OPS_CENTER_AS_OF_DATE
from trading_core.equity_ops_history.ops_history_config import ALLOWED_MODES as A_SHARE_OPS_HISTORY_MODES
from trading_core.equity_ops_history.ops_history_config import DEFAULT_AS_OF_DATE as DEFAULT_OPS_HISTORY_AS_OF_DATE
from trading_core.equity_ops_history.ops_history_config import DEFAULT_BASELINE_WINDOW_OBSERVATIONS as DEFAULT_OPS_HISTORY_BASELINE_WINDOW_OBSERVATIONS
from trading_core.equity_ops_history.ops_history_config import DEFAULT_HISTORY_WINDOW_DAYS as DEFAULT_OPS_HISTORY_WINDOW_DAYS
from trading_core.equity_ops_history.ops_history_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS as DEFAULT_OPS_HISTORY_MINIMUM_REQUIRED_OBSERVATIONS
from trading_core.equity_owner_closeout_review.closeout_config import ALLOWED_MODES as A_SHARE_OWNER_CLOSEOUT_REVIEW_MODES
from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_CLOSEOUT_REVIEW_AS_OF_DATE
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import ALLOWED_MODES as A_SHARE_OWNER_CONTROLLED_GATE_REEVALUATION_MODES
from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_CONTROLLED_GATE_REEVALUATION_AS_OF_DATE
from trading_core.equity_owner_daily_pack.daily_pack_config import ALLOWED_MODES as A_SHARE_OWNER_DAILY_PACK_MODES
from trading_core.equity_owner_daily_pack.daily_pack_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_DAILY_PACK_AS_OF_DATE
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import ALLOWED_MODES as A_SHARE_OWNER_DAILY_PACK_HISTORY_MODES
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_DAILY_PACK_HISTORY_AS_OF_DATE
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import DEFAULT_BASELINE_WINDOW_OBSERVATIONS as DEFAULT_OWNER_DAILY_PACK_HISTORY_BASELINE_WINDOW_OBSERVATIONS
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import DEFAULT_HISTORY_WINDOW_DAYS as DEFAULT_OWNER_DAILY_PACK_HISTORY_WINDOW_DAYS
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS as DEFAULT_OWNER_DAILY_PACK_HISTORY_MINIMUM_REQUIRED_OBSERVATIONS
from trading_core.equity_owner_dashboard.dashboard_config import ALLOWED_MODES as A_SHARE_OWNER_DASHBOARD_MODES
from trading_core.equity_owner_dashboard.dashboard_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_DASHBOARD_AS_OF_DATE
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import ALLOWED_MODES as A_SHARE_OWNER_EVIDENCE_BACKED_PREP_MODES
from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_EVIDENCE_BACKED_PREP_AS_OF_DATE
from trading_core.equity_owner_monitoring.monitoring_config import ALLOWED_MODES as A_SHARE_OWNER_MONITORING_MODES
from trading_core.equity_owner_monitoring.monitoring_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_MONITORING_AS_OF_DATE
from trading_core.equity_owner_monitoring.monitoring_config import DEFAULT_HISTORY_WINDOW_DAYS, DEFAULT_MINIMUM_HISTORY_OBSERVATIONS
from trading_core.equity_owner_operator_experience.operator_config import ALLOWED_MODES as A_SHARE_OWNER_OPERATOR_EXPERIENCE_MODES
from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_OPERATOR_EXPERIENCE_AS_OF_DATE
from trading_core.equity_owner_quality_exceptions.exception_workflow_config import ALLOWED_MODES as A_SHARE_OWNER_QUALITY_EXCEPTION_MODES
from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_QUALITY_EXCEPTION_AS_OF_DATE
from trading_core.equity_owner_readiness_gate.gate_config import ALLOWED_MODES as A_SHARE_OWNER_READINESS_GATE_MODES
from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_READINESS_GATE_AS_OF_DATE
from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_MINIMUM_OWNER_READINESS_SCORE
from trading_core.equity_owner_readiness_recovery.recovery_config import ALLOWED_MODES as A_SHARE_OWNER_READINESS_RECOVERY_MODES
from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_READINESS_RECOVERY_AS_OF_DATE
from trading_core.equity_owner_readiness_recovery_execution.execution_config import ALLOWED_MODES as A_SHARE_OWNER_READINESS_RECOVERY_EXECUTION_MODES
from trading_core.equity_owner_readiness_recovery_execution.execution_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_READINESS_RECOVERY_EXECUTION_AS_OF_DATE
from trading_core.equity_owner_recovery_evidence.evidence_config import ALLOWED_MODES as A_SHARE_OWNER_RECOVERY_EVIDENCE_MODES
from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_RECOVERY_EVIDENCE_AS_OF_DATE
from trading_core.equity_owner_remediation.remediation_config import ALLOWED_MODES as A_SHARE_OWNER_REMEDIATION_MODES
from trading_core.equity_owner_remediation.remediation_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_REMEDIATION_AS_OF_DATE
from trading_core.equity_owner_v0820_gate_outcome.outcome_config import ALLOWED_MODES as A_SHARE_OWNER_V0820_GATE_OUTCOME_MODES
from trading_core.equity_owner_v0820_gate_outcome.outcome_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_V0820_GATE_OUTCOME_AS_OF_DATE
from trading_core.equity_owner_v090_rc.v090_config import ALLOWED_MODES as A_SHARE_OWNER_V090_RC_MODES
from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE as DEFAULT_OWNER_V090_RC_AS_OF_DATE
from trading_core.equity_performance.performance_config import ALLOWED_MODES as A_SHARE_PERFORMANCE_MODES
from trading_core.equity_performance.performance_config import DEFAULT_AS_OF_DATE as DEFAULT_PERFORMANCE_AS_OF_DATE
from trading_core.equity_performance.performance_config import DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS, DEFAULT_ROLLING_WINDOW_DAYS, DEFAULT_TRACKING_START_DATE
from trading_core.equity_portfolio_tracking.tracking_config import DEFAULT_AS_OF_DATE as DEFAULT_TRACKING_AS_OF_DATE
from trading_core.equity_portfolios.portfolio_config import DEFAULT_AS_OF_DATE as DEFAULT_PORTFOLIO_AS_OF_DATE
from trading_core.equity_scoring.score_config import DEFAULT_AS_OF_DATE as DEFAULT_SCORE_AS_OF_DATE
from trading_core.equity_selection.candidate_config import DEFAULT_AS_OF_DATE as DEFAULT_CANDIDATE_AS_OF_DATE
from trading_core.equity_selection.filter_config import TradableUniverseFilterConfig, parse_bool
from trading_core.equity_workflows.workflow_config import ALLOWED_MODES as A_SHARE_WORKFLOW_MODES
from trading_core.equity_workflows.workflow_config import DEFAULT_AS_OF_DATE as DEFAULT_WORKFLOW_AS_OF_DATE


def _canonical_iso_date(value: str) -> str:
    try:
        normalized = Date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be a valid YYYY-MM-DD value") from exc
    if value != normalized:
        raise argparse.ArgumentTypeError("date must use canonical YYYY-MM-DD format")
    return normalized


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
    parser.add_argument("--as-of-date", type=_canonical_iso_date, default=DEFAULT_GATED_BUILD_AS_OF_DATE)
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
    parser.add_argument("--as-of-date", type=_canonical_iso_date, default=DEFAULT_BUILD_REPEATABILITY_AS_OF_DATE)
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


def _add_a_share_owner_daily_pack_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_DAILY_PACK_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_DAILY_PACK_MODES, default="build_owner_operations_decision_pack")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_DAILY_PACK_MODES, default="validate_daily_pack_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_daily_pack_history_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_DAILY_PACK_HISTORY_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_DAILY_PACK_HISTORY_MODES, default="build_owner_readiness_trends")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_DAILY_PACK_HISTORY_MODES, default="validate_daily_pack_history_inputs")
    parser.add_argument("--history-window-days", type=int, default=DEFAULT_OWNER_DAILY_PACK_HISTORY_WINDOW_DAYS)
    parser.add_argument("--minimum-required-observations", type=int, default=DEFAULT_OWNER_DAILY_PACK_HISTORY_MINIMUM_REQUIRED_OBSERVATIONS)
    parser.add_argument("--baseline-window-observations", type=int, default=DEFAULT_OWNER_DAILY_PACK_HISTORY_BASELINE_WINDOW_OBSERVATIONS)
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-rebuild-history", action="store_true")
    parser.add_argument("--allow-synthetic-history", action="store_true")


def _add_a_share_owner_readiness_gate_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_READINESS_GATE_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_READINESS_GATE_MODES, default="evaluate_owner_readiness_gate")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_READINESS_GATE_MODES, default="validate_owner_readiness_gate_inputs")
    parser.add_argument("--minimum-owner-readiness-score", type=int, default=DEFAULT_MINIMUM_OWNER_READINESS_SCORE)
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--allow-known-non-blocking-warnings", nargs="?", const=True, default=True, type=parse_bool)
    parser.add_argument("--allow-insufficient-history-if-correctly-flagged", nargs="?", const=True, default=True, type=parse_bool)


def _add_a_share_owner_quality_exception_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_QUALITY_EXCEPTION_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_QUALITY_EXCEPTION_MODES, default="build_escalation_workflow")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_QUALITY_EXCEPTION_MODES, default="validate_quality_exception_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_readiness_recovery_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_READINESS_RECOVERY_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_READINESS_RECOVERY_MODES, default="build_quality_improvement_plan")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_READINESS_RECOVERY_MODES, default="validate_recovery_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_readiness_recovery_execution_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_READINESS_RECOVERY_EXECUTION_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_READINESS_RECOVERY_EXECUTION_MODES, default="prepare_gate_reevaluation")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_READINESS_RECOVERY_EXECUTION_MODES, default="validate_recovery_execution_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_controlled_gate_reevaluation_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_CONTROLLED_GATE_REEVALUATION_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_CONTROLLED_GATE_REEVALUATION_MODES, default="record_reevaluation_skip_decision")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_CONTROLLED_GATE_REEVALUATION_MODES, default="validate_controlled_reevaluation_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_recovery_evidence_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_RECOVERY_EVIDENCE_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_RECOVERY_EVIDENCE_MODES, default="collect_recovery_evidence")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_RECOVERY_EVIDENCE_MODES, default="validate_recovery_evidence_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_evidence_backed_prep_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_EVIDENCE_BACKED_PREP_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_EVIDENCE_BACKED_PREP_MODES, default="evaluate_evidence_sufficiency_for_reevaluation")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_EVIDENCE_BACKED_PREP_MODES, default="validate_evidence_backed_prep_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_v0820_gate_outcome_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_V0820_GATE_OUTCOME_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_V0820_GATE_OUTCOME_MODES, default="build_and_audit_v0820_outcome")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_V0820_GATE_OUTCOME_MODES, default="validate_v0820_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_closeout_review_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_CLOSEOUT_REVIEW_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_CLOSEOUT_REVIEW_MODES, default="build_v090_rc_scope")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_CLOSEOUT_REVIEW_MODES, default="validate_closeout_review_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_owner_v090_rc_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_V090_RC_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_V090_RC_MODES, default="run_v090_full_regression")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_V090_RC_MODES, default="validate_v090_rc_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")
    parser.add_argument("--skip-full-pytest", action="store_true")


def _add_a_share_owner_operator_experience_arguments(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_OWNER_OPERATOR_EXPERIENCE_AS_OF_DATE)
    if include_mode:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_OPERATOR_EXPERIENCE_MODES, default="build_owner_daily_status")
    else:
        parser.add_argument("--mode", choices=A_SHARE_OWNER_OPERATOR_EXPERIENCE_MODES, default="validate_operator_experience_inputs")
    parser.add_argument("--allow-date-mismatch", action="store_true")


def _add_a_share_historical_evidence_backfill_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_HISTORICAL_EVIDENCE_BACKFILL_AS_OF_DATE)
    parser.add_argument("--lookback-start", default=DEFAULT_LOOKBACK_START)
    parser.add_argument("--target-evidence-days", type=int, default=DEFAULT_TARGET_EVIDENCE_DAYS)


def _add_a_share_v09_platform_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_V09_PLATFORM_AS_OF_DATE)
    parser.add_argument("--simulation-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")


def _add_a_share_v09_simulation_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--as-of-date", default=DEFAULT_V09_PLATFORM_AS_OF_DATE)
    parser.add_argument("--simulation-only", action="store_true")


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
