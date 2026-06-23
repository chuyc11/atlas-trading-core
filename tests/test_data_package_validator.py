from __future__ import annotations

from pathlib import Path

from trading_core.data.data_package_validator import validate_data_package
from trading_core.data.historical_prices import import_prices_csv, load_imported_prices
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json


HEADER = "date,symbol,open,high,low,close,volume,source,quality"


def _write_csv(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_validate_data_package_accepts_directory_and_warns_on_suspicious_return(tmp_path: Path) -> None:
    data_dir = tmp_path / "package"
    _write_csv(
        data_dir / "part1.csv",
        [
            "2026-01-01,510300.SH,4.00,4.05,3.99,4.02,1000,test,fresh",
            "2026-01-02,510300.SH,4.80,4.90,4.70,4.85,1000,test,fresh",
        ],
    )
    _write_csv(
        data_dir / "part2.csv",
        [
            "2026-01-01,159915.SZ,2.00,2.05,1.99,2.02,1000,test,fallback",
            "2026-01-05,159915.SZ,2.01,2.04,2.00,2.03,1000,test,stale",
        ],
    )

    result = validate_data_package(data_dir, project_paths(tmp_path), timestamp="20260101-000000")

    assert result["passed"] is True
    assert result["total_rows"] == 4
    assert result["symbols_count"] == 2
    assert result["suspicious_return_count"] == 1
    assert result["quality_distribution"] == {"fallback": 1, "fresh": 2, "stale": 1}
    assert result["missing_trading_days_by_symbol"]["159915.SZ"] == 1
    assert Path(result["report_path"]).name == "DATA_PACKAGE_VALIDATION-20260101-000000.md"
    assert Path(result["json_path"]).name == "data_validation.json"
    assert read_json(Path(result["json_path"]))["passed"] is True


def test_validate_data_package_fails_dirty_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "dirty.csv"
    _write_csv(
        csv_path,
        [
            "2026-01-01,510300.SH,4.00,4.05,3.99,4.02,1000,test,fresh",
            "2026-01-01,510300.SH,4.00,3.90,3.99,4.02,1000,test,bad_quality",
            "not-a-date,,0,4.05,3.99,4.02,-1,test,fresh",
        ],
    )

    result = validate_data_package(csv_path, project_paths(tmp_path), timestamp="20260101-000000")

    assert result["passed"] is False
    assert result["duplicate_records_count"] == 1
    assert result["ohlc_anomaly_count"] >= 2
    assert result["missing_values_count"] == 1
    assert any("invalid quality" in error for error in result["errors"])


def test_import_prices_csv_accepts_directory(tmp_path: Path) -> None:
    data_dir = tmp_path / "package"
    _write_csv(data_dir / "a.csv", ["2026-01-01,510300.SH,4.00,4.05,3.99,4.02,1000,test,fresh"])
    _write_csv(data_dir / "b.csv", ["2026-01-01,159915.SZ,2.00,2.05,1.99,2.02,1000,test,fresh"])
    paths = project_paths(tmp_path)

    result = import_prices_csv(data_dir, "A_SHARE", paths)

    assert result["rows_imported"] == 2
    assert len(result["input_files"]) == 2
    assert len(load_imported_prices("A_SHARE", paths)) == 2
