from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from trading_core import cli
from trading_core.evaluation.strategy_leaderboard import build_strategy_leaderboard
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl


def _dates(count: int) -> list[str]:
    current = date(2026, 1, 1)
    result = []
    while len(result) < count:
        if current.weekday() < 5:
            result.append(current.isoformat())
        current += timedelta(days=1)
    return result


def _seed_backtest(
    root: Path,
    strategy_id: str,
    days: int,
    trades: int,
    final_asset: float,
    excess_return: float | None,
) -> None:
    start_date = "2026-01-01"
    end_date = "2026-04-30"
    suffix = f"{start_date}-{end_date}-{strategy_id}"
    base = root / "work" / "trading-core" / "data" / "backtests"
    dates = _dates(days)
    rows = []
    for index, row_date in enumerate(dates):
        asset = 100000.0 + (final_asset - 100000.0) * ((index + 1) / days)
        rows.append(
            {
                "date": row_date,
                "strategy_id": strategy_id,
                "total_asset": round(asset, 6),
                "daily_return": 0.001 if index else 0.0,
                "max_drawdown": 0.0,
            }
        )
    trade_rows = [
        {
            "trade_id": f"TRD-{strategy_id}-{index:03d}",
            "date": dates[min(index, len(dates) - 1)],
            "strategy_id": strategy_id,
            "commission": 1.0,
            "tax": 0.0,
            "net_amount": 1000.0,
        }
        for index in range(trades)
    ]
    write_jsonl(base / f"backtest_portfolio-{suffix}.jsonl", rows)
    write_jsonl(base / f"backtest_trades-{suffix}.jsonl", trade_rows)
    if excess_return is not None:
        write_json(
            base / f"backtest_benchmark-{suffix}.json",
            {
                "benchmarks": {"EQUAL_ETF": {"return": 0.001}, "CSI300": {"return": 0.0008}},
                "excess_return": {"EQUAL_ETF": excess_return, "CSI300": excess_return + 0.0002},
            },
        )


def test_strategy_leaderboard_ranks_only_supported_samples(tmp_path: Path) -> None:
    _seed_backtest(tmp_path, "strong_strategy", days=65, trades=12, final_asset=103000.0, excess_return=0.01)
    _seed_backtest(tmp_path, "small_sample_strategy", days=5, trades=2, final_asset=106000.0, excess_return=0.02)
    _seed_backtest(tmp_path, "missing_benchmark_strategy", days=70, trades=15, final_asset=104000.0, excess_return=None)

    result = build_strategy_leaderboard("2026-01-01", "2026-04-30", project_paths(tmp_path))

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    payload = read_json(Path(result["json_path"]))
    items = {row["strategy_id"]: row for row in result["items"]}

    assert result["items"][0]["strategy_id"] == "strong_strategy"
    assert items["strong_strategy"]["rank_eligible"] is True
    assert items["strong_strategy"]["admission_status"] == "shadow_allowed"
    assert items["small_sample_strategy"]["recommendation"] == "insufficient_sample"
    assert items["small_sample_strategy"]["rank"] > items["strong_strategy"]["rank"]
    assert items["missing_benchmark_strategy"]["recommendation"] == "not_recommended_missing_benchmark"
    assert payload["auto_strategy_status_mutation"] is False
    assert not (tmp_path / "work" / "trading-core" / "data" / "strategy_versions").exists()
    assert "No strategy status mutation" in report


def test_strategy_leaderboard_cli_writes_report(tmp_path: Path, monkeypatch) -> None:
    paths = project_paths(tmp_path)
    _seed_backtest(tmp_path, "strong_strategy", days=65, trades=12, final_asset=103000.0, excess_return=0.01)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["leaderboard", "--start-date", "2026-01-01", "--end-date", "2026-04-30"]) == 0

    assert (tmp_path / "work" / "trading-core" / "outputs" / "strategy-leaderboard-2026-01-01-2026-04-30.md").exists()
