from __future__ import annotations

from pathlib import Path

import pytest

from day0_test_utils import make_day0_paths
from global_briefing_test_utils import write_json
from trading_core.forward_dry_run.day0_warning_register import build_day0_warning_register


def test_day0_warning_register_classifies_known_warnings(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    result = build_day0_warning_register(paths=paths)
    assert result["accepted_count"] == 6
    assert result["unresolved_count"] == 0
    assert result["blocking_count"] == 0
    assert {item["category"] for item in result["warnings"]} >= {"source_download_failed", "coverage_gap", "lot_size_constraint"}
    assert "Day-0 Accepted Warning Register" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_day0_warning_register_blocks_low_coverage_and_bad_epu_oecd(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    report_path = paths.data_dir / "system" / "historical_data_gap_closure_report.json"
    write_json(report_path, {"epu": {"current_status": "failed"}, "oecd": {"current_status": "downloaded", "source": "official"}, "proxy_coverage_ratio": {"current": 0.70}})
    result = build_day0_warning_register(paths=paths)
    assert result["blocking_count"] >= 2
    assert any(item["category"] == "coverage_gap" and item["status"] == "blocking" for item in result["warnings"])


def test_day0_warning_register_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["day0-warning-register"]) == 0
