"""CLI dispatch handlers: versions commands (EARLY and LATE regions)."""

from __future__ import annotations

from collections.abc import Callable

import argparse


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












DISPATCH_HANDLERS_EARLY: dict[str, Callable[..., int]] = {
    "build-a-share-v100-prep": _handle_build_a_share_v100_prep,
    "audit-a-share-v100-prep": _handle_audit_a_share_v100_prep,
    "build-and-audit-a-share-v100-prep": _handle_build_and_audit_a_share_v100_prep,
    "build-a-share-v100-release": _handle_build_a_share_v100_release,
    "audit-a-share-v100-release": _handle_audit_a_share_v100_release,
    "build-and-audit-a-share-v100-release": _handle_build_and_audit_a_share_v100_release,
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
