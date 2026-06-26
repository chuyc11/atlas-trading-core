from __future__ import annotations

import json

from forward_dry_run_day1_continuation_test_utils import build_day1_continuation_stack, make_day1_continuation_paths


def make_day1_owner_report_paths(tmp_path):
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    write_v064_fail_closed_evidence(paths)
    return paths


def write_v064_fail_closed_evidence(paths) -> None:
    preflight = {
        "preflight_id": "FORWARD-DRY-RUN-DAY2-CONTINUATION-PREFLIGHT-V064",
        "baseline_tag": "v0.6.3.1-forward-dry-run-day1-continuation-artifacts",
        "target_version": "v0.6.4-forward-dry-run-day2-continuation-audited",
        "overall_passed": False,
        "blocking_reasons": [
            "eligible_day2_local_date_exists=false",
            "no_eligible_local_trading_date_after_day1_as_of_date=2026-06-25",
        ],
        "local_data_coverage": {
            "latest_common_local_data_date": "2026-06-25",
            "common_dates_after_day1": [],
        },
        "actions_taken": {
            "day2_executed": False,
            "day3_executed": False,
            "run_daily_called": False,
            "release_tag_created": False,
        },
        "boundary": {
            "preflight_only": True,
            "day2_executed": False,
            "run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
    readiness = {
        "audit_id": "FORWARD-DRY-RUN-DAY2-INPUT-READINESS-AUDIT",
        "baseline_tag": "v0.6.3.1-forward-dry-run-day1-continuation-artifacts",
        "target_version": "v0.6.4-forward-dry-run-day2-continuation-audited",
        "overall_passed": False,
        "blocking_reasons": ["no_eligible_local_trading_date_after_day1_as_of_date=2026-06-25"],
        "day2_candidate_date": None,
        "eligible_day2_local_date_exists": False,
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "required_next_action": "load_authorized_local_market_benchmark_and_risk_proxy_data_after_2026-06-25_before_day2",
        "actions_taken": {
            "day2_executed": False,
            "day3_executed": False,
            "run_daily_called": False,
            "release_tag_created": False,
        },
        "boundary": {
            "audit_only": True,
            "day2_executed": False,
            "run_daily_called": False,
            "external_api_called": False,
            "real_time_market_data_downloaded": False,
            "broker_connected": False,
            "real_orders_placed": False,
        },
    }
    files = {
        "data/system/forward_dry_run_day2_continuation_preflight_v064.json": json.dumps(preflight),
        "data/system/forward_dry_run_day2_input_readiness_audit.json": json.dumps(readiness),
        "outputs/audit/FORWARD_DRY_RUN_DAY2_CONTINUATION_PREFLIGHT_V064.md": "day2 was not executed\n",
        "outputs/audit/FORWARD_DRY_RUN_DAY2_INPUT_READINESS_AUDIT.md": "day2 input readiness blocked\n",
    }
    for relative, content in files.items():
        path = paths.project_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def build_owner_report_pack(paths) -> None:
    from trading_core.forward_dry_run.day1_continuation_blocker_note import build_day1_continuation_blocker_note
    from trading_core.forward_dry_run.day1_data_reproducibility_appendix import build_day1_data_reproducibility_appendix
    from trading_core.forward_dry_run.day1_isolated_ledger_report import build_day1_isolated_ledger_report
    from trading_core.forward_dry_run.day1_owner_report_pack_summary import build_day1_owner_report_pack_summary
    from trading_core.forward_dry_run.day1_owner_report_scope_plan import build_day1_owner_report_scope_plan
    from trading_core.forward_dry_run.day1_owner_summary_report import build_day1_owner_summary_report
    from trading_core.forward_dry_run.day1_strategy_signal_explanation import build_day1_strategy_signal_explanation
    from trading_core.forward_dry_run.day1_virtual_order_fill_report import build_day1_virtual_order_fill_report

    build_day1_owner_report_scope_plan(paths=paths)
    build_day1_owner_summary_report(paths=paths)
    build_day1_strategy_signal_explanation(paths=paths)
    build_day1_virtual_order_fill_report(paths=paths)
    build_day1_isolated_ledger_report(paths=paths)
    build_day1_data_reproducibility_appendix(paths=paths)
    build_day1_continuation_blocker_note(paths=paths)
    build_day1_owner_report_pack_summary(paths=paths)
