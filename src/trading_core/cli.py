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

    return parser


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
