"""CLI dispatch handlers: versions commands (EARLY and LATE regions)."""

from __future__ import annotations

from collections.abc import Callable

import argparse

def _handle_run_a_share_v09_daily_platform(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v09_daily_platform(as_of_date=args.as_of_date, simulation_only=args.simulation_only, dry_run=args.dry_run, paths=paths)

    print(_cli._v09_platform_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v09_platform(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v09_platform(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "artifact_checks": result["artifact_checks"],

            "boundary": result["boundary"],

            "workflow": result["workflow"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_run_and_audit_a_share_v09_platform(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v09_daily_platform(as_of_date=args.as_of_date, simulation_only=args.simulation_only, dry_run=args.dry_run, paths=paths)

    audit_result = _cli.audit_a_share_v09_platform(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._v09_platform_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v100_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_v100_prep(as_of_date=args.as_of_date, paths=paths)

    print(_cli._v100_prep_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v100_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v100_prep(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "artifact_checks": result["artifact_checks"],

            "readiness_decision": result["readiness_decision"],

            "owner_readiness": result["owner_readiness"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v100_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_v100_prep(as_of_date=args.as_of_date, paths=paths)

    audit_result = _cli.audit_a_share_v100_prep(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._v100_prep_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v100_release(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_v100_release(as_of_date=args.as_of_date, paths=paths)

    print(_cli._v100_release_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v100_release(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v100_release(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "artifact_checks": result["artifact_checks"],

            "release_decision": result["release_decision"],

            "owner_readiness": result["owner_readiness"],

            "boundary": result["boundary"],

            "known_limitations_count": result["known_limitations_count"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v100_release(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_v100_release(as_of_date=args.as_of_date, paths=paths)

    audit_result = _cli.audit_a_share_v100_release(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._v100_release_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_run_a_share_v11_owner_ops_platform(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v11_owner_ops_platform(

        as_of_date=args.as_of_date,

        simulation_only=args.simulation_only,

        dry_run=args.dry_run,

        paths=paths,

    )

    print(_cli._v11_owner_ops_cli_payload(result) if result.get("overall_passed") is not False or "owner_command_center_generated" in result else result)

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v11_owner_ops_platform(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "artifact_checks": result["artifact_checks"],

            "claim_guard": result["claim_guard"],

            "owner_readiness": result["owner_readiness"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_run_and_audit_a_share_v11_owner_ops_platform(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print(

        {

            **(_cli._v11_owner_ops_cli_payload(build_result) if "owner_command_center_generated" in build_result else build_result),

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_run_a_share_v12_continuous_ops(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=args.simulation_only, dry_run=args.dry_run, paths=paths)

    print(_cli._v12_continuous_ops_cli_payload(result) if "local_schedule_policy_generated" in result else result)

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v12_continuous_ops(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v12_continuous_ops(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "schedule": result["schedule"], "claim_guard": result["claim_guard"], "owner_readiness": result["owner_readiness"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_run_and_audit_a_share_v12_continuous_ops(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v12_continuous_ops(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**(_cli._v12_continuous_ops_cli_payload(build_result) if "local_schedule_policy_generated" in build_result else build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v13_research_quality_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v13_research_quality_lab_cli_payload(result) if "research_quality_scorecard_generated" in result else result)

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v13_research_quality_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "owner_readiness": result["owner_readiness"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v13_research_quality_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**(_cli._v13_research_quality_lab_cli_payload(build_result) if "research_quality_scorecard_generated" in build_result else build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v14_portfolio_risk_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v14_portfolio_risk_lab_cli_payload(result) if "portfolio_risk_scorecard_generated" in result else result)

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v14_portfolio_risk_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "owner_readiness": result["owner_readiness"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v14_portfolio_risk_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**(_cli._v14_portfolio_risk_lab_cli_payload(build_result) if "portfolio_risk_scorecard_generated" in build_result else build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v15_market_regime_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v15_market_regime_lab_cli_payload(result) if "market_regime_classification_generated" in result else result)

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v15_market_regime_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "owner_readiness": result["owner_readiness"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v15_market_regime_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**(_cli._v15_market_regime_lab_cli_payload(build_result) if "market_regime_classification_generated" in build_result else build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v16_pit_backtest_market_rules(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v16_pit_backtest_market_rules_cli_payload(result) if "point_in_time_data_registry_generated" in result else result)

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v16_pit_backtest_market_rules(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v16_pit_backtest_market_rules(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**(_cli._v16_pit_backtest_market_rules_cli_payload(build_result) if "point_in_time_data_registry_generated" in build_result else build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v17_strategy_validation_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v17_strategy_validation_lab_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v17_strategy_validation_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v17_strategy_validation_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v17_strategy_validation_lab_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v18_research_db_feature_ml_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v18_research_db_feature_ml_lab_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v18_research_db_feature_ml_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v18_research_db_feature_ml_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v18_research_db_feature_ml_lab_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v19_ml_validation_model_risk(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v19_ml_validation_model_risk_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v19_ml_validation_model_risk(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v19_ml_validation_model_risk(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v19_ml_validation_model_risk_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v20_platform_closeout(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v20_platform_closeout_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v20_platform_closeout(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v20_platform_closeout(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v20_platform_closeout(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v20_platform_closeout(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v20_platform_closeout_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v20_plan_book_capability_map(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "plan_book_capability_map_generated": result.get("plan_book_capability_map_generated"), "plan_book_p0_trusted_research_status": result.get("plan_book_p0_trusted_research_status"), "plan_book_p5_rl_autonomous_simulation_status": result.get("plan_book_p5_rl_autonomous_simulation_status"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_v20_release_lineage(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "release_lineage_registry_generated": result.get("release_lineage_registry_generated"), "v19_baseline_verified": result.get("v19_baseline_verified"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_v20_safety_boundary_sweep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "safety_boundary_final_sweep_generated": result.get("safety_boundary_final_sweep_generated"), "safety_boundary_sweep_passed": result.get("safety_boundary_sweep_passed"), "live_trading_ready": result.get("live_trading_ready"), "buy_sell_signals_generated": result.get("buy_sell_signals_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_v20_platform_health_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "release_health_report_generated": result.get("release_health_report_generated"), "release_decision": result.get("release_decision"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_v20_owner_release_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "owner_release_dashboard_generated": result.get("owner_release_dashboard_generated"), "owner_readiness_state": result.get("owner_readiness_state"), "owner_operationally_acceptable": result.get("owner_operationally_acceptable"), "live_trading_ready": result.get("live_trading_ready"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_v20_known_limitations_and_next_phase(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v20_platform_closeout(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "plan_gap_known_limitations_generated": result.get("plan_gap_known_limitations_generated"), "known_limitations_count": result.get("known_limitations_count"), "recommended_next_version": result.get("recommended_next_version"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_v21_data_source_benchmark_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v21_data_source_benchmark_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v21_data_source_benchmark_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v21_data_source_benchmark_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v21_data_source_benchmark_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v22_ensemble_meta_strategy(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v22_ensemble_meta_strategy_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v22_ensemble_meta_strategy(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v22_ensemble_meta_strategy(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v22_ensemble_meta_strategy_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v23_operator_ux_journal(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v23_operator_ux_journal_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v23_operator_ux_journal(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v23_operator_ux_journal(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v23_operator_ux_journal_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v24_maintenance_quality(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(_cli._v24_maintenance_quality_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v24_maintenance_quality(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, paths=paths)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v24_maintenance_quality(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    audit_result = _cli.audit_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, paths=paths) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v24_maintenance_quality_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_v31_post_v3_verification(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        output_dir = _cli._resolve_v31_artifact_dir(args.output_dir, paths)

    except ValueError as exc:

        print({"error": str(exc)})

        return 2

    result = _cli.run_a_share_v31_post_v3_verification(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths, output_dir=output_dir)

    print(_cli._v31_post_v3_verification_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_v31_post_v3_verification(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        input_dir = _cli._resolve_v31_artifact_dir(args.input_dir or args.output_dir, paths)

    except ValueError as exc:

        print({"error": str(exc)})

        return 2

    result = _cli.audit_a_share_v31_post_v3_verification(as_of_date=args.as_of_date, paths=paths, input_dir=input_dir)

    print({"audit_id": result["audit_id"], "target_version": result["target_version"], "as_of_date": result["as_of_date"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "artifact_checks": result["artifact_checks"], "quality_checks": result["quality_checks"], "forbidden_checks": result["forbidden_checks"], "recommended_next_version": result["recommended_next_version"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_v31_post_v3_verification(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    try:

        output_dir = _cli._resolve_v31_artifact_dir(args.output_dir, paths)

        input_dir = _cli._resolve_v31_artifact_dir(args.input_dir, paths) or output_dir

    except ValueError as exc:

        print({"error": str(exc)})

        return 2

    build_result = _cli.run_a_share_v31_post_v3_verification(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths, output_dir=output_dir)

    audit_result = _cli.audit_a_share_v31_post_v3_verification(as_of_date=args.as_of_date, paths=paths, input_dir=input_dir) if build_result["overall_passed"] else {"overall_passed": False, "blocking_reasons": ["build_failed"], "warnings": []}

    print({**_cli._v31_post_v3_verification_cli_payload(build_result), "audit_overall_passed": audit_result["overall_passed"], "audit_blocking_reasons": audit_result["blocking_reasons"], "audit_warnings": len(audit_result["warnings"])})

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1


DISPATCH_HANDLERS_EARLY: dict[str, Callable[..., int]] = {
    "run-a-share-v09-daily-platform": _handle_run_a_share_v09_daily_platform,
    "audit-a-share-v09-platform": _handle_audit_a_share_v09_platform,
    "run-and-audit-a-share-v09-platform": _handle_run_and_audit_a_share_v09_platform,
    "build-a-share-v100-prep": _handle_build_a_share_v100_prep,
    "audit-a-share-v100-prep": _handle_audit_a_share_v100_prep,
    "build-and-audit-a-share-v100-prep": _handle_build_and_audit_a_share_v100_prep,
    "build-a-share-v100-release": _handle_build_a_share_v100_release,
    "audit-a-share-v100-release": _handle_audit_a_share_v100_release,
    "build-and-audit-a-share-v100-release": _handle_build_and_audit_a_share_v100_release,
    "run-a-share-v11-owner-ops-platform": _handle_run_a_share_v11_owner_ops_platform,
    "audit-a-share-v11-owner-ops-platform": _handle_audit_a_share_v11_owner_ops_platform,
    "run-and-audit-a-share-v11-owner-ops-platform": _handle_run_and_audit_a_share_v11_owner_ops_platform,
    "run-a-share-v12-continuous-ops": _handle_run_a_share_v12_continuous_ops,
    "audit-a-share-v12-continuous-ops": _handle_audit_a_share_v12_continuous_ops,
    "run-and-audit-a-share-v12-continuous-ops": _handle_run_and_audit_a_share_v12_continuous_ops,
    "build-a-share-v13-research-quality-lab": _handle_build_a_share_v13_research_quality_lab,
    "audit-a-share-v13-research-quality-lab": _handle_audit_a_share_v13_research_quality_lab,
    "build-and-audit-a-share-v13-research-quality-lab": _handle_build_and_audit_a_share_v13_research_quality_lab,
    "build-a-share-v14-portfolio-risk-lab": _handle_build_a_share_v14_portfolio_risk_lab,
    "audit-a-share-v14-portfolio-risk-lab": _handle_audit_a_share_v14_portfolio_risk_lab,
    "build-and-audit-a-share-v14-portfolio-risk-lab": _handle_build_and_audit_a_share_v14_portfolio_risk_lab,
    "build-a-share-v15-market-regime-lab": _handle_build_a_share_v15_market_regime_lab,
    "audit-a-share-v15-market-regime-lab": _handle_audit_a_share_v15_market_regime_lab,
    "build-and-audit-a-share-v15-market-regime-lab": _handle_build_and_audit_a_share_v15_market_regime_lab,
    "build-a-share-v16-pit-backtest-market-rules": _handle_build_a_share_v16_pit_backtest_market_rules,
    "audit-a-share-v16-pit-backtest-market-rules": _handle_audit_a_share_v16_pit_backtest_market_rules,
    "build-and-audit-a-share-v16-pit-backtest-market-rules": _handle_build_and_audit_a_share_v16_pit_backtest_market_rules,
    "build-a-share-v17-strategy-validation-lab": _handle_build_a_share_v17_strategy_validation_lab,
    "audit-a-share-v17-strategy-validation-lab": _handle_audit_a_share_v17_strategy_validation_lab,
    "build-and-audit-a-share-v17-strategy-validation-lab": _handle_build_and_audit_a_share_v17_strategy_validation_lab,
    "build-a-share-v18-research-db-feature-ml-lab": _handle_build_a_share_v18_research_db_feature_ml_lab,
    "audit-a-share-v18-research-db-feature-ml-lab": _handle_audit_a_share_v18_research_db_feature_ml_lab,
    "build-and-audit-a-share-v18-research-db-feature-ml-lab": _handle_build_and_audit_a_share_v18_research_db_feature_ml_lab,
    "build-a-share-v19-ml-validation-model-risk": _handle_build_a_share_v19_ml_validation_model_risk,
    "audit-a-share-v19-ml-validation-model-risk": _handle_audit_a_share_v19_ml_validation_model_risk,
    "build-and-audit-a-share-v19-ml-validation-model-risk": _handle_build_and_audit_a_share_v19_ml_validation_model_risk,
    "build-a-share-v20-platform-closeout": _handle_build_a_share_v20_platform_closeout,
    "audit-a-share-v20-platform-closeout": _handle_audit_a_share_v20_platform_closeout,
    "build-and-audit-a-share-v20-platform-closeout": _handle_build_and_audit_a_share_v20_platform_closeout,
    "build-a-share-v20-plan-book-capability-map": _handle_build_a_share_v20_plan_book_capability_map,
    "build-a-share-v20-release-lineage": _handle_build_a_share_v20_release_lineage,
    "build-a-share-v20-safety-boundary-sweep": _handle_build_a_share_v20_safety_boundary_sweep,
    "build-a-share-v20-platform-health-report": _handle_build_a_share_v20_platform_health_report,
    "build-a-share-v20-owner-release-dashboard": _handle_build_a_share_v20_owner_release_dashboard,
    "build-a-share-v20-known-limitations-and-next-phase": _handle_build_a_share_v20_known_limitations_and_next_phase,
    "build-a-share-v21-data-source-benchmark-hardening": _handle_build_a_share_v21_data_source_benchmark_hardening,
    "audit-a-share-v21-data-source-benchmark-hardening": _handle_audit_a_share_v21_data_source_benchmark_hardening,
    "build-and-audit-a-share-v21-data-source-benchmark-hardening": _handle_build_and_audit_a_share_v21_data_source_benchmark_hardening,
    "build-a-share-v22-ensemble-meta-strategy": _handle_build_a_share_v22_ensemble_meta_strategy,
    "audit-a-share-v22-ensemble-meta-strategy": _handle_audit_a_share_v22_ensemble_meta_strategy,
    "build-and-audit-a-share-v22-ensemble-meta-strategy": _handle_build_and_audit_a_share_v22_ensemble_meta_strategy,
    "build-a-share-v23-operator-ux-journal": _handle_build_a_share_v23_operator_ux_journal,
    "audit-a-share-v23-operator-ux-journal": _handle_audit_a_share_v23_operator_ux_journal,
    "build-and-audit-a-share-v23-operator-ux-journal": _handle_build_and_audit_a_share_v23_operator_ux_journal,
    "build-a-share-v24-maintenance-quality": _handle_build_a_share_v24_maintenance_quality,
    "audit-a-share-v24-maintenance-quality": _handle_audit_a_share_v24_maintenance_quality,
    "build-and-audit-a-share-v24-maintenance-quality": _handle_build_and_audit_a_share_v24_maintenance_quality,
    "build-a-share-v31-post-v3-verification": _handle_build_a_share_v31_post_v3_verification,
    "audit-a-share-v31-post-v3-verification": _handle_audit_a_share_v31_post_v3_verification,
    "build-and-audit-a-share-v31-post-v3-verification": _handle_build_and_audit_a_share_v31_post_v3_verification,
}


def _handle_validate_a_share_owner_v090_rc_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_v090_rc_inputs(as_of_date=args.as_of_date, allow_date_mismatch=args.allow_date_mismatch, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "v0821_closeout_review_audit_passed": result["v0821_closeout_review_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "v090_rc_readiness_source_decision": result["v090_rc_readiness_source_decision"],

            "owner_operationally_acceptable": result["owner_operationally_acceptable"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_v090_rc(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_v090_rc(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        skip_full_pytest=args.skip_full_pytest,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "known_owner_readiness_state": result.get("known_owner_readiness_state"),

            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),

            "previous_readiness_score": result.get("previous_readiness_score"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "score_gap": result.get("score_gap"),

            "full_pytest_run": result.get("full_pytest_run"),

            "full_pytest_passed": result.get("full_pytest_passed"),

            "full_pytest_passed_count": result.get("full_pytest_passed_count"),

            "full_pytest_failed_count": result.get("full_pytest_failed_count"),

            "audit_sweep_passed": result.get("audit_sweep_passed"),

            "boundary_sweep_passed": result.get("boundary_sweep_passed"),

            "source_trace_sweep_passed": result.get("source_trace_sweep_passed"),

            "documentation_freeze_passed": result.get("documentation_freeze_passed"),

            "v090_release_candidate_decision": result.get("v090_release_candidate_decision"),

            "recommended_next_version": result.get("recommended_next_version"),

            "v090_rc_report": result.get("v090_rc_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_v090_rc(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_v090_rc(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "regression_checks": result["regression_checks"],

            "known_blocked_state_checks": result["known_blocked_state_checks"],

            "boundary": result["boundary"],

            "release_candidate_decision": result["release_candidate_decision"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_v090_rc(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_v090_rc(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        skip_full_pytest=args.skip_full_pytest,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_v090_rc(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "regression_checks": audit_result["regression_checks"],

            "known_blocked_state_checks": audit_result["known_blocked_state_checks"],

            "release_candidate_decision": audit_result["release_candidate_decision"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1


DISPATCH_HANDLERS_LATE: dict[str, Callable[..., int]] = {
    "validate-a-share-owner-v090-rc-inputs": _handle_validate_a_share_owner_v090_rc_inputs,
    "build-a-share-owner-v090-rc": _handle_build_a_share_owner_v090_rc,
    "audit-a-share-owner-v090-rc": _handle_audit_a_share_owner_v090_rc,
    "build-and-audit-a-share-owner-v090-rc": _handle_build_and_audit_a_share_owner_v090_rc,
}
