"""Tests for v0.5.1 remediation artifact."""

from __future__ import annotations

from pathlib import Path

from trading_core.reports.v051_validation_gap_remediation import write_v051_validation_gap_remediation
from trading_core.storage.file_paths import ProjectPaths


def test_v051_remediation_artifacts_and_boundary(tmp_path: Path) -> None:
    paths = ProjectPaths(workspace_root=tmp_path)

    result = write_v051_validation_gap_remediation(paths)

    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert [gap["gap_id"] for gap in result["remediated_gaps"]] == ["GAP-002", "GAP-003", "GAP-004"]
    assert [gap["gap_id"] for gap in result["deferred_gaps"]] == ["GAP-001", "GAP-005"]
    assert result["boundary"]["write_main_ledger"] is False
    assert result["boundary"]["run_daily_called"] is False
    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "# v0.5.1 Validation Gap Remediation" in report
    assert "max_daily_turnover enforcement" in report
    assert "run-daily not called" in report
