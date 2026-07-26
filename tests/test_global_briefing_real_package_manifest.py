from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, make_paths, write_json, write_text
from trading_core.global_briefing.real_package_manifest import build_global_briefing_package_manifest


def test_empty_directory_does_not_crash(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    (paths.project_root / "empty").mkdir(parents=True)

    result = build_global_briefing_package_manifest(root="empty", paths=paths)

    assert result["counts"]["packages"] == 0


def test_jsonl_package_discovered(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    result = build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)

    assert any(item["format"] == "jsonl" and "real_package_canonical" in item["path"] for item in result["packages"])


def test_json_package_discovered(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_json(paths.project_root / "data" / "global_briefing" / "package.json", {"signals": [{"as_of_date": "2024-01-02", "region": "CN", "source": "global_briefing"}]})

    result = build_global_briefing_package_manifest(root="data/global_briefing", paths=paths)

    assert result["counts"]["json"] == 1


def test_csv_package_discovered(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)

    assert result["counts"]["csv"] >= 1


def test_unsupported_file_warns(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "data" / "global_briefing" / "readme.txt", "not a package")

    result = build_global_briefing_package_manifest(root="data/global_briefing", paths=paths)

    assert any("unsupported package file" in item for item in result["warnings"])


def test_parquet_dependency_warning_not_blocking(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(paths.project_root / "data" / "global_briefing" / "sample.parquet", "not parquet")

    result = build_global_briefing_package_manifest(root="data/global_briefing", paths=paths)

    assert result["counts"]["parquet"] == 1
    assert any("parquet support is optional" in item for package in result["packages"] for item in package["warnings"])


def test_detected_rows_and_dates_region_source(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)
    canonical = next(item for item in result["packages"] if "real_package_canonical" in item["path"])

    assert canonical["detected_rows"] == 4
    assert canonical["date_min"] == "2024-01-02"
    assert canonical["date_max"] == "2024-01-05"
    assert canonical["region_values"] == ["CN"]
    assert canonical["source_values"] == ["global_briefing"]


def test_manifest_boundary_no_network_no_main_ledger(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = build_global_briefing_package_manifest(root="tests/fixtures/global_briefing_real", paths=paths)

    assert result["boundary"]["network_access"] is False
    assert_no_protected_paths(paths)


def test_manifest_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-package-manifest", "--root", "tests/fixtures/global_briefing_real"]) == 0


def test_manifest_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["global-briefing-package-manifest", "--root", "tests/fixtures/global_briefing_real"]) == 0
    assert (paths.data_dir / "system" / "global_briefing_package_manifest.json").exists()
