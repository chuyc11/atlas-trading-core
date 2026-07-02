from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from trading_core.equity_benchmark_claim_hardening.builder import DEFAULT_AS_OF_DATE
from trading_core.storage.file_paths import ProjectPaths


def make_claim_paths(tmp_path: Path) -> ProjectPaths:
    project = tmp_path / "work" / "trading-core"
    (project / "data").mkdir(parents=True)
    (project / "outputs").mkdir(parents=True)
    return ProjectPaths(tmp_path)


def write_claim_base_inputs(paths: ProjectPaths, *, as_of_date: str = DEFAULT_AS_OF_DATE, with_prices: bool = True, with_index: bool = False) -> None:
    dates = ["2026-06-29", "2026-06-30", as_of_date]
    selection_dir = paths.data_dir / "equity_selection" / "daily" / as_of_date
    tracking_dir = paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date
    selection_dir.mkdir(parents=True, exist_ok=True)
    tracking_dir.mkdir(parents=True, exist_ok=True)
    _write_json(selection_dir / "tradable_universe.json", [{"symbol": "000001.SZ", "passed": True}, {"symbol": "600000.SH", "passed": True}])
    _write_json(
        tracking_dir / "portfolio_performance_snapshot.json",
        {"records": [{"date": day, "daily_return": value} for day, value in zip(dates, [0.0, 0.01, -0.002], strict=True)]},
    )
    if with_prices:
        rows = []
        for symbol, base in [("000001.SZ", 10.0), ("600000.SH", 20.0)]:
            for idx, day in enumerate(dates):
                rows.append({"date": day, "symbol": symbol, "adj_close": base + idx})
        path = paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_parquet(path, index=False)
    if with_index:
        write_index_inputs(paths, as_of_date=as_of_date)


def write_index_inputs(paths: ProjectPaths, *, as_of_date: str = DEFAULT_AS_OF_DATE) -> None:
    dates = ["2026-06-29", "2026-06-30", as_of_date]
    rows = []
    for offset, benchmark_id in enumerate(["CSI300", "CSI500", "CSI1000"], start=1):
        for idx, day in enumerate(dates):
            close = 1000.0 * offset + idx * 10.0
            rows.append(
                {
                    "date": day,
                    "benchmark_id": benchmark_id,
                    "symbol_or_index_code": {"CSI300": "000300.SH", "CSI500": "000905.SH", "CSI1000": "000852.SH"}[benchmark_id],
                    "close": close,
                    "source_type": "local_index_price_panel",
                    "source_timestamp": "2026-07-01T15:00:00Z",
                    "is_placeholder": False,
                }
            )
    path = paths.data_dir / "equity_benchmarks" / "history" / "index_price_history_panel.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)


def claim_data_dir(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> Path:
    return paths.data_dir / "equity_benchmark_claim_hardening" / "daily" / as_of_date


def claim_json(paths: ProjectPaths, name: str, as_of_date: str = DEFAULT_AS_OF_DATE):
    return json.loads((claim_data_dir(paths, as_of_date) / f"{name}.json").read_text(encoding="utf-8"))


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
