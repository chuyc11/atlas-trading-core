from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from trading_core.features.feature_store import build_feature_matrix
from trading_core.storage.file_paths import project_paths


def _trading_days(count: int, start: date = date(2026, 1, 1)) -> list[str]:
    days = []
    current = start
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def _write_prices(path: Path, days: list[str], *, skip_index: int | None = None) -> None:
    path.mkdir(parents=True, exist_ok=True)
    rows = ["date,symbol,open,high,low,close,volume,source,quality"]
    for index, day in enumerate(days):
        if skip_index is not None and index == skip_index:
            continue
        close = 100.0 + index
        rows.append(f"{day},510300.SH,{close - 0.5},{close + 1.0},{close - 1.0},{close},{1000 + index * 10},test,fresh")
    (path / "510300.SH.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _read_feature_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_feature_store_writes_feature_file_and_report(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_feature_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))

    output_path = Path(result["output_path"])
    report_path = Path(result["report_path"])
    rows = _read_feature_rows(output_path)

    assert output_path.name == f"feature_matrix-{days[0]}-{days[-1]}.csv"
    assert report_path.name == f"FEATURE_REPORT-{days[0]}-{days[-1]}.md"
    assert result["rows"] == 25
    assert rows[0]["feature_version"] == "feature_store_v1"
    assert rows[0]["source"] == "test"
    assert rows[0]["quality"] == "fresh"
    report = report_path.read_text(encoding="utf-8")
    assert "leakage_check_passed: True" in report
    assert "missing feature counts" in report


def test_return_5d_uses_only_past_data(tmp_path: Path) -> None:
    days = _trading_days(10)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_feature_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_feature_rows(Path(result["output_path"]))

    expected = (105.0 / 100.0) - 1
    assert abs(float(rows[5]["return_5d"]) - expected) < 0.0000000001


def test_volatility_20d_uses_only_past_data(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)
    result = build_feature_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    before = _read_feature_rows(Path(result["output_path"]))[20]["volatility_20d"]

    path = data_dir / "510300.SH.csv"
    lines = path.read_text(encoding="utf-8").splitlines()
    future = lines[22].split(",")
    future[5] = "9999"
    lines[22] = ",".join(future)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result_after = build_feature_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    after = _read_feature_rows(Path(result_after["output_path"]))[20]["volatility_20d"]

    assert before == after


def test_missing_price_day_does_not_crash(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days, skip_index=7)

    result = build_feature_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_feature_rows(Path(result["output_path"]))

    assert result["rows"] == 24
    assert all(row["date"] != days[7] for row in rows)


def test_feature_store_does_not_write_main_account_ledgers(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    build_feature_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    paths = project_paths(tmp_path)

    assert not (paths.data_dir / "orders").exists()
    assert not (paths.data_dir / "trades").exists()
    assert not (paths.data_dir / "portfolios").exists()
    assert (paths.data_dir / "features" / f"feature_matrix-{days[0]}-{days[-1]}.csv").exists()
