from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from trading_core.storage.jsonl_store import write_json, write_jsonl


def write_test_calendar(root: Path) -> None:
    calendar_dir = root / "work" / "trading-core" / "data" / "equity_universe"
    calendar_dir.mkdir(parents=True, exist_ok=True)
    first_day = date(2026, 6, 1)
    rows = [
        {
            "date": (first_day + timedelta(days=offset)).isoformat(),
            "is_trading_day": (first_day + timedelta(days=offset)).weekday() < 5,
        }
        for offset in range(90)
    ]
    write_json(calendar_dir / "trading_calendar.json", {"rows": rows})


@pytest.fixture
def workspace_with_calendar(tmp_path: Path) -> Path:
    write_test_calendar(tmp_path)
    return tmp_path


@pytest.fixture
def sample_workspace(tmp_path: Path) -> Path:
    root = tmp_path
    write_test_calendar(root)
    data_dir = root / "work" / "global-briefing" / "data"
    data_dir.mkdir(parents=True)
    write_jsonl(
        data_dir / "macro_signals-2026-06-23.jsonl",
        [
            {
                "macro_signal_id": "MACRO-20260623-001",
                "date": "2026-06-23",
                "region": "CHINA",
                "theme": "policy_support",
                "scenario": "Policy support favors broad ETF exposure",
                "confidence": "medium",
                "affected_assets": ["510300.SH", "999999.SH"],
                "risk_flags": [],
                "status": "open",
            }
        ],
    )
    write_json(
        data_dir / "china-market-snapshot-2026-06-23.json",
        {
            "provider": "test",
            "items": [
                {
                    "symbol": "510300.SH",
                    "market": "A_SHARE",
                    "price": 4.0,
                    "change_pct": 1.0,
                    "provider": "test",
                    "data_status": "ok",
                },
                {
                    "symbol": "000300.SH",
                    "market": "A_SHARE_INDEX",
                    "price": 5000.0,
                    "change_pct": 0.5,
                    "provider": "test",
                    "data_status": "ok",
                },
            ],
        },
    )
    write_json(
        data_dir / "china-market-snapshot-2026-06-24.json",
        {
            "provider": "test",
            "items": [
                {
                    "symbol": "510300.SH",
                    "market": "A_SHARE",
                    "price": 4.1,
                    "change_pct": 2.5,
                    "provider": "test",
                    "data_status": "ok",
                },
                {
                    "symbol": "000300.SH",
                    "market": "A_SHARE_INDEX",
                    "price": 5050.0,
                    "change_pct": 1.0,
                    "provider": "test",
                    "data_status": "ok",
                },
            ],
        },
    )
    write_json(
        data_dir / "china-market-snapshot-2026-06-25.json",
        {
            "provider": "test",
            "items": [
                {
                    "symbol": "510300.SH",
                    "market": "A_SHARE",
                    "price": 4.2,
                    "previous_close": 4.1,
                    "provider": "test",
                    "data_status": "ok",
                },
                {
                    "symbol": "000300.SH",
                    "market": "A_SHARE_INDEX",
                    "price": 5100.0,
                    "previous_close": 5050.0,
                    "provider": "test",
                    "data_status": "ok",
                },
            ],
        },
    )
    return root
