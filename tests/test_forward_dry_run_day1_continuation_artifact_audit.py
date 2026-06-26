from __future__ import annotations

import json
from pathlib import Path

import pytest

from forward_dry_run_day1_continuation_test_utils import build_day1_continuation_stack, make_day1_continuation_paths
from trading_core.forward_dry_run.day1_continuation_artifact_audit import audit_day1_continuation_artifacts


def test_day1_continuation_artifact_audit_passes(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    result = audit_day1_continuation_artifacts(paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["warnings"] == []
    assert result["summary"]["missing_continuation_artifacts_resolved"] is True
    assert result["summary"]["recommended_next_version"] == "v0.6.4-forward-dry-run-day2-continuation"
    assert result["boundary"]["day2_executed"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["main_ledger_written"] is False


@pytest.mark.parametrize(
    ("relative", "expected"),
    [
        ("data/system/forward_dry_run_day1_continuation_gap_analysis.json", "gap_analysis_missing"),
        ("data/forward_dry_run/day_001/day1_artifact_manifest.json", "day1_artifact_manifest_missing"),
        ("data/forward_dry_run/day_001/day1_reproducibility_manifest.json", "day1_reproducibility_manifest_missing"),
        ("data/forward_dry_run/day_001/day2_readiness_packet.json", "day2_readiness_packet_missing"),
        ("data/forward_dry_run/day_001/day2_continuation_gate_preview.json", "day2_continuation_gate_preview_missing"),
    ],
)
def test_day1_continuation_artifact_audit_blocks_missing_inputs(tmp_path: Path, relative: str, expected: str) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    (paths.project_root / relative).unlink()
    result = audit_day1_continuation_artifacts(paths=paths)
    assert result["overall_passed"] is False
    assert expected in result["blocking_reasons"]


def test_day1_continuation_artifact_audit_blocks_boundary_true(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    packet_path = paths.data_dir / "forward_dry_run" / "day_001" / "day2_readiness_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["boundary"]["main_ledger_written"] = True
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    result = audit_day1_continuation_artifacts(paths=paths)
    assert result["overall_passed"] is False
    assert "main_ledger_written=true" in result["blocking_reasons"]


def test_day1_continuation_artifact_audit_blocks_day2_execution_marker(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    marker = paths.data_dir / "forward_dry_run" / "day_002" / "day2_virtual_execution_result.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"executed": True}), encoding="utf-8")
    result = audit_day1_continuation_artifacts(paths=paths)
    assert result["overall_passed"] is False
    assert "day2_executed=true" in result["blocking_reasons"]


def test_day1_continuation_artifact_audit_blocks_forbidden_wording(tmp_path: Path) -> None:
    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    (paths.outputs_dir / "forward_dry_run" / "day_001" / "BAD.md").write_text("strategy effectiveness proven\n", encoding="utf-8")
    result = audit_day1_continuation_artifacts(paths=paths)
    assert result["overall_passed"] is False
    assert any("strategy effectiveness proven" in item for item in result["blocking_reasons"])


def test_day1_continuation_artifact_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day1_continuation_paths(tmp_path)
    build_day1_continuation_stack(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-forward-dry-run-day1-continuation-artifacts"]) == 0

