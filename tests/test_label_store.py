from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from trading_core import cli
from trading_core.daily_run import run_daily
from trading_core.labels.label_store import build_label_matrix
from trading_core.storage.file_paths import project_paths


def _trading_days(count: int, start: date = date(2026, 1, 1)) -> list[str]:
    days = []
    current = start
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def _write_prices(path: Path, days: list[str]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    symbol_specs = {
        "510300.SH": {"base": 100.0, "step": 1.0},
        "159915.SZ": {"base": 50.0, "step": 1.0},
    }
    for symbol, spec in symbol_specs.items():
        rows = ["date,symbol,open,high,low,close,volume,source,quality"]
        for index, day in enumerate(days):
            close = spec["base"] + spec["step"] * index
            rows.append(
                f"{day},{symbol},{close - 0.5},{close + 1.0},{close - 1.0},{close},{1000 + index * 10},test,fresh"
            )
        (path / f"{symbol}.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _read_label_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _row(rows: list[dict[str, str]], day: str, symbol: str) -> dict[str, str]:
    return next(row for row in rows if row["date"] == day and row["symbol"] == symbol)


def test_label_store_writes_label_file_and_report(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))

    output_path = Path(result["output_path"])
    report_path = Path(result["report_path"])
    rows = _read_label_rows(output_path)

    assert output_path.name == f"label_matrix-{days[0]}-{days[-1]}.csv"
    assert report_path.name == f"LABEL_REPORT-{days[0]}-{days[-1]}.md"
    assert result["rows"] == 50
    assert rows[0]["label_version"] == "etf_label_v1"
    assert rows[0]["source"] == "test"
    assert rows[0]["quality"] == "fresh"
    report = report_path.read_text(encoding="utf-8")
    assert "labels are offline-only" in report
    assert "labels use future data by design" in report
    assert "labels must not be used in run-daily decision path" in report
    assert "offline_only=true" in report


def test_future_1d_return_is_correct(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_label_rows(Path(result["output_path"]))

    expected = (101.0 / 100.0) - 1
    assert abs(float(_row(rows, days[0], "510300.SH")["future_1d_return"]) - expected) < 0.0000000001


def test_future_5d_return_is_correct(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_label_rows(Path(result["output_path"]))

    expected = (105.0 / 100.0) - 1
    assert abs(float(_row(rows, days[0], "510300.SH")["future_5d_return"]) - expected) < 0.0000000001


def test_future_5d_excess_vs_equal_etf_is_correct(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_label_rows(Path(result["output_path"]))

    symbol_return = (105.0 / 100.0) - 1
    peer_return = (55.0 / 50.0) - 1
    expected = symbol_return - ((symbol_return + peer_return) / 2)
    assert abs(float(_row(rows, days[0], "510300.SH")["future_5d_excess_vs_equal_etf"]) - expected) < 0.0000000001


def test_future_price_shortage_marks_label_unavailable(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_label_rows(Path(result["output_path"]))
    last = _row(rows, days[-1], "510300.SH")

    assert last["label_available"] == "false"
    assert last["future_1d_return"] == ""
    assert last["future_5d_return"] == ""
    assert last["future_20d_return"] == ""


def test_missing_future_price_is_not_filled_with_zero(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    result = build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    rows = _read_label_rows(Path(result["output_path"]))
    last = _row(rows, days[-1], "159915.SZ")

    assert last["future_20d_return"] == ""
    assert last["future_20d_return"] not in {"0", "0.0", "0.0000000000"}


def test_label_store_does_not_write_main_account_ledgers(tmp_path: Path) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    build_label_matrix(days[0], days[-1], data_dir, project_paths(tmp_path))
    paths = project_paths(tmp_path)

    assert not (paths.data_dir / "orders").exists()
    assert not (paths.data_dir / "trades").exists()
    assert not (paths.data_dir / "portfolios").exists()
    assert (paths.data_dir / "labels" / f"label_matrix-{days[0]}-{days[-1]}.csv").exists()


def test_run_daily_does_not_read_label_files(sample_workspace: Path) -> None:
    paths = project_paths(sample_workspace)
    label_dir = paths.data_dir / "labels"
    label_dir.mkdir(parents=True, exist_ok=True)
    poison_label = label_dir / "label_matrix-2026-06-23-2026-06-23.csv"
    poison_label.write_text("this is not a valid label matrix for run-daily\n", encoding="utf-8")

    result = run_daily("2026-06-23", sample_workspace)

    assert result["date"] == "2026-06-23"
    assert poison_label.read_text(encoding="utf-8") == "this is not a valid label matrix for run-daily\n"


def test_build_labels_cli_command(tmp_path: Path, capsys) -> None:
    days = _trading_days(25)
    data_dir = tmp_path / "prices"
    _write_prices(data_dir, days)

    exit_code = cli.main(
        [
            "build-labels",
            "--start-date",
            days[0],
            "--end-date",
            days[-1],
            "--data",
            str(data_dir),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "label_matrix" in captured.out
    assert "LABEL_REPORT" in captured.out
