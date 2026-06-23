from __future__ import annotations

from pathlib import Path

from trading_core.accounting.consistency_checker import check_consistency, check_consistency_range
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl


def _seed_consistent_day(root: Path, day: str, *, cash: float = 95000.0, total_asset: float = 100000.0) -> None:
    paths = project_paths(root)
    market_value = total_asset - cash
    write_json(
        paths.dated_json("portfolios", "portfolio", day),
        {
            "date": day,
            "cash": cash,
            "market_value": market_value,
            "total_asset": total_asset,
            "daily_return": 0.0,
            "positions": [
                {
                    "symbol": "510300.SH",
                    "quantity": 1000,
                    "available_quantity": 1000,
                    "current_price": market_value / 1000,
                    "market_value": market_value,
                }
            ],
        },
    )
    write_jsonl(
        paths.dated_jsonl("signals", "trading_signals", day),
        [{"signal_id": f"SIG-{day}", "date": day, "symbol": "510300.SH"}],
    )
    write_jsonl(
        paths.dated_jsonl("orders", "orders", day),
        [{"order_id": f"ORD-{day}", "signal_id": f"SIG-{day}", "date": day, "risk_reason": "passed"}],
    )
    write_jsonl(
        paths.dated_jsonl("trades", "trades", day),
        [{"trade_id": f"TRD-{day}", "order_id": f"ORD-{day}", "date": day, "side": "BUY", "net_amount": 5000.0}],
    )
    write_jsonl(paths.dated_jsonl("valuations", "valuations", day), [{"date": day, "total_asset": total_asset}])
    write_json(paths.dated_json("attribution", "attribution", day), {"date": day, "total_pnl": 0.0, "residual_pnl": 0.0})


def test_consistency_checker_passes_clean_day(tmp_path: Path) -> None:
    _seed_consistent_day(tmp_path, "2026-06-23")

    result = check_consistency("2026-06-23", project_paths(tmp_path))

    assert result["passed"] is True
    assert result["errors"] == []
    assert Path(result["report_path"]).name == "CONSISTENCY-2026-06-23.md"
    assert read_json(Path(result["json_path"]))["passed"] is True


def test_consistency_checker_flags_accounting_breaks(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    _seed_consistent_day(tmp_path, "2026-06-23")
    _seed_consistent_day(tmp_path, "2026-06-24", cash=94000.0, total_asset=101000.0)
    portfolio_path = paths.dated_json("portfolios", "portfolio", "2026-06-24")
    portfolio = read_json(portfolio_path)
    portfolio["cash"] = -10.0
    portfolio["positions"][0]["available_quantity"] = 1001
    portfolio["positions"][0]["market_value"] = 1.0
    write_json(portfolio_path, portfolio)
    write_jsonl(paths.dated_jsonl("orders", "orders", "2026-06-24"), [{"order_id": "ORPHAN-ORDER", "date": "2026-06-24"}])
    write_jsonl(paths.dated_jsonl("trades", "trades", "2026-06-24"), [{"trade_id": "TRD-ORPHAN", "order_id": "NO-ORDER", "date": "2026-06-24", "side": "BUY", "net_amount": 1.0}])
    write_jsonl(paths.dated_jsonl("valuations", "valuations", "2026-06-24"), [{"date": "2026-06-24", "total_asset": 1.0}])
    write_json(paths.dated_json("attribution", "attribution", "2026-06-24"), {"date": "2026-06-24", "total_pnl": 999.0, "residual_pnl": 0.0})

    result = check_consistency("2026-06-24", paths)

    assert result["passed"] is False
    assert any("cash is negative" in error for error in result["errors"])
    assert any("total_asset does not equal" in error for error in result["errors"])
    assert any("available_quantity exceeds quantity" in error for error in result["errors"])
    assert any("position market_value mismatch" in error for error in result["errors"])
    assert any("cash ledger mismatch" in error for error in result["errors"])
    assert any("valuation total_asset mismatch" in error for error in result["errors"])
    assert any("attribution total_pnl mismatch" in error for error in result["errors"])
    assert any("orphan trade" in error for error in result["errors"])
    assert any("orphan order" in error for error in result["errors"])


def test_consistency_checker_range_aggregates_days(tmp_path: Path) -> None:
    _seed_consistent_day(tmp_path, "2026-06-23")
    _seed_consistent_day(tmp_path, "2026-06-24")

    result = check_consistency_range("2026-06-23", "2026-06-24", project_paths(tmp_path))

    assert result["passed"] is False
    assert len(result["items"]) == 2
    assert result["critical_errors"]
