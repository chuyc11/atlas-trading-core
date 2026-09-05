"""CLI dispatch handlers: a_share commands (EARLY and LATE regions)."""

from __future__ import annotations

from collections.abc import Callable

import argparse

def _handle_ashare_execution_gap_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_ashare_execution_gap_plan(mvp_gaps_path=args.mvp_gaps, day1_blockers_path=args.day1_blockers, next_work_path=args.next_work, paths=paths)

    print({"plan_id": result["plan_id"], "baseline_day1_blocker_count": result["baseline_day1_blocker_count"], "target_day1_blocker_count": result["target_day1_blocker_count"], "work_items": len(result["work_items"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_ashare_trading_calendar_audit(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    contract = _cli.build_trading_calendar_contract(paths=paths)

    result = _cli.audit_trading_calendar(paths=paths)

    print({"contract_path": contract["json_path"], "audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_ashare_price_status_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_price_status_contract(paths=paths)

    print({"contract_id": result["contract_id"], "statuses": len(result["supported_statuses"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_ashare_lot_and_position_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_lot_position_contract(paths=paths)

    print({"contract_id": result["contract_id"], "default_board_lot": result["default_board_lot"], "t_plus_1_available_after_settlement": result["t_plus_1_available_after_settlement"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_ashare_execution_cost_contract(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_execution_cost_contract(paths=paths)

    print({"contract_id": result["contract_id"], "commission_bps": result["commission_bps"], "slippage_bps": result["slippage_bps"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_audit_ashare_execution_rules(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_ashare_execution_rules(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "summary": result["summary"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_equity_master(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_equity_master(paths=paths)

    print({"artifact_id": result["artifact_id"], "symbols": result["symbols"], "exchanges": result["exchanges"], "parquet_path": result["parquet_path"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["symbols"] > 0 else 1

def _handle_build_a_share_trading_calendar(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_trading_calendar(paths=paths)

    print({"artifact_id": result["artifact_id"], "trading_days": result["trading_days"], "min_date": result["min_date"], "max_date": result["max_date"], "parquet_path": result["parquet_path"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["trading_days"] > 0 else 1

def _handle_ingest_a_share_daily_prices(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.ingest_a_share_daily_prices(paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "min_date": result["min_date"], "max_date": result["max_date"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["symbol_count"] > 0 and result["non_positive_prices"] == 0 else 1

def _handle_ingest_a_share_adjusted_prices(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.ingest_a_share_adjusted_prices(paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "adjustment_types": result["adjustment_types"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["symbol_count"] > 0 else 1

def _handle_ingest_a_share_daily_basic(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.ingest_a_share_daily_basic(paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "partial_fields": result["partial_fields"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["symbol_count"] > 0 else 1

def _handle_ingest_a_share_industry_classification(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.ingest_a_share_industry_classification(paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "industry_standard": result["industry_standard"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["symbol_count"] > 0 else 1

def _handle_ingest_a_share_basic_financials(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.ingest_a_share_basic_financials(paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "report_date_coverage": result["report_date_coverage"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["symbol_count"] > 0 else 1

def _handle_audit_a_share_data_coverage(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_data_coverage(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "coverage": result["coverage"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_data_schema(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_data_schema(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_data_foundation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_data_foundation(paths=paths)

    print({"foundation_id": result["foundation_id"], "overall_passed": result["overall_passed"], "coverage_overall_passed": result["coverage_audit"]["overall_passed"], "schema_overall_passed": result["schema_audit"]["overall_passed"], "coverage": result["coverage_audit"]["coverage"]})

    return 0 if result["overall_passed"] else 1

def _handle_a_share_historical_backfill_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_historical_backfill_plan(target_start_date=args.target_start_date, minimum_start_date=args.minimum_start_date, end_date=args.end_date, paths=paths)

    print({"plan_id": result["plan_id"], "target_start_date": result["target_start_date"], "minimum_start_date": result["minimum_start_date"], "end_date": result["end_date"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_diagnose_a_share_historical_backfill_coverage(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.diagnose_a_share_historical_backfill_coverage(paths=paths)

    print({"diagnostic_id": result["diagnostic_id"], "overall_diagnosis_passed": result["overall_diagnosis_passed"], "confirmed_root_causes": result["confirmed_root_causes"], "historical_price_symbols": result["historical_price_symbols"], "backfill_input_symbols": result["backfill_input_symbols"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0

def _handle_build_a_share_historical_backfill_symbol_queue(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_historical_backfill_symbol_queue(target_start_date=args.target_start_date, end_date=args.end_date, paths=paths)

    print({"queue_id": result["queue_id"], "queue_total_symbols": result["queue_total_symbols"], "eligible_price_backfill_symbols": result["eligible_price_backfill_symbols"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["queue_total_symbols"] > 0 else 1

def _handle_backfill_a_share_daily_price_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.backfill_a_share_daily_price_history(start_date=args.start_date, end_date=args.end_date, max_symbols=args.max_symbols, provider_priority=args.provider_priority, rate_limit_per_minute=args.rate_limit_per_minute, retry=args.retry, paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "date_count": result["date_count"], "min_date": result["min_date"], "max_date": result["max_date"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["rows"] > 0 else 1

def _handle_backfill_a_share_adjusted_price_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.backfill_a_share_adjusted_price_history(start_date=args.start_date, end_date=args.end_date, paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "adjustment_types": result["adjustment_types"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["rows"] > 0 else 1

def _handle_backfill_a_share_daily_basic_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.backfill_a_share_daily_basic_history(start_date=args.start_date, end_date=args.end_date, paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["rows"] > 0 else 1

def _handle_backfill_a_share_financial_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.backfill_a_share_financial_history(start_date=args.start_date, end_date=args.end_date, paths=paths)

    print({"manifest_id": result["manifest_id"], "rows": result["rows"], "symbol_count": result["symbol_count"], "report_date_coverage": result["report_date_coverage"], "parquet_path": result["parquet_path"], "manifest_path": result["manifest_path"]})

    return 0 if result["rows"] > 0 else 1

def _handle_audit_a_share_historical_panel_coverage(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_historical_panel_coverage(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "coverage": result["coverage"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_feature_readiness(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_feature_readiness(paths=paths)

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "readiness": result["readiness"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_backfill_a_share_historical_panels(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.backfill_a_share_historical_panels(target_start_date=args.target_start_date, minimum_start_date=args.minimum_start_date, end_date=args.end_date, max_symbols=args.max_symbols, paths=paths)

    print({"backfill_id": result["backfill_id"], "overall_passed": result["overall_passed"], "coverage_overall_passed": result["coverage_audit"]["overall_passed"], "feature_readiness_overall_passed": result["feature_readiness_audit"]["overall_passed"], "coverage": result["coverage_audit"]["coverage"]})

    return 0 if result["overall_passed"] else 1

def _handle_backfill_a_share_historical_panels_full_market(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.backfill_a_share_historical_panels_full_market(

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

def _handle_build_a_share_tradable_universe(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_tradable_universe(config=_cli._tradable_universe_config(args), paths=paths)

    print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "counts": result["counts"], "warnings": len(result["warnings"]), "tradable_universe_path": result["artifacts"]["tradable_universe_json"], "manifest_path": result["artifacts"]["manifest"]})

    return 0 if result["counts"]["strict_tradable_count"] > 0 else 1

def _handle_audit_a_share_tradable_universe(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_tradable_universe(

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

def _handle_build_and_audit_a_share_tradable_universe(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_tradable_universe(config=_cli._tradable_universe_config(args), paths=paths)

    audit_result = _cli.audit_a_share_tradable_universe(

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

def _handle_build_a_share_multi_horizon_features(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_multi_horizon_features(

        as_of_date=args.as_of_date,

        allow_latest_tradable_universe=args.allow_latest_tradable_universe,

        paths=paths,

    )

    print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "strict_tradable_count": result["strict_tradable_count"], "feature_groups": result["feature_groups"], "warnings": len(result["warnings"]), "feature_manifest_path": result["feature_manifest_path"]})

    return 0 if result["strict_tradable_count"] > 0 else 1

def _handle_audit_a_share_multi_horizon_features(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_multi_horizon_features(

        as_of_date=args.as_of_date,

        allow_latest_tradable_universe=args.allow_latest_tradable_universe,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "coverage": result["coverage"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_multi_horizon_features(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_multi_horizon_features(

        as_of_date=args.as_of_date,

        allow_latest_tradable_universe=args.allow_latest_tradable_universe,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_multi_horizon_features(

        as_of_date=args.as_of_date,

        allow_latest_tradable_universe=args.allow_latest_tradable_universe,

        paths=paths,

    )

    print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "coverage": audit_result["coverage"], "recommended_next_version": audit_result["recommended_next_version"]})

    return 0 if audit_result["overall_passed"] else 1

def _handle_build_a_share_scores(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_scores(

        as_of_date=args.as_of_date,

        allow_latest_feature_date=args.allow_latest_feature_date,

        paths=paths,

    )

    print({"builder_id": result["builder_id"], "as_of_date": result["as_of_date"], "strict_tradable_count": result["strict_tradable_count"], "scored_symbols": result["scored_symbols"], "warnings": len(result["warnings"]), "score_manifest_path": result["artifacts"]["score_manifest"]})

    return 0 if result["scored_symbols"] == result["strict_tradable_count"] else 1

def _handle_audit_a_share_scores(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_scores(

        as_of_date=args.as_of_date,

        allow_latest_feature_date=args.allow_latest_feature_date,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "score_ranges": result["score_ranges"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_scores(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_scores(

        as_of_date=args.as_of_date,

        allow_latest_feature_date=args.allow_latest_feature_date,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_scores(

        as_of_date=args.as_of_date,

        allow_latest_feature_date=args.allow_latest_feature_date,

        paths=paths,

    )

    print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "score_ranges": audit_result["score_ranges"], "recommended_next_version": audit_result["recommended_next_version"]})

    return 0 if audit_result["overall_passed"] else 1

def _handle_generate_a_share_candidates(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.generate_a_share_candidates(

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

def _handle_audit_a_share_candidates(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_candidates(

        as_of_date=args.as_of_date,

        allow_latest_score_date=args.allow_latest_score_date,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_generate_and_audit_a_share_candidates(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.generate_a_share_candidates(

        as_of_date=args.as_of_date,

        long_count=args.long_count,

        mid_count=args.mid_count,

        short_count=args.short_count,

        extended_count=args.extended_count,

        allow_latest_score_date=args.allow_latest_score_date,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_candidates(

        as_of_date=args.as_of_date,

        allow_latest_score_date=args.allow_latest_score_date,

        paths=paths,

    )

    print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "recommended_next_version": audit_result["recommended_next_version"]})

    return 0 if audit_result["overall_passed"] else 1

def _handle_build_a_share_virtual_portfolios(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_virtual_portfolios(

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

def _handle_audit_a_share_virtual_portfolios(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_virtual_portfolios(

        as_of_date=args.as_of_date,

        allow_latest_candidate_date=args.allow_latest_candidate_date,

        paths=paths,

    )

    print({"audit_id": result["audit_id"], "overall_passed": result["overall_passed"], "blocking_reasons": result["blocking_reasons"], "warnings": len(result["warnings"]), "counts": result["counts"], "weight_checks": result["weight_checks"], "recommended_next_version": result["recommended_next_version"], "json_path": result["json_path"], "report_path": result["report_path"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_virtual_portfolios(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_virtual_portfolios(

        as_of_date=args.as_of_date,

        long_holdings=args.long_holdings,

        mid_holdings=args.mid_holdings,

        short_holdings=args.short_holdings,

        allow_latest_candidate_date=args.allow_latest_candidate_date,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_virtual_portfolios(

        as_of_date=args.as_of_date,

        allow_latest_candidate_date=args.allow_latest_candidate_date,

        paths=paths,

    )

    print({"builder_id": build_result["builder_id"], "audit_id": audit_result["audit_id"], "overall_passed": audit_result["overall_passed"], "blocking_reasons": audit_result["blocking_reasons"], "counts": audit_result["counts"], "weight_checks": audit_result["weight_checks"], "recommended_next_version": audit_result["recommended_next_version"]})

    return 0 if audit_result["overall_passed"] else 1

def _handle_build_a_share_daily_stock_selection_briefing(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_daily_stock_selection_briefing(

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

def _handle_audit_a_share_daily_stock_selection_briefing(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_daily_stock_selection_briefing(

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

def _handle_build_and_audit_a_share_daily_stock_selection_briefing(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_daily_stock_selection_briefing(

        as_of_date=args.as_of_date,

        allow_latest_artifact_date=args.allow_latest_artifact_date,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_daily_stock_selection_briefing(

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

def _handle_build_a_share_virtual_portfolio_tracking(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_virtual_portfolio_tracking(

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

def _handle_audit_a_share_virtual_portfolio_tracking(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_virtual_portfolio_tracking(

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

def _handle_build_and_audit_a_share_virtual_portfolio_tracking(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_virtual_portfolio_tracking(

        as_of_date=args.as_of_date,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_virtual_portfolio_tracking(

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

def _handle_preflight_a_share_daily_workflow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    allow_build_timestamp_drift = False if args.fail_on_build_timestamp_drift else args.allow_build_timestamp_drift

    result = _cli.preflight_a_share_daily_workflow(

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

def _handle_run_a_share_daily_research_workflow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    allow_build_timestamp_drift = False if args.fail_on_build_timestamp_drift else args.allow_build_timestamp_drift

    result = _cli.run_a_share_daily_research_workflow(

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

def _handle_audit_a_share_daily_research_workflow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_daily_research_workflow(

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

def _handle_run_and_audit_a_share_daily_research_workflow(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    allow_build_timestamp_drift = False if args.fail_on_build_timestamp_drift else args.allow_build_timestamp_drift

    run_result = _cli.run_a_share_daily_research_workflow(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_latest_artifact_date=args.allow_latest_artifact_date,

        allow_public_data_refresh=args.allow_public_data_refresh,

        allow_build_timestamp_drift=allow_build_timestamp_drift,

        fail_on_build_timestamp_drift=args.fail_on_build_timestamp_drift,

        allow_version_shim_warning=args.allow_version_shim_warning,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_daily_research_workflow(

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

def _handle_build_a_share_benchmark_comparison(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_benchmark_comparison(

        as_of_date=args.as_of_date,

        lookback_trading_days=args.lookback_trading_days,

        minimum_required_trading_days=args.minimum_required_trading_days,

        allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,

        fail_on_placeholder_benchmarks=_cli._benchmark_fail_on_placeholder(args),

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

def _handle_audit_a_share_benchmark_comparison(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_benchmark_comparison(

        as_of_date=args.as_of_date,

        allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,

        fail_on_placeholder_benchmarks=_cli._benchmark_fail_on_placeholder(args),

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

def _handle_build_and_audit_a_share_benchmark_comparison(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_benchmark_comparison(

        as_of_date=args.as_of_date,

        lookback_trading_days=args.lookback_trading_days,

        minimum_required_trading_days=args.minimum_required_trading_days,

        allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,

        fail_on_placeholder_benchmarks=_cli._benchmark_fail_on_placeholder(args),

        paths=paths,

    )

    audit_result = _cli.audit_a_share_benchmark_comparison(

        as_of_date=args.as_of_date,

        allow_placeholder_benchmarks=args.allow_placeholder_benchmarks,

        fail_on_placeholder_benchmarks=_cli._benchmark_fail_on_placeholder(args),

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

def _handle_build_a_share_multi_day_performance(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_multi_day_performance(

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

def _handle_audit_a_share_multi_day_performance(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_multi_day_performance(

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

def _handle_build_and_audit_a_share_multi_day_performance(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_multi_day_performance(

        as_of_date=args.as_of_date,

        tracking_start_date=args.tracking_start_date,

        mode=args.mode,

        minimum_required_observations=args.minimum_required_observations,

        rolling_window_days=args.rolling_window_days,

        allow_rebuild=args.allow_rebuild,

        allow_historical_reconstruction=args.allow_historical_reconstruction,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_multi_day_performance(

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

def _handle_build_a_share_performance_attribution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_performance_attribution(

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

def _handle_audit_a_share_performance_attribution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_performance_attribution(

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

def _handle_build_and_audit_a_share_performance_attribution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_performance_attribution(

        as_of_date=args.as_of_date,

        mode=args.mode,

        minimum_required_observations=args.minimum_required_observations,

        allow_limited_history=args.allow_limited_history,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_performance_attribution(

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

def _handle_refresh_a_share_data_freshness(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.refresh_a_share_data_freshness(target_as_of_date=args.target_as_of_date, dry_run=args.dry_run, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "requested_target_as_of_date": result["requested_target_as_of_date"],

            "resolved_actual_data_date": result["resolved_actual_data_date"],

            "date_resolution_reason": result["date_resolution_reason"],

            "dry_run": result["dry_run"],

            "provider_status": result["provider_status"],

            "coverage_ratio": result["coverage_ratio"],

            "coverage_passed": result["coverage_passed"],

            "data_refresh_executed": result["data_refresh_executed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_rerun_a_share_research_pipeline_from_refreshed_data(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.rerun_a_share_research_pipeline_from_refreshed_data(as_of_date=args.as_of_date, dry_run=args.dry_run, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "source_data_date": result["source_data_date"],

            "dry_run": result["dry_run"],

            "overall_passed": result["overall_passed"],

            "source_data_freshness_validation_passed": result["source_data_freshness_validation_passed"],

            "pipeline_execution_passed": result["pipeline_execution_passed"],

            "research_output_validation_passed": result["research_output_validation_passed"],

            "candidate_output_generated": result["candidate_output_generated"],

            "score_output_generated": result["score_output_generated"],

            "virtual_portfolio_output_generated": result["virtual_portfolio_output_generated"],

            "research_briefing_generated": result["research_briefing_generated"],

            "protected_order_trade_account_paths_untouched": result["protected_order_trade_account_paths_untouched"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_research_evidence_accumulation_and_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_research_evidence_accumulation_and_prep(as_of_date=args.as_of_date, paths=paths)

    print(_cli._research_evidence_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_research_evidence_accumulation_and_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_research_evidence_accumulation_and_prep(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "phase_a_checks": result["phase_a_checks"],

            "phase_b_checks": result["phase_b_checks"],

            "gate_safety": result["gate_safety"],

            "trading_boundary": result["trading_boundary"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_research_evidence_accumulation_and_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_research_evidence_accumulation_and_prep(as_of_date=args.as_of_date, paths=paths)

    audit_result = _cli.audit_a_share_research_evidence_accumulation_and_prep(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._research_evidence_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_final_not_ready_closeout(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_final_not_ready_closeout(as_of_date=args.as_of_date, paths=paths)

    print(_cli._final_closeout_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_final_not_ready_closeout(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_final_not_ready_closeout(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "target_version": result["target_version"],

            "as_of_date": result["as_of_date"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": len(result["warnings"]),

            "source_checks": result["source_checks"],

            "branch_checks": result["branch_checks"],

            "closeout_checks": result["closeout_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_final_not_ready_closeout(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_final_not_ready_closeout(as_of_date=args.as_of_date, paths=paths)

    audit_result = _cli.audit_a_share_final_not_ready_closeout(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._final_closeout_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_historical_evidence_backfill_and_refresh_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_historical_evidence_backfill_and_refresh_plan(

        as_of_date=args.as_of_date,

        lookback_start=args.lookback_start,

        target_evidence_days=args.target_evidence_days,

        paths=paths,

    )

    print(_cli._historical_evidence_backfill_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_historical_evidence_backfill_and_refresh_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_historical_evidence_backfill_and_refresh_plan(as_of_date=args.as_of_date, paths=paths)

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

            "refresh_checks": result["refresh_checks"],

            "readiness_checks": result["readiness_checks"],

            "go_no_go_after_backfill_decision": result["go_no_go_after_backfill_decision"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_historical_evidence_backfill_and_refresh_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_historical_evidence_backfill_and_refresh_plan(

        as_of_date=args.as_of_date,

        lookback_start=args.lookback_start,

        target_evidence_days=args.target_evidence_days,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_historical_evidence_backfill_and_refresh_plan(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._historical_evidence_backfill_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_experiment_registry(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_experiment_registry(as_of_date=args.as_of_date, paths=paths)

    print(result)

    return 0 if result["overall_passed"] else 1

def _handle_run_a_share_automated_experiments(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_automated_experiments(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(result)

    return 0 if result["overall_passed"] else 1

def _handle_run_a_share_rl_simulated_strategy_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_rl_simulated_strategy_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print(result)

    return 0 if result["overall_passed"] else 1

def _handle_evaluate_a_share_simulated_strategy_promotion(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.evaluate_a_share_simulated_strategy_promotion(as_of_date=args.as_of_date, paths=paths)

    print(result)

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_benchmark_claim_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_benchmark_claim_hardening(

        as_of_date=args.as_of_date,

        allow_public_benchmark_refresh=args.allow_public_benchmark_refresh,

        paths=paths,

    )

    print(_cli._benchmark_claim_hardening_cli_payload(result))

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_benchmark_claim_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_benchmark_claim_hardening(as_of_date=args.as_of_date, paths=paths)

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

            "benchmark_status": result["benchmark_status"],

            "owner_readiness": result["owner_readiness"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_benchmark_claim_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_benchmark_claim_hardening(

        as_of_date=args.as_of_date,

        allow_public_benchmark_refresh=args.allow_public_benchmark_refresh,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_benchmark_claim_hardening(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            **_cli._benchmark_claim_hardening_cli_payload(build_result),

            "audit_id": audit_result["audit_id"],

            "audit_overall_passed": audit_result["overall_passed"],

            "audit_blocking_reasons": audit_result["blocking_reasons"],

            "audit_warnings": len(audit_result["warnings"]),

        }

    )

    return 0 if build_result["overall_passed"] and audit_result["overall_passed"] else 1

def _handle_build_a_share_owner_command_center(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "owner_command_center_generated": result.get("owner_command_center_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_simulated_account_reconciliation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "simulated_account_reconciled": result.get("simulated_account_reconciled"), "paper_ledger_invariant_passed": result.get("paper_ledger_invariant_passed"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_strategy_lifecycle_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "strategy_registry_expanded": result.get("strategy_registry_expanded"), "shadow_canary_lifecycle_generated": result.get("shadow_canary_lifecycle_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_monitoring_remediation_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v11_owner_ops_platform(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "monitoring_alerts_generated": result.get("monitoring_alerts_generated"), "remediation_checklist_generated": result.get("remediation_checklist_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_plan_a_share_local_post_close_schedule(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=True, dry_run=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "local_schedule_policy_generated": result.get("local_schedule_policy_generated"), "trading_day_run_plan_generated": result.get("trading_day_run_plan_generated"), "scheduler_template_plan_generated": result.get("scheduler_template_plan_generated"), "silent_scheduler_installation": result.get("silent_scheduler_installation"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_local_scheduler_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "local_schedule_policy_generated": result.get("local_schedule_policy_generated"), "scheduler_template_plan_generated": result.get("scheduler_template_plan_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_operator_runbook(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "operator_runbook_generated": result.get("operator_runbook_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_continuous_simulation_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "simulated_account_history_generated": result.get("simulated_account_history_generated"), "simulated_account_continuity_passed": result.get("simulated_account_continuity_passed"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_incident_remediation_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "incident_register_generated": result.get("incident_register_generated"), "retry_recovery_plan_generated": result.get("retry_recovery_plan_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_artifact_index_and_health_report(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v12_continuous_ops(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "artifact_index_generated": result.get("artifact_index_generated"), "artifact_health_passed": result.get("artifact_health_passed"), "platform_health_report_generated": result.get("platform_health_report_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_research_quality_scorecard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "research_quality_scorecard_generated": result.get("research_quality_scorecard_generated"), "data_leakage_guard_passed": result.get("data_leakage_guard_passed"), "lookahead_bias_check_passed": result.get("lookahead_bias_check_passed"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_strategy_lab_quality_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "strategy_lab_registry_expanded": result.get("strategy_lab_registry_expanded"), "strategy_card_register_generated": result.get("strategy_card_register_generated"), "shadow_canary_quality_gate_result_generated": result.get("shadow_canary_quality_gate_result_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_llm_proposal_quality_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "llm_proposal_quality_result_generated": result.get("llm_proposal_quality_result_generated"), "llm_proposals_are_trade_instructions": result.get("llm_proposals_are_trade_instructions"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_rl_policy_quality_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "rl_policy_quality_result_generated": result.get("rl_policy_quality_result_generated"), "rl_actions_are_real_account_actions": result.get("rl_actions_are_real_account_actions"), "rl_actions_are_real_orders": result.get("rl_actions_are_real_orders"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_strategy_lifecycle_quality_gates(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "strategy_promotion_hard_gate_generated": result.get("strategy_promotion_hard_gate_generated"), "strategy_rejection_hard_gate_generated": result.get("strategy_rejection_hard_gate_generated"), "strategy_rollback_gate_generated": result.get("strategy_rollback_gate_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_robustness_and_overfit_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v13_research_quality_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "robustness_sensitivity_stress_result_generated": result.get("robustness_sensitivity_stress_result_generated"), "overfitting_false_discovery_result_generated": result.get("overfitting_false_discovery_result_generated"), "overfitting_risk_classified": result.get("overfitting_risk_classified"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_portfolio_risk_scorecard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "portfolio_risk_scorecard_generated": result.get("portfolio_risk_scorecard_generated"), "exposure_concentration_result_generated": result.get("exposure_concentration_result_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_capacity_liquidity_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "capacity_liquidity_result_generated": result.get("capacity_liquidity_result_generated"), "capacity_estimate_is_simulated": result.get("capacity_estimate_is_simulated"), "liquidity_estimate_is_simulated": result.get("liquidity_estimate_is_simulated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_simulated_allocation_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "simulated_allocation_result_generated": result.get("simulated_allocation_result_generated"), "allocation_is_simulated": result.get("allocation_is_simulated"), "real_allocation_instruction_generated": result.get("real_allocation_instruction_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_simulated_rebalance_plan(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "simulated_rebalance_plan_generated": result.get("simulated_rebalance_plan_generated"), "rebalance_plan_is_simulated": result.get("rebalance_plan_is_simulated"), "real_rebalance_instruction_generated": result.get("real_rebalance_instruction_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_portfolio_stress_test(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "stress_scenario_result_generated": result.get("stress_scenario_result_generated"), "stress_result_is_simulated": result.get("stress_result_is_simulated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_risk_guardrail_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v14_portfolio_risk_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "risk_limit_guardrail_result_generated": result.get("risk_limit_guardrail_result_generated"), "protected_path_sweep_passed": result.get("protected_path_sweep_passed"), "safety_boundary_sweep_passed": result.get("safety_boundary_sweep_passed"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_market_regime_classification(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "market_regime_classification_generated": result.get("market_regime_classification_generated"), "market_regime_fabricated": result.get("market_regime_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_regime_factor_candidate_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "regime_factor_quality_overlay_generated": result.get("regime_factor_quality_overlay_generated"), "regime_candidate_quality_overlay_generated": result.get("regime_candidate_quality_overlay_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_regime_strategy_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "regime_strategy_quality_result_generated": result.get("regime_strategy_quality_result_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_adaptive_research_queue(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "adaptive_research_queue_generated": result.get("adaptive_research_queue_generated"), "adaptive_queue_generates_trade_instruction": result.get("adaptive_queue_generates_trade_instruction"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_regime_llm_rl_governance(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "llm_regime_governance_generated": result.get("llm_regime_governance_generated"), "rl_regime_governance_generated": result.get("rl_regime_governance_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_regime_portfolio_overlay(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v15_market_regime_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "regime_portfolio_overlay_generated": result.get("regime_portfolio_overlay_generated"), "regime_overlay_generates_real_allocation": result.get("regime_overlay_generates_real_allocation"), "regime_overlay_generates_real_rebalance": result.get("regime_overlay_generates_real_rebalance"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_point_in_time_data_registry(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "point_in_time_data_registry_generated": result.get("point_in_time_data_registry_generated"), "dataset_feature_label_version_registry_generated": result.get("dataset_feature_label_version_registry_generated"), "point_in_time_visibility_fabricated": result.get("point_in_time_visibility_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_event_driven_backtest_replay(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "event_driven_replay_result_generated": result.get("event_driven_replay_result_generated"), "backtest_results_fabricated": result.get("backtest_results_fabricated"), "simulated_fills_fabricated": result.get("simulated_fills_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_market_rule_simulation_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "a_share_market_rule_registry_generated": result.get("a_share_market_rule_registry_generated"), "t_plus_one_rule_checked": result.get("t_plus_one_rule_checked"), "price_limit_rule_checked": result.get("price_limit_rule_checked"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_virtual_broker_rule_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "virtual_broker_rule_hardening_result_generated": result.get("virtual_broker_rule_hardening_result_generated"), "virtual_broker_rule_audit_passed": result.get("virtual_broker_rule_audit_passed"), "paper_ledger_replay_passed": result.get("paper_ledger_replay_passed"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_benchmark_index_source_hardening(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "benchmark_index_source_result_generated": result.get("benchmark_index_source_result_generated"), "benchmark_index_data_fabricated": result.get("benchmark_index_data_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_backtest_trust_scorecard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v16_pit_backtest_market_rules(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "backtest_trust_scorecard_generated": result.get("backtest_trust_scorecard_generated"), "backtest_trust_decision": result.get("backtest_trust_decision"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_factor_validation_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "factor_validation_result_generated": result.get("factor_validation_result_generated"), "factor_results_fabricated": result.get("factor_results_fabricated"), "ic_results_fabricated": result.get("ic_results_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_candidate_ranking_validation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "candidate_ranking_validation_result_generated": result.get("candidate_ranking_validation_result_generated"), "candidate_validation_generates_buy_sell_signal": result.get("candidate_validation_generates_buy_sell_signal"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_strategy_oos_walkforward_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "walkforward_oos_evaluation_result_generated": result.get("walkforward_oos_evaluation_result_generated"), "oos_results_fabricated": result.get("oos_results_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_robustness_statistical_validation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "robustness_sensitivity_validation_result_generated": result.get("robustness_sensitivity_validation_result_generated"), "statistical_false_discovery_result_generated": result.get("statistical_false_discovery_result_generated"), "statistical_significance_fabricated": result.get("statistical_significance_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_strategy_admission_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "strategy_admission_decision_result_generated": result.get("strategy_admission_decision_result_generated"), "strategy_admission_generates_real_trade": result.get("strategy_admission_generates_real_trade"), "strategy_real_trading_active_state_present": result.get("strategy_real_trading_active_state_present"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_experiment_validation_registry(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v17_strategy_validation_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "experiment_validation_registry_generated": result.get("experiment_validation_registry_generated"), "llm_rl_validation_result_generated": result.get("llm_rl_validation_result_generated"), "llm_rl_validation_generates_trade_instruction": result.get("llm_rl_validation_generates_trade_instruction"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_research_database_index(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "research_database_registry_generated": result.get("research_database_registry_generated"), "storage_snapshot_reproducibility_result_generated": result.get("storage_snapshot_reproducibility_result_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_feature_store(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "feature_store_result_generated": result.get("feature_store_result_generated"), "feature_store_pit_validated": result.get("feature_store_pit_validated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_label_store(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "label_store_result_generated": result.get("label_store_result_generated"), "label_store_leakage_checked": result.get("label_store_leakage_checked"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_pit_ml_dataset(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "pit_ml_dataset_result_generated": result.get("pit_ml_dataset_result_generated"), "pit_aware_dataset_used": result.get("pit_aware_dataset_used"), "future_data_usage_detected": result.get("future_data_usage_detected"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_offline_ml_model_lab(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_lab_result_generated": result.get("model_lab_result_generated"), "model_training_evaluation_result_generated": result.get("model_training_evaluation_result_generated"), "model_results_fabricated": result.get("model_results_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_model_registry_and_cards(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_registry_generated": result.get("model_registry_generated"), "model_card_register_generated": result.get("model_card_register_generated"), "model_status_real_trading_active_present": result.get("model_status_real_trading_active_present"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_prediction_registry(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v18_research_db_feature_ml_lab(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "prediction_registry_generated": result.get("prediction_registry_generated"), "prediction_results_fabricated": result.get("prediction_results_fabricated"), "predictions_are_trade_signals": result.get("predictions_are_trade_signals"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_model_validation_scorecard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_validation_scorecard_generated": result.get("model_validation_scorecard_generated"), "model_validation_results_fabricated": result.get("model_validation_results_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_model_risk_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_risk_review_result_generated": result.get("model_risk_review_result_generated"), "model_risk_results_fabricated": result.get("model_risk_results_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_prediction_quality_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "prediction_quality_validation_result_generated": result.get("prediction_quality_validation_result_generated"), "prediction_quality_results_fabricated": result.get("prediction_quality_results_fabricated"), "predictions_are_trade_signals": result.get("predictions_are_trade_signals"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_model_monitoring_drift_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_monitoring_drift_result_generated": result.get("model_monitoring_drift_result_generated"), "model_monitoring_results_fabricated": result.get("model_monitoring_results_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_model_explainability_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_explainability_result_generated": result.get("model_explainability_result_generated"), "model_explainability_fabricated": result.get("model_explainability_fabricated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_research_portfolio_model_integration(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v19_ml_validation_model_risk(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "research_portfolio_model_integration_result_generated": result.get("research_portfolio_model_integration_result_generated"), "research_portfolio_is_real_portfolio": result.get("research_portfolio_is_real_portfolio"), "model_integration_generates_real_trade": result.get("model_integration_generates_real_trade"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_data_source_reliability_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "public_data_source_adapter_registry_generated": result.get("public_data_source_adapter_registry_generated"), "broker_adapter_added": result.get("broker_adapter_added"), "private_account_adapter_added": result.get("private_account_adapter_added"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_benchmark_source_depth_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "benchmark_source_depth_result_generated": result.get("benchmark_source_depth_result_generated"), "fabricated_benchmark_data": result.get("fabricated_benchmark_data"), "benchmark_relative_claim_allowed": result.get("benchmark_relative_claim_allowed"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_index_constituent_source_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "index_constituent_source_result_generated": result.get("index_constituent_source_result_generated"), "fabricated_index_constituents": result.get("fabricated_index_constituents"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_industry_sector_source_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "industry_sector_source_result_generated": result.get("industry_sector_source_result_generated"), "fabricated_industry_classification": result.get("fabricated_industry_classification"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_corporate_action_status_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "corporate_action_adjusted_price_result_generated": result.get("corporate_action_adjusted_price_result_generated"), "suspension_delisting_st_status_result_generated": result.get("suspension_delisting_st_status_result_generated"), "fabricated_corporate_action": result.get("fabricated_corporate_action"), "fabricated_suspension_delisting_st_status": result.get("fabricated_suspension_delisting_st_status"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_financial_pit_source_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "financial_statement_pit_result_generated": result.get("financial_statement_pit_result_generated"), "fabricated_financial_pit_visibility": result.get("fabricated_financial_pit_visibility"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_data_reliability_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v21_data_source_benchmark_hardening(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "owner_data_reliability_dashboard_generated": result.get("owner_data_reliability_dashboard_generated"), "owner_readiness_state": result.get("owner_readiness_state"), "owner_operationally_acceptable": result.get("owner_operationally_acceptable"), "live_trading_ready": result.get("live_trading_ready"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_model_ensemble_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "model_ensemble_result_generated": result.get("model_ensemble_result_generated"), "ensemble_outputs_are_trade_signals": result.get("ensemble_outputs_are_trade_signals"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_factor_ensemble_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "factor_ensemble_result_generated": result.get("factor_ensemble_result_generated"), "ensemble_outputs_are_trade_signals": result.get("ensemble_outputs_are_trade_signals"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_candidate_rank_ensemble(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "candidate_rank_ensemble_result_generated": result.get("candidate_rank_ensemble_result_generated"), "candidate_ensemble_generates_buy_sell_signal": result.get("candidate_ensemble_generates_buy_sell_signal"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_strategy_ensemble_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "strategy_ensemble_result_generated": result.get("strategy_ensemble_result_generated"), "strategy_ensemble_generates_real_trade": result.get("strategy_ensemble_generates_real_trade"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_meta_strategy_research_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "meta_strategy_research_result_generated": result.get("meta_strategy_research_result_generated"), "meta_strategy_generates_real_trade": result.get("meta_strategy_generates_real_trade"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_adaptive_model_selection_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "adaptive_model_selection_result_generated": result.get("adaptive_model_selection_result_generated"), "adaptive_selection_changes_real_account": result.get("adaptive_selection_changes_real_account"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_ensemble_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v22_ensemble_meta_strategy(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "owner_ensemble_dashboard_generated": result.get("owner_ensemble_dashboard_generated"), "owner_readiness_state": result.get("owner_readiness_state"), "owner_operationally_acceptable": result.get("owner_operationally_acceptable"), "live_trading_ready": result.get("live_trading_ready"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_decision_journal(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "decision_journal_generated": result.get("decision_journal_generated"), "decision_journal_generates_trade_instruction": result.get("decision_journal_generates_trade_instruction"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_daily_research_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "daily_research_review_generated": result.get("daily_research_review_generated"), "owner_reports_generate_buy_sell_signal": result.get("owner_reports_generate_buy_sell_signal"), "owner_reports_generate_real_allocation": result.get("owner_reports_generate_real_allocation"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_periodic_research_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "periodic_research_review_generated": result.get("periodic_research_review_generated"), "warnings": len(result["warnings"]), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_report_artifact_index(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=True, paths=paths)

    print({"overall_passed": result["overall_passed"], "report_artifact_index_generated": result.get("report_artifact_index_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_warning_blocker_explanations(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "warning_blocker_explanation_generated": result.get("warning_blocker_explanation_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_operator_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v23_operator_ux_journal(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "owner_operator_dashboard_generated": result.get("owner_operator_dashboard_generated"), "owner_readiness_state": result.get("owner_readiness_state"), "owner_operationally_acceptable": result.get("owner_operationally_acceptable"), "live_trading_ready": result.get("live_trading_ready"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_artifact_bloat_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "artifact_inventory_bloat_result_generated": result.get("artifact_inventory_bloat_result_generated"), "artifact_inventory_fabricated": result.get("artifact_inventory_fabricated"), "required_artifacts_deleted": result.get("required_artifacts_deleted"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_report_deduplication_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "report_deduplication_result_generated": result.get("report_deduplication_result_generated"), "historical_evidence_deleted": result.get("historical_evidence_deleted"), "release_evidence_deleted": result.get("release_evidence_deleted"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_cli_hygiene_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "cli_hygiene_result_generated": result.get("cli_hygiene_result_generated"), "cli_broker_command_added": result.get("cli_broker_command_added"), "cli_live_trading_command_added": result.get("cli_live_trading_command_added"), "cli_order_command_added": result.get("cli_order_command_added"), "cli_owner_gate_command_added": result.get("cli_owner_gate_command_added"), "old_run_daily_present": result.get("old_run_daily_present"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_shared_result_contract_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "shared_result_contract_result_generated": result.get("shared_result_contract_result_generated"), "audit_contract_consolidation_result_generated": result.get("audit_contract_consolidation_result_generated"), "new_gate_score_generated": result.get("new_gate_score_generated"), "new_gate_decision_generated": result.get("new_gate_decision_generated"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_test_maintenance_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "test_maintenance_result_generated": result.get("test_maintenance_result_generated"), "code_organization_result_generated": result.get("code_organization_result_generated"), "test_result_fabricated": result.get("test_result_fabricated"), "full_pytest_run": result.get("full_pytest_run"), "targeted_pytest_required": result.get("targeted_pytest_required"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_maintenance_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_v24_maintenance_quality(as_of_date=args.as_of_date, simulation_only=args.simulation_only, paths=paths)

    print({"overall_passed": result["overall_passed"], "owner_maintenance_dashboard_generated": result.get("owner_maintenance_dashboard_generated"), "owner_readiness_state": result.get("owner_readiness_state"), "owner_operationally_acceptable": result.get("owner_operationally_acceptable"), "maintenance_quality_pass_means_live_trading_ready": result.get("maintenance_quality_pass_means_live_trading_ready"), "live_trading_ready": result.get("live_trading_ready"), "blocking_reasons": result["blocking_reasons"]})

    return 0 if result["overall_passed"] else 1


DISPATCH_HANDLERS_EARLY: dict[str, Callable[..., int]] = {
    "ashare-execution-gap-plan": _handle_ashare_execution_gap_plan,
    "ashare-trading-calendar-audit": _handle_ashare_trading_calendar_audit,
    "ashare-price-status-contract": _handle_ashare_price_status_contract,
    "ashare-lot-and-position-contract": _handle_ashare_lot_and_position_contract,
    "ashare-execution-cost-contract": _handle_ashare_execution_cost_contract,
    "audit-ashare-execution-rules": _handle_audit_ashare_execution_rules,
    "build-a-share-equity-master": _handle_build_a_share_equity_master,
    "build-a-share-trading-calendar": _handle_build_a_share_trading_calendar,
    "ingest-a-share-daily-prices": _handle_ingest_a_share_daily_prices,
    "ingest-a-share-adjusted-prices": _handle_ingest_a_share_adjusted_prices,
    "ingest-a-share-daily-basic": _handle_ingest_a_share_daily_basic,
    "ingest-a-share-industry-classification": _handle_ingest_a_share_industry_classification,
    "ingest-a-share-basic-financials": _handle_ingest_a_share_basic_financials,
    "audit-a-share-data-coverage": _handle_audit_a_share_data_coverage,
    "audit-a-share-data-schema": _handle_audit_a_share_data_schema,
    "build-a-share-data-foundation": _handle_build_a_share_data_foundation,
    "a-share-historical-backfill-plan": _handle_a_share_historical_backfill_plan,
    "diagnose-a-share-historical-backfill-coverage": _handle_diagnose_a_share_historical_backfill_coverage,
    "build-a-share-historical-backfill-symbol-queue": _handle_build_a_share_historical_backfill_symbol_queue,
    "backfill-a-share-daily-price-history": _handle_backfill_a_share_daily_price_history,
    "backfill-a-share-adjusted-price-history": _handle_backfill_a_share_adjusted_price_history,
    "backfill-a-share-daily-basic-history": _handle_backfill_a_share_daily_basic_history,
    "backfill-a-share-financial-history": _handle_backfill_a_share_financial_history,
    "audit-a-share-historical-panel-coverage": _handle_audit_a_share_historical_panel_coverage,
    "audit-a-share-feature-readiness": _handle_audit_a_share_feature_readiness,
    "backfill-a-share-historical-panels": _handle_backfill_a_share_historical_panels,
    "backfill-a-share-historical-panels-full-market": _handle_backfill_a_share_historical_panels_full_market,
    "build-a-share-tradable-universe": _handle_build_a_share_tradable_universe,
    "audit-a-share-tradable-universe": _handle_audit_a_share_tradable_universe,
    "build-and-audit-a-share-tradable-universe": _handle_build_and_audit_a_share_tradable_universe,
    "build-a-share-multi-horizon-features": _handle_build_a_share_multi_horizon_features,
    "audit-a-share-multi-horizon-features": _handle_audit_a_share_multi_horizon_features,
    "build-and-audit-a-share-multi-horizon-features": _handle_build_and_audit_a_share_multi_horizon_features,
    "build-a-share-scores": _handle_build_a_share_scores,
    "audit-a-share-scores": _handle_audit_a_share_scores,
    "build-and-audit-a-share-scores": _handle_build_and_audit_a_share_scores,
    "generate-a-share-candidates": _handle_generate_a_share_candidates,
    "audit-a-share-candidates": _handle_audit_a_share_candidates,
    "generate-and-audit-a-share-candidates": _handle_generate_and_audit_a_share_candidates,
    "build-a-share-virtual-portfolios": _handle_build_a_share_virtual_portfolios,
    "audit-a-share-virtual-portfolios": _handle_audit_a_share_virtual_portfolios,
    "build-and-audit-a-share-virtual-portfolios": _handle_build_and_audit_a_share_virtual_portfolios,
    "build-a-share-daily-stock-selection-briefing": _handle_build_a_share_daily_stock_selection_briefing,
    "audit-a-share-daily-stock-selection-briefing": _handle_audit_a_share_daily_stock_selection_briefing,
    "build-and-audit-a-share-daily-stock-selection-briefing": _handle_build_and_audit_a_share_daily_stock_selection_briefing,
    "build-a-share-virtual-portfolio-tracking": _handle_build_a_share_virtual_portfolio_tracking,
    "audit-a-share-virtual-portfolio-tracking": _handle_audit_a_share_virtual_portfolio_tracking,
    "build-and-audit-a-share-virtual-portfolio-tracking": _handle_build_and_audit_a_share_virtual_portfolio_tracking,
    "preflight-a-share-daily-workflow": _handle_preflight_a_share_daily_workflow,
    "run-a-share-daily-research-workflow": _handle_run_a_share_daily_research_workflow,
    "audit-a-share-daily-research-workflow": _handle_audit_a_share_daily_research_workflow,
    "run-and-audit-a-share-daily-research-workflow": _handle_run_and_audit_a_share_daily_research_workflow,
    "build-a-share-benchmark-comparison": _handle_build_a_share_benchmark_comparison,
    "audit-a-share-benchmark-comparison": _handle_audit_a_share_benchmark_comparison,
    "build-and-audit-a-share-benchmark-comparison": _handle_build_and_audit_a_share_benchmark_comparison,
    "build-a-share-multi-day-performance": _handle_build_a_share_multi_day_performance,
    "audit-a-share-multi-day-performance": _handle_audit_a_share_multi_day_performance,
    "build-and-audit-a-share-multi-day-performance": _handle_build_and_audit_a_share_multi_day_performance,
    "build-a-share-performance-attribution": _handle_build_a_share_performance_attribution,
    "audit-a-share-performance-attribution": _handle_audit_a_share_performance_attribution,
    "build-and-audit-a-share-performance-attribution": _handle_build_and_audit_a_share_performance_attribution,
    "refresh-a-share-data-freshness": _handle_refresh_a_share_data_freshness,
    "rerun-a-share-research-pipeline-from-refreshed-data": _handle_rerun_a_share_research_pipeline_from_refreshed_data,
    "build-a-share-research-evidence-accumulation-and-prep": _handle_build_a_share_research_evidence_accumulation_and_prep,
    "audit-a-share-research-evidence-accumulation-and-prep": _handle_audit_a_share_research_evidence_accumulation_and_prep,
    "build-and-audit-a-share-research-evidence-accumulation-and-prep": _handle_build_and_audit_a_share_research_evidence_accumulation_and_prep,
    "build-a-share-final-not-ready-closeout": _handle_build_a_share_final_not_ready_closeout,
    "audit-a-share-final-not-ready-closeout": _handle_audit_a_share_final_not_ready_closeout,
    "build-and-audit-a-share-final-not-ready-closeout": _handle_build_and_audit_a_share_final_not_ready_closeout,
    "build-a-share-historical-evidence-backfill-and-refresh-plan": _handle_build_a_share_historical_evidence_backfill_and_refresh_plan,
    "audit-a-share-historical-evidence-backfill-and-refresh-plan": _handle_audit_a_share_historical_evidence_backfill_and_refresh_plan,
    "build-and-audit-a-share-historical-evidence-backfill-and-refresh-plan": _handle_build_and_audit_a_share_historical_evidence_backfill_and_refresh_plan,
    "build-a-share-experiment-registry": _handle_build_a_share_experiment_registry,
    "run-a-share-automated-experiments": _handle_run_a_share_automated_experiments,
    "run-a-share-rl-simulated-strategy-lab": _handle_run_a_share_rl_simulated_strategy_lab,
    "evaluate-a-share-simulated-strategy-promotion": _handle_evaluate_a_share_simulated_strategy_promotion,
    "build-a-share-benchmark-claim-hardening": _handle_build_a_share_benchmark_claim_hardening,
    "audit-a-share-benchmark-claim-hardening": _handle_audit_a_share_benchmark_claim_hardening,
    "build-and-audit-a-share-benchmark-claim-hardening": _handle_build_and_audit_a_share_benchmark_claim_hardening,
    "build-a-share-owner-command-center": _handle_build_a_share_owner_command_center,
    "build-a-share-simulated-account-reconciliation": _handle_build_a_share_simulated_account_reconciliation,
    "build-a-share-strategy-lifecycle-review": _handle_build_a_share_strategy_lifecycle_review,
    "build-a-share-monitoring-remediation-pack": _handle_build_a_share_monitoring_remediation_pack,
    "plan-a-share-local-post-close-schedule": _handle_plan_a_share_local_post_close_schedule,
    "build-a-share-local-scheduler-plan": _handle_build_a_share_local_scheduler_plan,
    "build-a-share-operator-runbook": _handle_build_a_share_operator_runbook,
    "build-a-share-continuous-simulation-history": _handle_build_a_share_continuous_simulation_history,
    "build-a-share-incident-remediation-pack": _handle_build_a_share_incident_remediation_pack,
    "build-a-share-artifact-index-and-health-report": _handle_build_a_share_artifact_index_and_health_report,
    "build-a-share-research-quality-scorecard": _handle_build_a_share_research_quality_scorecard,
    "build-a-share-strategy-lab-quality-review": _handle_build_a_share_strategy_lab_quality_review,
    "build-a-share-llm-proposal-quality-review": _handle_build_a_share_llm_proposal_quality_review,
    "build-a-share-rl-policy-quality-review": _handle_build_a_share_rl_policy_quality_review,
    "build-a-share-strategy-lifecycle-quality-gates": _handle_build_a_share_strategy_lifecycle_quality_gates,
    "build-a-share-robustness-and-overfit-review": _handle_build_a_share_robustness_and_overfit_review,
    "build-a-share-portfolio-risk-scorecard": _handle_build_a_share_portfolio_risk_scorecard,
    "build-a-share-capacity-liquidity-review": _handle_build_a_share_capacity_liquidity_review,
    "build-a-share-simulated-allocation-plan": _handle_build_a_share_simulated_allocation_plan,
    "build-a-share-simulated-rebalance-plan": _handle_build_a_share_simulated_rebalance_plan,
    "build-a-share-portfolio-stress-test": _handle_build_a_share_portfolio_stress_test,
    "build-a-share-risk-guardrail-review": _handle_build_a_share_risk_guardrail_review,
    "build-a-share-market-regime-classification": _handle_build_a_share_market_regime_classification,
    "build-a-share-regime-factor-candidate-review": _handle_build_a_share_regime_factor_candidate_review,
    "build-a-share-regime-strategy-review": _handle_build_a_share_regime_strategy_review,
    "build-a-share-adaptive-research-queue": _handle_build_a_share_adaptive_research_queue,
    "build-a-share-regime-llm-rl-governance": _handle_build_a_share_regime_llm_rl_governance,
    "build-a-share-regime-portfolio-overlay": _handle_build_a_share_regime_portfolio_overlay,
    "build-a-share-point-in-time-data-registry": _handle_build_a_share_point_in_time_data_registry,
    "build-a-share-event-driven-backtest-replay": _handle_build_a_share_event_driven_backtest_replay,
    "build-a-share-market-rule-simulation-review": _handle_build_a_share_market_rule_simulation_review,
    "build-a-share-virtual-broker-rule-hardening": _handle_build_a_share_virtual_broker_rule_hardening,
    "build-a-share-benchmark-index-source-hardening": _handle_build_a_share_benchmark_index_source_hardening,
    "build-a-share-backtest-trust-scorecard": _handle_build_a_share_backtest_trust_scorecard,
    "build-a-share-factor-validation-review": _handle_build_a_share_factor_validation_review,
    "build-a-share-candidate-ranking-validation": _handle_build_a_share_candidate_ranking_validation,
    "build-a-share-strategy-oos-walkforward-review": _handle_build_a_share_strategy_oos_walkforward_review,
    "build-a-share-robustness-statistical-validation": _handle_build_a_share_robustness_statistical_validation,
    "build-a-share-strategy-admission-review": _handle_build_a_share_strategy_admission_review,
    "build-a-share-experiment-validation-registry": _handle_build_a_share_experiment_validation_registry,
    "build-a-share-research-database-index": _handle_build_a_share_research_database_index,
    "build-a-share-feature-store": _handle_build_a_share_feature_store,
    "build-a-share-label-store": _handle_build_a_share_label_store,
    "build-a-share-pit-ml-dataset": _handle_build_a_share_pit_ml_dataset,
    "build-a-share-offline-ml-model-lab": _handle_build_a_share_offline_ml_model_lab,
    "build-a-share-model-registry-and-cards": _handle_build_a_share_model_registry_and_cards,
    "build-a-share-prediction-registry": _handle_build_a_share_prediction_registry,
    "build-a-share-model-validation-scorecard": _handle_build_a_share_model_validation_scorecard,
    "build-a-share-model-risk-review": _handle_build_a_share_model_risk_review,
    "build-a-share-prediction-quality-review": _handle_build_a_share_prediction_quality_review,
    "build-a-share-model-monitoring-drift-review": _handle_build_a_share_model_monitoring_drift_review,
    "build-a-share-model-explainability-review": _handle_build_a_share_model_explainability_review,
    "build-a-share-research-portfolio-model-integration": _handle_build_a_share_research_portfolio_model_integration,
    "build-a-share-data-source-reliability-review": _handle_build_a_share_data_source_reliability_review,
    "build-a-share-benchmark-source-depth-review": _handle_build_a_share_benchmark_source_depth_review,
    "build-a-share-index-constituent-source-review": _handle_build_a_share_index_constituent_source_review,
    "build-a-share-industry-sector-source-review": _handle_build_a_share_industry_sector_source_review,
    "build-a-share-corporate-action-status-review": _handle_build_a_share_corporate_action_status_review,
    "build-a-share-financial-pit-source-review": _handle_build_a_share_financial_pit_source_review,
    "build-a-share-owner-data-reliability-dashboard": _handle_build_a_share_owner_data_reliability_dashboard,
    "build-a-share-model-ensemble-review": _handle_build_a_share_model_ensemble_review,
    "build-a-share-factor-ensemble-review": _handle_build_a_share_factor_ensemble_review,
    "build-a-share-candidate-rank-ensemble": _handle_build_a_share_candidate_rank_ensemble,
    "build-a-share-strategy-ensemble-review": _handle_build_a_share_strategy_ensemble_review,
    "build-a-share-meta-strategy-research-review": _handle_build_a_share_meta_strategy_research_review,
    "build-a-share-adaptive-model-selection-review": _handle_build_a_share_adaptive_model_selection_review,
    "build-a-share-owner-ensemble-dashboard": _handle_build_a_share_owner_ensemble_dashboard,
    "build-a-share-decision-journal": _handle_build_a_share_decision_journal,
    "build-a-share-daily-research-review": _handle_build_a_share_daily_research_review,
    "build-a-share-periodic-research-review": _handle_build_a_share_periodic_research_review,
    "build-a-share-report-artifact-index": _handle_build_a_share_report_artifact_index,
    "build-a-share-warning-blocker-explanations": _handle_build_a_share_warning_blocker_explanations,
    "build-a-share-owner-operator-dashboard": _handle_build_a_share_owner_operator_dashboard,
    "build-a-share-artifact-bloat-review": _handle_build_a_share_artifact_bloat_review,
    "build-a-share-report-deduplication-review": _handle_build_a_share_report_deduplication_review,
    "build-a-share-cli-hygiene-review": _handle_build_a_share_cli_hygiene_review,
    "build-a-share-shared-result-contract-review": _handle_build_a_share_shared_result_contract_review,
    "build-a-share-test-maintenance-review": _handle_build_a_share_test_maintenance_review,
    "build-a-share-owner-maintenance-dashboard": _handle_build_a_share_owner_maintenance_dashboard,
}


def _handle_build_a_share_daily_data_refresh(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_daily_data_refresh(

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

def _handle_audit_a_share_daily_data_refresh(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_daily_data_refresh(

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

def _handle_build_and_audit_a_share_daily_data_refresh(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_daily_data_refresh(

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

    audit_result = _cli.audit_a_share_daily_data_refresh(

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

def _handle_validate_a_share_current_day_readiness(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_current_day_readiness(

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

def _handle_run_a_share_current_day_research(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.run_a_share_current_day_research(

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

def _handle_audit_a_share_current_day_research_run(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_current_day_research_run(

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

def _handle_run_and_audit_a_share_current_day_research(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    run_result = _cli.run_a_share_current_day_research(

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

    audit_result = _cli.audit_a_share_current_day_research_run(

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

def _handle_validate_a_share_owner_dashboard_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_dashboard_inputs(

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

def _handle_build_a_share_owner_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_dashboard(

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

def _handle_audit_a_share_owner_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_dashboard(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_owner_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_dashboard(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        fail_on_missing_optional_card=args.fail_on_missing_optional_card,

        compact_only=args.compact_only,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_dashboard(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_owner_monitoring_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_monitoring_inputs(

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

def _handle_build_a_share_owner_monitoring(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_monitoring(

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

def _handle_audit_a_share_owner_monitoring(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_monitoring(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_owner_monitoring(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_monitoring(

        as_of_date=args.as_of_date,

        mode=args.mode,

        history_window_days=args.history_window_days,

        minimum_history_observations=args.minimum_history_observations,

        allow_rebuild_history=args.allow_rebuild_history,

        send_external_notifications=args.send_external_notifications,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_monitoring(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_owner_remediation_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_remediation_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_owner_remediation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_remediation(

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

def _handle_audit_a_share_owner_remediation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_remediation(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_owner_remediation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_remediation(

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

    audit_result = _cli.audit_a_share_owner_remediation(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_daily_ops_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_daily_ops_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_daily_ops_center(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_daily_ops_center(

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

def _handle_audit_a_share_daily_ops_center(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_daily_ops_center(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_daily_ops_center(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_daily_ops_center(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_safe_validation_chain=args.allow_safe_validation_chain,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_daily_ops_center(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_ops_history_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_ops_history_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_ops_history_baseline(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_ops_history_baseline(

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

def _handle_audit_a_share_ops_history_baseline(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_ops_history_baseline(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_ops_history_baseline(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_ops_history_baseline(

        as_of_date=args.as_of_date,

        mode=args.mode,

        history_window_days=args.history_window_days,

        minimum_required_observations=args.minimum_required_observations,

        baseline_window_observations=args.baseline_window_observations,

        allow_rebuild_history=args.allow_rebuild_history,

        allow_synthetic_history=args.allow_synthetic_history,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_ops_history_baseline(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_gated_build_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_gated_build_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_gated_build_from_existing_data(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_gated_build(

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

def _handle_audit_a_share_gated_build_from_existing_data(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_gated_build(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_gated_build_from_existing_data(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_gated_build(

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

    audit_result = _cli.audit_a_share_gated_build(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_build_repeatability_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_build_repeatability_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_build_repeatability(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_build_repeatability(

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

def _handle_audit_a_share_build_repeatability(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_build_repeatability(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_build_repeatability(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_build_repeatability(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_business_output_drift=args.allow_business_output_drift,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_build_repeatability(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_build_output_owner_dashboard_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_build_output_owner_dashboard_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_build_output_owner_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_build_output_owner_dashboard(

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

def _handle_audit_a_share_build_output_owner_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_build_output_owner_dashboard(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_build_output_owner_dashboard(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_build_output_owner_dashboard(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_required_validate_fallback=args.allow_required_validate_fallback,

        allow_business_output_drift=args.allow_business_output_drift,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_build_output_owner_dashboard(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_build_output_ops_refresh_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_build_output_ops_refresh_inputs(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_a_share_build_output_ops_refresh(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_build_output_ops_refresh(

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

def _handle_audit_a_share_build_output_ops_refresh(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_build_output_ops_refresh(as_of_date=args.as_of_date, paths=paths)

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

def _handle_build_and_audit_a_share_build_output_ops_refresh(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_build_output_ops_refresh(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_business_output_drift=args.allow_business_output_drift,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_build_output_ops_refresh(as_of_date=args.as_of_date, paths=paths)

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

def _handle_validate_a_share_owner_daily_pack_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_daily_pack_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "build_output_ops_refresh_audit_passed": result["build_output_ops_refresh_audit_passed"],

            "build_output_dashboard_audit_passed": result["build_output_dashboard_audit_passed"],

            "repeatability_audit_passed": result["repeatability_audit_passed"],

            "gated_build_audit_passed": result["gated_build_audit_passed"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_daily_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_daily_pack(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_workflow_mode": result["source_workflow_mode"],

            "not_investment_decision_pack": result["not_investment_decision_pack"],

            "build_output_ops_refresh_audit_passed": result["build_output_ops_refresh_audit_passed"],

            "build_output_dashboard_audit_passed": result["build_output_dashboard_audit_passed"],

            "repeatability_audit_passed": result["repeatability_audit_passed"],

            "gated_build_audit_passed": result["gated_build_audit_passed"],

            "business_output_drift_count": result["business_output_drift_count"],

            "protected_path_modifications_detected": result["protected_path_modifications_detected"],

            "automatic_action_count": result["automatic_action_count"],

            "execute_remediation_actions": result["execute_remediation_actions"],

            "external_notifications_sent": result["external_notifications_sent"],

            "forbidden_decision_categories_detected": result["forbidden_decision_categories_detected"],

            "recommended_next_version": result["recommended_next_version"],

            "daily_pack_report": result["daily_pack_report"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_daily_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_daily_pack(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "daily_pack_checks": result["daily_pack_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_daily_pack(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_daily_pack(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_daily_pack(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "daily_pack_checks": audit_result["daily_pack_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_daily_pack_history_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_daily_pack_history_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "owner_daily_pack_audit_passed": result["owner_daily_pack_audit_passed"],

            "source_workflow_mode": result["source_workflow_mode"],

            "not_investment_decision_pack": result["not_investment_decision_pack"],

            "boundary_clean": result["boundary_clean"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_daily_pack_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_daily_pack_history(

        as_of_date=args.as_of_date,

        mode=args.mode,

        history_window_days=args.history_window_days,

        minimum_required_observations=args.minimum_required_observations,

        baseline_window_observations=args.baseline_window_observations,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_rebuild_history=args.allow_rebuild_history,

        allow_synthetic_history=args.allow_synthetic_history,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_workflow_mode": result["source_workflow_mode"],

            "daily_pack_history_observation_count": result["daily_pack_history_observation_count"],

            "minimum_required_observations": result["minimum_required_observations"],

            "trend_analysis_available": result["trend_analysis_available"],

            "readiness_trend_status": result["readiness_trend_status"],

            "owner_readiness_score": result["owner_readiness_score"],

            "owner_readiness_grade": result["owner_readiness_grade"],

            "append_only_history": result["append_only_history"],

            "idempotent_append": result["idempotent_append"],

            "duplicate_detected": result["duplicate_detected"],

            "same_date_changed_content_warning": result["same_date_changed_content_warning"],

            "synthetic_history_used": result["synthetic_history_used"],

            "future_dates_used": result["future_dates_used"],

            "recommended_next_version": result["recommended_next_version"],

            "daily_pack_history_report": result["daily_pack_history_report"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_daily_pack_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_daily_pack_history(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "history_checks": result["history_checks"],

            "readiness_checks": result["readiness_checks"],

            "boundary": result["boundary"],

            "append_result": result["append_result"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_daily_pack_history(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_daily_pack_history(

        as_of_date=args.as_of_date,

        mode=args.mode,

        history_window_days=args.history_window_days,

        minimum_required_observations=args.minimum_required_observations,

        baseline_window_observations=args.baseline_window_observations,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_rebuild_history=args.allow_rebuild_history,

        allow_synthetic_history=args.allow_synthetic_history,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_daily_pack_history(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "history_checks": audit_result["history_checks"],

            "readiness_checks": audit_result["readiness_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_readiness_gate_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_readiness_gate_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "owner_daily_pack_history_audit_passed": result["owner_daily_pack_history_audit_passed"],

            "owner_daily_pack_audit_passed": result["owner_daily_pack_audit_passed"],

            "source_workflow_mode": result["source_workflow_mode"],

            "boundary_clean": result["boundary_clean"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_readiness_gate(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_readiness_gate(

        as_of_date=args.as_of_date,

        mode=args.mode,

        minimum_owner_readiness_score=args.minimum_owner_readiness_score,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_known_non_blocking_warnings=args.allow_known_non_blocking_warnings,

        allow_insufficient_history_if_correctly_flagged=args.allow_insufficient_history_if_correctly_flagged,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_workflow_mode": result.get("source_workflow_mode"),

            "decision": result.get("decision"),

            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),

            "required_gates_passed": result.get("required_gates_passed"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "actual_owner_readiness_score": result.get("actual_owner_readiness_score"),

            "actual_owner_readiness_grade": result.get("actual_owner_readiness_grade"),

            "quality_exception_candidate_count": result.get("quality_exception_candidate_count"),

            "recommended_next_version": result.get("recommended_next_version"),

            "owner_readiness_gate_report": result.get("owner_readiness_gate_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_readiness_gate(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_readiness_gate(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "gate_checks": result["gate_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_readiness_gate(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_readiness_gate(

        as_of_date=args.as_of_date,

        mode=args.mode,

        minimum_owner_readiness_score=args.minimum_owner_readiness_score,

        allow_date_mismatch=args.allow_date_mismatch,

        allow_known_non_blocking_warnings=args.allow_known_non_blocking_warnings,

        allow_insufficient_history_if_correctly_flagged=args.allow_insufficient_history_if_correctly_flagged,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_readiness_gate(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "decision": audit_result["gate_checks"]["decision"],

            "owner_operationally_acceptable": audit_result["gate_checks"]["owner_operationally_acceptable"],

            "required_gates_passed": audit_result["gate_checks"]["required_gates_passed"],

            "input_checks": audit_result["input_checks"],

            "gate_checks": audit_result["gate_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_quality_exceptions_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_quality_exception_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "owner_readiness_gate_audit_passed": result["owner_readiness_gate_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "blocked_state_represented_correctly": result["blocked_state_represented_correctly"],

            "no_automatic_waiver": result["no_automatic_waiver"],

            "boundary_clean": result["boundary_clean"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_quality_exceptions(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_quality_exceptions(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "blocked_gate_decision_preserved": result.get("blocked_gate_decision_preserved"),

            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "actual_owner_readiness_score": result.get("actual_owner_readiness_score"),

            "readiness_score_gap": result.get("readiness_score_gap"),

            "quality_exception_count": result.get("quality_exception_count"),

            "developer_follow_up_count": result.get("developer_follow_up_count"),

            "manual_waiver_decision_status": result.get("manual_waiver_decision_status"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "waiver_changes_gate_decision": result.get("waiver_changes_gate_decision"),

            "recommended_next_version": result.get("recommended_next_version"),

            "quality_exception_workflow_report": result.get("quality_exception_workflow_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_quality_exceptions(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_quality_exceptions(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "exception_checks": result["exception_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_quality_exceptions(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_quality_exceptions(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_quality_exceptions(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "exception_checks": audit_result["exception_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_readiness_recovery_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_readiness_recovery_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "quality_exception_workflow_audit_passed": result["quality_exception_workflow_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "blocked_gate_decision_preserved": result["blocked_gate_decision_preserved"],

            "owner_operationally_acceptable": result["owner_operationally_acceptable"],

            "auto_waiver_allowed": result["auto_waiver_allowed"],

            "waiver_changes_gate_decision": result["waiver_changes_gate_decision"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_readiness_recovery(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_readiness_recovery(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "blocked_gate_decision_preserved": result.get("blocked_gate_decision_preserved"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "actual_owner_readiness_score": result.get("actual_owner_readiness_score"),

            "actual_owner_readiness_grade": result.get("actual_owner_readiness_grade"),

            "readiness_score_gap": result.get("readiness_score_gap"),

            "recovery_task_count": result.get("recovery_task_count"),

            "developer_follow_up_task_count": result.get("developer_follow_up_task_count"),

            "owner_follow_up_task_count": result.get("owner_follow_up_task_count"),

            "ready_for_future_gate_reevaluation": result.get("ready_for_future_gate_reevaluation"),

            "recovery_plan_changes_gate_decision": result.get("recovery_plan_changes_gate_decision"),

            "threshold_lowered": result.get("threshold_lowered"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "execute_recovery_tasks": result.get("execute_recovery_tasks"),

            "recommended_next_version": result.get("recommended_next_version"),

            "owner_readiness_recovery_plan_report": result.get("owner_readiness_recovery_plan_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_readiness_recovery(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_readiness_recovery(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "recovery_checks": result["recovery_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_readiness_recovery(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_readiness_recovery(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_readiness_recovery(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "recovery_checks": audit_result["recovery_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_readiness_recovery_execution_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_readiness_recovery_execution_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "recovery_audit_passed": result["recovery_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "blocked_gate_decision_preserved": result["blocked_gate_decision_preserved"],

            "recovery_plan_changes_gate_decision": result["recovery_plan_changes_gate_decision"],

            "threshold_lowered": result["threshold_lowered"],

            "auto_waiver_allowed": result["auto_waiver_allowed"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_readiness_recovery_execution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_readiness_recovery_execution(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "blocked_gate_decision_preserved": result.get("blocked_gate_decision_preserved"),

            "task_count": result.get("task_count"),

            "evidence_available_count": result.get("evidence_available_count"),

            "verified_by_audit_only_count": result.get("verified_by_audit_only_count"),

            "completed_count": result.get("completed_count"),

            "tasks_marked_complete_by_default": result.get("tasks_marked_complete_by_default"),

            "ready_for_future_gate_reevaluation": result.get("ready_for_future_gate_reevaluation"),

            "gate_reevaluation_readiness_decision": result.get("gate_reevaluation_readiness_decision"),

            "gate_reevaluation_executed": result.get("gate_reevaluation_executed"),

            "threshold_lowered": result.get("threshold_lowered"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "recommended_next_version": result.get("recommended_next_version"),

            "recovery_execution_tracker_report": result.get("recovery_execution_tracker_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_readiness_recovery_execution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_readiness_recovery_execution(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "execution_checks": result["execution_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_readiness_recovery_execution(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_readiness_recovery_execution(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_readiness_recovery_execution(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "execution_checks": audit_result["execution_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_controlled_gate_reevaluation_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_controlled_gate_reevaluation_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "recovery_execution_audit_passed": result["recovery_execution_audit_passed"],

            "owner_readiness_gate_audit_passed": result["owner_readiness_gate_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "blocked_gate_decision_preserved": result["blocked_gate_decision_preserved"],

            "source_ready_for_future_gate_reevaluation": result["source_ready_for_future_gate_reevaluation"],

            "source_gate_reevaluation_executed": result["source_gate_reevaluation_executed"],

            "threshold_lowered": result["threshold_lowered"],

            "auto_waiver_allowed": result["auto_waiver_allowed"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_controlled_gate_reevaluation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_controlled_gate_reevaluation(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "blocked_gate_decision_preserved": result.get("blocked_gate_decision_preserved"),

            "readiness_guard_passed": result.get("readiness_guard_passed"),

            "reevaluation_allowed": result.get("reevaluation_allowed"),

            "reevaluation_skipped": result.get("reevaluation_skipped"),

            "reevaluation_skip_reason": result.get("reevaluation_skip_reason"),

            "controlled_reevaluation_decision": result.get("controlled_reevaluation_decision"),

            "gate_reevaluation_executed": result.get("gate_reevaluation_executed"),

            "new_gate_score_generated": result.get("new_gate_score_generated"),

            "new_gate_decision_generated": result.get("new_gate_decision_generated"),

            "threshold_lowered": result.get("threshold_lowered"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "recommended_next_version": result.get("recommended_next_version"),

            "controlled_reevaluation_report": result.get("controlled_reevaluation_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_controlled_gate_reevaluation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_controlled_gate_reevaluation(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "reevaluation_checks": result["reevaluation_checks"],

            "boundary": result["boundary"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_controlled_gate_reevaluation(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_controlled_gate_reevaluation(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_controlled_gate_reevaluation(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "reevaluation_checks": audit_result["reevaluation_checks"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_recovery_evidence_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_recovery_evidence_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "controlled_reevaluation_audit_passed": result["controlled_reevaluation_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "reevaluation_skipped": result["reevaluation_skipped"],

            "new_gate_score_generated": result["new_gate_score_generated"],

            "new_gate_decision_generated": result["new_gate_decision_generated"],

            "source_readiness_score": result["source_readiness_score"],

            "minimum_owner_readiness_score": result["minimum_owner_readiness_score"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_recovery_evidence(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_recovery_evidence(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "source_readiness_score": result.get("source_readiness_score"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "score_gap": result.get("score_gap"),

            "evidence_record_count": result.get("evidence_record_count"),

            "strong_evidence_count": result.get("strong_evidence_count"),

            "audit_verified_evidence_count": result.get("audit_verified_evidence_count"),

            "missing_evidence_count": result.get("missing_evidence_count"),

            "overall_evidence_quality": result.get("overall_evidence_quality"),

            "evidence_ready_for_next_reevaluation_prep": result.get("evidence_ready_for_next_reevaluation_prep"),

            "actual_audited_score_changed": result.get("actual_audited_score_changed"),

            "new_audited_score": result.get("new_audited_score"),

            "new_gate_score_generated": result.get("new_gate_score_generated"),

            "new_gate_decision_generated": result.get("new_gate_decision_generated"),

            "source_gate_decision_preserved": result.get("source_gate_decision_preserved"),

            "threshold_lowered": result.get("threshold_lowered"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "forbidden_evidence_types_detected": result.get("forbidden_evidence_types_detected"),

            "forbidden_owner_developer_actions_detected": result.get("forbidden_owner_developer_actions_detected"),

            "recommended_next_version": result.get("recommended_next_version"),

            "recovery_evidence_report": result.get("recovery_evidence_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_recovery_evidence(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_recovery_evidence(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "evidence_checks": result["evidence_checks"],

            "boundary": result["boundary"],

            "test_policy": result["test_policy"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_recovery_evidence(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_recovery_evidence(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_recovery_evidence(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "evidence_checks": audit_result["evidence_checks"],

            "test_policy": audit_result["test_policy"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_evidence_backed_reevaluation_prep_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_evidence_backed_reevaluation_prep_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "recovery_evidence_audit_passed": result["recovery_evidence_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "source_gate_decision_preserved": result["source_gate_decision_preserved"],

            "evidence_ready_for_next_reevaluation_prep": result["evidence_ready_for_next_reevaluation_prep"],

            "new_gate_score_generated": result["new_gate_score_generated"],

            "new_gate_decision_generated": result["new_gate_decision_generated"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_evidence_backed_reevaluation_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_evidence_backed_reevaluation_prep(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_gate_decision": result.get("source_gate_decision"),

            "source_readiness_score": result.get("source_readiness_score"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "score_gap": result.get("score_gap"),

            "evidence_record_count": result.get("evidence_record_count"),

            "strong_evidence_count": result.get("strong_evidence_count"),

            "audit_verified_evidence_count": result.get("audit_verified_evidence_count"),

            "missing_evidence_count": result.get("missing_evidence_count"),

            "overall_evidence_quality": result.get("overall_evidence_quality"),

            "remaining_gap_count": result.get("remaining_gap_count"),

            "blocking_gap_count": result.get("blocking_gap_count"),

            "evidence_ready_for_next_reevaluation_prep": result.get("evidence_ready_for_next_reevaluation_prep"),

            "ready_for_controlled_gate_reevaluation": result.get("ready_for_controlled_gate_reevaluation"),

            "eligibility_decision": result.get("eligibility_decision"),

            "reevaluation_input_package_generated": result.get("reevaluation_input_package_generated"),

            "reevaluation_executed": result.get("reevaluation_executed"),

            "new_gate_score_generated": result.get("new_gate_score_generated"),

            "new_gate_decision_generated": result.get("new_gate_decision_generated"),

            "source_gate_decision_preserved": result.get("source_gate_decision_preserved"),

            "threshold_lowered": result.get("threshold_lowered"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "score_impact_readiness_is_not_official_score": result.get("score_impact_readiness_is_not_official_score"),

            "recommended_next_version": result.get("recommended_next_version"),

            "evidence_backed_prep_report": result.get("evidence_backed_prep_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_evidence_backed_reevaluation_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "prep_checks": result["prep_checks"],

            "boundary": result["boundary"],

            "test_policy": result["test_policy"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_evidence_backed_reevaluation_prep(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_evidence_backed_reevaluation_prep(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_evidence_backed_reevaluation_prep(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "prep_checks": audit_result["prep_checks"],

            "test_policy": audit_result["test_policy"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_v0820_gate_outcome_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_v0820_gate_outcome_inputs(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "evidence_backed_prep_audit_passed": result["evidence_backed_prep_audit_passed"],

            "source_gate_decision": result["source_gate_decision"],

            "source_gate_decision_preserved": result["source_gate_decision_preserved"],

            "v0819_eligibility_decision": result["v0819_eligibility_decision"],

            "v0819_ready_for_controlled_gate_reevaluation": result["v0819_ready_for_controlled_gate_reevaluation"],

            "reevaluation_input_package_generated": result["reevaluation_input_package_generated"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_v0820_gate_outcome(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_v0820_gate_outcome(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "selected_branch": result.get("selected_branch"),

            "branch_decision_consistent": result.get("branch_decision_consistent"),

            "controlled_reevaluation_allowed": result.get("controlled_reevaluation_allowed"),

            "controlled_reevaluation_executed": result.get("controlled_reevaluation_executed"),

            "final_blocked_closeout_generated": result.get("final_blocked_closeout_generated"),

            "source_gate_decision": result.get("source_gate_decision"),

            "previous_readiness_score": result.get("previous_readiness_score"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "new_controlled_readiness_score_generated": result.get("new_controlled_readiness_score_generated"),

            "new_controlled_readiness_score": result.get("new_controlled_readiness_score"),

            "new_controlled_readiness_grade": result.get("new_controlled_readiness_grade"),

            "new_controlled_gate_decision_generated": result.get("new_controlled_gate_decision_generated"),

            "new_controlled_gate_decision": result.get("new_controlled_gate_decision"),

            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),

            "threshold_lowered": result.get("threshold_lowered"),

            "auto_waiver_allowed": result.get("auto_waiver_allowed"),

            "manual_waiver_approval_recorded": result.get("manual_waiver_approval_recorded"),

            "waiver_used_for_outcome": result.get("waiver_used_for_outcome"),

            "recommended_next_version": result.get("recommended_next_version"),

            "v0820_owner_outcome_report": result.get("v0820_owner_outcome_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_v0820_gate_outcome(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_v0820_gate_outcome(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "outcome_checks": result["outcome_checks"],

            "boundary": result["boundary"],

            "test_policy": result["test_policy"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_v0820_gate_outcome(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_v0820_gate_outcome(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_v0820_gate_outcome(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "outcome_checks": audit_result["outcome_checks"],

            "test_policy": audit_result["test_policy"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_closeout_review_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_closeout_review_inputs(as_of_date=args.as_of_date, allow_date_mismatch=args.allow_date_mismatch, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "v0820_outcome_audit_passed": result["v0820_outcome_audit_passed"],

            "selected_v0820_branch": result["selected_v0820_branch"],

            "source_gate_decision": result["source_gate_decision"],

            "controlled_reevaluation_executed": result["controlled_reevaluation_executed"],

            "final_blocked_closeout_generated": result["final_blocked_closeout_generated"],

            "threshold_lowered": result["threshold_lowered"],

            "auto_waiver_allowed": result["auto_waiver_allowed"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_closeout_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_closeout_review(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "selected_v0820_branch": result.get("selected_v0820_branch"),

            "source_gate_decision": result.get("source_gate_decision"),

            "previous_readiness_score": result.get("previous_readiness_score"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "score_gap": result.get("score_gap"),

            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),

            "blocked_state_intentional": result.get("blocked_state_intentional"),

            "blocked_state_audited": result.get("blocked_state_audited"),

            "new_gate_score_generated": result.get("new_gate_score_generated"),

            "new_gate_decision_generated": result.get("new_gate_decision_generated"),

            "execute_full_pytest": result.get("execute_full_pytest"),

            "v090_release_candidate_readiness_decision": result.get("v090_release_candidate_readiness_decision"),

            "v090_full_regression_plan_generated": result.get("v090_full_regression_plan_generated"),

            "v090_audit_sweep_plan_generated": result.get("v090_audit_sweep_plan_generated"),

            "full_pytest_run": result.get("full_pytest_run"),

            "recommended_next_version": result.get("recommended_next_version"),

            "closeout_review_report": result.get("closeout_review_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_closeout_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_closeout_review(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "closeout_checks": result["closeout_checks"],

            "boundary": result["boundary"],

            "test_policy": result["test_policy"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_closeout_review(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_closeout_review(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_closeout_review(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "closeout_checks": audit_result["closeout_checks"],

            "test_policy": audit_result["test_policy"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1

def _handle_validate_a_share_owner_operator_experience_inputs(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.validate_a_share_owner_operator_experience_inputs(as_of_date=args.as_of_date, allow_date_mismatch=args.allow_date_mismatch, paths=paths)

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_release_candidate": result["source_release_candidate"],

            "known_owner_readiness_state": result["known_owner_readiness_state"],

            "owner_operationally_acceptable": result["owner_operationally_acceptable"],

            "v090_full_pytest_passed": result["v090_full_pytest_passed"],

            "v090_audit_sweep_passed": result["v090_audit_sweep_passed"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_a_share_owner_operator_experience(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.build_a_share_owner_operator_experience(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    print(

        {

            "builder_id": result["builder_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "source_release_candidate": result.get("source_release_candidate"),

            "known_owner_readiness_state": result.get("known_owner_readiness_state"),

            "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),

            "readiness_score": result.get("readiness_score"),

            "minimum_owner_readiness_score": result.get("minimum_owner_readiness_score"),

            "score_gap": result.get("score_gap"),

            "owner_daily_status_generated": result.get("owner_daily_status_generated"),

            "known_blocked_state_banner_generated": result.get("known_blocked_state_banner_generated"),

            "operator_action_menu_generated": result.get("operator_action_menu_generated"),

            "artifact_navigation_index_generated": result.get("artifact_navigation_index_generated"),

            "forbidden_operator_actions_present": result.get("forbidden_operator_actions_present"),

            "v090_full_pytest_passed": result.get("v090_full_pytest_passed"),

            "v090_audit_sweep_passed": result.get("v090_audit_sweep_passed"),

            "run_full_pytest": result.get("run_full_pytest"),

            "recommended_next_version": result.get("recommended_next_version"),

            "owner_daily_status_report": result.get("owner_daily_status_report"),

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_audit_a_share_owner_operator_experience(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    result = _cli.audit_a_share_owner_operator_experience(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "audit_id": result["audit_id"],

            "overall_passed": result["overall_passed"],

            "blocking_reasons": result["blocking_reasons"],

            "warnings": result["warnings"],

            "input_checks": result["input_checks"],

            "operator_experience_checks": result["operator_experience_checks"],

            "boundary": result["boundary"],

            "test_policy": result["test_policy"],

            "recommended_next_version": result["recommended_next_version"],

            "json_path": result["json_path"],

            "report_path": result["report_path"],

        }

    )

    return 0 if result["overall_passed"] else 1

def _handle_build_and_audit_a_share_owner_operator_experience(args: argparse.Namespace, paths) -> int:
    from trading_core import cli as _cli

    build_result = _cli.build_a_share_owner_operator_experience(

        as_of_date=args.as_of_date,

        mode=args.mode,

        allow_date_mismatch=args.allow_date_mismatch,

        paths=paths,

    )

    audit_result = _cli.audit_a_share_owner_operator_experience(as_of_date=args.as_of_date, paths=paths)

    print(

        {

            "builder_id": build_result["builder_id"],

            "audit_id": audit_result["audit_id"],

            "overall_passed": audit_result["overall_passed"],

            "blocking_reasons": audit_result["blocking_reasons"],

            "warnings": audit_result["warnings"],

            "input_checks": audit_result["input_checks"],

            "operator_experience_checks": audit_result["operator_experience_checks"],

            "test_policy": audit_result["test_policy"],

            "recommended_next_version": audit_result["recommended_next_version"],

        }

    )

    return 0 if audit_result["overall_passed"] else 1


DISPATCH_HANDLERS_LATE: dict[str, Callable[..., int]] = {
    "build-a-share-daily-data-refresh": _handle_build_a_share_daily_data_refresh,
    "audit-a-share-daily-data-refresh": _handle_audit_a_share_daily_data_refresh,
    "build-and-audit-a-share-daily-data-refresh": _handle_build_and_audit_a_share_daily_data_refresh,
    "validate-a-share-current-day-readiness": _handle_validate_a_share_current_day_readiness,
    "run-a-share-current-day-research": _handle_run_a_share_current_day_research,
    "audit-a-share-current-day-research-run": _handle_audit_a_share_current_day_research_run,
    "run-and-audit-a-share-current-day-research": _handle_run_and_audit_a_share_current_day_research,
    "validate-a-share-owner-dashboard-inputs": _handle_validate_a_share_owner_dashboard_inputs,
    "build-a-share-owner-dashboard": _handle_build_a_share_owner_dashboard,
    "audit-a-share-owner-dashboard": _handle_audit_a_share_owner_dashboard,
    "build-and-audit-a-share-owner-dashboard": _handle_build_and_audit_a_share_owner_dashboard,
    "validate-a-share-owner-monitoring-inputs": _handle_validate_a_share_owner_monitoring_inputs,
    "build-a-share-owner-monitoring": _handle_build_a_share_owner_monitoring,
    "audit-a-share-owner-monitoring": _handle_audit_a_share_owner_monitoring,
    "build-and-audit-a-share-owner-monitoring": _handle_build_and_audit_a_share_owner_monitoring,
    "validate-a-share-owner-remediation-inputs": _handle_validate_a_share_owner_remediation_inputs,
    "build-a-share-owner-remediation": _handle_build_a_share_owner_remediation,
    "audit-a-share-owner-remediation": _handle_audit_a_share_owner_remediation,
    "build-and-audit-a-share-owner-remediation": _handle_build_and_audit_a_share_owner_remediation,
    "validate-a-share-daily-ops-inputs": _handle_validate_a_share_daily_ops_inputs,
    "build-a-share-daily-ops-center": _handle_build_a_share_daily_ops_center,
    "audit-a-share-daily-ops-center": _handle_audit_a_share_daily_ops_center,
    "build-and-audit-a-share-daily-ops-center": _handle_build_and_audit_a_share_daily_ops_center,
    "validate-a-share-ops-history-inputs": _handle_validate_a_share_ops_history_inputs,
    "build-a-share-ops-history-baseline": _handle_build_a_share_ops_history_baseline,
    "audit-a-share-ops-history-baseline": _handle_audit_a_share_ops_history_baseline,
    "build-and-audit-a-share-ops-history-baseline": _handle_build_and_audit_a_share_ops_history_baseline,
    "validate-a-share-gated-build-inputs": _handle_validate_a_share_gated_build_inputs,
    "build-a-share-gated-build-from-existing-data": _handle_build_a_share_gated_build_from_existing_data,
    "audit-a-share-gated-build-from-existing-data": _handle_audit_a_share_gated_build_from_existing_data,
    "build-and-audit-a-share-gated-build-from-existing-data": _handle_build_and_audit_a_share_gated_build_from_existing_data,
    "validate-a-share-build-repeatability-inputs": _handle_validate_a_share_build_repeatability_inputs,
    "build-a-share-build-repeatability": _handle_build_a_share_build_repeatability,
    "audit-a-share-build-repeatability": _handle_audit_a_share_build_repeatability,
    "build-and-audit-a-share-build-repeatability": _handle_build_and_audit_a_share_build_repeatability,
    "validate-a-share-build-output-owner-dashboard-inputs": _handle_validate_a_share_build_output_owner_dashboard_inputs,
    "build-a-share-build-output-owner-dashboard": _handle_build_a_share_build_output_owner_dashboard,
    "audit-a-share-build-output-owner-dashboard": _handle_audit_a_share_build_output_owner_dashboard,
    "build-and-audit-a-share-build-output-owner-dashboard": _handle_build_and_audit_a_share_build_output_owner_dashboard,
    "validate-a-share-build-output-ops-refresh-inputs": _handle_validate_a_share_build_output_ops_refresh_inputs,
    "build-a-share-build-output-ops-refresh": _handle_build_a_share_build_output_ops_refresh,
    "audit-a-share-build-output-ops-refresh": _handle_audit_a_share_build_output_ops_refresh,
    "build-and-audit-a-share-build-output-ops-refresh": _handle_build_and_audit_a_share_build_output_ops_refresh,
    "validate-a-share-owner-daily-pack-inputs": _handle_validate_a_share_owner_daily_pack_inputs,
    "build-a-share-owner-daily-pack": _handle_build_a_share_owner_daily_pack,
    "audit-a-share-owner-daily-pack": _handle_audit_a_share_owner_daily_pack,
    "build-and-audit-a-share-owner-daily-pack": _handle_build_and_audit_a_share_owner_daily_pack,
    "validate-a-share-owner-daily-pack-history-inputs": _handle_validate_a_share_owner_daily_pack_history_inputs,
    "build-a-share-owner-daily-pack-history": _handle_build_a_share_owner_daily_pack_history,
    "audit-a-share-owner-daily-pack-history": _handle_audit_a_share_owner_daily_pack_history,
    "build-and-audit-a-share-owner-daily-pack-history": _handle_build_and_audit_a_share_owner_daily_pack_history,
    "validate-a-share-owner-readiness-gate-inputs": _handle_validate_a_share_owner_readiness_gate_inputs,
    "build-a-share-owner-readiness-gate": _handle_build_a_share_owner_readiness_gate,
    "audit-a-share-owner-readiness-gate": _handle_audit_a_share_owner_readiness_gate,
    "build-and-audit-a-share-owner-readiness-gate": _handle_build_and_audit_a_share_owner_readiness_gate,
    "validate-a-share-owner-quality-exceptions-inputs": _handle_validate_a_share_owner_quality_exceptions_inputs,
    "build-a-share-owner-quality-exceptions": _handle_build_a_share_owner_quality_exceptions,
    "audit-a-share-owner-quality-exceptions": _handle_audit_a_share_owner_quality_exceptions,
    "build-and-audit-a-share-owner-quality-exceptions": _handle_build_and_audit_a_share_owner_quality_exceptions,
    "validate-a-share-owner-readiness-recovery-inputs": _handle_validate_a_share_owner_readiness_recovery_inputs,
    "build-a-share-owner-readiness-recovery": _handle_build_a_share_owner_readiness_recovery,
    "audit-a-share-owner-readiness-recovery": _handle_audit_a_share_owner_readiness_recovery,
    "build-and-audit-a-share-owner-readiness-recovery": _handle_build_and_audit_a_share_owner_readiness_recovery,
    "validate-a-share-owner-readiness-recovery-execution-inputs": _handle_validate_a_share_owner_readiness_recovery_execution_inputs,
    "build-a-share-owner-readiness-recovery-execution": _handle_build_a_share_owner_readiness_recovery_execution,
    "audit-a-share-owner-readiness-recovery-execution": _handle_audit_a_share_owner_readiness_recovery_execution,
    "build-and-audit-a-share-owner-readiness-recovery-execution": _handle_build_and_audit_a_share_owner_readiness_recovery_execution,
    "validate-a-share-owner-controlled-gate-reevaluation-inputs": _handle_validate_a_share_owner_controlled_gate_reevaluation_inputs,
    "build-a-share-owner-controlled-gate-reevaluation": _handle_build_a_share_owner_controlled_gate_reevaluation,
    "audit-a-share-owner-controlled-gate-reevaluation": _handle_audit_a_share_owner_controlled_gate_reevaluation,
    "build-and-audit-a-share-owner-controlled-gate-reevaluation": _handle_build_and_audit_a_share_owner_controlled_gate_reevaluation,
    "validate-a-share-owner-recovery-evidence-inputs": _handle_validate_a_share_owner_recovery_evidence_inputs,
    "build-a-share-owner-recovery-evidence": _handle_build_a_share_owner_recovery_evidence,
    "audit-a-share-owner-recovery-evidence": _handle_audit_a_share_owner_recovery_evidence,
    "build-and-audit-a-share-owner-recovery-evidence": _handle_build_and_audit_a_share_owner_recovery_evidence,
    "validate-a-share-owner-evidence-backed-reevaluation-prep-inputs": _handle_validate_a_share_owner_evidence_backed_reevaluation_prep_inputs,
    "build-a-share-owner-evidence-backed-reevaluation-prep": _handle_build_a_share_owner_evidence_backed_reevaluation_prep,
    "audit-a-share-owner-evidence-backed-reevaluation-prep": _handle_audit_a_share_owner_evidence_backed_reevaluation_prep,
    "build-and-audit-a-share-owner-evidence-backed-reevaluation-prep": _handle_build_and_audit_a_share_owner_evidence_backed_reevaluation_prep,
    "validate-a-share-owner-v0820-gate-outcome-inputs": _handle_validate_a_share_owner_v0820_gate_outcome_inputs,
    "build-a-share-owner-v0820-gate-outcome": _handle_build_a_share_owner_v0820_gate_outcome,
    "audit-a-share-owner-v0820-gate-outcome": _handle_audit_a_share_owner_v0820_gate_outcome,
    "build-and-audit-a-share-owner-v0820-gate-outcome": _handle_build_and_audit_a_share_owner_v0820_gate_outcome,
    "validate-a-share-owner-closeout-review-inputs": _handle_validate_a_share_owner_closeout_review_inputs,
    "build-a-share-owner-closeout-review": _handle_build_a_share_owner_closeout_review,
    "audit-a-share-owner-closeout-review": _handle_audit_a_share_owner_closeout_review,
    "build-and-audit-a-share-owner-closeout-review": _handle_build_and_audit_a_share_owner_closeout_review,
    "validate-a-share-owner-operator-experience-inputs": _handle_validate_a_share_owner_operator_experience_inputs,
    "build-a-share-owner-operator-experience": _handle_build_a_share_owner_operator_experience,
    "audit-a-share-owner-operator-experience": _handle_audit_a_share_owner_operator_experience,
    "build-and-audit-a-share-owner-operator-experience": _handle_build_and_audit_a_share_owner_operator_experience,
}
