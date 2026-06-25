from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, real_fixture_path, write_text
from trading_core.global_briefing.real_package_coverage_audit import audit_global_briefing_package_coverage
from trading_core.global_briefing.real_package_normalizer import normalize_global_briefing_package


def _normalized(paths) -> str:
    result = normalize_global_briefing_package(real_fixture_path(paths, "real_package_aliases.csv"), package_id="GB-REAL-FIXTURE", source="global_briefing", version="v1", paths=paths)
    return result["output"]


def test_adequate_coverage_passed(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = audit_global_briefing_package_coverage(_normalized(paths), prices_path=real_fixture_path(paths, "prices_valid.csv"), start_date="2024-01-02", end_date="2024-01-08", min_coverage=0.60, paths=paths)

    assert result["overall_passed"] is True
    assert result["coverage"]["coverage_ratio"] == 0.6


def test_inadequate_coverage_strict_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = audit_global_briefing_package_coverage(_normalized(paths), prices_path=real_fixture_path(paths, "prices_valid.csv"), start_date="2024-01-02", end_date="2024-01-08", min_coverage=0.90, strict=True, paths=paths)

    assert result["overall_passed"] is False
    assert any("coverage below" in item for item in result["blocking_reasons"])


def test_missing_signals_blocks(tmp_path: Path) -> None:
    result = audit_global_briefing_package_coverage("missing.jsonl", start_date="2024-01-02", end_date="2024-01-08", paths=make_paths(tmp_path))

    assert result["overall_passed"] is False


def test_future_signal_leakage_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = audit_global_briefing_package_coverage(real_fixture_path(paths, "real_package_future.jsonl"), start_date="2024-01-03", end_date="2024-01-03", paths=paths)

    assert any("future signal leakage" in item for item in result["blocking_reasons"])


def test_duplicate_signals_warn(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = audit_global_briefing_package_coverage(_normalized(paths), prices_path=real_fixture_path(paths, "prices_valid.csv"), start_date="2024-01-02", end_date="2024-01-08", min_coverage=0.60, paths=paths)

    assert result["coverage"]["duplicate_signal_days"] == ["2024-01-05"]
    assert any("duplicate signal days" in item for item in result["warnings"])


def test_timezone_ambiguity_warns(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "tz.jsonl", '{"as_of_date":"2024-01-02","generated_at":"2024-01-02T06:00:00","region":"CN","signals":{"risk_on":0.1},"source":"global_briefing","version":"v1"}\n')

    result = audit_global_briefing_package_coverage("tz.jsonl", start_date="2024-01-02", end_date="2024-01-02", paths=paths)

    assert result["point_in_time"]["timezone_ambiguous_rows"] == 1


def test_price_expected_dates_and_missing_days_recorded(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = audit_global_briefing_package_coverage(_normalized(paths), prices_path=real_fixture_path(paths, "prices_valid.csv"), start_date="2024-01-02", end_date="2024-01-08", min_coverage=0.60, paths=paths)

    assert result["coverage"]["expected_days"] == 5
    assert "2024-01-04" in result["coverage"]["missing_signal_days"]


def test_region_source_inconsistency_warns(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.project_root / "inconsistent.jsonl",
        '{"as_of_date":"2024-01-02","generated_at":"2024-01-02T06:00:00Z","region":"CN","signals":{"risk_on":0.1},"source":"a","version":"v1"}\n'
        '{"as_of_date":"2024-01-03","generated_at":"2024-01-03T06:00:00Z","region":"HK","signals":{"risk_on":0.1},"source":"b","version":"v1"}\n',
    )

    result = audit_global_briefing_package_coverage("inconsistent.jsonl", start_date="2024-01-02", end_date="2024-01-03", paths=paths)

    assert any("inconsistency" in item for item in result["warnings"])


def test_coverage_boundaries(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = audit_global_briefing_package_coverage(_normalized(paths), start_date="2024-01-02", end_date="2024-01-08", paths=paths)

    assert result["boundary"]["run_daily_called"] is False
    assert_no_protected_paths(paths)


def test_coverage_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    signals = _normalized(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["audit-global-briefing-package-coverage", "--signals", signals, "--prices", real_fixture_path(paths, "prices_valid.csv"), "--start-date", "2024-01-02", "--end-date", "2024-01-08", "--min-coverage", "0.60"]) == 0
