from __future__ import annotations

import json
from pathlib import Path

from forward_dry_run_day1_test_utils import build_day1_execution_stack, make_day1_paths


MISSING_CONTINUATION = [
    "data/forward_dry_run/day_001/day1_artifact_manifest.json",
    "data/forward_dry_run/day_001/day1_reproducibility_manifest.json",
    "data/forward_dry_run/day_001/day2_readiness_packet.json",
    "data/forward_dry_run/day_001/day2_continuation_gate_preview.json",
]


def make_day1_continuation_paths(tmp_path: Path):
    paths = make_day1_paths(tmp_path)
    build_day1_execution_stack(paths)
    write_v064_blocking_preflight(paths)
    return paths


def write_v064_blocking_preflight(paths) -> None:
    payload = {
        "preflight_id": "FORWARD-DRY-RUN-DAY2-CONTINUATION-PREFLIGHT",
        "baseline_from": "v0.6.3-forward-dry-run-day1-executed-audited",
        "target_version": "v0.6.4-forward-dry-run-day2-continuation-audited",
        "overall_passed": False,
        "day2_execution_allowed": False,
        "release_allowed": False,
        "blocking_reasons": ["required_v063_continuation_artifacts_exist=false"],
        "missing_required_artifacts": MISSING_CONTINUATION,
        "actions_taken": {
            "day2_executed": False,
            "day3_executed": False,
            "run_daily_called": False,
            "release_tag_created": False,
        },
        "boundary": {
            "preflight_only": True,
            "virtual_forward_dry_run_only": True,
            "real_trading": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "main_ledger_written": False,
        },
    }
    json_path = paths.data_dir / "system" / "forward_dry_run_day2_continuation_preflight.json"
    report_path = paths.outputs_dir / "audit" / "FORWARD_DRY_RUN_DAY2_CONTINUATION_PREFLIGHT.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload), encoding="utf-8")
    report_path.write_text("blocking preflight\n", encoding="utf-8")


def build_day1_continuation_stack(paths) -> None:
    from trading_core.forward_dry_run.day1_artifact_manifest import build_day1_artifact_manifest
    from trading_core.forward_dry_run.day1_continuation_artifact_audit import audit_day1_continuation_artifacts
    from trading_core.forward_dry_run.day1_continuation_gap_analysis import build_day1_continuation_gap_analysis
    from trading_core.forward_dry_run.day1_reproducibility_manifest import build_day1_reproducibility_manifest
    from trading_core.forward_dry_run.day2_continuation_gate_preview import build_day2_continuation_gate_preview
    from trading_core.forward_dry_run.day2_readiness_packet import build_day2_readiness_packet
    from trading_core.planning.day1_continuation_reclassification_v0631 import reclassify_day1_continuation_artifacts_v0631

    build_day1_continuation_gap_analysis(paths=paths)
    build_day1_artifact_manifest(paths=paths)
    build_day1_reproducibility_manifest(paths=paths)
    build_day2_readiness_packet(paths=paths)
    build_day2_continuation_gate_preview(paths=paths)
    audit_day1_continuation_artifacts(paths=paths)
    reclassify_day1_continuation_artifacts_v0631(paths=paths)

