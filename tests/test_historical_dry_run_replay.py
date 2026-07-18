from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest

from trading_core.evaluation import historical_dry_run_replay
from trading_core.evaluation.historical_dry_run_replay import replay_dry_run, replay_last_trading_days
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json, write_jsonl


def _trading_days(count: int, start: date = date(2026, 1, 1)) -> list[str]:
    days = []
    current = start
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current.isoformat())
        current += timedelta(days=1)
    return days


def _write_prices(
    path: Path,
    days: list[str],
    *,
    quality: str = "fresh",
    include_510300: bool = True,
    primary_open_premium: float = 0.0,
) -> None:
    path.mkdir(parents=True, exist_ok=True)
    rows = ["date,symbol,open,high,low,close,volume,source,quality"]
    for index, day in enumerate(days):
        if include_510300:
            price = 4.0 + index * 0.01
            open_price = price + primary_open_premium
            high = max(open_price, price) + 0.02
            low = min(open_price, price) - 0.02
            rows.append(f"{day},510300.SH,{open_price:.4f},{high:.4f},{low:.4f},{price:.4f},100000,test,{quality}")
        other = 2.0 + index * 0.005
        rows.append(f"{day},159915.SZ,{other:.4f},{other + 0.02:.4f},{other - 0.02:.4f},{other:.4f},100000,test,fresh")
        index_price = 5000.0 + index
        rows.append(f"{day},000300.SH,{index_price:.4f},{index_price + 1:.4f},{index_price - 1:.4f},{index_price:.4f},100000,test,fresh")
    (path / "prices.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def _write_macro(root: Path, day: str, *, side: str = "LONG", symbol: str = "510300.SH") -> None:
    data_dir = root / "work" / "global-briefing" / "data"
    write_jsonl(
        data_dir / f"macro_signals-{day}.jsonl",
        [
            {
                "macro_signal_id": f"MACRO-{day}",
                "date": day,
                "region": "CHINA",
                "confidence": "medium",
                "affected_assets": [symbol],
                "side": side,
                "risk_flags": [],
                "status": "open",
            }
        ],
    )
    write_json(
        data_dir / f"china-market-snapshot-{day}.json",
        {"provider": "test", "items": [{"symbol": symbol, "price": 4.0, "previous_close": 3.99}]},
    )


def test_replay_last_30_trading_days_rejects_price_only_replay(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)

    result = replay_last_trading_days(30, days[-1], price_dir, project_paths(tmp_path))

    assert result["historical_replay_passed"] is False
    assert result["forward_30d_dry_run_passed"] is False
    assert result["trading_days_replayed"] == 30
    assert result["price_only_replay"] is True
    assert result["missing_global_briefing_days"] == days
    assert "price-only replay" in " ".join(result["warnings"])
    assert Path(result["report_path"]).name == "REPLAY_AUDIT.md"
    assert "historical_replay_requires_actionable_macro_signals" in result["consistency_status"]["critical_errors"]
    assert "historical_replay_requires_at_least_one_filled_trade" in result["consistency_status"]["critical_errors"]
    assert read_json(Path(result["json_path"]))["historical_replay_passed"] is False


def test_missing_macro_signals_records_warning_and_hold(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    replay_data = project_paths(tmp_path).data_dir / "replays" / f"replay-{days[0]}-{days[-1]}"
    first_signals = read_jsonl(replay_data / "signals" / f"trading_signals-{days[0]}.jsonl")

    assert result["historical_replay_passed"] is False
    assert first_signals[0]["side"] == "HOLD"
    assert "no_signal/HOLD" in first_signals[0]["reason"]
    assert any("no_signal/HOLD" in warning for warning in result["warnings"])


def test_replay_account_continues_across_days_and_t_plus_one(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)
    _write_macro(tmp_path, days[0])

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    replay_data = project_paths(tmp_path).data_dir / "replays" / f"replay-{days[0]}-{days[-1]}"
    day1 = read_json(replay_data / "portfolios" / f"portfolio-{days[0]}.json")
    day2 = read_json(replay_data / "portfolios" / f"portfolio-{days[1]}.json")

    assert result["historical_replay_passed"] is True
    assert day1["cash"] == 100000.0
    assert day2["cash"] < 100000.0
    assert day2["positions"][0]["available_quantity"] == 0
    assert day2["positions"][0]["pending_t1_quantity"] == day2["positions"][0]["quantity"]
    day3 = read_json(replay_data / "portfolios" / f"portfolio-{days[2]}.json")
    assert day3["positions"][0]["available_quantity"] == day2["positions"][0]["quantity"]
    assert result["T+1_status"]["passed"] is True


def test_replay_is_idempotent(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)
    _write_macro(tmp_path, days[0])

    first = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    second = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))

    assert second["historical_replay_passed"] == first["historical_replay_passed"]
    assert second["total_orders"] == first["total_orders"]
    assert second["total_trades"] == first["total_trades"]
    assert second["duplicate_order_status"]["passed"] is True
    assert second["duplicate_trade_status"]["passed"] is True


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [
        ("../2026-01-01", "2026-01-02"),
        ("2026-01-01", "..\\2026-01-02"),
        ("2026-1-1", "2026-01-02"),
        ("2026-01-03", "2026-01-02"),
    ],
)
def test_replay_rejects_unsafe_or_invalid_dates_without_deleting_files(
    tmp_path: Path,
    start_date: str,
    end_date: str,
) -> None:
    days = _trading_days(2)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(ValueError):
        replay_dry_run(start_date, end_date, price_dir, project_paths(tmp_path))

    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_replay_last_days_rejects_non_positive_window(tmp_path: Path) -> None:
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, _trading_days(2))

    with pytest.raises(ValueError, match="days must be positive"):
        replay_last_trading_days(0, "2026-01-02", price_dir, project_paths(tmp_path))


