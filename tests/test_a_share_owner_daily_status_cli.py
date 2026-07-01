import json
from pathlib import Path

import pytest

from tests.a_share_operator_experience_test_utils import AS_OF_DATE, make_paths, seed_operator_outputs, write_json
from trading_core.cli import build_parser, main


def test_owner_daily_status_cli_command_registered():
    args = build_parser().parse_args(["owner-daily-status", "--as-of-date", AS_OF_DATE])
    assert args.command == "owner-daily-status"
    assert args.format == "text"


def test_owner_daily_status_default_output_is_text_not_json(tmp_path, capsys, monkeypatch):
    paths = _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "trading-core owner daily status" in out
    with pytest.raises(json.JSONDecodeError):
        json.loads(out)
    assert paths.data_dir.exists()


def test_owner_daily_status_output_contains_blocked(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert any("OWNER-READINESS: BLOCKED" in line for line in lines[:10])


def test_owner_daily_status_output_contains_score_threshold_gap(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "score: 54 / threshold: 75 / gap: 21" in out


def test_owner_daily_status_output_contains_v090_full_pytest_passed(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "v0.9.0 full pytest passed: 1701 passed, 1 skipped" in out
    assert "audit sweep passed: true" in out


def test_owner_daily_status_output_contains_data_staleness(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "data staleness" in out
    assert "this version does not refresh data" in out
    assert "v0.9.3-a-share-data-freshness-refresh" in out


def test_owner_daily_status_output_contains_safe_actions(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "safe actions" in out
    assert "View owner daily status" in out


def test_owner_daily_status_output_contains_forbidden_actions(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "forbidden actions" in out
    assert "broker / real account / real orders / order preview" in out
    assert "buy/sell signals / old run-daily / official day2" in out


def test_owner_daily_status_json_format_is_valid_json(tmp_path, capsys, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE, "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "owner-daily-status"
    assert payload["known_owner_readiness_state"] == "blocked"
    assert payload["owner_operationally_acceptable"] is False
    assert payload["readiness_score"] == 54
    assert payload["minimum_owner_readiness_score"] == 75
    assert payload["score_gap"] == 21
    assert payload["v090_full_pytest_passed"] is True
    assert payload["v090_audit_sweep_passed"] is True
    assert payload["data_staleness"]["data_refresh_executed"] is False
    assert len(payload["key_artifacts"]) <= 8


def test_owner_daily_status_does_not_write_files(tmp_path, capsys, monkeypatch):
    paths = _seed(tmp_path, monkeypatch)
    before = _file_snapshot(paths.project_root)
    assert main(["owner-daily-status", "--as-of-date", AS_OF_DATE]) == 0
    capsys.readouterr()
    after = _file_snapshot(paths.project_root)
    assert after == before


def _seed(tmp_path: Path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    write_json(
        paths.data_dir / "equity_data_quality" / "a_share_owner_operator_experience_audit.json",
        {"as_of_date": AS_OF_DATE, "overall_passed": True, "blocking_reasons": []},
    )
    write_json(
        paths.data_dir / "equity_owner_v090_rc" / "daily" / AS_OF_DATE / "v090_audit_sweep_result.json",
        {"as_of_date": AS_OF_DATE, "audit_sweep_passed": True, "overall_passed": True, "blocking_reasons": []},
    )
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    return paths


def _file_snapshot(project_root: Path) -> set[str]:
    roots = [project_root / "data", project_root / "outputs", project_root / "docs"]
    return {
        str(path.relative_to(project_root)).replace("\\", "/")
        for root in roots
        if root.exists()
        for path in root.rglob("*")
        if path.is_file()
    }
