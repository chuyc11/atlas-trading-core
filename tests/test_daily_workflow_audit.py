from pathlib import Path
import json

import pytest

from daily_workflow_test_utils import AS_OF, build_daily_workflow_stack, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_workflow_audit import audit_daily_workflow


def test_daily_workflow_audit_passes(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    build_daily_workflow_stack(paths)
    result = audit_daily_workflow(as_of_date=AS_OF, paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["summary"]["strategies_with_daily_signals"] == 3
    assert result["summary"]["protected_path_blocker_count"] == 0
    assert result["summary"]["recommended_next_version"] == "v0.6.2-forward-dry-run-start-authorization-pack"
    assert "v0.6.1-daily-workflow-binding-audited" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_daily_workflow_audit_blocks_missing_artifacts_and_bad_boundaries(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    build_daily_workflow_stack(paths)
    (paths.data_dir / "daily_workflow" / "snapshots" / f"daily_market_data_snapshot-{AS_OF}.json").unlink()
    (paths.data_dir / "daily_workflow" / "freeze_manifests" / f"daily_input_freeze_manifest-{AS_OF}.json").unlink()
    signals = paths.data_dir / "daily_workflow" / "signals" / f"daily_baseline_signals-{AS_OF}.json"
    signals.unlink()
    preview = paths.data_dir / "daily_workflow" / "order_previews" / f"daily_order_preview-{AS_OF}.json"
    payload = json.loads(preview.read_text(encoding="utf-8"))
    payload["executed"] = True
    preview.write_text(json.dumps(payload), encoding="utf-8")
    execution = paths.data_dir / "daily_workflow" / "execution_previews" / f"daily_isolated_execution_preview-{AS_OF}.json"
    execution_payload = json.loads(execution.read_text(encoding="utf-8"))
    execution_payload["state_updated"] = True
    execution.write_text(json.dumps(execution_payload), encoding="utf-8")
    (paths.data_dir / "daily_workflow" / "reports" / f"daily_report_packet-{AS_OF}.json").unlink()
    residue = paths.data_dir / "system" / "protected_path_residue_scan.json"
    residue_payload = json.loads(residue.read_text(encoding="utf-8"))
    residue_payload["blocker_count"] = 1
    residue.write_text(json.dumps(residue_payload), encoding="utf-8")
    (paths.outputs_dir / "daily_workflow" / "BAD_WORDING.md").write_text(
        "strategy effectiveness proven\nML approved for trading\nLLM approved for trading\nRL approved for trading\nproduction daily trading ready\n",
        encoding="utf-8",
    )
    result = audit_daily_workflow(as_of_date=AS_OF, paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"]).lower()
    for expected in ["snapshot", "freeze", "daily signals", "executed", "state_updated", "daily report", "protected path blocker", "strategy effectiveness proven", "production daily trading ready"]:
        assert expected in joined


def test_daily_workflow_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    build_daily_workflow_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-daily-workflow", "--as-of-date", AS_OF]) == 0

