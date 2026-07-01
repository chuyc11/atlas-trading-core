import json
from pathlib import Path

from trading_core.storage.file_paths import ProjectPaths

AS_OF_DATE = "2026-06-26"
SOURCE_RELEASE = "v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression"


def make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path
    project = root / "work" / "trading-core"
    (project / "data").mkdir(parents=True, exist_ok=True)
    (project / "outputs").mkdir(parents=True, exist_ok=True)
    return ProjectPaths(root)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def seed_operator_inputs(paths: ProjectPaths, as_of_date: str = AS_OF_DATE) -> None:
    v090_root = paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date
    closeout_root = paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date
    (paths.outputs_dir / "equity_owner_closeout_review" / "daily" / as_of_date).mkdir(parents=True, exist_ok=True)
    summary = {
        "target_version": SOURCE_RELEASE,
        "as_of_date": as_of_date,
        "source_gate_decision": "blocked",
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "previous_readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "full_pytest_passed": True,
        "audit_sweep_passed": True,
    }
    full_pytest = {
        "result_id": "A-SHARE-V090-FULL-PYTEST-RESULT",
        "target_version": SOURCE_RELEASE,
        "as_of_date": as_of_date,
        "command": "python -m pytest",
        "full_pytest_run": True,
        "full_pytest_skipped": False,
        "exit_code": 0,
        "passed_count": 1701,
        "failed_count": 0,
        "skipped_count": 1,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
    }
    disclosure = {
        "target_version": SOURCE_RELEASE,
        "as_of_date": as_of_date,
        "owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "previous_readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "blocked_state_intentional": True,
        "blocked_state_audited": True,
        "blocked_state_misrepresented_as_acceptable": False,
        "blocks_v090_rc": False,
        "overall_passed": True,
        "blocking_reasons": [],
    }
    boundary = {
        "target_version": SOURCE_RELEASE,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
    }
    decision = {
        "target_version": SOURCE_RELEASE,
        "as_of_date": as_of_date,
        "decision": "v090_rc_passed_with_known_blocked_owner_readiness",
        "overall_passed": True,
        "blocking_reasons": [],
    }
    audit = {
        "audit_id": "A-SHARE-OWNER-V090-RC-AUDIT",
        "target_version": SOURCE_RELEASE,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "blocking_reasons": [],
        "release_candidate_decision": "v090_rc_passed_with_known_blocked_owner_readiness",
    }
    generic = {"target_version": SOURCE_RELEASE, "as_of_date": as_of_date, "overall_passed": True, "blocking_reasons": []}
    for name in [
        "v090_rc_config",
        "v090_input_availability",
        "v090_source_resolution",
        "v090_date_alignment",
        "v090_audit_sweep_result",
        "v090_boundary_sweep_result",
        "v090_source_trace_sweep_result",
        "v090_documentation_freeze_result",
        "v090_source_trace",
        "v090_manifest",
    ]:
        write_json(v090_root / f"{name}.json", generic)
    write_json(v090_root / "v090_full_pytest_result.json", full_pytest)
    write_json(v090_root / "v090_known_blocked_state_disclosure.json", disclosure)
    write_json(v090_root / "v090_release_candidate_decision.json", decision)
    write_json(v090_root / "v090_owner_release_summary.json", summary)
    write_json(v090_root / "v090_boundary_check.json", boundary)
    write_json(paths.data_dir / "equity_data_quality" / "a_share_owner_v090_rc_audit.json", audit)
    write_json(paths.data_dir / "equity_data_quality" / "a_share_owner_closeout_review_audit.json", {"overall_passed": True, "as_of_date": as_of_date})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_owner_v0820_gate_outcome_audit.json", {"overall_passed": True, "as_of_date": as_of_date})
    write_json(
        closeout_root / "unresolved_blocker_register.json",
        {
            "as_of_date": as_of_date,
            "unresolved_blocker_count": 7,
            "blockers_that_block_owner_readiness_acceptance": 6,
            "blockers_that_block_v090_rc": 0,
            "blockers": [
                {
                    "blocker_id": "B001",
                    "category": "readiness_score_gap",
                    "description": "Owner-readiness score remains below threshold.",
                    "owner_visible": True,
                    "blocks_owner_readiness_acceptance": True,
                    "blocks_v090_rc": False,
                    "recommended_resolution": "Collect future evidence.",
                }
            ],
        },
    )
    (paths.outputs_dir / "equity_owner_closeout_review" / "daily" / as_of_date / "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md").write_text("# closeout\n", encoding="utf-8")


def seed_operator_outputs(paths: ProjectPaths, as_of_date: str = AS_OF_DATE):
    seed_operator_inputs(paths, as_of_date)
    from trading_core.equity_owner_operator_experience.builder import build_a_share_owner_operator_experience

    return build_a_share_owner_operator_experience(paths=paths, as_of_date=as_of_date)


def operator_data(paths: ProjectPaths, name: str, as_of_date: str = AS_OF_DATE):
    return json.loads((paths.data_dir / "equity_owner_operator_experience" / "daily" / as_of_date / name).read_text(encoding="utf-8"))
