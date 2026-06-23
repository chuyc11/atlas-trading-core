from __future__ import annotations

from pathlib import Path

from trading_core.evaluation.dry_run_auditor import audit_dry_run
from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl


def _seed_day(root: Path, day: str, *, total_asset: float = 100000.0, cash: float = 95000.0) -> None:
    paths = project_paths(root)
    write_json(
        paths.dated_json("runtime", "health", day),
        {
            "date": day,
            "errors": [],
            "input_files_missing": [],
            "portfolio_total_asset": total_asset,
            "orders_count": 1,
            "trades_count": 1,
            "rejected_orders_count": 0,
        },
    )
    write_json(
        paths.dated_json("portfolios", "portfolio", day),
        {
            "date": day,
            "cash": cash,
            "market_value": total_asset - cash,
            "total_asset": total_asset,
            "positions": [
                {
                    "symbol": "510300.SH",
                    "quantity": 1000,
                    "available_quantity": 1000,
                    "current_price": (total_asset - cash) / 1000,
                    "market_value": total_asset - cash,
                }
            ],
        },
    )
    write_jsonl(
        paths.dated_jsonl("orders", "orders", day),
        [
            {
                "order_id": f"ORD-{day}-001",
                "signal_id": f"SIG-{day}",
                "date": day,
                "symbol": "510300.SH",
                "side": "BUY",
                "status": "submitted",
                "risk_reason": "passed",
            }
        ],
    )
    write_jsonl(
        paths.dated_jsonl("trades", "trades", day),
        [
            {
                "trade_id": f"TRD-{day}-001",
                "order_id": f"ORD-{day}-001",
                "date": day,
                "symbol": "510300.SH",
                "side": "BUY",
                "filled_price": 5.0,
                "filled_quantity": 1000,
            }
        ],
    )
    write_json(paths.dated_json("snapshots", "data_quality", day), {"limitations": []})
    write_json(paths.data_dir / "evolution" / f"evolution-summary-{day}.json", {"rule_memory": {"rules": []}})


def test_dry_run_auditor_passes_clean_range(tmp_path: Path) -> None:
    _seed_day(tmp_path, "2026-06-23", total_asset=100000.0)
    _seed_day(tmp_path, "2026-06-24", total_asset=100200.0)

    result = audit_dry_run("2026-06-23", "2026-06-24", project_paths(tmp_path))

    assert result["passed"] is True
    assert result["critical_errors"] == []
    assert Path(result["report_path"]).name == "DRY_RUN_AUDIT-2026-06-23-2026-06-24.md"
    assert read_json(Path(result["json_path"]))["passed"] is True


def test_dry_run_auditor_flags_drift_and_duplicates(tmp_path: Path) -> None:
    paths = project_paths(tmp_path)
    _seed_day(tmp_path, "2026-06-23", total_asset=100000.0)
    _seed_day(tmp_path, "2026-06-24", total_asset=140000.0, cash=-1.0)
    portfolio_path = paths.dated_json("portfolios", "portfolio", "2026-06-24")
    portfolio = read_json(portfolio_path)
    portfolio["positions"][0]["available_quantity"] = 1001
    write_json(portfolio_path, portfolio)
    write_jsonl(
        paths.dated_jsonl("orders", "orders", "2026-06-24"),
        [
            {"order_id": "ORD-2026-06-23-001", "date": "2026-06-24", "symbol": "510300.SH", "side": "BUY", "status": "submitted", "price_quality": "stale"},
            {"order_id": "ORD-2026-06-24-002", "date": "2026-06-24", "symbol": "510300.SH", "side": "SELL", "status": "rejected", "risk_reason": "sell quantity exceeds available position"},
        ],
    )
    write_jsonl(
        paths.dated_jsonl("trades", "trades", "2026-06-24"),
        [
            {"trade_id": "TRD-2026-06-23-001", "order_id": "ORD-2026-06-23-001", "date": "2026-06-24", "symbol": "510300.SH", "side": "BUY", "filled_price": 5.0, "filled_quantity": 1000},
            {"trade_id": "TRD-2026-06-24-002", "order_id": "ORD-2026-06-24-002", "date": "2026-06-24", "symbol": "510300.SH", "side": "BUY", "filled_price": 5.0, "filled_quantity": 1000},
        ],
    )
    write_jsonl(paths.data_dir / "experiments" / "shadow_signals-2026-06-24.jsonl", [{"signal_id": "SHADOW", "cash": 1.0}])
    write_json(
        paths.data_dir / "evolution" / "evolution-summary-2026-06-24.json",
        {"rule_memory": {"rules": [{"rule_id": f"R{i}", "created_date": "2026-06-24"} for i in range(4)]}},
    )
    write_jsonl(
        paths.data_dir / "experiments" / "experiment_queue.jsonl",
        [
            {"experiment_id": "EXP-1", "rule_id": "RULE-1"},
            {"experiment_id": "EXP-1", "rule_id": "RULE-1"},
        ],
    )

    result = audit_dry_run("2026-06-23", "2026-06-24", paths)

    assert result["passed"] is False
    assert any("cash is negative" in item for item in result["critical_errors"])
    assert any("available_quantity exceeds quantity" in item for item in result["critical_errors"])
    assert any("duplicate order_id" in item for item in result["critical_errors"])
    assert any("duplicate trade_id" in item for item in result["critical_errors"])
    assert any("blocked data quality" in item for item in result["critical_errors"])
    assert any("shadow artifact" in item for item in result["critical_errors"])
    assert any("evolution proposals exceed throttle" in item for item in result["critical_errors"])
    assert result["rejection_reason_distribution"]["sell quantity exceeds available position"] == 1