def test_missing_price_rejects_trade(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days, include_510300=False)
    _write_macro(tmp_path, days[0], symbol="510300.SH")

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    replay_data = project_paths(tmp_path).data_dir / "replays" / f"replay-{days[0]}-{days[-1]}"
    orders = read_jsonl(replay_data / "orders" / f"orders-{days[1]}.jsonl")
    trades = read_jsonl(replay_data / "trades" / f"trades-{days[1]}.jsonl")

    assert orders[0]["status"] == "rejected"
    assert orders[0]["price_quality"] == "missing"
    assert trades == []
    assert result["total_trades"] == 0


def test_replay_executes_prior_day_macro_signal_at_next_day_open(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days, primary_open_premium=0.10)
    _write_macro(tmp_path, days[0])

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    replay_data = project_paths(tmp_path).data_dir / "replays" / f"replay-{days[0]}-{days[-1]}"
    first_day_orders = read_jsonl(replay_data / "orders" / f"orders-{days[0]}.jsonl")
    next_day_orders = read_jsonl(replay_data / "orders" / f"orders-{days[1]}.jsonl")
    next_day_trades = read_jsonl(replay_data / "trades" / f"trades-{days[1]}.jsonl")

    assert first_day_orders == []
    assert len(next_day_orders) == 1
    assert len(next_day_trades) == 1
    assert next_day_orders[0]["signal_date"] == days[0]
    assert next_day_orders[0]["date"] == days[1]
    # The next bar has a different open and close, so this assertion proves
    # that the fill did not use either the source-day or execution-day close.
    assert next_day_orders[0]["estimated_price"] == pytest.approx(4.11)
    assert next_day_orders[0]["estimated_price"] != pytest.approx(4.01)
    assert next_day_orders[0]["execution_price_basis"] == "next_trading_day_open"
    assert next_day_trades[0]["signal_date"] == days[0]
    assert next_day_trades[0]["execution_price_basis"] == "next_trading_day_open"
    assert result["signal_execution_status"]["passed"] is True


def test_replay_rejects_actionable_signal_without_executable_next_day(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)
    _write_macro(tmp_path, days[-1])

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))

    assert result["price_only_replay"] is False
    assert result["total_trades"] == 0
    assert result["historical_replay_passed"] is False
    assert result["unexecuted_end_of_window_signal_count"] == 1
    assert "historical_replay_requires_at_least_one_filled_trade" in result["consistency_status"]["critical_errors"]


def test_replay_blocks_misdated_macro_signal_even_when_other_trade_is_valid(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)
    _write_macro(tmp_path, days[0])
    source = tmp_path / "work" / "global-briefing" / "data" / f"macro_signals-{days[0]}.jsonl"
    rows = read_jsonl(source)
    rows.append({**rows[0], "macro_signal_id": "MACRO-FUTURE", "date": days[1]})
    write_jsonl(source, rows)

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))

    assert result["total_trades"] == 1
    assert result["historical_replay_passed"] is False
    assert result["macro_signal_timing_violations"] == [
        f"{days[0]}: macro signal MACRO-FUTURE has source date {days[1]}"
    ]
    assert any(
        error.startswith("macro_signal_point_in_time_violation:")
        for error in result["consistency_status"]["critical_errors"]
    )


def test_replay_outputs_do_not_pollute_main_daily_run_dirs(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)

    replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    paths = project_paths(tmp_path)

    assert not paths.dated_json("portfolios", "portfolio", days[0]).exists()
    assert not paths.dated_jsonl("orders", "orders", days[0]).exists()
    assert (paths.data_dir / "replays" / f"replay-{days[0]}-{days[-1]}" / "portfolios" / f"portfolio-{days[0]}.json").exists()


def test_replay_audit_contains_required_forward_false(tmp_path: Path) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days)

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["forward_30d_dry_run_passed"] is False
    assert "forward_30d_dry_run_passed: False" in report
    assert "must not be represented as future 30-day forward dry-run validation" in report


def test_replay_critical_error_marks_historical_replay_failed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    days = _trading_days(30)
    price_dir = tmp_path / "prices"
    _write_prices(price_dir, days, quality="stale")
    _write_macro(tmp_path, days[0])

    def bad_process_signals(signals: list[dict[str, Any]], day: str, account: Any, prices: dict[str, dict[str, Any]], **_: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        return (
            [
                {
                    "order_id": f"ORD-{day}-BAD",
                    "signal_id": signals[0]["signal_id"],
                    "date": day,
                    "account_id": signals[0]["account_id"],
                    "symbol": "510300.SH",
                    "market": "A_SHARE",
                    "side": "BUY",
                    "quantity": 100,
                    "status": "submitted",
                    "risk_reason": "passed",
                }
            ],
            [],
        )

    monkeypatch.setattr(historical_dry_run_replay, "process_signals", bad_process_signals)

    result = replay_dry_run(days[0], days[-1], price_dir, project_paths(tmp_path))

    assert result["historical_replay_passed"] is False
    assert any("BUY on stale price" in error for error in result["consistency_status"]["critical_errors"])
