from __future__ import annotations

import csv
from pathlib import Path

from trading_core.data.price_dataset_merge import merge_price_data
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_jsonl


HEADER = "date,symbol,open,high,low,close,volume,source,quality"


def _write_csv(path: Path, rows: list[str], header: str = HEADER) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_merge_price_data_combines_directories_and_validates(tmp_path: Path) -> None:
    dir_a = tmp_path / "manual"
    dir_b = tmp_path / "yf"
    output = tmp_path / "merged"
    _write_csv(dir_a / "510300.SH.csv", ["2026-01-01,510300.SH,4.0,4.1,3.9,4.05,1000,manual_csv,fresh"])
    _write_csv(dir_b / "159915.SZ.csv", ["2026-01-01,159915.SZ,2.0,2.1,1.9,2.05,1000,yfinance,fresh"])

    result = merge_price_data([dir_a, dir_b], output, project_paths(tmp_path))

    assert result["manifest"]["passed"] is True
    assert result["manifest"]["total_output_rows"] == 2
    assert (output / "510300.SH.csv").exists()
    assert (output / "159915.SZ.csv").exists()
    assert result["validation"]["passed"] is True


def test_merge_price_data_uses_source_priority_and_discards_duplicate(tmp_path: Path) -> None:
    manual = tmp_path / "manual"
    yf = tmp_path / "yf"
    output = tmp_path / "merged"
    _write_csv(manual / "510300.SH.csv", ["2026-01-01,510300.SH,4.0,4.1,3.9,4.05,1000,manual_csv,fresh"])
    _write_csv(yf / "510300.SH.csv", ["2026-01-01,510300.SH,9.0,9.1,8.9,9.05,1000,yfinance,fresh"])

    result = merge_price_data([yf, manual], output, project_paths(tmp_path))

    with (output / "510300.SH.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    discarded = read_jsonl(output / "discarded_records.jsonl")

    assert rows[0]["source"] == "manual_csv"
    assert rows[0]["close"] == "4.05"
    assert result["manifest"]["duplicate_records_count"] == 1
    assert result["manifest"]["discarded_records_count"] == 1
    assert discarded[0]["source"] == "yfinance"
    assert discarded[0]["discard_reason"] == "duplicate_lower_priority"


def test_merge_price_data_fails_on_missing_columns(tmp_path: Path) -> None:
    bad = tmp_path / "bad"
    output = tmp_path / "merged"
    _write_csv(
        bad / "bad.csv",
        ["2026-01-01,510300.SH,4.0,4.1,3.9,4.05,1000,manual_csv"],
        header="date,symbol,open,high,low,close,volume,source",
    )

    result = merge_price_data([bad], output, project_paths(tmp_path))

    assert result["manifest"]["passed"] is False
    assert result["manifest"]["errors"]
    assert result["validation"]["passed"] is False
