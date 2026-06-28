from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from a_share_feature_test_utils import AS_OF_DATE
from trading_core.equity_data_refresh.data_refresh_audit import audit_a_share_daily_data_refresh
from trading_core.equity_data_refresh.data_refresh_builder import build_a_share_daily_data_refresh
from trading_core.equity_data_refresh.data_refresh_config import DATA_REFRESH_FILES, DATA_REFRESH_REPORTS
from trading_core.storage.file_paths import ProjectPaths


SYMBOLS = ["600001.SH", "600002.SH", "600003.SH"]


def make_data_refresh_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    paths = ProjectPaths(root)
    for relative in [
        "data/equity_universe",
        "data/equity_market/history",
        "data/equity_benchmarks/history",
        "data/equity_industry",
        "data/equity_fundamental/history",
        "data/equity_data_quality",
        "outputs/audit",
    ]:
        (project / relative).mkdir(parents=True, exist_ok=True)
    write_refresh_fixture(paths)
    return paths


def build_data_refresh_package(paths: ProjectPaths, **kwargs):
    return build_a_share_daily_data_refresh(paths=paths, as_of_date=AS_OF_DATE, **kwargs)


def audit_data_refresh_package(paths: ProjectPaths):
    return audit_a_share_daily_data_refresh(paths=paths, as_of_date=AS_OF_DATE)


def data_refresh_data_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_data_refresh" / "daily" / AS_OF_DATE


def data_refresh_json(paths: ProjectPaths, key: str):
    return json.loads((data_refresh_data_dir(paths) / DATA_REFRESH_FILES[key]).read_text(encoding="utf-8"))


def data_refresh_report(paths: ProjectPaths, key: str) -> str:
    return (paths.outputs_dir / "equity_data_refresh" / "daily" / AS_OF_DATE / DATA_REFRESH_REPORTS[key]).read_text(encoding="utf-8")


def write_refresh_fixture(paths: ProjectPaths) -> None:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    dates = ["2026-06-24", "2026-06-25", AS_OF_DATE]
    pd.DataFrame(
        [
            {
                "symbol": symbol,
                "exchange": "SSE",
                "market": "A_SHARE",
                "name": f"Name {idx}",
                "list_date": "2020-01-01",
                "delist_date": "",
                "board": "SSE_MAIN",
                "is_active": True,
                "source": "fixture",
                "source_timestamp": now,
            }
            for idx, symbol in enumerate(SYMBOLS, start=1)
        ]
    ).to_parquet(paths.data_dir / "equity_universe" / "equity_master.parquet", index=False)
    pd.DataFrame(
        [
            {"date": day, "exchange": exchange, "is_trading_day": True, "previous_trading_day": "", "next_trading_day": "", "source": "fixture", "source_timestamp": now}
            for day in dates
            for exchange in ["SSE", "SZSE"]
        ]
    ).to_parquet(paths.data_dir / "equity_universe" / "trading_calendar.parquet", index=False)
    price_rows = []
    adjusted_rows = []
    basic_rows = []
    for idx, symbol in enumerate(SYMBOLS, start=1):
        for offset, day in enumerate(dates):
            close = 10.0 * idx + offset
            price_rows.append({"date": day, "symbol": symbol, "open": close - 0.2, "high": close + 0.5, "low": close - 0.5, "close": close, "volume": 1000, "amount": 1000 * close, "turnover": 1.0, "pre_close": close - 1.0, "change": 1.0, "pct_change": 1.0, "source": "fixture", "source_timestamp": now, "provider": "fixture", "ingested_at": now})
            adjusted_rows.append({"date": day, "symbol": symbol, "adj_open": close - 0.2, "adj_high": close + 0.5, "adj_low": close - 0.5, "adj_close": close, "adj_factor": 1.0, "adjustment_type": "qfq", "source": "fixture", "source_timestamp": now, "provider": "fixture", "ingested_at": now})
            basic_rows.append({"date": day, "symbol": symbol, "turnover_rate": 1.0, "total_mv": 100000000.0, "circ_mv": 80000000.0, "source": "fixture", "source_timestamp": now, "provider": "fixture", "ingested_at": now})
    pd.DataFrame(price_rows).to_parquet(paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet", index=False)
    pd.DataFrame(adjusted_rows).to_parquet(paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet", index=False)
    pd.DataFrame(basic_rows).to_parquet(paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet", index=False)
    pd.DataFrame(
        [
            {"date": day, "benchmark_id": benchmark, "symbol_or_index_code": code, "open": 1000.0, "high": 1002.0, "low": 999.0, "close": 1001.0, "volume": 1000, "amount": 1001000.0, "source_type": "fixture", "source_path": "", "source_timestamp": now, "is_placeholder": False}
            for benchmark, code in [("CSI300", "000300.SH"), ("CSI500", "000905.SH"), ("CSI1000", "000852.SH")]
            for day in dates
        ]
    ).to_parquet(paths.data_dir / "equity_benchmarks" / "history" / "index_price_history_panel.parquet", index=False)
    pd.DataFrame([{"symbol": symbol, "industry_level_1": "Industry", "industry_level_2": "Sub", "source": "fixture", "source_timestamp": now} for symbol in SYMBOLS]).to_parquet(paths.data_dir / "equity_industry" / "industry_classification.parquet", index=False)
    pd.DataFrame([{"symbol": symbol, "report_date": "2026-03-31", "ann_date": "2026-04-30", "revenue": 1.0, "net_profit": 1.0, "source": "fixture", "source_timestamp": now, "provider": "fixture", "ingested_at": now} for symbol in SYMBOLS]).to_parquet(paths.data_dir / "equity_fundamental" / "history" / "basic_financials_history_panel.parquet", index=False)
