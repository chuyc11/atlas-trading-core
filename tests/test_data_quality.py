from trading_core.data.data_quality import limitation_for_quality, normalize_quality, trade_action_for_quality
from trading_core.data.price_loader import prices_by_symbol_from_snapshot
from trading_core.storage.jsonl_store import write_json


def test_data_quality_blocks_bad_buy() -> None:
    assert normalize_quality({"price": 1, "provider": "fallback vendor"}) == "fallback"
    assert trade_action_for_quality("fallback", "BUY")[0] == "REJECT"
    assert trade_action_for_quality("stale", "SELL")[0] == "ALLOW"
    assert limitation_for_quality("510300.SH", "stale")


def test_price_loader_reads_snapshot(tmp_path) -> None:
    path = tmp_path / "snapshot.json"
    write_json(path, {"items": [{"symbol": "510300.SH", "price": 4.0, "data_status": "ok"}]})
    rows = prices_by_symbol_from_snapshot(path, "2026-06-23")
    assert rows["510300.SH"]["price"] == 4.0
    assert rows["510300.SH"]["quality"] == "fresh"
