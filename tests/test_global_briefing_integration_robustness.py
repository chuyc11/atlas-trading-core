from __future__ import annotations

from pathlib import Path

import pytest

from trading_core.daily_run import run_daily
from trading_core.storage.jsonl_store import write_json


def _gb_dir(root: Path) -> Path:
    path = root / "work" / "global-briefing" / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_macro(path: Path, date: str, text: str | None = None) -> None:
    if text is not None:
        (path / f"macro_signals-{date}.jsonl").write_text(text, encoding="utf-8")


def _write_snapshot(path: Path, date: str, items: list[dict] | None = None, raw: str | None = None) -> None:
    target = path / f"china-market-snapshot-{date}.json"
    if raw is not None:
        target.write_text(raw, encoding="utf-8")
    else:
        write_json(target, {"provider": "test", "items": items or []})


def _valid_macro_line(date: str, *, assets='["510300.SH"]', confidence: str = '"medium"') -> str:
    return (
        '{"macro_signal_id":"M-'
        + date
        + '","date":"'
        + date
        + '","region":"CHINA","theme":"test","scenario":"test",'
        + f'"confidence":{confidence},"affected_assets":{assets},"risk_flags":[],"status":"open"}}'
    )


def _fresh_snapshot_items() -> list[dict]:
    return [
        {"symbol": "510300.SH", "market": "A_SHARE", "price": 4.0, "previous_close": 3.98, "data_status": "ok"},
        {"symbol": "000300.SH", "market": "A_SHARE_INDEX", "price": 5000.0, "previous_close": 4980.0, "data_status": "ok"},
    ]


@pytest.mark.parametrize(
    ("date", "macro_text", "snapshot_items", "snapshot_raw", "expected_limitation"),
    [
        ("2026-07-01", None, _fresh_snapshot_items(), None, "missing macro_signals"),
        ("2026-07-02", "", _fresh_snapshot_items(), None, "empty macro_signals"),
        ("2026-07-03", "{bad json}\n" + _valid_macro_line("2026-07-03"), _fresh_snapshot_items(), None, "bad macro_signals JSONL line"),
        ("2026-07-06", '{"region":"CHINA","confidence":"medium","risk_flags":[]}\n', _fresh_snapshot_items(), None, "missing affected_assets"),
        ("2026-07-07", _valid_macro_line("2026-07-07", assets="[]"), _fresh_snapshot_items(), None, "empty affected_assets"),
        ("2026-07-08", _valid_macro_line("2026-07-08", confidence='"impossible"'), _fresh_snapshot_items(), None, "invalid confidence"),
        ("2026-07-09", _valid_macro_line("2026-07-09"), None, "{not-json", "invalid China market snapshot"),
        ("2026-07-10", _valid_macro_line("2026-07-10"), [{"symbol": "510300.SH", "market": "A_SHARE", "data_status": "ok"}], None, "missing price field"),
        ("2026-07-13", _valid_macro_line("2026-07-13"), [{"symbol": "510300", "market": "A_SHARE", "price": 4.0, "data_status": "ok"}], None, "missing_price: 510300.SH"),
    ],
)
def test_global_briefing_bad_inputs_degrade_without_illegal_trades(
    tmp_path: Path,
    date: str,
    macro_text: str | None,
    snapshot_items: list[dict] | None,
    snapshot_raw: str | None,
    expected_limitation: str,
) -> None:
    data_dir = _gb_dir(tmp_path)
    _write_macro(data_dir, date, macro_text)
    _write_snapshot(data_dir, date, snapshot_items, snapshot_raw)

    result = run_daily(date, tmp_path)
    combined_limitations = "\n".join(result["limitations"])

    assert expected_limitation in combined_limitations
    if expected_limitation == "bad macro_signals JSONL line":
        assert all(trade["symbol"] == "510300.SH" for trade in result["trades"])
    else:
        assert result["trades"] == []
    assert expected_limitation in result["report_markdown"]
    assert any(expected_limitation in warning for warning in result["health"]["warnings"])


def test_market_snapshot_mixed_change_pct_units_do_not_crash(tmp_path: Path) -> None:
    date = "2026-07-14"
    data_dir = _gb_dir(tmp_path)
    _write_macro(data_dir, date, _valid_macro_line(date))
    _write_snapshot(
        data_dir,
        date,
        [
            {"symbol": "510300.SH", "market": "A_SHARE", "price": 4.0, "previous_close": 3.98, "change_pct": 0.50, "change_pct_unit": "%", "data_status": "ok"},
            {"symbol": "000300.SH", "market": "A_SHARE_INDEX", "change_pct": 0.63, "change_pct_unit": "pct", "data_status": "ok"},
        ],
    )

    result = run_daily(date, tmp_path)

    assert result["benchmark"]["benchmarks"]["CSI300"]["return"] == pytest.approx(0.0063)
    assert result["health"]["warnings"] or result["orders"]
