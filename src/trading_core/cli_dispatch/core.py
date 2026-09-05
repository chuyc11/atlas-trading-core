"""CLI dispatch handlers: core commands (EARLY and LATE regions)."""

from __future__ import annotations

from collections.abc import Callable

import argparse

def _handle_init(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    _cli.ensure_project_dirs(paths)

    print(f"initialized {paths.project_root}")

    return 0

def _handle_load_macro(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    rows, limitations = _cli.sync_macro_signals(args.date, paths, write_local=not args.dry_run)

    print({"macro_signals": len(rows), "limitations": limitations})

    return 1 if limitations else 0

def _handle_backtest(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    if args.strategy_id:

        result = _cli.run_historical_backtest(args.start_date, args.end_date, args.strategy_id)

        print({"days": result["days"], "trades": result["trades_count"], "strategy_id": result["strategy_id"]})

    else:

        result = _cli.run_event_backtest(args.start_date, args.end_date)

        print({"days": result["days"], "total_return": result["total_return"]})

    return 0

def _handle_walk_forward(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_walk_forward(args.start_date, args.end_date, args.window_days)

    print({"windows": len(result["windows"])})

    return 0

def _handle_summarize_health(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.summarize_health(args.start_date, args.end_date)

    print(result)

    return 0

def _handle_import_prices(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.import_prices_csv(_cli._resolve_cli_path(args.input, paths), args.market)

    print(result)

    return 0

def _handle_validate_data_package(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_data_package(_cli._resolve_cli_path(args.input, paths), paths)

    print({"passed": result["passed"], "report_path": result["report_path"]})

    return 0

def _handle_run_backtest_batch(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_backtest_batch(args.start_date, args.end_date, _cli._resolve_cli_path(args.data, paths), paths)

    print({"passed": result["passed"], "output_dir": result["output_dir"]})

    return 0

def _handle_audit_dry_run(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_dry_run(args.start_date, args.end_date, paths)

    print({"passed": result["passed"], "report_path": result["report_path"]})

    return 0

def _handle_check_consistency(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.check_consistency(args.date, paths)

    print({"passed": result["passed"], "report_path": result["report_path"]})

    return 0

def _handle_check_consistency_range(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    artifact_dir = _cli._resolve_cli_path(args.artifact_dir, paths) if args.artifact_dir else None

    result = _cli.check_consistency_range(args.start_date, args.end_date, paths, mode=args.mode, artifact_dir=artifact_dir)

    print(

        {

            "passed": result["passed"],

            "mode": result["mode"],

            "items": len(result.get("items", [])),

            "report_path": result.get("report_path"),

        }

    )

    return 0

def _handle_fetch_prices(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.fetch_prices(

            args.start_date,

            args.end_date,

            _cli._resolve_cli_path(args.output, paths),

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

    return 1 if _cli.should_return_failure(result) else 0

def _handle_merge_price_data(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.merge_price_data(

        [_cli._resolve_cli_path(value, paths) for value in args.inputs],

        _cli._resolve_cli_path(args.output, paths),

        paths,

    )

    print({"passed": result["manifest"]["passed"], "manifest_path": result["manifest_path"]})

    return 0 if result["manifest"]["passed"] else 1

def _handle_real_data_validation_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_real_data_validation_report(_cli._resolve_cli_path(args.artifact_dir, paths), paths)

    print({"release_candidate_passed": result["release_candidate_passed"], "report_path": result["report_path"]})

    return 0

def _handle_dry_run_validation_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_dry_run_validation_report(args.start_date, args.end_date, paths)

    print({"dry_run_30d_passed": result["dry_run_30d_passed"], "report_path": result["report_path"]})

    return 0

def _handle_replay_dry_run(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.replay_dry_run(

        args.start_date,

        args.end_date,

        _cli._resolve_cli_path(args.data, paths),

        paths,

        write_main_ledger=args.write_main_ledger,

    )

    print({"historical_replay_passed": result["historical_replay_passed"], "report_path": result["report_path"]})

    return 0

def _handle_replay_last_trading_days(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.replay_last_trading_days(

        args.days,

        args.end_date,

        _cli._resolve_cli_path(args.data, paths),

        paths,

        write_main_ledger=args.write_main_ledger,

    )

    print({"historical_replay_passed": result["historical_replay_passed"], "report_path": result["report_path"]})

    return 0

def _handle_build_features(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_feature_matrix(args.start_date, args.end_date, _cli._resolve_cli_path(args.data, paths), paths)

    print({"rows": result["rows"], "output_path": result["output_path"], "report_path": result["report_path"]})

    return 0

def _handle_build_labels(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_label_matrix(args.start_date, args.end_date, _cli._resolve_cli_path(args.data, paths), paths)

    print({"rows": result["rows"], "output_path": result["output_path"], "report_path": result["report_path"]})

    return 0

def _handle_build_ml_dataset(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_walk_forward_dataset(

        _cli._resolve_cli_path(args.features, paths),

        _cli._resolve_cli_path(args.labels, paths),

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

def _handle_train_ml_shadow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.train_ml_shadow_model(

            _cli._resolve_cli_path(args.dataset, paths),

            _cli._resolve_cli_path(args.rows, paths),

            args.model_type,

            args.label_column,

            paths,

        )

    except RuntimeError as exc:

        print(str(exc))

        return 1

    print({"model_id": result["model_id"], "model_path": result["model_path"], "report_path": result["report_path"]})

    return 0

def _handle_predict_ml_shadow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.generate_ml_shadow_predictions(

        _cli._resolve_cli_path(args.model, paths),

        _cli._resolve_cli_path(args.rows, paths),

        paths,

    )

    print({"predictions": result["prediction_count"], "output_path": result["output_path"]})

    return 0

def _handle_generate_ml_shadow_signals(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.generate_ml_shadow_signals(

        _cli._resolve_cli_path(args.predictions, paths),

        args.top_k,

        args.target_weight,

        paths,

    )

    print({"signals": result["signal_count"], "output_path": result["output_path"]})

    return 0

def _handle_ml_shadow_leaderboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_ml_shadow_leaderboard(

        _cli._resolve_cli_path(args.predictions, paths),

        _cli._resolve_cli_path(args.signals, paths),

        args.benchmark,

        paths,

    )

    print({"recommendation": result["shadow_recommendation"], "output_path": result["output_path"]})

    return 0

def _handle_ml_shadow_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_ml_shadow_report(

        _cli._resolve_cli_path(args.dataset, paths),

        _cli._resolve_cli_path(args.model, paths),

        _cli._resolve_cli_path(args.predictions, paths),

        _cli._resolve_cli_path(args.signals, paths),

        _cli._resolve_cli_path(args.leaderboard, paths),

        paths,

    )

    print({"model_id": result["model_id"], "report_path": result["report_path"]})

    return 0

def _handle_register_experiment(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.register_experiment(_cli._resolve_cli_path(args.config, paths), paths)

    except Exception as exc:

        print(str(exc))

        return 1

    print({"experiment_id": result["experiment_id"], "status": result["status"]})

    return 0

def _handle_list_experiments(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    experiments = _cli.list_experiments(paths)

    print({"total": len(experiments), "experiments": [

        {"experiment_id": exp["experiment_id"], "status": exp.get("status", "unknown")}

        for exp in experiments

    ]})

    return 0

def _handle_show_experiment(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    experiment = _cli.get_experiment(args.experiment_id, paths)

    if experiment is None:

        print(f"Experiment '{args.experiment_id}' not found")

        return 1

    print(experiment)

    return 0

def _handle_run_parameter_sweep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.run_parameter_sweep_from_config(

            _cli._resolve_cli_path(args.config, paths), paths

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

def _handle_experiment_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_experiment_dashboard(

        experiments_dir=_cli._resolve_project_path(args.experiments_dir, paths),

        shadow_dir=_cli._resolve_project_path(args.shadow_dir, paths),

        output_dir=_cli._resolve_project_path(args.output_dir, paths),

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

def _handle_simulate_promotion(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.run_promotion_simulation(

            args.comparison,

            score_threshold=args.score_threshold,

            strict=args.strict,

            paths=paths,

        )

    except _cli.PromotionSimulationInputError as exc:

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

def _handle_compare_strategies(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.build_strategy_comparison(args.inputs, paths)

    except _cli.StrategyComparisonInputError as exc:

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

def _handle_update_mistake_patterns(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.update_mistake_pattern_library(

            args.inputs,

            min_evidence=args.min_evidence,

            paths=paths,

        )

    except _cli.MistakePatternLibraryInputError as exc:

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

def _handle_audit_experiment_system(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_experiment_system(

        experiments_dir=_cli._resolve_project_path(args.experiments_dir, paths),

        shadow_dir=_cli._resolve_project_path(args.shadow_dir, paths),

        outputs_dir=_cli._resolve_project_path(args.outputs_dir, paths),

        audit_dir=_cli._resolve_project_path(args.audit_dir, paths),

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

def _handle_weekly_research_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_weekly_research_report(

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

def _handle_monthly_research_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.build_monthly_research_report(

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

def _handle_system_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_system_dashboard(

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

def _handle_project_status_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_project_status_report(

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

def _handle_run_research_pipeline(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_research_pipeline(

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

def _handle_audit_reporting_system(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_reporting_system(

        reports_dir=_cli._resolve_project_path(args.reports_dir, paths),

        system_dir=_cli._resolve_project_path(args.system_dir, paths),

        audit_dir=_cli._resolve_project_path(args.audit_dir, paths),

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

def _handle_cli_inventory(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_cli_inventory(paths)

    print({"commands": len(result["commands"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_artifact_inventory(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_artifact_inventory(paths)

    print({"artifacts": len(result["artifacts"]), "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_system_smoke_test(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_system_smoke_test(

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

def _handle_boundary_regression_audit(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_boundary_regression_audit(paths=paths)

    print({

        "passed": result["passed"],

        "blocking_reasons": result["blocking_reasons"],

        "warnings": len(result["warnings"]),

        "json_path": result["json_path"],

        "report_path": result["report_path"],

    })

    return 0 if result["passed"] else 1

def _handle_system_integrity_audit(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_system_integrity_audit(paths)

    print({

        "overall_passed": result["overall_passed"],

        "blocking_reasons": result["blocking_reasons"],

        "warnings": len(result["warnings"]),

        "json_path": result["json_path"],

        "report_path": result["report_path"],

    })

    return 0 if result["overall_passed"] else 1

def _handle_final_handoff_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_final_handoff_review(paths)

    print({

        "review_id": result["review_id"],

        "overall_status": result["overall_status"],

        "warnings": len(result["warnings"]),

        "json_path": result["json_path"],

        "report_path": result["report_path"],

    })

    return 0

def _handle_report_index(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_report_index(

        include_audit=args.include_audit,

        include_experiments=args.include_experiments,

        include_system=args.include_system,

        paths=paths,

    )

    print({"reports": len(result["reports"]), "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_latest_artifact(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.locate_latest_artifact(args.type, open_command=args.open_command, paths=paths)

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

def _handle_artifact_browser(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_artifact_browser(

        include_missing=args.include_missing,

        group_by=args.group_by,

        paths=paths,

    )

    print({"start_here": len(result["start_here"]), "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_quick_status(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_quick_status(paths)

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

def _handle_usability_audit(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_usability_audit(paths)

    print({

        "overall_passed": result["overall_passed"],

        "blocking_reasons": result["blocking_reasons"],

        "warnings": len(result["warnings"]),

        "json_path": result["json_path"],

        "report_path": result["report_path"],

    })

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_readiness(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_forward_dry_run_readiness(

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

def _handle_global_briefing_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_signal_contract(paths)

    print({"contract_id": result["contract_id"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_validate_global_briefing_signals(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_global_briefing_signals(

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

def _handle_build_global_briefing_replay_bundle(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.build_global_briefing_replay_bundle(

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

def _handle_replay_global_briefing_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        result = _cli.replay_global_briefing_history(

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

def _handle_global_briefing_replay_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_global_briefing_replay_report(

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

def _handle_audit_global_briefing_replay(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_global_briefing_replay(

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

def _handle_audit_isolated_replay_adapter(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_isolated_replay_adapter(

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

def _handle_global_briefing_package_manifest(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_global_briefing_package_manifest(root=args.root, include=args.include, output=args.output, paths=paths)

    print({"packages": result["counts"]["packages"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_normalize_global_briefing_package(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.normalize_global_briefing_package(

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

def _handle_audit_global_briefing_package_coverage(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_global_briefing_package_coverage(

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

def _handle_run_global_briefing_real_package_replay(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_global_briefing_real_package_replay(

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

def _handle_global_briefing_real_package_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_global_briefing_real_package_report(

        manifest_path=args.manifest,

        workflow_path=args.workflow,

        coverage_path=args.coverage,

        evaluation_path=args.evaluation,

        paths=paths,

    )

    print({"report_id": result["report_id"], "overall_status": result["overall_status"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_global_briefing_real_package_integration(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_global_briefing_real_package_integration(

        manifest_path=args.manifest,

        workflow_path=args.workflow,

        report_path=args.report,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_global_briefing_warning_triage(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_global_briefing_warning_triage(

        coverage_path=args.coverage,

        workflow_path=args.workflow,

        report_path=args.report,

        audit_path=args.audit,

        paths=paths,

    )

    print({"triage_id": result["triage_id"], "warning_count": result["warning_count"], "production_blockers": result["production_blockers"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_global_briefing_evidence_quality_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_global_briefing_evidence_quality_report(

        triage_path=args.triage,

        coverage_path=args.coverage,

        workflow_path=args.workflow,

        audit_path=args.audit,

        paths=paths,

    )

    print({"report_id": result["report_id"], "overall_evidence_status": result["overall_evidence_status"], "production_ready": result["production_readiness"]["ready"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_global_briefing_production_acceptance_criteria(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_global_briefing_production_acceptance_criteria(paths=paths)

    print({"criteria_id": result["criteria_id"], "json_path": result["json_path"], "report_path": result["report_path"], "docs_path": result["docs_path"]})

    return 0

def _handle_audit_global_briefing_evidence_quality(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_global_briefing_evidence_quality(

        triage_path=args.triage,

        evidence_path=args.evidence,

        criteria_path=args.criteria,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_historical_data_source_resolution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.resolve_historical_data_sources(

        packages=_cli._split_csv_arg(args.packages),

        start_date=args.start_date,

        end_date=args.end_date,

        preferred_source=args.preferred_source,

        paths=paths,

    )

    print({"resolution_id": result["resolution_id"], "packages": len(result["packages"]), "overall_passed": result["overall_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_download_historical_data_packages(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.download_historical_data_packages(

        packages=_cli._split_csv_arg(args.packages),

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

def _handle_normalize_historical_data_packages(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.normalize_historical_data_packages(

        download_manifest_path=args.download_manifest,

        start_date=args.start_date,

        end_date=args.end_date,

        paths=paths,

    )

    print({"normalization_id": result["normalization_id"], "proxy_validated": result["proxy_package"]["validated"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["proxy_package"]["validated"] else 1

def _handle_audit_historical_data_quality(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_historical_data_quality(

        download_manifest_path=args.download_manifest,

        normalization_path=args.normalization,

        start_date=args.start_date,

        end_date=args.end_date,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_run_full_historical_proxy_replay(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_full_historical_proxy_replay(

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

def _handle_historical_data_acquisition_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_historical_data_acquisition_report(

        download_manifest_path=args.download_manifest,

        normalization_path=args.normalization,

        quality_audit_path=args.quality_audit,

        proxy_workflow_path=args.proxy_workflow,

        paths=paths,

    )

    print({"report_id": result["report_id"], "overall_status": result["overall_status"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_historical_data_acquisition(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_historical_data_acquisition(

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

def _handle_historical_warning_inventory(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_historical_warning_inventory(

        quality_audit_path=args.quality_audit,

        workflow_path=args.workflow,

        download_manifest_path=args.download_manifest,

        paths=paths,

    )

    print({"inventory_id": result["inventory_id"], "raw_warning_count": result["raw_warning_count"], "grouped_warning_count": result["grouped_warning_count"], "unknown_warning_count": result["unknown_warning_count"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["unknown_warning_count"] == 0 else 1

def _handle_close_historical_data_gaps(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.close_historical_data_gaps(

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

def _handle_historical_data_gap_closure_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_historical_data_gap_closure_report(workflow_path=args.workflow, paths=paths)

    print({"report_id": result["report_id"], "overall_status": result["overall_status"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_historical_data_gap_closure(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_historical_data_gap_closure(workflow_path=args.workflow, report_path=args.report, paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_day0_data_freeze(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day0_data_freeze(download_manifest_path=args.download_manifest, quality_audit_path=args.quality_audit, gap_closure_audit_path=args.gap_closure_audit, proxy_package_path=args.proxy_package, paths=paths)

    print({"freeze_id": result["freeze_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_day0_warning_register(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day0_warning_register(warning_inventory_path=args.warning_inventory, gap_closure_report_path=args.gap_closure_report, paths=paths)

    print({"register_id": result["register_id"], "accepted_count": result["accepted_count"], "unresolved_count": result["unresolved_count"], "blocking_count": result["blocking_count"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["blocking_count"] == 0 else 1

def _handle_day0_blocking_conditions(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day0_blocking_conditions(data_freeze_path=args.data_freeze, warning_register_path=args.warning_register, gap_closure_audit_path=args.gap_closure_audit, paths=paths)

    print({"register_id": result["register_id"], "current_blocking_count": result["current_blocking_count"], "manual_confirmation_still_required": result["manual_confirmation_still_required"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["current_blocking_count"] == 0 else 1

def _handle_day0_run_daily_preflight(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day0_run_daily_preflight(data_freeze_path=args.data_freeze, warning_register_path=args.warning_register, blocking_conditions_path=args.blocking_conditions, paths=paths)

    print({"preflight_id": result["preflight_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "executed": result["run_daily_command_preview"]["executed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_day0_manual_confirmation_packet(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day0_manual_confirmation_packet(paths=paths)

    print({"packet_id": result["packet_id"], "manual_confirmation_complete": result["manual_confirmation_complete"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_operating_calendar(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_operating_calendar(start_date=args.start_date, trading_days=args.trading_days, paths=paths)

    print({"calendar_id": result["calendar_id"], "calendar_status": result["calendar_status"], "days": len(result["days"]), "json_path": result["json_path"], "report_path": result["report_path"], "daily_log_template_path": result["daily_log_template_path"]})

    return 0

def _handle_day0_readiness_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day0_readiness_report(paths=paths)

    print({"report_id": result["report_id"], "overall_status": result["overall_status"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_day0_readiness(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_day0_readiness(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_plan_checklist(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_plan_checklist(plan_path=args.plan, paths=paths)

    print({"checklist_id": result["checklist_id"], "requirements": len(result["requirements"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_mvp_requirement_map(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_mvp_requirement_map(checklist_path=args.checklist, paths=paths)

    print({"map_id": result["map_id"], "requirements": len(result["requirements"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_artifact_coverage_scanner(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_artifact_coverage_scan(paths=paths)

    print({"scan_id": result["scan_id"], "counts": result["counts"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_classify_mvp_gaps(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.classify_mvp_gaps(checklist_path=args.checklist, requirement_map_path=args.requirement_map, artifact_scan_path=args.artifact_scan, paths=paths)

    print({"classification_id": result["classification_id"], "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_classify_day1_blockers(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.classify_day1_blockers(mvp_gap_classification_path=args.mvp_gap_classification, paths=paths)

    print({"classifier_id": result["classifier_id"], "day1_allowed": result["day1_allowed"], "blocking_count": result["blocking_count"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_next_work_register(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_next_work_register(mvp_gap_classification_path=args.mvp_gap_classification, day1_blocker_classification_path=args.day1_blocker_classification, paths=paths)

    print({"register_id": result["register_id"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_plan_alignment(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_plan_alignment(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_execution_timeline_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_execution_timeline_contract(paths=paths)

    print({"contract_id": result["contract_id"], "same_day_close_signal_execution_rejected": result["same_day_close_signal_execution_rejected"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_virtual_execution_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_virtual_execution_contract(paths=paths)

    print({"contract_id": result["contract_id"], "integrates": len(result["integrates"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_isolated_ledger_invariants(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_isolated_ledger_invariants(ledger_dir=args.ledger_dir, paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_execution_aware_replay_smoke(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_execution_aware_replay_smoke(start_date=args.start_date, end_date=args.end_date, execution_mode=args.execution_mode, paths=paths)

    print({"smoke_id": result["smoke_id"], "overall_passed": result["overall_passed"], "included_scenarios": result["included_scenarios"], "ledger_invariant_audit_passed": result["ledger_invariant_audit_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_reclassify_day1_blockers_after_execution_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_blockers_after_execution_hardening(baseline_path=args.baseline, paths=paths)

    print({"reclassification_id": result["reclassification_id"], "baseline_day1_blocker_count": result["baseline_day1_blocker_count"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_baseline_strategy_scope_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_baseline_strategy_scope_plan(paths=paths)

    print({"plan_id": result["plan_id"], "execution_day1_blockers_closed": result["execution_day1_blockers_closed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_baseline_strategy_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_baseline_strategy_contract(paths=paths)

    print({"contract_id": result["contract_id"], "strategies": len(result["strategies"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_baseline_strategy_registry(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_baseline_strategy_registry(paths=paths)

    print({"registry_id": result["registry_id"], "strategies": len(result["strategies"]), "parameter_versions": result["parameter_versions"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_generate_baseline_strategy_signals(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.generate_baseline_strategy_signals(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, paths=paths)

    print({"strategies": result["strategies"], "all_signals_generated": result["all_signals_generated"], "all_pit_constraints_passed": result["all_pit_constraints_passed"], "paths": result["paths"]})

    return 0 if result["all_signals_generated"] and result["all_pit_constraints_passed"] else 1

def _handle_build_baseline_order_preview(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_baseline_order_preview(strategy=args.strategy, signals=args.signals, execution_mode=args.execution_mode, paths=paths)

    print({"strategy": result["strategy"], "execution_mode": result["execution_mode"], "preview_only": result["preview_only"], "executed": result["executed"], "paths": result["paths"]})

    return 0 if result["preview_only"] and not result["executed"] else 1

def _handle_replay_baseline_strategy(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.replay_baseline_strategy(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, execution_mode=args.execution_mode, paths=paths)

    print({"strategy": result["strategy"], "execution_mode": result["execution_mode"], "all_replays_complete": result["all_replays_complete"], "paths": result["paths"]})

    return 0 if result["all_replays_complete"] else 1

def _handle_compare_baseline_strategy_benchmarks(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.compare_baseline_strategy_benchmarks(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, paths=paths)

    print({"comparison_id": result["comparison_id"], "strategies": list(result["strategies"].keys()), "benchmarks": list(result["benchmarks"].keys()), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_baseline_strategy_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_baseline_strategy_report(strategy=args.strategy, start_date=args.start_date, end_date=args.end_date, paths=paths)

    print({"strategy": result["strategy"], "all_reports_generated": result["all_reports_generated"], "paths": result["paths"]})

    return 0 if result["all_reports_generated"] else 1

def _handle_baseline_strategy_pack_summary(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_baseline_strategy_pack_summary(paths=paths)

    print({"summary_id": result["summary_id"], "all_strategies_complete": result["all_strategies_complete"], "strategy_count": result["strategy_count"], "strategies_complete": result["strategies_complete"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_baseline_strategy_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_baseline_strategy_pack(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_reclassify_day1_blockers_after_baseline_strategies(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_blockers_after_baseline_strategies(paths=paths)

    print({"reclassification_id": result["reclassification_id"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_version": result["recommended_next_version"], "day1_start_allowed": result["day1_start_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_daily_workflow_scope_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_workflow_scope_plan(paths=paths)

    print({"plan_id": result["plan_id"], "target_version": result["target_version"], "baseline_strategy_pack_complete": result["baseline_strategy_pack_complete"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_daily_market_data_snapshot(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_market_data_snapshot(as_of_date=args.as_of_date, paths=paths)

    print({"snapshot_id": result["snapshot_id"], "as_of_date": result["as_of_date"], "latest_available_trading_date": result["latest_available_trading_date"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_daily_data_quality(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_daily_data_quality(snapshot=args.snapshot, paths=paths)

    print({"as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_daily_input_freeze_manifest(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_input_freeze_manifest(as_of_date=args.as_of_date, paths=paths)

    print({"manifest_id": result["manifest_id"], "as_of_date": result["as_of_date"], "latest_available_trading_date": result["latest_available_trading_date"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_daily_baseline_signals(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_baseline_signals(as_of_date=args.as_of_date, strategy=args.strategy, paths=paths)

    print({"as_of_date": result["as_of_date"], "strategies_total": result["strategies_total"], "all_pit_constraints_passed": result["all_pit_constraints_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["all_pit_constraints_passed"] else 1

def _handle_daily_order_preview(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_order_preview(as_of_date=args.as_of_date, strategy=args.strategy, execution_mode=args.execution_mode, paths=paths)

    print({"as_of_date": result["as_of_date"], "proposal_count": result["proposal_count"], "preview_only": result["preview_only"], "executed": result["executed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["preview_only"] and not result["executed"] else 1

def _handle_daily_isolated_execution_preview(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_isolated_execution_preview(as_of_date=args.as_of_date, execution_mode=args.execution_mode, paths=paths)

    print({"as_of_date": result["as_of_date"], "execution_mode": result["execution_mode"], "preview_only": result["preview_only"], "executed": result["executed"], "state_updated": result["state_updated"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["preview_only"] and not result["executed"] and not result["state_updated"] else 1

def _handle_daily_report_packet(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_daily_report_packet(as_of_date=args.as_of_date, paths=paths)

    print({"as_of_date": result["as_of_date"], "latest_available_trading_date": result["latest_available_trading_date"], "signals": len(result["signals_summary_by_strategy"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_protected_path_residue_scan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.scan_protected_path_residue(paths=paths)

    print({"scan_id": result["scan_id"], "overall_passed": result["overall_passed"], "blocker_count": result["blocker_count"], "warning_count": result["warning_count"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_audit_daily_workflow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_daily_workflow(as_of_date=args.as_of_date, paths=paths)

    print({"release_candidate": result["release_candidate"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_reclassify_day1_blockers_after_daily_workflow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_blockers_after_daily_workflow(paths=paths)

    print({"reclassification_id": result["reclassification_id"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_version": result["recommended_next_version"], "day1_start_allowed": result["day1_start_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_authorization_scope_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_authorization_scope_plan(paths=paths)

    print({"plan_id": result["plan_id"], "target_version": result["target_version"], "daily_workflow_audit_passed": result["daily_workflow_audit_passed"], "known_day1_blockers_closed": result["known_day1_blockers_closed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_start_prerequisite_inventory(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_start_prerequisite_inventory(paths=paths)

    print({"inventory_id": result["inventory_id"], "overall_day1_allowed": result["overall_day1_allowed"], "prerequisites": len(result["prerequisites"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_current_daily_workflow_readiness_snapshot(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_current_daily_workflow_readiness_snapshot(paths=paths)

    print({"snapshot_id": result["snapshot_id"], "historical_daily_workflow_fixture_passed": result["historical_daily_workflow_fixture_passed"], "current_production_daily_workflow_authorized": result["current_production_daily_workflow_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_manual_confirmation_checklist_v2(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)

    print({"checklist_id": result["checklist_id"], "manual_confirmation_complete": result["manual_confirmation_complete"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_owner_authorization_packet(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_owner_authorization_packet(paths=paths)

    print({"authorization_packet_id": result["authorization_packet_id"], "authorization_status": result["authorization_status"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_validate_forward_dry_run_start_gate_v062(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_forward_dry_run_start_gate_v062(paths=paths)

    print({"gate_id": result["gate_id"], "day1_start_allowed": result["day1_start_allowed"], "deny_reasons": result["deny_reasons"], "run_daily_command_preview": result["run_daily_command_preview"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_run_daily_command_preview(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_run_daily_command_preview(paths=paths)

    print({"preview_id": result["preview_id"], "preview_only": result["preview_only"], "executed": result["executed"], "run_daily_called": result["run_daily_called"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_day1_prompt_eligibility(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_day1_prompt_eligibility(paths=paths)

    print({"eligibility_id": result["eligibility_id"], "day1_prompt_eligible": result["day1_prompt_eligible"], "day1_prompt_generated": result["day1_prompt_generated"], "deny_reasons": result["deny_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_forward_dry_run_start_authorization(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_forward_dry_run_start_authorization(paths=paths)

    print({"release_candidate": result["release_candidate"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_reclassify_day1_blockers_after_start_authorization(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_blockers_after_start_authorization(paths=paths)

    print({"reclassification_id": result["reclassification_id"], "technical_day1_blocker_count": result["technical_day1_blocker_count"], "authorization_blocker_count": result["authorization_blocker_count"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_action": result["recommended_next_action"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_owner_manual_confirmation_record(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_owner_manual_confirmation_record(paths=paths)

    print({"record_id": result["record_id"], "owner_confirmation_recorded": result["owner_confirmation_recorded"], "owner_authorized_next_step": result["owner_authorized_next_step"], "owner_authorized_day1_execution": result["owner_authorized_day1_execution"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_complete_forward_dry_run_manual_confirmation_checklist_v2(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.complete_forward_dry_run_manual_confirmation_checklist_v2(paths=paths)

    print({"checklist_id": result["checklist_id"], "manual_confirmation_complete": result["manual_confirmation_complete"], "day1_execution_authorized": result["day1_execution_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_update_forward_dry_run_owner_authorization_packet(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.update_forward_dry_run_owner_authorization_packet(paths=paths)

    print({"authorization_packet_id": result["authorization_packet_id"], "authorization_status": result["authorization_status"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "day1_execution_authorized": result["day1_execution_authorized"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_revalidate_forward_dry_run_start_gate_v0621(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.revalidate_forward_dry_run_start_gate_v0621(paths=paths)

    print({"gate_id": result["gate_id"], "technical_prerequisites_passed": result["technical_prerequisites_passed"], "manual_confirmation_complete": result["manual_confirmation_complete"], "forward_dry_run_start_authorized": result["forward_dry_run_start_authorized"], "day1_prompt_eligible": result["day1_prompt_eligible"], "day1_start_allowed": result["day1_start_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_revalidate_forward_dry_run_day1_prompt_eligibility(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.revalidate_forward_dry_run_day1_prompt_eligibility(paths=paths)

    print({"eligibility_id": result["eligibility_id"], "day1_prompt_eligible": result["day1_prompt_eligible"], "day1_prompt_generated": result["day1_prompt_generated"], "next_required_action": result["next_required_action"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_forward_dry_run_authorization_materialization(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_forward_dry_run_authorization_materialization(paths=paths)

    print({"release_candidate": result["release_candidate"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_reclassify_day1_blockers_after_authorization_materialization(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_blockers_after_authorization_materialization(paths=paths)

    print({"reclassification_id": result["reclassification_id"], "technical_day1_blocker_count": result["technical_day1_blocker_count"], "authorization_blocker_count": result["authorization_blocker_count"], "updated_day1_blocker_count": result["updated_day1_blocker_count"], "recommended_next_action": result["recommended_next_action"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_day1_pre_execution_gate(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_pre_execution_gate(allow_rerun=args.allow_rerun, paths=paths)

    print({"gate_id": result["gate_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_day1_input_snapshot(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_input_snapshot(as_of_date=args.as_of_date, paths=paths)

    print({"snapshot_id": result["snapshot_id"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_day1_strategy_signals(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_strategy_signals(paths=paths)

    print({"signals_id": result["signals_id"], "as_of_date": result["as_of_date"], "strategies_total": result["strategies_total"], "strategies_generated": result["strategies_generated"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["strategies_generated"] == result["strategies_total"] else 1

def _handle_forward_dry_run_day1_virtual_order_preview(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_virtual_order_preview(paths=paths)

    print({"order_preview_id": result["order_preview_id"], "as_of_date": result["as_of_date"], "orders_total": result["summary"]["orders_total"], "orders_rejected": result["summary"]["orders_rejected"], "preview_only": result["preview_only"], "real_order": result["real_order"], "broker_order": result["broker_order"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["preview_only"] and not result["real_order"] and not result["broker_order"] else 1

def _handle_forward_dry_run_day1_virtual_execution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_virtual_execution_result(paths=paths)

    print({"execution_result_id": result["execution_result_id"], "as_of_date": result["as_of_date"], "execution_mode": result["execution_mode"], "virtual_execution": result["virtual_execution"], "real_execution": result["real_execution"], "broker_execution": result["broker_execution"], "fills": len(result["fills"]), "rejects": len(result["rejects"]), "ledger_writes": result["ledger_writes"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["virtual_execution"] and not result["real_execution"] and not result["broker_execution"] else 1

def _handle_forward_dry_run_day1_ledger_snapshot(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_ledger_snapshot(paths=paths)

    print({"ledger_snapshot_id": result["ledger_snapshot_id"], "forward_dry_run_started": result["forward_dry_run_started"], "forward_dry_run_days_completed": result["forward_dry_run_days_completed"], "next_day_index": result["next_day_index"], "fills_count": result["fills_count"], "rejects_count": result["rejects_count"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_day1_risk_boundary_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_risk_and_boundary_report(paths=paths)

    print({"report_id": result["report_id"], "risk_summary": result["risk_summary"], "boundary_summary": result["boundary_summary"], "warnings": len(result["warnings"]), "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if not result["blocking_reasons"] else 1

def _handle_forward_dry_run_day1_operator_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_operator_report(paths=paths)

    print({"report_id": result["report_id"], "as_of_date": result["as_of_date"], "execution_date": result["execution_date"], "strategies_included": result["strategies_included"], "next_allowed_action": result["next_allowed_action"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_forward_dry_run_day1(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_forward_dry_run_day1(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_status(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_forward_dry_run_status(paths=paths)

    print({"status_id": result["status_id"], "forward_dry_run_started": result["forward_dry_run_started"], "forward_dry_run_days_completed": result["forward_dry_run_days_completed"], "next_day_index": result["next_day_index"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_reclassify_day1_blockers_after_forward_dry_run_day1(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_blockers_after_forward_dry_run_day1(paths=paths)

    print({"reclassification_id": result["reclassification_id"], "remaining_day1_blocker_count": result["remaining_day1_blocker_count"], "day2_blocker_count": result["day2_blocker_count"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_day1_continuation_gap_analysis(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_continuation_gap_analysis(paths=paths)

    print({"analysis_id": result["analysis_id"], "day1_core_execution_passed": result["day1_core_execution_passed"], "v064_preflight_blocked": result["v064_preflight_blocked"], "missing_artifacts": result["missing_artifacts"], "day2_execution_allowed_in_this_stage": result["day2_execution_allowed_in_this_stage"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_day1_artifact_manifest(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_artifact_manifest(paths=paths)

    print({"manifest_id": result["manifest_id"], "required_artifacts_total": result["required_artifacts_total"], "required_artifacts_present": result["required_artifacts_present"], "missing_required_artifacts": result["missing_required_artifacts"], "overall_passed": result["overall_passed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_day1_reproducibility_manifest(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_reproducibility_manifest(paths=paths)

    print({"manifest_id": result["manifest_id"], "baseline_tag": result["baseline_tag"], "day1_as_of_date": result["day1_as_of_date"], "external_api_called": result["external_api_called"], "real_time_market_data_downloaded": result["real_time_market_data_downloaded"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_day2_readiness_packet(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day2_readiness_packet(paths=paths)

    print({"packet_id": result["packet_id"], "day1_passed": result["day1_passed"], "day1_artifacts_complete": result["day1_artifacts_complete"], "day2_prompt_eligible_after_operator_review": result["day2_prompt_eligible_after_operator_review"], "operator_review_required": result["operator_review_required"], "day2_executed": result["day2_executed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_forward_dry_run_day2_continuation_gate_preview(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day2_continuation_gate_preview(paths=paths)

    print({"preview_id": result["preview_id"], "day2_continuation_structurally_eligible": result["day2_continuation_structurally_eligible"], "operator_review_required": result["operator_review_required"], "day2_execution_authorized_in_this_artifact": result["day2_execution_authorized_in_this_artifact"], "day2_executed": result["day2_executed"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_audit_forward_dry_run_day1_continuation_artifacts(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_day1_continuation_artifacts(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_reclassify_day1_continuation_artifacts_v0631(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.reclassify_day1_continuation_artifacts_v0631(paths=paths)

    print({"reclassification_id": result["reclassification_id"], "continuation_artifact_gap_resolved": result["continuation_artifact_gap_resolved"], "remaining_continuation_artifact_gap_count": result["remaining_continuation_artifact_gap_count"], "day2_blocker_count": result["day2_blocker_count"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["continuation_artifact_gap_resolved"] else 1

def _handle_forward_dry_run_day1_owner_report_scope_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_owner_report_scope_plan(paths=paths)

    print({"scope_plan_id": result["scope_plan_id"], "target_version": result["target_version"], "report_only": result["report_only"], "day2_execution_allowed": result["day2_execution_allowed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_day1_owner_summary_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_owner_summary_report(paths=paths)

    print({"report_id": result["report_id"], "as_of_date": result["as_of_date"], "key_numbers": result["key_numbers"], "day2_executed": result["boundary"]["day2_executed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_forward_dry_run_day1_strategy_signal_explanation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_strategy_signal_explanation(paths=paths)

    print({"report_id": result["report_id"], "strategies_total": result["strategies_total"], "strategies_explained": result["strategies_explained"], "promotion_triggered": result["boundary"]["promotion_triggered"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["strategies_explained"] == result["strategies_total"] else 1

def _handle_forward_dry_run_day1_virtual_order_fill_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_virtual_order_fill_report(paths=paths)

    print({"report_id": result["report_id"], "orders_total": result["orders_total"], "fills_total": result["fills_total"], "rejects_total": result["rejects_total"], "real_orders_placed": result["real_orders_placed"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if not result["real_orders_placed"] and not result["broker_orders_placed"] else 1

def _handle_forward_dry_run_day1_isolated_ledger_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_isolated_ledger_report(paths=paths)

    print({"report_id": result["report_id"], "forward_dry_run_ledger_written": result["forward_dry_run_ledger_written"], "ledger_hash": result["ledger_hash"], "invariants": result["invariants"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["forward_dry_run_ledger_written"] and all(result["invariants"].values()) else 1

def _handle_forward_dry_run_day1_data_reproducibility_appendix(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_data_reproducibility_appendix(paths=paths)

    print({"appendix_id": result["appendix_id"], "day1_as_of_date": result["day1_as_of_date"], "external_api_called": result["external_api_called"], "real_time_market_data_downloaded": result["real_time_market_data_downloaded"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if not result["external_api_called"] and not result["real_time_market_data_downloaded"] else 1

def _handle_forward_dry_run_day1_continuation_blocker_note(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_continuation_blocker_note(paths=paths)

    print({"note_id": result["note_id"], "day1_completed": result["day1_completed"], "day2_executed": result["day2_executed"], "blocker_type": result["blocker_type"], "latest_common_local_data_date": result["latest_common_local_data_date"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["day1_completed"] and not result["day2_executed"] else 1

def _handle_forward_dry_run_day1_owner_report_pack_summary(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_day1_owner_report_pack_summary(paths=paths)

    print({"summary_id": result["summary_id"], "reports_total": result["reports_total"], "reports_complete": result["reports_complete"], "missing_reports": result["missing_reports"], "owner_report_pack_complete": result["owner_report_pack_complete"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["owner_report_pack_complete"] else 1

def _handle_audit_forward_dry_run_day1_owner_report_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_day1_owner_report_pack(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_external_project_intake(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_external_project_intake(paths=paths)

    print({"intake_id": result["intake_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "projects_downloaded": result["projects_downloaded"], "top_priority_repos": result["top_priority_repos"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_equity_data_source_manifest(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_data_source_manifest(paths=paths)

    print({"manifest_id": result["manifest_id"], "selected_provider": result["selected_provider"], "rows_available": result["rows_available"], "providers_succeeded": result["providers_succeeded"], "external_api_called": result["external_api_called"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["data_written_to_local_store"] else 1


DISPATCH_HANDLERS_EARLY: dict[str, Callable[..., int]] = {
    "init": _handle_init,
    "load-macro": _handle_load_macro,
    "backtest": _handle_backtest,
    "walk-forward": _handle_walk_forward,
    "summarize-health": _handle_summarize_health,
    "import-prices": _handle_import_prices,
    "validate-data-package": _handle_validate_data_package,
    "run-backtest-batch": _handle_run_backtest_batch,
    "audit-dry-run": _handle_audit_dry_run,
    "check-consistency": _handle_check_consistency,
    "check-consistency-range": _handle_check_consistency_range,
    "fetch-prices": _handle_fetch_prices,
    "merge-price-data": _handle_merge_price_data,
    "real-data-validation-report": _handle_real_data_validation_report,
    "dry-run-validation-report": _handle_dry_run_validation_report,
    "replay-dry-run": _handle_replay_dry_run,
    "replay-last-trading-days": _handle_replay_last_trading_days,
    "build-features": _handle_build_features,
    "build-labels": _handle_build_labels,
    "build-ml-dataset": _handle_build_ml_dataset,
    "train-ml-shadow": _handle_train_ml_shadow,
    "predict-ml-shadow": _handle_predict_ml_shadow,
    "generate-ml-shadow-signals": _handle_generate_ml_shadow_signals,
    "ml-shadow-leaderboard": _handle_ml_shadow_leaderboard,
    "ml-shadow-report": _handle_ml_shadow_report,
    "register-experiment": _handle_register_experiment,
    "list-experiments": _handle_list_experiments,
    "show-experiment": _handle_show_experiment,
    "run-parameter-sweep": _handle_run_parameter_sweep,
    "experiment-dashboard": _handle_experiment_dashboard,
    "simulate-promotion": _handle_simulate_promotion,
    "compare-strategies": _handle_compare_strategies,
    "update-mistake-patterns": _handle_update_mistake_patterns,
    "audit-experiment-system": _handle_audit_experiment_system,
    "weekly-research-report": _handle_weekly_research_report,
    "monthly-research-report": _handle_monthly_research_report,
    "system-dashboard": _handle_system_dashboard,
    "project-status-report": _handle_project_status_report,
    "run-research-pipeline": _handle_run_research_pipeline,
    "audit-reporting-system": _handle_audit_reporting_system,
    "cli-inventory": _handle_cli_inventory,
    "artifact-inventory": _handle_artifact_inventory,
    "system-smoke-test": _handle_system_smoke_test,
    "boundary-regression-audit": _handle_boundary_regression_audit,
    "system-integrity-audit": _handle_system_integrity_audit,
    "final-handoff-review": _handle_final_handoff_review,
    "report-index": _handle_report_index,
    "latest-artifact": _handle_latest_artifact,
    "artifact-browser": _handle_artifact_browser,
    "quick-status": _handle_quick_status,
    "usability-audit": _handle_usability_audit,
    "forward-dry-run-readiness": _handle_forward_dry_run_readiness,
    "global-briefing-contract": _handle_global_briefing_contract,
    "validate-global-briefing-signals": _handle_validate_global_briefing_signals,
    "build-global-briefing-replay-bundle": _handle_build_global_briefing_replay_bundle,
    "replay-global-briefing-history": _handle_replay_global_briefing_history,
    "global-briefing-replay-report": _handle_global_briefing_replay_report,
    "audit-global-briefing-replay": _handle_audit_global_briefing_replay,
    "audit-isolated-replay-adapter": _handle_audit_isolated_replay_adapter,
    "global-briefing-package-manifest": _handle_global_briefing_package_manifest,
    "normalize-global-briefing-package": _handle_normalize_global_briefing_package,
    "audit-global-briefing-package-coverage": _handle_audit_global_briefing_package_coverage,
    "run-global-briefing-real-package-replay": _handle_run_global_briefing_real_package_replay,
    "global-briefing-real-package-report": _handle_global_briefing_real_package_report,
    "audit-global-briefing-real-package-integration": _handle_audit_global_briefing_real_package_integration,
    "global-briefing-warning-triage": _handle_global_briefing_warning_triage,
    "global-briefing-evidence-quality-report": _handle_global_briefing_evidence_quality_report,
    "global-briefing-production-acceptance-criteria": _handle_global_briefing_production_acceptance_criteria,
    "audit-global-briefing-evidence-quality": _handle_audit_global_briefing_evidence_quality,
    "historical-data-source-resolution": _handle_historical_data_source_resolution,
    "download-historical-data-packages": _handle_download_historical_data_packages,
    "normalize-historical-data-packages": _handle_normalize_historical_data_packages,
    "audit-historical-data-quality": _handle_audit_historical_data_quality,
    "run-full-historical-proxy-replay": _handle_run_full_historical_proxy_replay,
    "historical-data-acquisition-report": _handle_historical_data_acquisition_report,
    "audit-historical-data-acquisition": _handle_audit_historical_data_acquisition,
    "historical-warning-inventory": _handle_historical_warning_inventory,
    "close-historical-data-gaps": _handle_close_historical_data_gaps,
    "historical-data-gap-closure-report": _handle_historical_data_gap_closure_report,
    "audit-historical-data-gap-closure": _handle_audit_historical_data_gap_closure,
    "day0-data-freeze": _handle_day0_data_freeze,
    "day0-warning-register": _handle_day0_warning_register,
    "day0-blocking-conditions": _handle_day0_blocking_conditions,
    "day0-run-daily-preflight": _handle_day0_run_daily_preflight,
    "day0-manual-confirmation-packet": _handle_day0_manual_confirmation_packet,
    "forward-dry-run-operating-calendar": _handle_forward_dry_run_operating_calendar,
    "day0-readiness-report": _handle_day0_readiness_report,
    "audit-day0-readiness": _handle_audit_day0_readiness,
    "plan-checklist": _handle_plan_checklist,
    "mvp-requirement-map": _handle_mvp_requirement_map,
    "artifact-coverage-scanner": _handle_artifact_coverage_scanner,
    "classify-mvp-gaps": _handle_classify_mvp_gaps,
    "classify-day1-blockers": _handle_classify_day1_blockers,
    "next-work-register": _handle_next_work_register,
    "audit-plan-alignment": _handle_audit_plan_alignment,
    "execution-timeline-contract": _handle_execution_timeline_contract,
    "virtual-execution-contract": _handle_virtual_execution_contract,
    "audit-isolated-ledger-invariants": _handle_audit_isolated_ledger_invariants,
    "execution-aware-replay-smoke": _handle_execution_aware_replay_smoke,
    "reclassify-day1-blockers-after-execution-hardening": _handle_reclassify_day1_blockers_after_execution_hardening,
    "baseline-strategy-scope-plan": _handle_baseline_strategy_scope_plan,
    "baseline-strategy-contract": _handle_baseline_strategy_contract,
    "baseline-strategy-registry": _handle_baseline_strategy_registry,
    "generate-baseline-strategy-signals": _handle_generate_baseline_strategy_signals,
    "build-baseline-order-preview": _handle_build_baseline_order_preview,
    "replay-baseline-strategy": _handle_replay_baseline_strategy,
    "compare-baseline-strategy-benchmarks": _handle_compare_baseline_strategy_benchmarks,
    "baseline-strategy-report": _handle_baseline_strategy_report,
    "baseline-strategy-pack-summary": _handle_baseline_strategy_pack_summary,
    "audit-baseline-strategy-pack": _handle_audit_baseline_strategy_pack,
    "reclassify-day1-blockers-after-baseline-strategies": _handle_reclassify_day1_blockers_after_baseline_strategies,
    "daily-workflow-scope-plan": _handle_daily_workflow_scope_plan,
    "daily-market-data-snapshot": _handle_daily_market_data_snapshot,
    "audit-daily-data-quality": _handle_audit_daily_data_quality,
    "daily-input-freeze-manifest": _handle_daily_input_freeze_manifest,
    "daily-baseline-signals": _handle_daily_baseline_signals,
    "daily-order-preview": _handle_daily_order_preview,
    "daily-isolated-execution-preview": _handle_daily_isolated_execution_preview,
    "daily-report-packet": _handle_daily_report_packet,
    "protected-path-residue-scan": _handle_protected_path_residue_scan,
    "audit-daily-workflow": _handle_audit_daily_workflow,
    "reclassify-day1-blockers-after-daily-workflow": _handle_reclassify_day1_blockers_after_daily_workflow,
    "forward-dry-run-authorization-scope-plan": _handle_forward_dry_run_authorization_scope_plan,
    "forward-dry-run-start-prerequisite-inventory": _handle_forward_dry_run_start_prerequisite_inventory,
    "current-daily-workflow-readiness-snapshot": _handle_current_daily_workflow_readiness_snapshot,
    "forward-dry-run-manual-confirmation-checklist-v2": _handle_forward_dry_run_manual_confirmation_checklist_v2,
    "forward-dry-run-owner-authorization-packet": _handle_forward_dry_run_owner_authorization_packet,
    "validate-forward-dry-run-start-gate-v062": _handle_validate_forward_dry_run_start_gate_v062,
    "forward-dry-run-run-daily-command-preview": _handle_forward_dry_run_run_daily_command_preview,
    "forward-dry-run-day1-prompt-eligibility": _handle_forward_dry_run_day1_prompt_eligibility,
    "audit-forward-dry-run-start-authorization": _handle_audit_forward_dry_run_start_authorization,
    "reclassify-day1-blockers-after-start-authorization": _handle_reclassify_day1_blockers_after_start_authorization,
    "forward-dry-run-owner-manual-confirmation-record": _handle_forward_dry_run_owner_manual_confirmation_record,
    "complete-forward-dry-run-manual-confirmation-checklist-v2": _handle_complete_forward_dry_run_manual_confirmation_checklist_v2,
    "update-forward-dry-run-owner-authorization-packet": _handle_update_forward_dry_run_owner_authorization_packet,
    "revalidate-forward-dry-run-start-gate-v0621": _handle_revalidate_forward_dry_run_start_gate_v0621,
    "revalidate-forward-dry-run-day1-prompt-eligibility": _handle_revalidate_forward_dry_run_day1_prompt_eligibility,
    "audit-forward-dry-run-authorization-materialization": _handle_audit_forward_dry_run_authorization_materialization,
    "reclassify-day1-blockers-after-authorization-materialization": _handle_reclassify_day1_blockers_after_authorization_materialization,
    "forward-dry-run-day1-pre-execution-gate": _handle_forward_dry_run_day1_pre_execution_gate,
    "forward-dry-run-day1-input-snapshot": _handle_forward_dry_run_day1_input_snapshot,
    "forward-dry-run-day1-strategy-signals": _handle_forward_dry_run_day1_strategy_signals,
    "forward-dry-run-day1-virtual-order-preview": _handle_forward_dry_run_day1_virtual_order_preview,
    "forward-dry-run-day1-virtual-execution": _handle_forward_dry_run_day1_virtual_execution,
    "forward-dry-run-day1-ledger-snapshot": _handle_forward_dry_run_day1_ledger_snapshot,
    "forward-dry-run-day1-risk-boundary-report": _handle_forward_dry_run_day1_risk_boundary_report,
    "forward-dry-run-day1-operator-report": _handle_forward_dry_run_day1_operator_report,
    "audit-forward-dry-run-day1": _handle_audit_forward_dry_run_day1,
    "forward-dry-run-status": _handle_forward_dry_run_status,
    "reclassify-day1-blockers-after-forward-dry-run-day1": _handle_reclassify_day1_blockers_after_forward_dry_run_day1,
    "forward-dry-run-day1-continuation-gap-analysis": _handle_forward_dry_run_day1_continuation_gap_analysis,
    "forward-dry-run-day1-artifact-manifest": _handle_forward_dry_run_day1_artifact_manifest,
    "forward-dry-run-day1-reproducibility-manifest": _handle_forward_dry_run_day1_reproducibility_manifest,
    "forward-dry-run-day2-readiness-packet": _handle_forward_dry_run_day2_readiness_packet,
    "forward-dry-run-day2-continuation-gate-preview": _handle_forward_dry_run_day2_continuation_gate_preview,
    "audit-forward-dry-run-day1-continuation-artifacts": _handle_audit_forward_dry_run_day1_continuation_artifacts,
    "reclassify-day1-continuation-artifacts-v0631": _handle_reclassify_day1_continuation_artifacts_v0631,
    "forward-dry-run-day1-owner-report-scope-plan": _handle_forward_dry_run_day1_owner_report_scope_plan,
    "forward-dry-run-day1-owner-summary-report": _handle_forward_dry_run_day1_owner_summary_report,
    "forward-dry-run-day1-strategy-signal-explanation": _handle_forward_dry_run_day1_strategy_signal_explanation,
    "forward-dry-run-day1-virtual-order-fill-report": _handle_forward_dry_run_day1_virtual_order_fill_report,
    "forward-dry-run-day1-isolated-ledger-report": _handle_forward_dry_run_day1_isolated_ledger_report,
    "forward-dry-run-day1-data-reproducibility-appendix": _handle_forward_dry_run_day1_data_reproducibility_appendix,
    "forward-dry-run-day1-continuation-blocker-note": _handle_forward_dry_run_day1_continuation_blocker_note,
    "forward-dry-run-day1-owner-report-pack-summary": _handle_forward_dry_run_day1_owner_report_pack_summary,
    "audit-forward-dry-run-day1-owner-report-pack": _handle_audit_forward_dry_run_day1_owner_report_pack,
    "external-project-intake": _handle_external_project_intake,
    "equity-data-source-manifest": _handle_equity_data_source_manifest,
}


def _handle_owner_daily_status(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    print(_cli.owner_daily_status_output(as_of_date=args.as_of_date, output_format=args.format, paths=paths))

    return 0

def _handle_admission(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_admission(args.strategy_id, args.date)

    print(result)

    return 0

def _handle_acceptance_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.write_acceptance_materials(paths)

    print(result)

    return 0

def _handle_leaderboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_strategy_leaderboard(args.start_date, args.end_date, paths)

    print({"items": len(result["items"]), "report_path": result["report_path"]})

    return 0

def _handle_health(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    health = _cli.load_health(args.date)

    if health is None:

        health = _cli.run_daily(args.date)["health"]

    print(health)

    return 0

def _handle_export_summary(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.export_trading_summary(args.date)

    print(result)

    return 0


DISPATCH_HANDLERS_LATE: dict[str, Callable[..., int]] = {
    "owner-daily-status": _handle_owner_daily_status,
    "admission": _handle_admission,
    "acceptance-report": _handle_acceptance_report,
    "leaderboard": _handle_leaderboard,
    "health": _handle_health,
    "export-summary": _handle_export_summary,
}
